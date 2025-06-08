'''
    客户端列表相关方法
'''

from flask import current_app
from category.redisclient import RedisClient, connect_redis
from category.rssh import rssh_client
from module.webhook import handle_client_data
from module.session_info import check_key
import html
import time


def get_source_list():
    '''
        从redis内存数据中获取列表类型客户端数据
    '''
    source_list = []
    client = RedisClient(0)
    for sessid in client.conn.keys():
        tmp_dict = {}
        for key in client.conn.hkeys(sessid.decode()):
            tmp_dict[key.decode()] = client.conn.hget(sessid.decode(), key.decode()).decode()
        source_list.append(tmp_dict)
    current_app.logger.info('Redis Raw Client Data: ' + str(source_list))
    return source_list


def sorttime(dic):
    '''
        嵌套列表字典排序
    '''
    return dic['time']


def handle_clients(source_list, search_text, filter_choose):
    '''
        对全部客户端数据进行处理，返回处理后的客户端数据（搜索、筛选和排序）
    '''
    # 数据搜索
    if search_text != '':
        search_list = []
        for l in source_list:
            for e in l.values():
                if search_text.lower() in e.lower():
                    search_list.append(l)
                    break
        source_list = search_list

    # 数据筛选
    if filter_choose != {}:
        # k是attribution、os、arch、version、status和group
        for k in filter_choose.keys():
            filter_list = []
            # c是6个筛选项列表中的每个值
            for c in filter_choose[k]:
                # s是客户端list中的每一个条目
                for s in source_list:
                    if c == s[k]:
                        filter_list.append(s)
            source_list = filter_list

    # 嵌套列表字典排序
    source_list.sort(key=sorttime, reverse=True)
    return source_list


def get_filter_dict(source_list):
    '''
        获取全部数据特定项的全部取值，作为筛选的条件项
    '''
    # filter_dict = {
    #     'attribution': [],
    #     'os': [],
    #     'arch': [],
    #     'version': [],
    #     'group': [],
    #     'status': []
    # }
    # for s in source_list:
    #     for k in filter_dict.keys():
    #         if s[k] not in filter_dict[k]:
    #             filter_dict[k].append(s[k])
    # return filter_dict
    filter_dict = {
        'attribution': [],
        'os': [],
        'arch': [],
        'version': [],
        'group': [],
        'status': []
    }

    for s in source_list:
        for k in filter_dict:
            val = s.get(k)
            if val is not None and val not in filter_dict[k]:
                filter_dict[k].append(val)

    return filter_dict

def update_filter_choose(filter_choose, filter_dict, new_filter_dict):
    '''
        根据新获取的filter_dict：
        去掉filter_choose中已经不存在的筛选项，
        同时增加filter_dict新增的筛选项
    '''
    new_filter_choose = {}
    for key in filter_choose.keys():
        # 在每个字段对应的筛选项列表中选出在filter_choose中但不在new_filter_dict的元素列表，
        # 即获取要去除数据中已经不存在的筛选项
        removed_list = list(set(filter_choose[key]).difference(set(new_filter_dict[key])))
        # 在每个字段对应的筛选项列表中选出在new_filter_dict中但不在filter_dict的元素列表，
        # 即获取要增加数据中新增的筛选项
        add_list = list(set(new_filter_dict[key]).difference(set(filter_dict[key])))

        # 去除旧的筛选项
        new_list = list(set(filter_choose[key]) - set(removed_list))
        # 增加新的筛选项
        new_list = new_list + add_list
        new_filter_choose[key] = new_list
    return new_filter_choose


def writeInfo(group, mark, sessid):
    '''
        详细信息写入分组和备注信息
    '''
    try:
        # 写入客户端会话redis
        client = RedisClient(0)
        client.conn.hset(sessid, "group", html.escape(group))
        client.conn.hset(sessid, "mark", html.escape(mark))

        #写入分组、备注历史记录redis
        hostname = client.conn.hget(sessid, "hostname").decode()
        history = connect_redis(1)
        history.hset(hostname, "group", html.escape(group))
        history.hset(hostname, "mark", html.escape(mark))
        history.close()

        return {"stat": "success", "result": sessid}
    except Exception as e:
        current_app.logger.exception(e)
        return {"stat": "failed", "result": str(e)}


def disconnectClient(key_file, rssh_ip, rssh_port, sessid):
    '''
        断开连接
    '''
    try:
        with rssh_client(key_file, rssh_ip, rssh_port) as rssh_target:
            try:
                rssh_target.connect_rssh()
            except Exception as e:
                current_app.logger.exception(e)
                return {'stat': 'failed', 'result': 'Rssh Connect Error'}
            kill_cmd = 'kill -y ' + sessid
            kill_result = rssh_target.exec_command(kill_cmd)
            if kill_result['stat'] == 'success':
                if 'killed' in kill_result['result']:
                    return kill_result
                elif 'No clients matched' in kill_result['result']:
                    client = RedisClient(0)
                    client.conn.hset(sessid, "status", "false")
                    return {'stat': 'failed', 'result': kill_result['result']}
                else:
                    return {'stat': 'failed', 'result': kill_result['result']}
            else:
                return kill_result
    except Exception as e:
        current_app.logger.exception(e)
        return {'stat': 'failed', 'result': 'Key File Error'}


def deleteClient(sessid):
    '''
        删除记录
    '''
    try:
        client = RedisClient(0)
        client.conn.delete(sessid)
        return {"stat": "success", "result": sessid}
    except Exception as e:
        current_app.logger.exception(e)
        return {"stat": "failed", "result": str(e)}


def flush_redis():
    '''
        清空客户端会话redis
    '''
    client = RedisClient(0)
    for elem in client.conn.keys():
        client.conn.delete(elem)


def set_online_client_from_rssh(key_file, rssh_ip, rssh_port, ls_result):
    '''
        从rssh服务器中获取在线客户端写入redis
    '''
    try:
        error_num = 0
        flush_redis()
        line_list = ls_result.split('\n')
        for line in line_list:
            client_dict = {}
            sessid = line.split(' ')[0]
            hostname = line.split(' ')[2]
            address = line.split(' ')[3][:-1]
            version = line.split(' ')[-1]
            tim = time.strftime("%Y-%m-%dT%H:%M:%S.1", time.localtime())
            client_dict['Full'] = '{"Status":"connected", "ID":"' + sessid + '","IP":"' + address + '","HostName":"' + hostname + '","Version":"' + version + '","Timestamp":"' + tim + '"}'
            handle_result = handle_client_data(client_dict, key_file, rssh_ip, rssh_port)
            if handle_result['stat'] == 'failed':
                error_num = error_num + 1
        if error_num == 0:
            return {'stat': 'success', 'result': 'calibration'}
        else:
            return {'stat': 'failed', 'result': str(error_num) + ' records calibration error'}
    except Exception as e:
        current_app.logger.exception(e)
        return {'stat': 'failed', 'result': str(e)}


def calibrationClients(key_file, rssh_ip, rssh_port):
    '''
        客户端数据校准方法
    '''
    try:
        with rssh_client(key_file, rssh_ip, rssh_port) as rssh_target:
            try:
                rssh_target.connect_rssh()
            except Exception as e:
                current_app.logger.exception(e)
                return {'stat': 'failed', 'result': 'Rssh Connect Error'}
            ls_cmd = 'ls'
            ls_result = rssh_target.exec_command(ls_cmd)
            if ls_result['stat'] == 'success':
                if ls_result['result'] == 'No RSSH clients connected':
                    flush_redis()
                    return {'stat': 'success', 'result': ls_result['result']}
                else:
                    calibration_result = set_online_client_from_rssh(key_file, rssh_ip, rssh_port, ls_result['result'])
                    return calibration_result
            else:
                return ls_result
    except Exception as e:
        current_app.logger.exception(e)
        return {'stat': 'failed', 'result': 'Key File Error'}


def deleteAllOffClients():
    '''
        删除全部离线客户端
    '''
    try:
        client = RedisClient(0)
        for sessid in client.conn.keys():
            if client.conn.hget(sessid.decode(), 'status').decode() == 'false':
                client.conn.delete(sessid.decode())
        return {"stat": "success", "result": "deleteAllOff"}
    except Exception as e:
        current_app.logger.exception(e)
        return {"stat": "failed", "result": str(e)}


# def disconnectAllClients(key_file, rssh_ip, rssh_port):
#     '''
#         断开全部连接
#     '''
#     try:
#         with rssh_client(key_file, rssh_ip, rssh_port) as rssh_target:
#             try:
#                 rssh_target.connect_rssh()
#             except Exception as e:
#                 current_app.logger.exception(e)
#                 return {'stat': 'failed', 'result': 'Rssh Connect Error'}
#             kill_cmd = 'kill *'
#             kill_result = rssh_target.exec_command(kill_cmd)
#             return kill_result
#     except Exception as e:
#         current_app.logger.exception(e)
#         return {'stat': 'failed', 'result': 'Key File Error'}


def disconnectBatchClients(key_file, rssh_ip, rssh_port, sessid_list_str):
    '''
        批量断开连接
    '''
    try:
        sessid_list = sessid_list_str.split(',')
        current_app.logger.info('Received batch disconnect request, sessid: ' + str(sessid_list))
        success_sessid_num = 0
        failed_sessid_num = 0
        for sessid in sessid_list:
            if check_key(sessid) == 0:
                failed_sessid_num = failed_sessid_num + 1
                current_app.logger.info('Batch disconnect failed. No session in redis database: ' + sessid)
            else:
                kill_result = disconnectClient(key_file, rssh_ip, rssh_port, sessid)
                if kill_result["stat"] == "failed":
                    failed_sessid_num = failed_sessid_num + 1
                    current_app.logger.info('Batch disconnect failed: ' + kill_result['result'])
                else:
                    success_sessid_num = success_sessid_num + 1
        if success_sessid_num == 0:
            return {'stat': 'failed', 'result': 'Success: ' + str(success_sessid_num) + ' Failed: ' + str(failed_sessid_num)}
        else:
            return {'stat': 'success', 'result': 'Success: ' + str(success_sessid_num) + ' Failed: ' + str(failed_sessid_num)}
    except Exception as e:
        current_app.logger.exception(e)
        return {'stat': 'failed', 'result': str(e)}


def deleteBatchClients(sessid_list_str):
    '''
        批量删除离线记录
    '''
    try:
        sessid_list = sessid_list_str.split(',')
        current_app.logger.info('Received batch deletion request for offline records, sessid: ' + str(sessid_list))
        success_sessid_num = 0
        failed_sessid_num = 0
        client = RedisClient(0)
        for sessid in sessid_list:
            if check_key(sessid) == 0:
                failed_sessid_num = failed_sessid_num + 1
                current_app.logger.info('Batch deletion of offline records failed. No session in redis database: ' + sessid)
            else:
                if client.conn.hget(sessid, 'status').decode() == 'false':
                    client.conn.delete(sessid)
                    success_sessid_num = success_sessid_num + 1
                else:
                    failed_sessid_num = failed_sessid_num + 1
                    current_app.logger.info('Batch deletion of offline records failed: sessid' + sessid + '  is online and cannot be deleted')
        if success_sessid_num == 0:
            return {'stat': 'failed', 'result': 'Success: ' + str(success_sessid_num) + ' Failed: ' + str(failed_sessid_num)}
        else:
            return {'stat': 'success', 'result': 'Success: ' + str(success_sessid_num) + ' Failed: ' + str(failed_sessid_num)}
    except Exception as e:
        current_app.logger.exception(e)
        return {'stat': 'failed', 'result': str(e)}


def writeBatchInfo(group, mark, sessid_list_str):
    '''
        批量写入分组和备注信息
    '''
    try:
        sessid_list = sessid_list_str.split(',')
        current_app.logger.info('Received batch write group note request, sessid: ' + str(sessid_list))
        success_sessid_num = 0
        failed_sessid_num = 0
        client = RedisClient(0)
        history = connect_redis(1)
        for sessid in sessid_list:
            if check_key(sessid) == 0:
                failed_sessid_num = failed_sessid_num + 1
                current_app.logger.info('Batch write group note failed. No session in redis database: ' + sessid)
            else:
                # 写入客户端会话redis
                client.conn.hset(sessid, "group", html.escape(group))
                client.conn.hset(sessid, "mark", html.escape(mark))

                # 写入分组、备注历史记录redis
                hostname = client.conn.hget(sessid, "hostname").decode()
                history.hset(hostname, "group", html.escape(group))
                history.hset(hostname, "mark", html.escape(mark))
                success_sessid_num = success_sessid_num + 1
        history.close()
        if success_sessid_num == 0:
            return {'stat': 'failed', 'result': 'Success: ' + str(success_sessid_num) + ' Failed: ' + str(failed_sessid_num)}
        else:
            return {'stat': 'success', 'result': 'Success: ' + str(success_sessid_num) + ' Failed: ' + str(failed_sessid_num)}
    except Exception as e:
        current_app.logger.exception(e)
        return {'stat': 'failed', 'result': str(e)}