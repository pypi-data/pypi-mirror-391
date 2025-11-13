"""
SSH自动升级工具默认参数配置

本模块定义了SSH自动升级工具的所有默认参数值，这些参数值被main.py和service_registrar.py引用。
通过集中管理默认参数值，可以方便地维护和修改默认配置，同时确保各模块使用一致的默认值。
"""

# 默认镜像源URL
# 使用阿里云镜像源，提供稳定的OpenSSH源码下载服务
DEFAULT_MIRROR = 'https://mirrors.aliyun.com/openssh/portable/'

# 默认OpenSSH安装目录
# 安装到/usr/local/openssh目录，避免与系统自带的OpenSSH冲突
DEFAULT_INSTALL_DIR = '/usr/local/openssh'

# 默认下载目录
# 临时存放下载的OpenSSH源码压缩包
DEFAULT_DOWNLOAD_DIR = '/tmp/ssh-upgrade'

# 默认日志目录
# 存放SSH自动升级工具的运行日志
DEFAULT_LOG_DIR = '/var/log/ssh-auto-upgrade'

# 默认升级时间段
# 格式为HH:MM:SS-HH:MM:SS，设置为凌晨0点到8点，减少对业务的影响
DEFAULT_UPGRADE_TIME = '00:00:00-08:00:00'

# 默认root登录配置
# auto: 智能检测当前SSH配置，保持与当前配置一致
# yes: 强制启用root登录
# no: 强制禁用root登录
DEFAULT_ROOT_LOGIN = 'auto'

# 默认检测间隔时间(小时)
# 设置为1小时，即每小时检查一次是否有新版本
DEFAULT_CHECK_INTERVAL = 1

# 默认强制升级标志
# False: 只有检测到新版本时才升级
# True: 即使版本相同也执行安装过程
DEFAULT_FORCE = False

# 默认服务注册标志
# False: 不注册为系统服务
# True: 注册为系统服务并设置开机自启
DEFAULT_SERVICE = False

# 默认仅密钥登录配置
# auto: 智能检测当前SSH配置，保持与当前配置一致
# yes: 强制启用仅密钥登录（禁用密码登录）
# no: 强制禁用仅密钥登录（允许密码登录）
DEFAULT_KEY_ONLY_LOGIN = 'auto'

# 默认SSH端口配置
# 设置为22，可通过参数自定义其他端口
DEFAULT_SSH_PORT = 22