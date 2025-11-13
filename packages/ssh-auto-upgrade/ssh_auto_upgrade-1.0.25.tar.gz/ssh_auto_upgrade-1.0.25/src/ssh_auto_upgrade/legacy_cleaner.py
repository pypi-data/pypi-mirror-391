"""
传统启动脚本清理模块
提供独立的传统启动脚本清理功能
"""

import os
import shutil
from pathlib import Path


def get_legacy_startup_directories():
    """
    获取需要清理的传统启动脚本目录列表
    
    Returns:
        list: 传统启动脚本目录路径列表
    """
    legacy_dirs = [
        "/etc/rc.d",
        "/etc/rc.local",
        "/etc/init.d",
        "/etc/rc0.d",
        "/etc/rc1.d", 
        "/etc/rc2.d",
        "/etc/rc3.d",
        "/etc/rc4.d",
        "/etc/rc5.d",
        "/etc/rc6.d",
        "/etc/rcS.d",
        "/etc/rc.local.d"
    ]
    
    # 检查目录是否存在
    existing_dirs = []
    for dir_path in legacy_dirs:
        if os.path.exists(dir_path):
            existing_dirs.append(dir_path)
    
    return existing_dirs


def find_ssh_related_startup_files():
    """
    查找与SSH相关的传统启动脚本文件
    
    Returns:
        list: SSH相关启动脚本文件路径列表
    """
    ssh_files = []
    legacy_dirs = get_legacy_startup_directories()
    
    # SSH相关的文件名模式
    ssh_patterns = [
        "ssh",
        "sshd",
        "openssh"
    ]
    
    for dir_path in legacy_dirs:
        if os.path.isdir(dir_path):
            try:
                for item in os.listdir(dir_path):
                    item_path = os.path.join(dir_path, item)
                    
                    # 检查是否为文件且包含SSH相关模式
                    if os.path.isfile(item_path):
                        for pattern in ssh_patterns:
                            if pattern.lower() in item.lower():
                                ssh_files.append(item_path)
                                break
                    
                    # 检查符号链接
                    elif os.path.islink(item_path):
                        for pattern in ssh_patterns:
                            if pattern.lower() in item.lower():
                                ssh_files.append(item_path)
                                break
                                
            except (PermissionError, FileNotFoundError):
                continue
    
    return ssh_files


def backup_legacy_files(files_to_backup):
    """
    备份传统启动脚本文件
    
    Args:
        files_to_backup: 需要备份的文件列表
        
    Returns:
        str: 备份目录路径，如果备份失败返回None
    """
    if not files_to_backup:
        return None
    
    backup_dir = "/tmp/ssh_auto_upgrade_backup"
    
    try:
        # 创建备份目录
        Path(backup_dir).mkdir(parents=True, exist_ok=True)
        
        # 备份文件
        for file_path in files_to_backup:
            if os.path.exists(file_path):
                file_name = os.path.basename(file_path)
                backup_path = os.path.join(backup_dir, file_name)
                
                if os.path.isfile(file_path):
                    shutil.copy2(file_path, backup_path)
                elif os.path.islink(file_path):
                    # 备份符号链接的目标
                    target = os.readlink(file_path)
                    with open(backup_path + ".link", "w") as f:
                        f.write(target)
        
        return backup_dir
        
    except Exception as e:
        print(f"备份文件失败: {e}")
        return None


def remove_legacy_startup_files():
    """
    移除传统启动脚本文件
    
    Returns:
        dict: 清理结果信息
    """
    result = {
        "backup_dir": None,
        "removed_files": [],
        "failed_files": [],
        "total_found": 0
    }
    
    # 查找SSH相关的传统启动脚本
    ssh_files = find_ssh_related_startup_files()
    result["total_found"] = len(ssh_files)
    
    if not ssh_files:
        return result
    
    # 备份文件
    result["backup_dir"] = backup_legacy_files(ssh_files)
    
    # 移除文件
    for file_path in ssh_files:
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.remove(file_path)
                result["removed_files"].append(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
                result["removed_files"].append(file_path)
        except Exception as e:
            result["failed_files"].append({
                "file": file_path,
                "error": str(e)
            })
    
    return result


def check_legacy_startup_status():
    """
    检查传统启动脚本状态
    
    Returns:
        dict: 传统启动脚本状态信息
    """
    status = {
        "legacy_dirs_exist": [],
        "ssh_related_files": [],
        "has_legacy_startup": False
    }
    
    # 检查传统启动目录
    legacy_dirs = get_legacy_startup_directories()
    status["legacy_dirs_exist"] = legacy_dirs
    
    # 查找SSH相关文件
    ssh_files = find_ssh_related_startup_files()
    status["ssh_related_files"] = ssh_files
    
    # 判断是否存在传统启动脚本
    status["has_legacy_startup"] = len(ssh_files) > 0
    
    return status


def ensure_systemd_only_startup():
    """
    确保只有systemd进行开机启动管理
    如果不是systemd系统则终止运行，并清理传统启动脚本
    
    Raises:
        SystemExit: 如果不是systemd系统则终止程序
    """
    # 导入systemd检测模块
    from .systemd_checker import check_systemd_init_system
    
    # 检查是否为systemd系统
    if not check_systemd_init_system():
        print("错误: 当前系统不是systemd系统，本工具仅支持systemd系统")
        print("请确保系统使用systemd作为init系统")
        raise SystemExit(1)
    
    # 清理传统启动脚本
    print("正在检查传统启动脚本...")
    status = check_legacy_startup_status()
    
    if status["has_legacy_startup"]:
        print(f"发现 {len(status['ssh_related_files'])} 个传统启动脚本")
        print("正在清理传统启动脚本...")
        
        result = remove_legacy_startup_files()
        
        if result["backup_dir"]:
            print(f"已备份到: {result['backup_dir']}")
        
        print(f"成功移除 {len(result['removed_files'])} 个文件")
        
        if result["failed_files"]:
            print(f"移除失败 {len(result['failed_files'])} 个文件")
            for failed in result["failed_files"]:
                print(f"  {failed['file']}: {failed['error']}")
    else:
        print("未发现需要清理的传统启动脚本")


if __name__ == "__main__":
    # 独立运行时的测试代码
    print("传统启动脚本状态检查:")
    status = check_legacy_startup_status()
    
    print(f"存在的传统启动目录: {len(status['legacy_dirs_exist'])}")
    for dir_path in status['legacy_dirs_exist']:
        print(f"  - {dir_path}")
    
    print(f"发现的SSH相关启动脚本: {len(status['ssh_related_files'])}")
    for file_path in status['ssh_related_files']:
        print(f"  - {file_path}")
    
    if status['has_legacy_startup']:
        print("\n执行清理操作...")
        result = remove_legacy_startup_files()
        
        print(f"备份目录: {result['backup_dir']}")
        print(f"成功移除: {len(result['removed_files'])} 个文件")
        print(f"移除失败: {len(result['failed_files'])} 个文件")
    else:
        print("\n无需清理")