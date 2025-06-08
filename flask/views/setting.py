'''
    设置界面蓝图
'''

from flask import Blueprint, request, render_template, jsonify, Response, current_app
from config import user
from const import key_file, supershell_version_dict
from module.setting import clearUselessGroupMark
from module.server_files import downloadServerFile
import os


setting_view = Blueprint('setting', __name__)


@setting_view.route('/supershell/setting', methods=['GET'])
def setting_page():
    '''
        访问设置页面
    '''
    download_chunk_size = str(current_app.config['DOWNLOAD_CHUNK_SIZE'])
    upload_max_size = str(current_app.config['MAX_UPLOAD_SIZE'])
    return render_template('setting.html',
                           supershell_version=supershell_version_dict['version'],
                           year=supershell_version_dict['info'][supershell_version_dict['version']]['mtime'].split('-')[0],
                           username=user,
                           download_chunk_size=download_chunk_size,
                           upload_max_size=upload_max_size)


@setting_view.route('/supershell/setting/update/upload/size', methods=['POST'])
def upload_max_size():
    '''
        修改远程主机上传文件最大Size
    '''
    data = request.json
    size = data.get('size')
    try:
        new_size = int(size)
        current_app.config['MAX_UPLOAD_SIZE'] = new_size
        return jsonify({'stat': 'success', 'result': str(new_size)})
    except Exception as e:
        current_app.logger.exception(e)
        return {'stat': 'failed', 'result': str(e)}


@setting_view.route('/supershell/setting/update/download/chunk', methods=['POST'])
def download_chunk_size():
    '''
        修改远程主机下载文件Chunk Size
    '''
    data = request.json
    chunk = data.get('chunk')
    try:
        new_chunk = int(chunk)
        current_app.config['DOWNLOAD_CHUNK_SIZE'] = new_chunk
        return jsonify({'stat': 'success', 'result': str(new_chunk)})
    except Exception as e:
        current_app.logger.exception(e)
        return {'stat': 'failed', 'result': str(e)}


@setting_view.route('/supershell/setting/recovery', methods=['POST'])
def recovery():
    '''
        恢复默认设置
    '''
    try:
        current_app.config['DOWNLOAD_CHUNK_SIZE'] = 1 * 1024 * 1024
        current_app.config['MAX_UPLOAD_SIZE'] = 30 * 1024 * 1024
        return jsonify({'stat': 'success', 'result':
            {'download_chunk_size': current_app.config['DOWNLOAD_CHUNK_SIZE'],
             'upload_max_size': current_app.config['MAX_UPLOAD_SIZE']}})
    except Exception as e:
        current_app.logger.exception(e)
        return {'stat': 'failed', 'result': str(e)}


@setting_view.route('/supershell/setting/clear/groupmark/useless', methods=['POST'])
def clear_useless_group_mark():
    '''
        清除冗余分组备注记录接口
    '''
    clear_useless_group_mark_result = clearUselessGroupMark()
    return jsonify(clear_useless_group_mark_result)


@setting_view.route('/supershell/setting/download/rprikey', methods=['GET'])
def download_rprikey():
    '''
        rssh连接私钥文件下载接口
    '''
    response = Response(downloadServerFile(key_file), content_type='application/octet-stream')
    response.headers["Content-disposition"] = "attachment; filename*=utf-8''rprikey"
    response.headers['content-length'] = os.stat(key_file).st_size
    return response