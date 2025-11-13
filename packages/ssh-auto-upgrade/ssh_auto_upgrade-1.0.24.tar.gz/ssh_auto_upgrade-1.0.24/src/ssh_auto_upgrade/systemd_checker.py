"""
systemd检测模块
提供独立的systemd检测功能
"""

import os
import subprocess
import logging

logger = logging.getLogger(__name__)


def check_systemd_init_system():
    """
    检查当前系统是否使用systemd作为init系统
    
    Returns:
        bool: 如果是systemd系统返回True，否则返回False
    """
    try:
        # 检查/sbin/init是否为systemd的符号链接
        if os.path.exists("/sbin/init"):
            if os.path.islink("/sbin/init"):
                target = os.readlink("/sbin/init")
                if "systemd" in target:
                    return True
        
        # 检查/proc/1/comm是否为systemd
        if os.path.exists("/proc/1/comm"):
            with open("/proc/1/comm", "r") as f:
                comm = f.read().strip()
                if comm == "systemd":
                    return True
        
        # 检查systemctl命令是否可用
        try:
            result = subprocess.run(["systemctl", "--version"], 
                                  capture_output=True, text=True)
            if result.returncode != 0:
                return False
        except (subprocess.SubprocessError, FileNotFoundError):
            return False
        
        # 检查systemd是否正在运行
        result = subprocess.run(["systemctl", "is-system-running"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            return True
        
        return False
        
    except Exception as e:
        return False


def ensure_systemd_only():
    """
    确保只有systemd进行开机启动管理，如果不是systemd系统则终止运行
    
    Raises:
        SystemExit: 如果不是systemd系统则终止程序
    """
    if not check_systemd_init_system():
        logger.error("错误: 当前系统不是systemd系统，本工具仅支持systemd系统")
        logger.error("请确保系统使用systemd作为init系统")
        raise SystemExit(1)
    else:
        logger.info("✓ 系统检测: 当前系统使用systemd作为init系统")
        logger.info("  systemd检测通过，继续执行后续操作...")


def get_systemd_status():
    """
    获取systemd状态信息
    
    Returns:
        dict: 包含systemd状态信息的字典
    """
    status = {
        "is_systemd": False,
        "init_system": "unknown",
        "systemd_version": "unknown",
        "systemd_running": False
    }
    
    try:
        # 检查是否为systemd系统
        status["is_systemd"] = check_systemd_init_system()
        
        if status["is_systemd"]:
            status["init_system"] = "systemd"
            
            # 获取systemd版本
            result = subprocess.run(["systemctl", "--version"], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                if lines:
                    status["systemd_version"] = lines[0]
            
            # 检查systemd是否正在运行
            result = subprocess.run(["systemctl", "is-system-running"], 
                                  capture_output=True, text=True)
            status["systemd_running"] = result.returncode == 0
        else:
            # 尝试检测其他init系统
            if os.path.exists("/sbin/init"):
                if os.path.islink("/sbin/init"):
                    target = os.readlink("/sbin/init")
                    if "upstart" in target:
                        status["init_system"] = "upstart"
                    elif "sysvinit" in target:
                        status["init_system"] = "sysvinit"
            
            # 检查/proc/1/comm
            if os.path.exists("/proc/1/comm"):
                with open("/proc/1/comm", "r") as f:
                    comm = f.read().strip()
                    if comm != "systemd":
                        status["init_system"] = comm
        
    except Exception as e:
        status["error"] = str(e)
    
    return status


if __name__ == "__main__":
    # 独立运行时的测试代码
    status = get_systemd_status()
    logger.info("Systemd检测结果:")
    logger.info(f"是否为systemd系统: {status['is_systemd']}")
    logger.info(f"Init系统: {status['init_system']}")
    logger.info(f"Systemd版本: {status['systemd_version']}")
    logger.info(f"Systemd是否运行: {status['systemd_running']}")
    
    if not status['is_systemd']:
        logger.warning("警告: 当前系统不是systemd系统")
    else:
        logger.info("系统使用systemd作为init系统")