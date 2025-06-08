'''
    一些固定的全局变量配置
'''


# 连接rssh服务器的ip，不是rssh服务的开放ip
rssh_ip = 'rssh'

# rssh服务器的端口
rssh_port = 3232

# redis的ip
redis_ip = 'redis'

# redis的端口
redis_port = 6379

# redis的密码
redis_password = 'tdragon6'

# 连接rssh服务器的私钥
key_file = '/volume/key/id_rsa'

# rssh服务器的公钥
public_key_file = '/volume/authorized_keys'

# windows待检测是否存在的磁盘列表
win_disk = ['/C:', '/D:', '/E:', '/F:', '/G:', '/X:', '/Y:', 'Z:']

# 常用文件路径
server_files_path = '/downloads'

# 服务器文件下载Chunk Size
server_files_chunk_size = 20 * 1024 * 1024

# 已生成的客户端记录json文件路径
compiled_clients_file_path = '/cache'

# 备忘录路径
notes_path = '/volume/notes.md'

# 日志路径
log_path = '/volume/log'

# 日志最后几行
log_last_lines = 3000

#客户端日志
log_level=['INFO','WARNING','ERROR','FATAL','DISABLED']

# 客户端支持生成的系统架构数据列表
support_os_arch_list = ['android/amd64',
                        'android/arm64',
                        'darwin/amd64',
                        'darwin/arm64',
                        'dragonfly/amd64',
                        'freebsd/386',
                        'freebsd/amd64',
                        'freebsd/arm',
                        'freebsd/arm64',
                        'illumos/amd64',
                        'linux/386',
                        'linux/amd64',
                        'linux/arm',
                        'linux/arm64',
                        'linux/ppc64le',
                        'linux/s390x',
                        'linux/so',
                        'netbsd/386',
                        'netbsd/amd64',
                        'netbsd/arm',
                        'netbsd/arm64',
                        'openbsd/386',
                        'openbsd/amd64',
                        'openbsd/arm',
                        'openbsd/arm64',
                        'openbsd/mips64',
                        'solaris/amd64',
                        'windows/386',
                        'windows/amd64',
                        'windows/dll']

# 全部go支持的客户端支持生成的系统架构数据列表
all_go_support_os_arch_list = ['aix/ppc64',
                        'android/386',
                        'android/amd64',
                        'android/arm',
                        'android/arm64',
                        'darwin/amd64',
                        'darwin/arm64',
                        'dragonfly/amd64',
                        'freebsd/386',
                        'freebsd/amd64',
                        'freebsd/arm',
                        'freebsd/arm64',
                        'freebsd/riscv64',
                        'illumos/amd64',
                        'ios/amd64',
                        'ios/arm64',
                        'js/wasm',
                        'linux/386',
                        'linux/amd64',
                        'linux/arm',
                        'linux/arm64',
                        'linux/loong64',
                        'linux/mips',
                        'linux/mips64',
                        'linux/mips64le',
                        'linux/mipsle',
                        'linux/ppc64',
                        'linux/ppc64le',
                        'linux/riscv64',
                        'linux/s390x',
                        'netbsd/386',
                        'netbsd/amd64',
                        'netbsd/arm',
                        'netbsd/arm64',
                        'openbsd/386',
                        'openbsd/amd64',
                        'openbsd/arm',
                        'openbsd/arm64',
                        'openbsd/mips64',
                        'plan9/386',
                        'plan9/amd64',
                        'plan9/arm',
                        'solaris/amd64',
                        'windows/386',
                        'windows/amd64',
                        'windows/arm',
                        'windows/arm64']

# 流量伪装类型数据列表
flow_list = ['ssh', 'ws', 'tls', 'wss']

# Supershell版本信息
supershell_version_dict = {
    "version": "v2.0.0",
    "info": {
        "v1.0.0": {
            "description": [
                "支持团队并发协作，一个浏览器使用所有功能",
                "支持多种系统架构的反弹Shell客户端Payload，集成压缩和免杀",
                "支持客户端断线自动重连",
                "支持全平台完全交互式Shell，支持在浏览器中使用Shell，支持分享Shell",
                "支持回连客户端列表管理",
                "内置文件服务器",
                "支持文件管理",
                "支持内存注入，即文件不落地执行木马（内存马）",
                "支持Windows安装反弹Shell服务和Linux尝试迁移uid与gid"
            ],
            "mtime": "2023-03-28"
        },
        "v2.0.0": {
            "description": [
                "修复share_pwd权限提升漏洞",
                "修复几处XSS漏洞",
                "修复rssh dockerfile换源错误，现可通过远程pull和本地原生两种方式构建镜像",
                "修复非'utf-8'编码文件读取出错的BUG",
                "修复客户端生成界面切换页数失效的BUG",
                "修复更改rssh端口后无法回连的BUG",
                "新增分组备注历史记录存储功能，现数据校准后分组记录不会丢失，可在设置中清除历史冗余缓存",
                "新增设置界面下载rssh私钥功能",
                "新增自定义页面显示个数功能",
                "新增客户端会话批量断开、删除和设置分组备注功能",
                "新增Linux客户端执行时自定义进程名功能",
                "新增一行命令上线功能",
                "新增客户端回连代理，可在客户端生成中指定",
                "新增客户端流量封装，默认为ssh，可封装为tls、websockets和secure websockets",
                "新增客户端开启监听功能，对于内网不出网的主机，可通过其他客户端的监听端口回连，实现内网链",
                "新增客户端参数功能，可在执行客户端时指定代理和目的地址等参数",
                "优化回连地址支持域名",
                "优化docker映射时ssh私钥的权限问题",
                "优化garble，进一步模糊签名",
                "优化稳定性和其他代码结构"
            ],
            "mtime": "2023-09-26"
        }
    }
}
