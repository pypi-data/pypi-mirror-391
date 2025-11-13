"""
安装器服务检测模块
专门处理OpenSSH安装过程中的服务检测流程
"""

import os

from .service_detector import (
    get_ssh_guard_services, 
    get_service_detection_prompt,
    get_non_ssh_warning, 
    get_ssh_confirmation
)
from .service_manager import ServiceManager


class InstallerServiceDetector:
    """安装器服务检测器"""
    
    def __init__(self):
        """初始化服务检测器"""
        self.ssh_guard_services = get_ssh_guard_services()
        # 通过环境变量判断是否需要交互模式
        self.interactive_mode = os.environ.get('SSH_AUTO_UPGRADE_INTERACTIVE', 'false').lower() == 'true'
    
    def check_service_exists(self, service_name):
        """
        检查systemd服务是否存在
        
        Args:
            service_name: 服务名称
            
        Returns:
            bool: 服务是否存在
        """
        try:
            # 直接调用ServiceManager的get_service_status方法来检查服务状态
            service_mgr = ServiceManager(
                service_name=service_name,
                executable_path="/usr/bin/echo"  # 临时路径，仅用于检测
            )
            exists, _ = service_mgr.get_service_status()
            return exists
            
        except Exception as e:
            print(f"检查服务 {service_name} 时出错: {e}")
            return False
    
    def detect_ssh_guard_services(self):
        """
        检测系统中已安装的SSH防护服务
        
        Returns:
            list: 已安装的SSH防护服务列表
        """
        installed_services = []
        
        for service_name in self.ssh_guard_services:
            if self.check_service_exists(service_name):
                installed_services.append(service_name)
        
        return installed_services
    
    def handle_non_ssh_services(self, non_ssh_services):
        """
        处理非SSH守护服务
        
        Args:
            non_ssh_services: 非SSH守护服务列表
            
        Returns:
            bool: 是否继续注册流程
        """
        if non_ssh_services:
            # 使用配置的警告信息
            print(get_non_ssh_warning(non_ssh_services))
            
            if self.interactive_mode:
                # 交互模式：询问用户是否继续
                while True:
                    response = input("是否继续注册服务？(y/n): ").strip().lower()
                    if response in ['y', 'yes', '是']:
                        print("继续注册服务...")
                        return True
                    elif response in ['n', 'no', '否']:
                        return False
                    else:
                        print("请输入 'y' 或 'n' 来确认是否继续")
            else:
                # 非交互模式：默认继续
                print("继续注册服务...")
        
        return True
    
    def confirm_ssh_services(self, ssh_services):
        """
        确认SSH守护服务处理方式
        
        Args:
            ssh_services: SSH守护服务列表
        """
        if ssh_services:
            # 使用配置的确认信息
            print(get_ssh_confirmation(ssh_services))
    
    def perform_service_detection(self):
        """
        执行完整的服务检测流程
        
        Returns:
            tuple: (ssh_services, non_ssh_services, should_continue)
                   - SSH守护服务列表
                   - 非SSH守护服务列表  
                   - 是否继续注册流程
        """
        print("=== 开始服务检测流程 ===")
        
        # 检测已安装的SSH防护服务
        installed_services = self.detect_ssh_guard_services()
        
        ssh_services = []
        non_ssh_services = []
        
        for service_name in installed_services:
            # 使用配置的提示信息
            print(get_service_detection_prompt(service_name))
            
            if self.interactive_mode:
                # 交互模式：询问用户服务分类
                while True:
                    response = input(f"{service_name}服务是否为SSH守护服务？(y/n): ").strip().lower()
                    if response in ['y', 'yes', '是']:
                        ssh_services.append(service_name)
                        print(f"确认{service_name}为SSH守护服务，继续注册...")
                        break
                    elif response in ['n', 'no', '否']:
                        non_ssh_services.append(service_name)
                        print(f"{service_name}不是SSH守护服务，建议重命名该服务")
                        break
                    else:
                        print("请输入 'y' 或 'n' 来确认")
            else:
                # 非交互模式：自动分类为SSH守护服务
                ssh_services.append(service_name)
                print(f"自动确认{service_name}为SSH守护服务，继续注册...")
        
        # 处理非SSH守护服务
        should_continue = self.handle_non_ssh_services(non_ssh_services)
        
        # 确认SSH守护服务处理方式
        self.confirm_ssh_services(ssh_services)
        
        print("=== 服务检测流程完成 ===")
        
        return ssh_services, non_ssh_services, should_continue


def detect_services_for_installation():
    """
    为安装过程执行服务检测的便捷函数
    
    Returns:
        tuple: (ssh_services, non_ssh_services, should_continue)
    """
    detector = InstallerServiceDetector()
    return detector.perform_service_detection()


def main():
    """测试函数"""
    detector = InstallerServiceDetector()
    
    # 测试服务检测流程
    ssh_services, non_ssh_services, should_continue = detector.perform_service_detection()
    
    print(f"检测结果:")
    print(f"  SSH守护服务: {ssh_services}")
    print(f"  非SSH守护服务: {non_ssh_services}")
    print(f"  是否继续: {should_continue}")


if __name__ == "__main__":
    main()