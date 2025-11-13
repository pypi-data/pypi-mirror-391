"""
systemd检测模块
提供独立的systemd检测功能（使用D-Bus API）
"""

import os
import logging

logger = logging.getLogger(__name__)

# 导入D-Bus和systemd模块
try:
    import systemd.daemon
    import dbus
    SYSTEMD_DBUS_AVAILABLE = True
except ImportError:
    SYSTEMD_DBUS_AVAILABLE = False


def check_systemd_init_system():
    """
    检查当前系统是否使用systemd作为init系统（使用D-Bus API）
    
    Returns:
        bool: 如果是systemd系统返回True，否则返回False
    """
    try:
        # 检查D-Bus和systemd模块是否可用
        if not SYSTEMD_DBUS_AVAILABLE:
            return False
        
        # 检查D-Bus连接是否成功
        bus = dbus.SystemBus()
        manager_proxy = bus.get_object(
            'org.freedesktop.systemd1',
            '/org/freedesktop/systemd1'
        )
        
        # 获取管理器接口
        manager_interface = dbus.Interface(
            manager_proxy,
            'org.freedesktop.systemd1.Manager'
        )
        
        # 如果能成功获取接口，说明systemd可用
        # 通过调用一个简单的方法来验证
        manager_interface.GetUnit()
        
        # 额外检查：检查/sbin/init是否为systemd的符号链接（作为补充验证）
        if os.path.exists("/sbin/init"):
            if os.path.islink("/sbin/init"):
                target = os.readlink("/sbin/init")
                if "systemd" in target:
                    return True
        
        # 额外检查：检查/proc/1/comm是否为systemd（作为补充验证）
        if os.path.exists("/proc/1/comm"):
            with open("/proc/1/comm", "r") as f:
                comm = f.read().strip()
                if comm == "systemd":
                    return True
        
        # 如果D-Bus连接成功，认为是systemd系统
        return True
        
    except Exception as e:
        # 如果D-Bus连接失败或发生异常，不是systemd系统
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
    获取systemd状态信息（使用D-Bus API）
    
    Returns:
        dict: 包含systemd状态信息的字典
    """
    status = {
        "is_systemd": False,
        "init_system": "unknown",
        "systemd_version": "unknown",
        "systemd_running": False,
        "dbus_available": False
    }
    
    try:
        # 检查D-Bus模块是否可用
        status["dbus_available"] = SYSTEMD_DBUS_AVAILABLE
        
        # 检查是否为systemd系统
        status["is_systemd"] = check_systemd_init_system()
        
        if status["is_systemd"]:
            status["init_system"] = "systemd"
            status["systemd_running"] = True
            
            try:
                # 通过D-Bus连接获取systemd版本信息
                bus = dbus.SystemBus()
                manager_proxy = bus.get_object(
                    'org.freedesktop.systemd1',
                    '/org/freedesktop/systemd1'
                )
                
                # 通过读取/proc/1/comm获取systemd进程信息
                if os.path.exists("/proc/1/comm"):
                    with open("/proc/1/comm", "r") as f:
                        comm = f.read().strip()
                        if comm == "systemd":
                            status["systemd_version"] = "systemd (detected via D-Bus)"
                
                # 通过读取systemd配置文件获取版本信息（备选方案）
                version_files = [
                    "/lib/systemd/systemd",
                    "/usr/lib/systemd/systemd"
                ]
                
                for version_file in version_files:
                    if os.path.exists(version_file):
                        try:
                            # 尝试读取systemd版本信息
                            result = os.popen(f'"{version_file}" --version 2>/dev/null | head -1').read().strip()
                            if result and "systemd" in result.lower():
                                status["systemd_version"] = result
                                break
                        except:
                            continue
                            
            except Exception:
                # 如果D-Bus信息获取失败，使用基本信息
                status["systemd_version"] = "systemd (D-Bus detected)"
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