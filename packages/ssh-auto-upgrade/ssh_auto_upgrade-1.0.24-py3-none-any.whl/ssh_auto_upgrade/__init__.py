"""
SSH Auto Upgrade Package
自动检测和升级OpenSSH的工具包
"""

__version__ = "1.0.24"
__author__ = "SSH Auto Upgrade Team"

# 核心功能模块
from .version_detector import VersionDetector
from .downloader import Downloader
from .installer import Installer
from .service_manager import ServiceManager

# 配置管理模块
from .ssh_config_manager import SSHConfigManager
from .mirror_checker import MirrorChecker, check_mirror_url
from .time_checker import TimeChecker, is_time_in_range, parse_time_range, validate_and_check_time_range

# 服务检测和管理模块
from .service_detector import (
    get_ssh_guard_services,
    get_service_detection_prompt,
    get_non_ssh_warning,
    get_ssh_confirmation
)
from .installer_service_detector import InstallerServiceDetector, detect_services_for_installation
from .installer_service_manager import InstallerServiceManager

# 文件管理模块
from .installer_file_manager import InstallerFileManager

# 系统检查模块
from .systemd_checker import (
    check_systemd_init_system,
    ensure_systemd_only,
    get_systemd_status
)

# 依赖检查模块
from .dependencies import DependencyManager

# 编译模块
from .compile import compile_openssh

# 日志模块
from .logger import (
    setup_logger,
    log_installation_start,
    log_installation_step,
    log_installation_success,
    log_installation_error,
    log_verification_result,
    get_log_file_path
)

__all__ = [
    # 核心功能类
    "VersionDetector", 
    "Downloader", 
    "Installer",
    "ServiceManager",
    
    # 配置管理类
    "SSHConfigManager",
    "MirrorChecker",
    "TimeChecker",
    
    # 服务检测和管理类
    "InstallerServiceDetector",
    "InstallerServiceManager",
    
    # 文件管理类
    "InstallerFileManager",
    
    # 系统检查函数
    "check_systemd_init_system",
    "ensure_systemd_only",
    "get_systemd_status",
    
    # 依赖检查类
    "DependencyManager",
    
    # 编译函数
    "compile_openssh",
    
    # 便捷函数
    "check_mirror_url",
    "is_time_in_range",
    "parse_time_range",
    "validate_and_check_time_range",
    "detect_services_for_installation",
    
    # 服务检测配置函数
    "get_ssh_guard_services",
    "get_service_detection_prompt",
    "get_non_ssh_warning",
    "get_ssh_confirmation",
    
    # 日志函数
    "setup_logger",
    "log_installation_start",
    "log_installation_step",
    "log_installation_success",
    "log_installation_error",
    "log_verification_result",
    "get_log_file_path"
]