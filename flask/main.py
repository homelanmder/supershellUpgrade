'''
    flask入口
'''

from flask import Flask, request, redirect
# from const import key_file, rssh_ip, rssh_port
# from category.rssh import rssh_client
from views import login, client, webhook, session_info, session_shell, session_files, \
    no_session, server_files, setting, compiled, session_memfd, session_advanced, notes, \
    monitor, log
from const import log_path
from config import user, global_salt
from module.func import no_proxy
import jwt
import logging
import time

# with rssh_client(key_file, rssh_ip, rssh_port) as rssh_target:
#     try:
#         rssh_target.connect_rssh()
#     except Exception as e:
#         current_app.logger.exception(e)
#         return {'stat': 'failed', 'result': 'Rssh Connect Error'}
#     webhook_cmd = 'webhook --on http://flask:5000/supershell/webhook‘
#     rssh_target.exec_command(webhook_cmd)


# 初始化flask对象
app = Flask(__name__)


# 业务日志
log_handler = logging.FileHandler(log_path + '/flask.log', encoding='UTF-8')
app.logger.setLevel(logging.INFO)
log_format = logging.Formatter('%(asctime)s - %(levelname)s - %(filename)s - %(funcName)s - %(lineno)s - %(message)s')
log_handler.setFormatter(log_format)
app.logger.addHandler(log_handler)


# 定义全局参数
app.config['DOWNLOAD_CHUNK_SIZE'] = 1 * 1024 * 1024    # 远程主机文件下载的Chunk_Size
app.config['MAX_UPLOAD_SIZE'] = 30 * 1024 * 1024    # 远程主机文件上传的最大Size
app.config['START_TIME'] = int(time.time())    # 获取supershell开始运行时的时间戳


# 注册蓝图
app.register_blueprint(login.login_view)
app.register_blueprint(client.client_view)
app.register_blueprint(webhook.webhook_view)
app.register_blueprint(session_info.session_info_view)
app.register_blueprint(session_shell.session_shell_view)
app.register_blueprint(session_files.session_files_view)
app.register_blueprint(no_session.no_session_view)
app.register_blueprint(server_files.server_files_view)
app.register_blueprint(setting.setting_view)
app.register_blueprint(compiled.compile_view)
app.register_blueprint(session_memfd.session_memfd_view)
app.register_blueprint(session_advanced.session_advanced_view)
app.register_blueprint(notes.notes_view)
app.register_blueprint(monitor.monitor_view)
app.register_blueprint(log.log_view)


# 所有请求前的权限认证（除去no_proxy中定义的接口）
@app.before_request
def check_login():
    '''判断token是否合法'''
    if no_proxy(request.path):
        return None
    else:
        try:
            token = request.cookies.get('token')
            result = jwt.decode(token, global_salt, algorithms=['HS256'])
            if result['username'] == user:
                return None
            else:
                return redirect('/supershell/login')
        except:
            return redirect('/supershell/login')