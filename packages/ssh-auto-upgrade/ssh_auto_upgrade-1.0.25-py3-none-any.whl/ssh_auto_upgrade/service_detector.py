"""
守护服务检测配置模块

定义需要检测的SSH守护服务列表和相关的检测逻辑配置。
"""

# 需要检测的SSH守护服务列表
SSH_GUARD_SERVICES = ['cls', 'xc-ssh', 'ssh-guardian']

def get_ssh_guard_services():
    """
    获取需要检测的SSH守护服务列表
    
    Returns:
        list: SSH守护服务名称列表
    """
    return SSH_GUARD_SERVICES.copy()

def get_service_detection_prompt(service_name):
    """
    获取服务检测的提示信息
    
    Args:
        service_name: 服务名称
        
    Returns:
        str: 提示信息
    """
    return f"""⚠️  检测到{service_name}服务存在
请确认该服务是否为SSH守护服务：
   - 如果是SSH守护服务，可以继续注册，升级期间会停止该服务，升级完成后启动
   - 如果不是SSH守护服务，建议重命名该服务以避免冲突"""

def get_non_ssh_warning(non_ssh_services):
    """
    获取非SSH守护服务的警告信息
    
    Args:
        non_ssh_services: 非SSH守护服务列表
        
    Returns:
        str: 警告信息
    """
    return f"""⚠️  警告: 检测到以下非SSH守护服务: {', '.join(non_ssh_services)}
这些服务可能与SSH自动升级服务产生冲突。
建议重命名这些服务或使用不同的端口以避免冲突。
如果继续注册，可能会在升级期间影响这些服务的正常运行。"""

def get_ssh_confirmation(ssh_services):
    """
    获取SSH守护服务的确认信息
    
    Args:
        ssh_services: SSH守护服务列表
        
    Returns:
        str: 确认信息
    """
    return f"""✓ 确认以下服务为SSH守护服务: {', '.join(ssh_services)}
这些服务将在升级期间被停止，升级完成后重新启动。"""