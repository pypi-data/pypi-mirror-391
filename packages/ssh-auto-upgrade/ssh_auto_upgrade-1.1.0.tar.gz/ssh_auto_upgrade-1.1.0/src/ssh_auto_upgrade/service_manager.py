"""
使用systemd-python的现代服务管理模块
提供完全基于systemd D-Bus API的服务管理功能
"""

import os
import logging
from pathlib import Path

# 设置日志记录器
logger = logging.getLogger(__name__)

# 导入systemd-python和D-Bus模块
try:
    import systemd.daemon
    import dbus
    SYSTEMD_PYTHON_AVAILABLE = True
except ImportError as e:
    raise ImportError("systemd-python或dbus模块不可用，请安装systemd-python>=234和python3-dbus")

# 导入端口检查模块
from .port_checker import PortChecker


class ServiceManager:
    """使用systemd-python D-Bus API的现代服务管理器"""
    
    def __init__(self, service_name, executable_path=None, user="root", 
                 group="root", description=None,
                 working_directory=None, environment_vars=None):
        """
        初始化服务管理器
        
        Args:
            service_name: 服务名称
            executable_path: 可执行文件的完整路径，默认为None（可选）
            user: 运行用户，默认为root
            group: 运行组，默认为root
            description: 服务描述，默认为服务名称
            working_directory: 工作目录，默认为None
            environment_vars: 环境变量字典，默认为None
        """
        if not SYSTEMD_PYTHON_AVAILABLE:
            raise ImportError("systemd-python模块不可用")
            
        self.service_name = service_name
        self.executable_path = executable_path
        self.user = user
        self.group = group
        self.description = description or "{0} Service".format(service_name)
        self.working_directory = working_directory
        self.environment_vars = environment_vars or {}
        self.service_file_path = "/etc/systemd/system/{0}.service".format(service_name)
        
        # 初始化systemd D-Bus连接
        self._bus = None
        self._manager_proxy = None
        self._init_systemd_dbus()
    
    def _init_systemd_dbus(self):
        """初始化systemd D-Bus连接"""
        try:
            # 连接到systemd D-Bus接口
            self._bus = dbus.SystemBus()
            self._manager_proxy = self._bus.get_object(
                'org.freedesktop.systemd1',
                '/org/freedesktop/systemd1'
            )
            # 获取管理器接口
            self._manager_interface = dbus.Interface(
                self._manager_proxy,
                'org.freedesktop.systemd1.Manager'
            )
        except Exception as e:
            raise RuntimeError("初始化systemd D-Bus连接失败: {0}".format(str(e)))
    
    def check_systemd_available(self):
        """检查systemd是否可用"""
        try:
            return systemd.daemon.booted()
        except Exception:
            return False
    
    def create_service_file(self, command_args="", description=None):
        """
        创建systemd服务文件
        
        Args:
            command_args: 完整的命令行参数字符串，默认为空
            description: 服务描述，默认为初始化时设置的描述
            
        Returns:
            tuple: (success, message) - 创建是否成功和相关信息
        """
        description = description or self.description
        
        # 构建环境变量部分
        env_vars = ""
        if self.environment_vars:
            for key, value in self.environment_vars.items():
                env_vars += "Environment=\"{0}={1}\"\n".format(key, value)
        
        # 构建工作目录部分
        working_dir = ""
        if self.working_directory:
            working_dir = "WorkingDirectory={0}\n".format(self.working_directory)
        
        service_content = """[Unit]
Description={0}
After=network.target

[Service]
Type=simple
User={1}
Group={2}
{3}
{4}
ExecStart={5} {6}
Restart=always
RestartSec=60
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
""".format(description, self.user, self.group, working_dir, env_vars, 
                   self.executable_path, command_args)
        
        try:
            # 确保目录存在
            Path("/etc/systemd/system").mkdir(parents=True, exist_ok=True)
            
            # 写入服务文件
            with open(self.service_file_path, 'w') as f:
                f.write(service_content)
            
            # 设置正确的权限
            os.chmod(self.service_file_path, 0o644)
            
            # 重新加载systemd配置
            self._reload_systemd()
            
            return True, "服务文件创建成功"
            
        except Exception as e:
            return False, "创建服务文件失败: {0}".format(str(e))
    
    def _reload_systemd(self):
        """重新加载systemd配置（内部方法）"""
        try:
            # 使用systemd D-Bus API重新加载配置
            self._manager_interface.Reload()
            return True
        except Exception as e:
            # 由于这是内部方法，不直接使用logger，让调用方处理错误
            return False
    
    def check_executable(self):
        """
        检查可执行文件是否存在且可执行
        
        Returns:
            tuple: (success, message) - 检查是否成功和相关信息
        """
        try:
            # 如果executable_path为None，跳过检查
            if self.executable_path is None:
                return True, "可执行文件路径未指定，跳过检查"
                
            # 检查可执行文件是否存在
            if os.path.exists(self.executable_path):
                # 检查文件是否可执行
                if os.access(self.executable_path, os.X_OK):
                    return True, "可执行文件已存在且可执行"
                else:
                    # 如果文件存在但不可执行，设置可执行权限
                    os.chmod(self.executable_path, 0o755)
                    return True, "可执行文件权限已修复"
            else:
                return False, "可执行文件不存在: {0}".format(self.executable_path)
            
        except Exception as e:
            return False, "检查可执行文件失败: {0}".format(str(e))
    
    def enable_service(self):
        """启用服务"""
        try:
            # 使用systemd D-Bus API启用服务
            self._manager_interface.EnableUnitFiles([self.service_name + ".service"], False, True)
            return True, "服务启用成功"
                
        except Exception as e:
            return False, "启用服务失败: {0}".format(str(e))
    
    def start_service(self):
        """启动服务"""
        try:
            # 使用systemd D-Bus API启动服务
            self._manager_interface.StartUnit(self.service_name + ".service", "replace")
            return True, "服务启动成功"
                
        except Exception as e:
            return False, "启动服务失败: {0}".format(str(e))
    
    def stop_service(self):
        """停止服务"""
        try:
            # 使用systemd D-Bus API停止服务
            self._manager_interface.StopUnit(self.service_name + ".service", "replace")
            return True, "服务停止成功"
                
        except Exception as e:
            return False, "停止服务失败: {0}".format(str(e))
    

    
    def disable_service(self):
        """禁用服务"""
        try:
            # 使用systemd D-Bus API禁用服务
            self._manager_interface.DisableUnitFiles([self.service_name + ".service"], False)
            return True, "服务禁用成功"
                
        except Exception as e:
            return False, "禁用服务失败: {0}".format(str(e))
    
    def remove_service(self):
        """
        移除服务
        
        Returns:
            tuple: (success, message) - 移除是否成功和相关信息
        """
        try:
            # 停止服务（只进行基本服务停止，不进行端口检查）
            success, message = self.stop_service()
            
            if not success:
                logger.warning(f"停止服务时出现问题: {message}")
            
            # 禁用服务
            self.disable_service()
            
            # 删除服务文件
            if os.path.exists(self.service_file_path):
                os.remove(self.service_file_path)
            
            # 删除可执行文件
            if os.path.exists(self.executable_path):
                os.remove(self.executable_path)
            
            # 重新加载systemd配置
            self._reload_systemd()
            
            return True, "服务移除成功"
            
        except Exception as e:
            return False, "移除服务失败: {0}".format(str(e))
    
    def get_service_status(self):
        """获取服务状态，使用systemd D-Bus API检测服务是否存在
        
        Returns:
            tuple: (exists, status_info) - 服务是否存在和状态信息
        """
        try:
            # 方法1：检查服务文件是否存在
            service_file_exists = os.path.exists(self.service_file_path)
            
            # 方法2：通过D-Bus获取服务单元信息
            service_exists = False
            active_state = "unknown"
            load_state = "unknown"
            
            try:
                # 获取服务单元对象路径
                unit_path = self._manager_interface.GetUnit(self.service_name + ".service")
                
                # 获取服务单元接口
                unit_proxy = self._bus.get_object('org.freedesktop.systemd1', unit_path)
                unit_interface = dbus.Interface(unit_proxy, 'org.freedesktop.systemd1.Unit')
                
                # 获取服务状态属性
                properties_interface = dbus.Interface(unit_proxy, 'org.freedesktop.DBus.Properties')
                active_state = properties_interface.Get('org.freedesktop.systemd1.Unit', 'ActiveState')
                load_state = properties_interface.Get('org.freedesktop.systemd1.Unit', 'LoadState')
                
                # 如果服务已加载或正在运行，则认为服务存在
                service_exists = load_state != "not-found"
                
            except Exception:
                # 如果获取服务信息失败，认为服务不存在
                service_exists = False
            
            # 构建详细的状态信息
            status_info = "服务检测结果（使用systemd D-Bus API）:\n"
            status_info += "- 服务文件存在: {0}\n".format(service_file_exists)
            status_info += "- D-Bus检测服务存在: {0}\n".format(service_exists)
            
            if service_exists:
                status_info += "- 加载状态: {0}\n".format(load_state)
                status_info += "- 活动状态: {0}\n".format(active_state)
                
                # 根据状态提供更多信息
                if active_state == "active":
                    status_info += "- 服务正在运行\n"
                elif active_state == "inactive":
                    status_info += "- 服务已停止\n"
                elif active_state == "failed":
                    status_info += "- 服务启动失败\n"
            else:
                status_info += "- 服务不存在或未在systemd中注册\n"
            
            return service_exists, status_info
            
        except Exception as e:
            # 如果出现异常，保守地认为服务不存在
            return False, "检测服务状态时出错: {0}".format(str(e))

    def register_service(self, command_args=""):
        """
        注册systemd服务
        
        Args:
            command_args: 完整的命令行参数字符串，默认为空
            
        Returns:
            tuple: (success, message) - 注册是否成功和相关信息
        """
        # 检查systemd是否可用
        if not self.check_systemd_available():
            return False, "systemd不可用，无法注册服务"
        
        # 检查权限
        if os.geteuid() != 0:
            return False, "需要root权限来注册systemd服务"
        
        try:
            # 检查服务是否已存在
            service_exists, status_info = self.get_service_status()
            
            # 如果服务存在且正在运行，先停止服务
            if service_exists:
                logger.info("检测到服务已存在，正在检查服务状态...")
                
                # 获取详细的服务状态
                try:
                    unit_path = self._manager_interface.GetUnit(self.service_name + ".service")
                    unit_proxy = self._bus.get_object('org.freedesktop.systemd1', unit_path)
                    
                    # 获取服务状态属性
                    properties_interface = dbus.Interface(unit_proxy, 'org.freedesktop.DBus.Properties')
                    active_state = properties_interface.Get('org.freedesktop.systemd1.Unit', 'ActiveState')
                    
                    if active_state == "active":
                        logger.info("服务正在运行，正在停止服务...")
                        # 服务注册时只进行基本停止，不进行SSH端口检查
                        success, message = self.stop_service()
                        if not success:
                            logger.warning(f"停止服务失败: {message}")
                        else:
                            logger.info("服务已成功停止")
                    elif active_state == "inactive":
                        logger.info("服务已停止，无需额外操作")
                    else:
                        logger.info(f"服务状态: {active_state}")
                        
                except Exception as e:
                    logger.warning(f"获取服务状态失败: {str(e)}")
            
            # 检查可执行文件
            success, message = self.check_executable()
            if not success:
                return False, message
            
            # 创建服务文件
            success, message = self.create_service_file(command_args)
            if not success:
                return False, message
            
            # 启用服务
            success, message = self.enable_service()
            if not success:
                return False, message
            
            # 启动服务
            success, message = self.start_service()
            if not success:
                return False, message
            
            return True, "systemd服务注册成功，服务已启动并设置为开机自启"
            
        except Exception as e:
            return False, f"注册服务失败: {str(e)}"


def main():
    """测试函数"""
    # 使用通用的服务管理器
    manager = ServiceManager(
        service_name="test-service",
        executable_path="/usr/bin/echo",
        description="Test Service for Generic Service Manager"
    )
    
    # 检查systemd
    if manager.check_systemd_available():
        logger.info("systemd可用")
    else:
        logger.error("systemd不可用")
    
    # 测试服务状态
    success, status = manager.get_service_status()
    logger.info(f"服务状态: {success}")
    logger.info(f"状态信息: {status}")


if __name__ == "__main__":
    main()