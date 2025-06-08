'''
    会话进阶功能页方法
'''

from flask import current_app
from category.ssh import ssh_client
from category.rssh import rssh_client
from module.func import check_address, check_port


def sub_system(key_file, sessid, rssh_ip, rssh_port, sub_str):
    '''
        ssh子系统功能
    '''
    try:
        with ssh_client(key_file, sessid, rssh_ip, rssh_port) as ssh_target:
            try:
                ssh_target.connect_ssh()
            except Exception as e:
                current_app.logger.exception(e)
                return {'stat': 'failed', 'result': 'Ssh Connect Error'}
            sub_result = ssh_target.exec_subsystem(sub_str)
            return sub_result
    except Exception as e:
        current_app.logger.exception(e)
        return {'stat': 'failed', 'result': 'Key File Error'}


def listenProxy(key_file, sessid, rssh_ip, rssh_port, address_proxy, port_proxy, type_str):
    '''
        打开关闭代理监听功能
    '''
    try:
        # 检查代理地址是否合法
        if check_address(address_proxy) == False and address_proxy != '':
            return {'stat': 'failed', 'result': '代理地址不合法'}
        # 检查代理端口是否合法
        if check_port(port_proxy) == False:
            return {'stat': 'failed', 'result': '代理端口不合法'}

        with rssh_client(key_file, rssh_ip, rssh_port) as rssh_target:
            try:
                rssh_target.connect_rssh()
            except Exception as e:
                current_app.logger.exception(e)
                return {'stat': 'failed', 'result': 'Rssh Connect Error'}
            listen_proxy_cmd = 'listen -c ' + sessid + ' --' + type_str + ' ' + address_proxy + ':' + port_proxy
            current_app.logger.info('Listen Proxy Cmd: ' + str(listen_proxy_cmd))
            listen_proxy_result = rssh_target.exec_command(listen_proxy_cmd)
            return {'stat': 'success', 'result': listen_proxy_result['result'].strip()}
    except Exception as e:
        current_app.logger.exception(e)
        return {'stat': 'failed', 'result': 'Key File Error'}


def showListenedProxy(key_file, sessid, rssh_ip, rssh_port):
    '''
        显示已开启的代理监听功能
    '''
    try:
        with rssh_client(key_file, rssh_ip, rssh_port) as rssh_target:
            try:
                rssh_target.connect_rssh()
            except Exception as e:
                current_app.logger.exception(e)
                return {'stat': 'failed', 'result': 'Rssh Connect Error'}
            show_listened_proxy_cmd = 'listen -c ' + sessid + ' -l'
            current_app.logger.info('Show Listened Proxy Cmd: ' + str(show_listened_proxy_cmd))
            show_listened_proxy_result = rssh_target.exec_command(show_listened_proxy_cmd)
            return {'stat': 'success', 'result': show_listened_proxy_result['result'].strip()}
    except Exception as e:
        current_app.logger.exception(e)
        return {'stat': 'failed', 'result': 'Key File Error'}