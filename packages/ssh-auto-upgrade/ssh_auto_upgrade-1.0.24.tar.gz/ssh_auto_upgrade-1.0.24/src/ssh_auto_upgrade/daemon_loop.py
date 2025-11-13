"""
守护进程主循环模块
处理SSH自动升级的守护进程逻辑
"""

import sys
import time
import signal
import logging
from datetime import datetime
from .version_detector import VersionDetector
from .installer import Installer
from .ssh_config_manager import SSHConfigManager
from .time_checker import TimeChecker
from .legacy_cleaner import ensure_systemd_only_startup

# 全局日志记录器
logger = logging.getLogger("ssh_auto_upgrade")


def signal_handler(signum, frame):
    """信号处理函数"""
    logger.info(f"收到信号 {signum}，守护进程正在退出")
    sys.exit(0)


def run_daemon_loop(args):
    """
    运行守护进程主循环
    
    Args:
        args: 命令行参数对象
        
    Returns:
        int: 退出码
    """
    logger.info("启动OpenSSH自动升级守护进程")
    
    # 注册信号处理
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    
    # 解析升级时间段
    try:
        time_checker = TimeChecker()
        start_time_str, end_time_str = time_checker.parse_time_range(args.upgrade_time)
        
        logger.info(f"升级时间段设置为: {start_time_str} - {end_time_str}")
        
    except ValueError as e:
        logger.error(f"升级时间段格式无效 - {e}")
        logger.error("请使用格式: HH:MM:SS-HH:MM:SS")
        return 1
    
    # 守护进程主循环
    while True:
        try:
            current_time = datetime.now().strftime('%H:%M:%S')
            
            # 检查当前时间是否在升级时间段内
            if time_checker.is_time_in_range(start_time_str, end_time_str):
                logger.info(f"当前时间 {current_time} 在升级时间段内，执行版本检查")
                
                # 执行一次升级检查
                logger.info("执行OpenSSH版本检查")
                
                # 检查当前版本
                detector = VersionDetector(args.mirror)
                current_version = detector.check_current_version()
                
                if not current_version:
                    logger.warning("无法检测当前OpenSSH版本")
                    time.sleep(3600)  # 等待1小时后重试
                    continue
                
                logger.info(f"当前OpenSSH版本: {current_version}")
                
                # 获取最新版本
                latest_version_info = detector.get_latest_version()
                
                logger.info(f"最新OpenSSH版本: {latest_version_info['version']}")
                
                # 检查是否需要升级
                if current_version != latest_version_info['version'] or args.force:
                    logger.info(f"检测到新版本 {latest_version_info['version']}，开始升级")
                    
                    # 执行安装
                    installer = Installer(latest_version_info['download_url'], args.install_dir)
                    
                    if installer.install_openssh():
                        # 验证安装
                        verification_result = installer.verify_installation()
                        
                        if verification_result['success']:
                            logger.info(f"OpenSSH升级成功! 新版本: {verification_result['current_version']}")
                            
                            # 重启SSH服务
                            config_manager = SSHConfigManager()
                            success, message = config_manager.restart_ssh_service()
                            if success:
                                logger.info("SSH服务重启成功")
                                
                                # 升级完成后清理传统启动脚本，确保只有systemd管理开机启动
                                try:
                                    ensure_systemd_only_startup()
                                    logger.info("传统启动脚本清理完成，确保只有systemd进行开机启动管理")
                                except SystemExit as e:
                                    logger.warning(f"传统启动脚本清理失败，但升级已完成: {e}")
                                except Exception as e:
                                    logger.warning(f"传统启动脚本清理过程中出错: {e}")
                                
                                # 处理root登录配置
                                if args.root_login != 'auto':
                                    config_manager = SSHConfigManager()
                                    enable_root = args.root_login == 'yes'
                                    success, message = config_manager.set_root_login(enable=enable_root, force=True)
                                    
                                    if success:
                                        action = "启用" if enable_root else "禁用"
                                        logger.info(f"已{action}root登录: {message}")
                                    else:
                                        action = "启用" if enable_root else "禁用"
                                        logger.warning(f"警告: {action}root登录失败: {message}")
                                
                                # 处理仅密钥登录配置
                                if args.key_only_login != 'auto':
                                    config_manager = SSHConfigManager()
                                    enable_key_only = args.key_only_login == 'yes'
                                    success, message = config_manager.set_key_only_login(enable=enable_key_only, force=True)
                                    
                                    if success:
                                        action = "启用" if enable_key_only else "禁用"
                                        logger.info(f"已{action}仅密钥登录: {message}")
                                    else:
                                        action = "启用" if enable_key_only else "禁用"
                                        logger.warning(f"警告: {action}仅密钥登录失败: {message}")
                                
                                # 重启SSH服务以应用配置更改
                                config_manager = SSHConfigManager()
                                success, message = config_manager.restart_ssh_service()
                                if success:
                                    logger.info(f"SSH服务重启成功（应用配置更改）: {message}")
                                else:
                                    logger.warning(f"警告: SSH服务重启失败，配置更改可能未生效: {message}")
                                
                                # 升级完成后验证SSH连接（使用临时账号）
                                logger.info("开始验证SSH升级后的连接功能")
                                try:
                                    from .temp_account_validator import validate_ssh_connection_after_upgrade
                                    validation_result = validate_ssh_connection_after_upgrade()
                                    if validation_result:
                                        logger.info("SSH升级验证成功，服务连接正常")
                                    else:
                                        logger.warning("SSH升级验证失败，可能存在连接问题")
                                except ImportError as e:
                                    logger.warning(f"SSH验证模块不可用，跳过验证: {e}")
                                except Exception as e:
                                    logger.warning(f"SSH连接验证过程中发生错误: {e}")
                            else:
                                logger.warning("SSH服务重启失败，请手动重启")
                        else:
                            logger.error("OpenSSH升级失败")
                    else:
                        logger.error("OpenSSH安装过程失败")
                else:
                    logger.info("当前已是最新版本，无需升级")
            else:
                logger.info(f"当前时间 {current_time} 不在升级时间段内，跳过检测")
            
            # 等待指定间隔时间后再检查
            interval_hours = getattr(args, 'check_interval', 1)
            interval_seconds = interval_hours * 3600
            logger.info(f"等待{interval_hours}小时后再次检查")
            time.sleep(interval_seconds)
            
        except KeyboardInterrupt:
            logger.info("守护进程被用户中断")
            break
        except Exception as e:
            logger.error(f"守护进程执行出错: {str(e)}")
            # 出错后等待5分钟再重试
            time.sleep(300)
    
    return 0


def main():
    """测试函数"""
    # 这里可以添加测试代码
    pass


if __name__ == "__main__":
    main()