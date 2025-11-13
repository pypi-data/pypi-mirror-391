"""
SSH配置状态检测模块
负责检测SSH配置文件中的各种设置状态
"""

import os
import re
import logging

# 设置日志记录器
logger = logging.getLogger(__name__)


def get_current_root_login_setting(ssh_config_path):
    """
    获取当前root登录设置
    
    Args:
        ssh_config_path: SSH配置文件路径
        
    Returns:
        dict: {
            'exists': bool,  # 配置文件是否存在
            'permit_root_login': str or None,  # 当前设置值
            'commented': bool  # 是否被注释
        }
    """
    if not os.path.exists(ssh_config_path):
        return {
            'exists': False,
            'permit_root_login': None,
            'commented': True
        }
    
    try:
        with open(ssh_config_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # 查找PermitRootLogin设置
        pattern = r'^\s*(#?)\s*PermitRootLogin\s+(\S+)'
        matches = re.findall(pattern, content, re.MULTILINE | re.IGNORECASE)
        
        if matches:
            # 取最后一个匹配项（配置文件中的最后一个设置生效）
            commented, value = matches[-1]
            return {
                'exists': True,
                'permit_root_login': value.strip(),
                'commented': bool(commented)
            }
        else:
            # 没有找到PermitRootLogin设置
            return {
                'exists': True,
                'permit_root_login': None,
                'commented': True
            }
            
    except Exception as e:
        return {
            'exists': False,
            'permit_root_login': None,
            'commented': True,
            'error': str(e)
        }


def get_current_key_only_login_setting(ssh_config_path):
    """
    获取当前仅密钥登录设置
    
    Args:
        ssh_config_path: SSH配置文件路径
        
    Returns:
        dict: {
            'exists': bool,  # 配置文件是否存在
            'password_authentication': str or None,  # 当前设置值
            'commented': bool  # 是否被注释
        }
    """
    if not os.path.exists(ssh_config_path):
        return {
            'exists': False,
            'password_authentication': None,
            'commented': True
        }
    
    try:
        with open(ssh_config_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # 查找PasswordAuthentication设置
        pattern = r'^\s*(#?)\s*PasswordAuthentication\s+(\S+)'
        matches = re.findall(pattern, content, re.MULTILINE | re.IGNORECASE)
        
        if matches:
            # 取最后一个匹配项（配置文件中的最后一个设置生效）
            commented, value = matches[-1]
            return {
                'exists': True,
                'password_authentication': value.strip(),
                'commented': bool(commented)
            }
        else:
            # 没有找到PasswordAuthentication设置
            return {
                'exists': True,
                'password_authentication': None,
                'commented': True
            }
            
    except Exception as e:
        return {
            'exists': False,
            'password_authentication': None,
            'commented': True,
            'error': str(e)
        }


def is_root_login_enabled(ssh_config_path):
    """
    检查root登录是否启用
    
    Args:
        ssh_config_path: SSH配置文件路径
        
    Returns:
        bool: True表示启用，False表示禁用
    """
    setting = get_current_root_login_setting(ssh_config_path)
    
    if not setting['exists']:
        # 配置文件不存在，默认启用
        return True
    
    if setting['permit_root_login'] is None or setting['commented']:
        # 没有设置PermitRootLogin或设置被注释，默认启用
        return True
    
    # 检查设置值（只有在设置存在且未被注释时）
    value = setting['permit_root_login'].lower()
    if value in ['yes', 'true', '1', 'without-password', 'prohibit-password']:
        return True
    elif value in ['no', 'false', '0']:
        return False
    else:
        # 未知值，默认启用
        return True


def is_key_only_login_enabled(ssh_config_path):
    """
    检查仅密钥登录是否启用（即密码认证是否禁用）
    
    Args:
        ssh_config_path: SSH配置文件路径
        
    Returns:
        bool: True表示启用仅密钥登录（禁用密码认证），False表示允许密码登录
    """
    setting = get_current_key_only_login_setting(ssh_config_path)
    
    if not setting['exists']:
        # 配置文件不存在，默认允许密码登录（不启用仅密钥登录）
        return False
    
    if setting['password_authentication'] is None or setting['commented']:
        # 没有设置PasswordAuthentication或设置被注释，默认允许密码登录（不启用仅密钥登录）
        return False
    
    # 检查设置值（只有在设置存在且未被注释时）
    value = setting['password_authentication'].lower()
    if value in ['no', 'false', '0']:
        # PasswordAuthentication被禁用，表示启用仅密钥登录
        return True
    elif value in ['yes', 'true', '1']:
        # PasswordAuthentication被启用，表示允许密码登录（不启用仅密钥登录）
        return False
    else:
        # 未知值，默认允许密码登录（不启用仅密钥登录）
        return False


def check_root_login_status(ssh_config_path="/etc/ssh/sshd_config"):
    """
    检查root登录状态的便捷函数
    
    Args:
        ssh_config_path: SSH配置文件路径
        
    Returns:
        dict: {
            'enabled': bool,  # 是否启用
            'config_exists': bool,  # 配置文件是否存在
            'current_setting': str,  # 当前设置
            'message': str  # 状态信息
        }
    """
    setting = get_current_root_login_setting(ssh_config_path)
    enabled = is_root_login_enabled(ssh_config_path)
    
    if not setting['exists']:
        return {
            'enabled': True,
            'config_exists': False,
            'current_setting': '默认启用（配置文件不存在）',
            'message': 'SSH配置文件不存在，root登录默认启用'
        }
    
    if setting['permit_root_login'] is None:
        return {
            'enabled': True,
            'config_exists': True,
            'current_setting': '默认启用（未设置PermitRootLogin）',
            'message': 'SSH配置文件中未设置PermitRootLogin，root登录默认启用'
        }
    
    if setting['commented']:
        return {
            'enabled': True,
            'config_exists': True,
            'current_setting': f'默认启用（{setting["permit_root_login"]}被注释）',
            'message': f'PermitRootLogin设置被注释，root登录默认启用'
        }
    
    return {
        'enabled': enabled,
        'config_exists': True,
        'current_setting': setting['permit_root_login'],
        'message': f'root登录{"启用" if enabled else "禁用"} (PermitRootLogin {setting["permit_root_login"]})'
    }


def check_key_only_login_status(ssh_config_path="/etc/ssh/sshd_config"):
    """
    检查仅密钥登录状态的便捷函数
    
    Args:
        ssh_config_path: SSH配置文件路径
        
    Returns:
        dict: {
            'enabled': bool,  # 是否启用仅密钥登录
            'config_exists': bool,  # 配置文件是否存在
            'current_setting': str,  # 当前设置
            'message': str  # 状态信息
        }
    """
    setting = get_current_key_only_login_setting(ssh_config_path)
    enabled = is_key_only_login_enabled(ssh_config_path)
    
    if not setting['exists']:
        return {
            'enabled': False,
            'config_exists': False,
            'current_setting': '默认禁用（配置文件不存在）',
            'message': 'SSH配置文件不存在，默认允许密码登录'
        }
    
    if setting['password_authentication'] is None:
        return {
            'enabled': False,
            'config_exists': True,
            'current_setting': '默认禁用（未设置PasswordAuthentication）',
            'message': 'SSH配置文件中未设置PasswordAuthentication，默认允许密码登录'
        }
    
    if setting['commented']:
        return {
            'enabled': False,
            'config_exists': True,
            'current_setting': f'默认禁用（{setting["password_authentication"]}被注释）',
            'message': f'PasswordAuthentication设置被注释，默认允许密码登录'
        }
    
    return {
        'enabled': enabled,
        'config_exists': True,
        'current_setting': setting['password_authentication'],
        'message': f'仅密钥登录{"启用" if enabled else "禁用"} (PasswordAuthentication {setting["password_authentication"]})'
    }