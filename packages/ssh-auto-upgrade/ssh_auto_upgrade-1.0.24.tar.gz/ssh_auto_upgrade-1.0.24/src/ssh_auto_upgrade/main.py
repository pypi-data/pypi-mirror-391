#!/usr/bin/env python3
"""
SSH自动升级程序主入口
支持服务注册和守护进程模式
"""

import sys
import os
import argparse

# 处理相对导入问题
if __name__ == "__main__" and __package__ is None:
    # 直接运行时的导入方式
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
    from ssh_auto_upgrade.logger import setup_logger
    from ssh_auto_upgrade.dependencies import DependencyManager
    from ssh_auto_upgrade.service_registrar import register_service
    from ssh_auto_upgrade.daemon_loop import run_daemon_loop
    from ssh_auto_upgrade.arg import (
        DEFAULT_MIRROR, DEFAULT_INSTALL_DIR, DEFAULT_DOWNLOAD_DIR,
        DEFAULT_LOG_DIR, DEFAULT_UPGRADE_TIME, DEFAULT_ROOT_LOGIN,
        DEFAULT_CHECK_INTERVAL, DEFAULT_FORCE, DEFAULT_SERVICE,
        DEFAULT_KEY_ONLY_LOGIN
    )
else:
    # 模块导入时的导入方式
    from .logger import setup_logger
    from .dependencies import DependencyManager
    from .service_registrar import register_service
    from .daemon_loop import run_daemon_loop
    from .arg import (
        DEFAULT_MIRROR, DEFAULT_INSTALL_DIR, DEFAULT_DOWNLOAD_DIR,
        DEFAULT_LOG_DIR, DEFAULT_UPGRADE_TIME, DEFAULT_ROOT_LOGIN,
        DEFAULT_CHECK_INTERVAL, DEFAULT_FORCE, DEFAULT_SERVICE,
        DEFAULT_KEY_ONLY_LOGIN
    )





def main():
    """主函数 - 专为守护进程模式设计"""
    
    # 检查root权限
    if os.geteuid() != 0:
        print("需要root权限来运行SSH自动升级工具")
        print("请使用sudo或切换到root用户运行此程序")
        return 1
    
    parser = argparse.ArgumentParser(description='OpenSSH自动升级守护进程工具-V1.0.23')
    parser.add_argument('--mirror', '-m', 
                        default=DEFAULT_MIRROR,
                        help='OpenSSH镜像源URL')
    parser.add_argument('--install-dir', '-i',
                        default=DEFAULT_INSTALL_DIR,
                        help='OpenSSH安装目录')
    parser.add_argument('--download-dir', '-d',
                        default=DEFAULT_DOWNLOAD_DIR,
                        help='下载目录')
    parser.add_argument('--log-dir', '-l',
                        default=DEFAULT_LOG_DIR,
                        help='日志目录')
    parser.add_argument('--force', '-f',
                        action='store_true',
                        default=DEFAULT_FORCE,
                        help='强制升级，即使版本相同也执行安装')
    parser.add_argument('--service', '-s',
                        action='store_true',
                        default=DEFAULT_SERVICE,
                        help='注册为systemd服务')
    parser.add_argument('--upgrade-time', '-t',
                        default=DEFAULT_UPGRADE_TIME,
                        help='升级时间段，格式为 HH:MM:SS-HH:MM:SS，默认00:00:00-08:00:00')
    parser.add_argument('--root-login', '-rl',
                        choices=['auto', 'yes', 'no'],
                        default=DEFAULT_ROOT_LOGIN,
                        help='升级后root登录配置: auto(智能检测当前配置，默认), yes(启用), no(禁用)')

    parser.add_argument('--key-only-login', '-kl',
                        choices=['auto', 'yes', 'no'],
                        default=DEFAULT_KEY_ONLY_LOGIN,
                        help='升级后仅密钥登录配置: auto(智能检测当前配置，默认), yes(启用仅密钥登录), no(允许密码登录)')

    parser.add_argument('--check-interval', '--interval',
                        type=int,
                        default=DEFAULT_CHECK_INTERVAL,
                        choices=range(1, 49),
                        metavar='[1-48]',
                        help='检测间隔时间，单位小时，默认1，最低1，最大48')
    
    # 解析参数
    args = parser.parse_args()
    
    # 设置日志
    logger = setup_logger(args.log_dir)
    
    # 智能检测root登录配置（在参数验证后，主逻辑前）
    if args.root_login == 'auto':
        from .ssh_config_manager import SSHConfigManager
        config_manager = SSHConfigManager()
        current_status = config_manager.is_root_login_enabled()
        args.root_login = 'yes' if current_status else 'no'
        logger.info(f"检测到当前root登录配置: {'启用' if current_status else '禁用'}")
        logger.info(f"默认设置为: {'--root-login yes' if current_status else '--root-login no'}")
        logger.info("可通过 --root-login yes/no 参数强制设置")
    
    # 智能检测仅密钥登录配置（在参数验证后，主逻辑前）
    if args.key_only_login == 'auto':
        from .ssh_config_manager import SSHConfigManager
        config_manager = SSHConfigManager()
        current_status = config_manager.is_key_only_login_enabled()
        args.key_only_login = 'yes' if current_status else 'no'
        logger.info(f"检测到当前仅密钥登录配置: {'启用' if current_status else '禁用'}")
        logger.info(f"默认设置为: {'--key-only-login yes' if current_status else '--key-only-login no'}")
        logger.info("可通过 --key-only-login yes/no 参数强制设置")
    
    # 检查镜像地址可用性
    logger.info("检查镜像地址可用性")
    
    from .mirror_checker import MirrorChecker
    mirror_checker = MirrorChecker()
    mirror_available = mirror_checker.check_mirror_availability(args.mirror)
    
    if not mirror_available:
        error_msg = f"镜像地址不可用: {args.mirror}"
        logger.error(error_msg)
        return 1
    
    logger.info("镜像地址检测通过")
    
    # 第三步：依赖检测（无论是否服务注册都需要）
    logger.info("检查编译依赖")
    
    dependency_manager = DependencyManager()
    
    # 确保所有依赖已安装（安装失败时会直接终止程序）
    deps_success, deps_message = dependency_manager.ensure_dependencies(auto_install=True)
    
    # 检查依赖检测结果，如果失败则终止程序
    if not deps_success:
        logger.error(f"依赖检查失败: {deps_message}")
        return 1
    
    # 如果依赖检查通过，继续执行
    logger.info("编译依赖检查通过")
    
    # 第二步：服务注册判断
    if args.service:
        # 调用服务注册模块
        success = register_service(args)
        return 0 if success else 1
    
    # 第三步：循环程序（如果没有传入服务注册参数）
    # 调用守护进程主循环模块
    return run_daemon_loop(args)


if __name__ == "__main__":
    sys.exit(main())