"""
SSH配置管理模块
负责检测和修改SSH配置文件中的root登录设置
"""

import os
import re
import logging
from .ssh_config_manager_status import (
    get_current_root_login_setting,
    get_current_key_only_login_setting,
    is_root_login_enabled,
    is_key_only_login_enabled,
    check_root_login_status,
    check_key_only_login_status
)
from .service_manager import ServiceManager
from .arg import DEFAULT_SSH_PORT

# 设置日志记录器
logger = logging.getLogger(__name__)


class SSHConfigManager:
    """SSH配置管理器"""
    
    def __init__(self, ssh_config_path="/etc/ssh/sshd_config"):
        """
        初始化SSH配置管理器
        
        Args:
            ssh_config_path: SSH配置文件路径
        """
        self.ssh_config_path = ssh_config_path
        self.backup_config_path = f"{ssh_config_path}.backup"
    
    def config_file_exists(self):
        """检查配置文件是否存在"""
        return os.path.exists(self.ssh_config_path)
    
    def get_current_root_login_setting(self):
        """
        获取当前root登录设置
        
        Returns:
            dict: {
                'exists': bool,  # 配置文件是否存在
                'permit_root_login': str or None,  # 当前设置值
                'commented': bool  # 是否被注释
            }
        """
        return get_current_root_login_setting(self.ssh_config_path)
    
    def get_current_key_only_login_setting(self):
        """
        获取当前仅密钥登录设置
        
        Returns:
            dict: {
                'exists': bool,  # 配置文件是否存在
                'password_authentication': str or None,  # 当前设置值
                'commented': bool  # 是否被注释
            }
        """
        return get_current_key_only_login_setting(self.ssh_config_path)
    
    def is_root_login_enabled(self):
        """
        检查root登录是否启用
        
        Returns:
            bool: True表示启用，False表示禁用
        """
        return is_root_login_enabled(self.ssh_config_path)
    
    def is_key_only_login_enabled(self):
        """
        检查仅密钥登录是否启用（即密码认证是否禁用）
        
        Returns:
            bool: True表示启用仅密钥登录（禁用密码认证），False表示允许密码登录
        """
        return is_key_only_login_enabled(self.ssh_config_path)
    
    def backup_config(self):
        """备份配置文件"""
        if not self.config_file_exists():
            return False, "配置文件不存在，无需备份"
        
        try:
            import shutil
            shutil.copy2(self.ssh_config_path, self.backup_config_path)
            return True, f"配置文件已备份到 {self.backup_config_path}"
        except Exception as e:
            return False, f"备份配置文件失败: {str(e)}"
    
    def set_root_login(self, enable=True, force=False):
        """
        设置root登录权限
        
        Args:
            enable: True启用，False禁用
            force: 是否强制设置（即使配置文件不存在也创建）
            
        Returns:
            tuple: (success, message)
        """
        # 备份配置文件
        backup_success, backup_message = self.backup_config()
        
        if not self.config_file_exists() and not force:
            return False, "配置文件不存在，使用force参数强制创建"
        
        try:
            # 读取现有内容或创建新文件
            if self.config_file_exists():
                with open(self.ssh_config_path, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
            else:
                lines = []
            
            # 构建新的设置行
            setting_value = "yes" if enable else "no"
            new_setting_line = f"PermitRootLogin {setting_value}\n"
            
            # 查找并替换现有的PermitRootLogin设置
            pattern = r'^\s*(#?)\s*PermitRootLogin\s+\S+'
            found = False
            new_lines = []
            
            for line in lines:
                if re.match(pattern, line, re.IGNORECASE):
                    if not found:
                        # 替换第一个匹配的设置
                        new_lines.append(new_setting_line)
                        found = True
                    # 跳过其他匹配的设置
                else:
                    new_lines.append(line)
            
            # 如果没有找到现有设置，在文件末尾添加
            if not found:
                # 确保文件以换行符结束
                if new_lines and not new_lines[-1].endswith('\n'):
                    new_lines[-1] = new_lines[-1] + '\n'
                new_lines.append(new_setting_line)
            
            # 写入新内容
            with open(self.ssh_config_path, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)
            
            # 设置正确的文件权限
            os.chmod(self.ssh_config_path, 0o644)
            
            action = "启用" if enable else "禁用"
            return True, f"root登录已{action}"
            
        except Exception as e:
            # 恢复备份
            if backup_success and os.path.exists(self.backup_config_path):
                try:
                    shutil.copy2(self.backup_config_path, self.ssh_config_path)
                except:
                    pass
            return False, f"设置root登录失败: {str(e)}"
    
    def set_key_only_login(self, enable=True, force=False):
        """
        设置仅密钥登录（禁用密码认证）
        
        Args:
            enable: True启用仅密钥登录（禁用密码认证），False禁用仅密钥登录（允许密码认证）
            force: 是否强制设置（即使配置文件不存在也创建）
            
        Returns:
            tuple: (success, message)
        """
        # 备份配置文件
        backup_success, backup_message = self.backup_config()
        
        if not self.config_file_exists() and not force:
            return False, "配置文件不存在，使用force参数强制创建"
        
        try:
            # 读取现有内容或创建新文件
            if self.config_file_exists():
                with open(self.ssh_config_path, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
            else:
                lines = []
            
            # 构建新的设置行
            setting_value = "no" if enable else "yes"
            new_setting_line = f"PasswordAuthentication {setting_value}\n"
            
            # 查找并替换现有的PasswordAuthentication设置
            pattern = r'^\s*(#?)\s*PasswordAuthentication\s+\S+'
            found = False
            new_lines = []
            
            for line in lines:
                if re.match(pattern, line, re.IGNORECASE):
                    if not found:
                        # 替换第一个匹配的设置
                        new_lines.append(new_setting_line)
                        found = True
                    # 跳过其他匹配的设置
                else:
                    new_lines.append(line)
            
            # 如果没有找到现有设置，在文件末尾添加
            if not found:
                # 确保文件以换行符结束
                if new_lines and not new_lines[-1].endswith('\n'):
                    new_lines[-1] = new_lines[-1] + '\n'
                new_lines.append(new_setting_line)
            
            # 写入新内容
            with open(self.ssh_config_path, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)
            
            # 设置正确的文件权限
            os.chmod(self.ssh_config_path, 0o644)
            
            action = "启用" if enable else "禁用"
            return True, f"仅密钥登录已{action}"
            
        except Exception as e:
            # 恢复备份
            if backup_success and os.path.exists(self.backup_config_path):
                try:
                    shutil.copy2(self.backup_config_path, self.ssh_config_path)
                except:
                    pass
            return False, f"设置仅密钥登录失败: {str(e)}"
    
    def restart_ssh_service(self, ssh_port=DEFAULT_SSH_PORT):
        """
        重启SSH服务使配置生效（包含端口检查）
        
        Args:
            ssh_port: SSH端口号，默认为22
            
        Returns:
            tuple: (success, message)
        """
        try:
            # 使用专业的ServiceManager来重启SSH服务
            ssh_service_manager = ServiceManager(
                service_name="sshd",
                executable_path="/usr/sbin/sshd",
                description="OpenBSD Secure Shell server"
            )
            
            # 检查服务是否存在
            service_exists, status_info = ssh_service_manager.get_service_status()
            
            if not service_exists:
                return False, "SSH服务不存在，无法重启"
            
            # 先停止服务（使用包含端口检查的停止方法），再启动服务（实现重启功能）
            logger.info(f"重启SSH服务，停止过程中会检查并清理{ssh_port}端口占用...")
            stop_success, stop_message = ssh_service_manager.stop_ssh_service_with_port_check(
                check_port=True, ssh_port=ssh_port
            )
            if not stop_success:
                return False, f"停止SSH服务失败: {stop_message}"
            
            # 等待一下确保服务完全停止
            import time
            time.sleep(2)
            
            start_success, start_message = ssh_service_manager.start_service()
            if not start_success:
                return False, f"启动SSH服务失败: {start_message}"
            
            return True, f"SSH服务重启成功，{ssh_port}端口已检查清理"
            
        except Exception as e:
            return False, f"重启SSH服务失败: {str(e)}"
    
    def get_ssh_service_status(self):
        """
        获取SSH服务状态
        
        Returns:
            tuple: (service_exists, status_info) - 服务是否存在和详细状态信息
        """
        try:
            ssh_service_manager = ServiceManager(
                service_name="sshd",
                executable_path="/usr/sbin/sshd",
                description="OpenBSD Secure Shell server"
            )
            
            return ssh_service_manager.get_service_status()
            
        except Exception as e:
            return False, f"获取SSH服务状态失败: {str(e)}"
    
    def start_ssh_service(self):
        """
        启动SSH服务
        
        Returns:
            tuple: (success, message) - 启动是否成功和相关信息
        """
        try:
            ssh_service_manager = ServiceManager(
                service_name="sshd",
                executable_path="/usr/sbin/sshd",
                description="OpenBSD Secure Shell server"
            )
            
            return ssh_service_manager.start_service()
            
        except Exception as e:
            return False, f"启动SSH服务失败: {str(e)}"
    
    def stop_ssh_service(self, ssh_port=DEFAULT_SSH_PORT):
        """
        停止SSH服务（包含端口检查和清理）
        
        Args:
            ssh_port: SSH端口号，默认为22
            
        Returns:
            tuple: (success, message) - 停止是否成功和相关信息
        """
        try:
            ssh_service_manager = ServiceManager(
                service_name="sshd",
                executable_path="/usr/sbin/sshd",
                description="OpenBSD Secure Shell server"
            )
            
            logger.info(f"停止SSH服务，同时检查并清理{ssh_port}端口占用...")
            return ssh_service_manager.stop_ssh_service_with_port_check(
                check_port=True, ssh_port=ssh_port
            )
            
        except Exception as e:
            return False, f"停止SSH服务失败: {str(e)}"


# 向后兼容，保持原有的独立函数接口
def check_root_login_status():
    """
    检查root登录状态的便捷函数
    
    Returns:
        dict: {
            'enabled': bool,  # 是否启用
            'config_exists': bool,  # 配置文件是否存在
            'current_setting': str,  # 当前设置
            'message': str  # 状态信息
        }
    """
    from .ssh_config_manager_status import check_root_login_status as _check_root_login_status
    return _check_root_login_status()