'''
    通用方法
'''

import jwt
import time
import ipaddress
import sqlite3
import os
import re
from const import compiled_clients_file_path
def query_db(query):
    db_path = compiled_clients_file_path + '/data.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(query)
    rows=cursor.fetchall()
    return rows

def query_file(filename):
    db_path = compiled_clients_file_path + '/data.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    query = "SELECT file_path FROM downloads where url_path = ?"
    cursor.execute( query,(filename ,))
    rows=cursor.fetchall()
    return rows

def delete_db(filename):
    #删除数据库记录
    db_path = compiled_clients_file_path + '/data.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    query = "DELETE FROM downloads where url_path = ?"
    cursor.execute(query,(filename,))
#     #删除文件
#     prefix = "/data"
#     rows=query_file(filename)
#     if len(rows) > 0:
#         real_path = rows[0][0][len(prefix):]
#         printf(real_path)
#         os.remove(real_path)



def get_jwt_token(username, salt, exp_time):
    '''
        获取jwt token
    '''
    exp = int(time.time() + exp_time)
    data = {
      "username": username,
      "exp": exp
    }
    token = jwt.encode(payload=data, key=salt, algorithm='HS256')
    return token


def no_proxy(path):
    '''
        设置拦截器白名单
    '''
    white_list = ['js', 'css', 'png', 'svg', 'jpg', 'jpeg']
    white_path_list = ['/supershell/login',
                       '/supershell/login/auth',
                       '/supershell/webhook',
                       '/supershell/share/shell/auth',
                       '/supershell/share/shell/login',
                       '/supershell/share/shell/login/auth',
                       '/supershell/session/nginx/void',
                       '/supershell/memfd/inject/auth'
                       ]
    back = path.split('.')[-1]
    if back.lower() in white_list or path in white_path_list \
            or path.startswith('/supershell/server/files/download/')\
            or path.startswith('/supershell/compile/download/'):
        return True
    else:
        return False


def check_address(address):
    '''
        检查地址是否合法，合法的地址为ipv4或域名
    '''
    try:
        ipaddress.ip_address(address)
        return True
    except:
        if bool(re.match("(?i)^([a-z0-9]+(-[a-z0-9]+)*\.)+[a-z]{2,}$", address)) == False:
            return False
        else:
            return True


def check_port(port):
    '''
        检查端口是否合法
    '''
    if bool(re.match("^([1-9][0-9]{0,3}|[1-5][0-9]{4}|6[0-4][0-9]{3}|65[0-4][0-9]{2}|655[0-2][0-9]|6553[0-5])$", port)) == False:
        return False
    else:
        return True