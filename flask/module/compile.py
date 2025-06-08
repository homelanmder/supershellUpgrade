'''
    客户端生成相关方法
'''

from flask import current_app
from const import compiled_clients_file_path, support_os_arch_list, flow_list
from category.rssh import rssh_client
from module.func import check_address, check_port,query_db,query_file,delete_db
import json
import os
import time

import re


def get_compiled_clients_list():
    '''
        从json文件中获取已生成的客户端数据
    '''
    compiled_clients_list = []
    query="""
        SELECT 
            url_path,
            callback_address,
            goos,
            goarch,
            file_type,
            file_size,
            version,
            file_path,
            updated_at
        FROM downloads
    """
    rows = query_db(query)
    for row in rows:
        tmp_dict = {
            'filename': row[0].split('/')[-1],  # 提取文件名
            'address': row[1],
            'os': row[2],
            'arch': row[3],
            'filetype': row[4],
            'size': row[5]*1024*1024,  # 将 float 类型的大小转为字符串整数
            'version': row[6].split('-')[0],  # 提取 version 主版本号
            'time': row[8]  # 使用 updated_at 字段作为时间
        }
        compiled_clients_list.append(tmp_dict)
    return compiled_clients_list


def sorttime(dic):
    '''
        嵌套列表字典排序
    '''
    return dic['time']


def handle_compiled_clients(source_list, search_text):
    '''
        对全部已生成客户端数据进行处理，返回处理后的客户端数据（搜索和排序）
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

    # 嵌套列表字典排序
    source_list.sort(key=sorttime, reverse=True)
    return source_list


def get_real_filename(filename):
    '''
        根据客户端文件名找到真实文件名
    '''
    rows = query_file(filename)
    prefix = "/data"
    real_path = rows[0][0][len(prefix):]

    return real_path


def deleteCompileClient(key_file, rssh_ip, rssh_port, filename):
    '''
        删除已生成客户端
    '''
    try:
        delete_db(filename)

        with rssh_client(key_file, rssh_ip, rssh_port) as rssh_target:
            try:
                rssh_target.connect_rssh()
            except Exception as e:
                current_app.logger.exception(e)
                return {'stat': 'failed', 'result': 'Rssh Connect Error'}
            delete_cmd = 'link -r ' + filename
            delete_result = rssh_target.exec_command(delete_cmd)
            if delete_result['stat'] == 'success':
                if 'Removed' in delete_result['result']:
                    return delete_result
                else:
                    return {'stat': 'failed', 'result': delete_result['result']}
            else:
                return delete_result
    except Exception as e:
        current_app.logger.exception(e)
        return {'stat': 'failed', 'result': 'Key File Error'}


def check_compile_input(filename, address, port, os_arch, address_proxy, port_proxy, flow, upx, garble,process,log_level):
    '''
        检查生成客户端Payload提交的输入是否合法
    '''
    try:
        # 检查文件名，只能包含大小写英文字母、数字、下划线和点
        if bool(re.match("^[A-Za-z0-9_.]*$", filename)) == False or filename == '':
            return {'stat': 'failed', 'result': '文件名只能包含大小写英文字母、数字、下划线和点'}
        # 检查回连地址是否合法
        if check_address(address) == False:
            return {'stat': 'failed', 'result': '回连地址不合法'}
        # 检查回连端口是否合法
        if check_port(port) == False:
            return {'stat': 'failed', 'result': '回连端口不合法'}
        # 检查系统架构是否在支持列表中
        if os_arch not in support_os_arch_list:
            return {'stat': 'failed', 'result': '系统架构不支持'}
        # 检查代理地址是否合法
        if check_address(address_proxy) == False and address_proxy != '':
            return {'stat': 'failed', 'result': '代理地址不合法'}
        # 检查代理端口是否合法
        if check_port(port_proxy) == False and port_proxy != '':
            return {'stat': 'failed', 'result': '代理端口不合法'}
        # 检查流量伪装类型是否在列表中
        if flow not in flow_list and flow != '':
            return {'stat': 'failed', 'result': '流量类型不支持'}
        # 检查upx是否合法
        if upx not in [True, False]:
            return {'stat': 'failed', 'result': '压缩参数不合法'}
        # 检查garble是否合法
        if garble not in [True, False]:
            return {'stat': 'failed', 'result': '免杀参数不合法'}
        make_input_dict = {
            'filename': filename,
            'address': address,
            'port': port,
            'os_arch': os_arch,
            'address_proxy': address_proxy,
            'port_proxy': port_proxy,
            'flow': flow,
            'upx': upx,
            'garble': garble,
            'process':process,
            'log_level':log_level
        }
        return {'stat': 'success', 'result': make_input_dict}
    except Exception as e:
        current_app.logger.exception(e)
        return {'stat': 'failed', 'result': '异常错误，参数校验不通过'}


def makeClient(key_file, rssh_ip, rssh_port, make_input_dict):
    '''
        生成客户端Payload
    '''
    try:
        with rssh_client(key_file, rssh_ip, rssh_port) as rssh_target:
            try:
                rssh_target.connect_rssh()
            except Exception as e:
                current_app.logger.exception(e)
                return {'stat': 'failed', 'result': 'Rssh Connect Error'}
            proxy_cmd = '--proxy ' + make_input_dict['address_proxy'] + ':' + make_input_dict['port_proxy'] if make_input_dict['address_proxy'] != '' and make_input_dict['port_proxy'] != '' else ''
            flow_cmd = '--' + make_input_dict['flow'] if make_input_dict['flow'] != '' and make_input_dict['flow'] != 'ssh' else ''
            upx = '--upx' if make_input_dict['upx'] else ''
            garble = '--garble' if make_input_dict['garble'] else ''
            os, arch = make_input_dict['os_arch'].split('/')
            if (os == 'windows' and arch == 'dll') or (os == 'linux' and arch == 'so'):
                make_cmd = 'link --name ' + make_input_dict['filename'] + ' --goos ' + os + ' --shared-object -s ' + \
                           make_input_dict['address'] + ':' + make_input_dict['port'] + ' ' + upx + ' ' + garble + ' ' + proxy_cmd + ' ' + flow_cmd + ' '+ '--process'+' '+make_input_dict['process'] + ' ' + '--log-level' + ' '+ make_input_dict['log_level']
            else:
                make_cmd = 'link --name ' + make_input_dict['filename'] + ' --goos ' + os + ' --goarch ' + arch + ' -s ' + \
                           make_input_dict['address'] + ':' + make_input_dict['port'] + ' ' + upx + ' ' + garble + ' ' + proxy_cmd + ' ' + flow_cmd +' '+ '--process'+' '+make_input_dict['process'] + ' ' + '--log-level' + ' '+ make_input_dict['log_level']
            current_app.logger.info('Make client Cmd: ' + str(make_cmd))
            make_result = rssh_target.exec_command(make_cmd)
            if make_result['stat'] == 'success':
                if 'http' in make_result['result']:
                    return make_result
                else:
                    return {'stat': 'failed', 'result': make_result['result']}
            else:
                return make_result
    except Exception as e:
        current_app.logger.exception(e)
        return {'stat': 'failed', 'result': 'Key File Error'}