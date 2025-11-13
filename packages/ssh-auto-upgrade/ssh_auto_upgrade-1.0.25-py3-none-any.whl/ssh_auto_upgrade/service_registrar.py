"""
服务注册模块
处理SSH自动升级服务的注册逻辑
"""

import os
import logging
from .service_manager import ServiceManager
from .installer_service_manager import InstallerServiceManager
from .logger import setup_logger
from .arg import (
    DEFAULT_MIRROR, DEFAULT_INSTALL_DIR, DEFAULT_DOWNLOAD_DIR,
    DEFAULT_LOG_DIR, DEFAULT_UPGRADE_TIME, DEFAULT_ROOT_LOGIN,
    DEFAULT_CHECK_INTERVAL, DEFAULT_FORCE, DEFAULT_KEY_ONLY_LOGIN
)

# 全局日志记录器
logger = logging.getLogger("ssh_auto_upgrade")


def register_service(args):
    """
    注册SSH自动升级服务
    
    Args:
        args: 命令行参数对象
        
    Returns:
        bool: 注册是否成功
    """
    try:
        logger.info("正在注册systemd服务...")
        
        # 设置系统环境变量开启交互模式
        os.environ["SSH_AUTO_UPGRADE_INTERACTIVE"] = "true"
        
        # 执行服务检测流程
        logger.info("开始服务检测流程...")
        installer_service_manager = InstallerServiceManager()
        ssh_services, non_ssh_services, should_continue = installer_service_manager.perform_service_detection()
        
        # 如果检测到非SSH服务且用户选择不继续，则终止注册
        if not should_continue:
            logger.warning("用户选择不继续注册服务，注册过程已终止")
            return False
        
        # 构建命令行参数 - 只添加与默认值不同的参数
        command_args = []
        if args.mirror != DEFAULT_MIRROR:
            command_args.append(f"-m {args.mirror}")
        if args.install_dir != DEFAULT_INSTALL_DIR:
            command_args.append(f"-i {args.install_dir}")
        if args.download_dir != DEFAULT_DOWNLOAD_DIR:
            command_args.append(f"-d {args.download_dir}")
        if args.log_dir != DEFAULT_LOG_DIR:
            command_args.append(f"-l {args.log_dir}")
        if args.upgrade_time != DEFAULT_UPGRADE_TIME:
            command_args.append(f"-t {args.upgrade_time}")
        if args.force != DEFAULT_FORCE:
            command_args.append("-f")
        if args.root_login != DEFAULT_ROOT_LOGIN:
            command_args.append(f"-rl {args.root_login}")
        # 添加仅密钥登录参数
        if hasattr(args, 'key_only_login') and args.key_only_login is not None and args.key_only_login != DEFAULT_KEY_ONLY_LOGIN:
            command_args.append(f"-kl {args.key_only_login}")
        # 添加检测间隔时间参数
        if hasattr(args, 'check_interval') and args.check_interval is not None and args.check_interval != DEFAULT_CHECK_INTERVAL:
            command_args.append(f"--interval {args.check_interval}")
        
        command_args_str = " ".join(command_args)
        
        # 创建ServiceManager实例，使用正确的参数
        service_manager = ServiceManager(
            service_name="ssh-auto-upgrade",
            executable_path="/usr/local/bin/ssh-auto-upgrade",
            description="SSH Auto Upgrade Service",
            working_directory="/tmp"
        )
        
        # 检查systemd是否可用
        if not service_manager.check_systemd_available():
            logger.error("systemd不可用，无法注册服务")
            return False
        
        # 检查权限
        if os.geteuid() != 0:
            logger.error("需要root权限来注册systemd服务")
            return False
        
        # 注册服务
        success, message = service_manager.register_service(command_args_str)
        
        if success:
            logger.info(f"成功: {message}")
            print("\n服务已注册，可以使用以下命令管理:")
            print("  systemctl start ssh-auto-upgrade    # 启动服务")
            print("  systemctl stop ssh-auto-upgrade     # 停止服务")
            print("  systemctl status ssh-auto-upgrade   # 查看服务状态")
            print("  systemctl enable ssh-auto-upgrade   # 启用开机自启")
            print("  systemctl disable ssh-auto-upgrade  # 禁用开机自启")
            
            # 打印ExecStart的值，方便用户查看完整的启动命令
            print("\n服务启动命令 (ExecStart):")
            exec_start_cmd = f"/usr/local/bin/ssh-auto-upgrade {command_args_str}"
            print(f"  {exec_start_cmd}")
            
            return True
        else:
            logger.error(f"错误: {message}")
            return False
            
    except Exception as e:
        logger.error(f"服务注册失败: {str(e)}")
        return False


def main():
    """测试函数"""
    # 这里可以添加测试代码
    pass


if __name__ == "__main__":
    main()