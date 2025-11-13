"""
安装器服务管理模块
专门处理OpenSSH安装过程中的系统服务管理功能
提供安装器特定的服务管理功能，通用服务管理由service_manager.py处理
"""

import logging

from .installer_service_detector import InstallerServiceDetector
from .service_manager import ServiceManager

# 设置日志记录器
logger = logging.getLogger(__name__)


class InstallerServiceManager:
    """安装器服务管理器"""
    
    def __init__(self):
        """初始化服务管理器"""
        # 使用服务检测器
        self.service_detector = InstallerServiceDetector()
        # 不在这里初始化ServiceManager，而是在需要时动态创建
        self._service_manager_cache = {}  # 缓存已创建的ServiceManager实例
    
    def _get_service_manager(self, service_name):
        """
        获取指定服务的ServiceManager实例
        
        Args:
            service_name: 服务名称
            
        Returns:
            ServiceManager: 对应的ServiceManager实例
        """
        if service_name not in self._service_manager_cache:
            # 动态创建ServiceManager实例
            self._service_manager_cache[service_name] = ServiceManager(service_name=service_name)
        return self._service_manager_cache[service_name]
    
    def detect_ssh_guard_services(self):
        """
        检测系统中已安装的SSH防护服务
        
        Returns:
            list: 已安装的SSH防护服务列表
        """
        try:
            # 直接调用服务检测器的检测方法
            return self.service_detector.detect_ssh_guard_services()
        except Exception as e:
            logger.error(f"检测SSH防护服务时出错: {e}")
            return []
    
    def perform_service_detection(self):
        """
        执行完整的服务检测流程
        
        Returns:
            tuple: (ssh_services, non_ssh_services, should_continue)
                   - SSH守护服务列表
                   - 非SSH守护服务列表  
                   - 是否继续注册流程
        """
        try:
            # 调用服务检测器的完整检测流程
            return self.service_detector.perform_service_detection()
        except Exception as e:
            logger.error(f"执行服务检测流程时出错: {e}")
            return [], [], False
    
    def check_and_handle_ssh_guard_services(self):
        """
        检查并处理SSH防护服务
        
        Returns:
            tuple: (ssh_services, should_continue)
                   - SSH守护服务列表
                   - 是否继续安装流程
        """
        try:
            logger.info("=== 开始SSH防护服务检测 ===")
            
            # 执行服务检测
            ssh_services, non_ssh_services, should_continue = self.perform_service_detection()
            
            # 如果有非SSH服务，需要用户确认
            if non_ssh_services:
                logger.info(f"检测到以下非SSH服务: {non_ssh_services}")
                logger.info("这些服务可能与SSH服务冲突，建议重命名或停止这些服务。")
            
            # 如果有SSH服务，显示确认信息
            if ssh_services:
                logger.info(f"检测到以下SSH守护服务: {ssh_services}")
                logger.info("这些服务将被用于SSH连接管理。")
            
            logger.info("=== SSH防护服务检测完成 ===")
            
            return ssh_services, should_continue
            
        except Exception as e:
            logger.error(f"检查和处理SSH防护服务时出错: {e}")
            return [], False
    
    def stop_ssh_guard_services(self):
        """
        停止所有SSH守护服务（包括CLS、xc-ssh等）
        
        Returns:
            bool: 停止是否成功
        """
        try:
            logger.info("=== 开始停止SSH守护服务 ===")
            
            # 获取所有SSH守护服务
            ssh_services, _ = self.check_and_handle_ssh_guard_services()
            
            success = True
            
            # 停止每个SSH守护服务
            for service_name in ssh_services:
                service_manager = self._get_service_manager(service_name)
                exists, _ = service_manager.get_service_status()
                if exists:
                    stop_success, message = service_manager.stop_service()
                    if stop_success:
                        logger.info(f"✓ {service_name} 服务已停止")
                    else:
                        logger.error(f"✗ {service_name} 服务停止失败: {message}")
                        success = False
                else:
                    logger.info(f"{service_name} 服务不存在，无需停止")
            
            logger.info("=== SSH守护服务停止完成 ===")
            return success
            
        except Exception as e:
            logger.error(f"停止SSH守护服务时出错: {e}")
            return False
    
    def start_ssh_guard_services(self):
        """
        启动所有SSH守护服务（包括CLS、xc-ssh等）
        
        Returns:
            bool: 启动是否成功
        """
        try:
            logger.info("=== 开始启动SSH守护服务 ===")
            
            # 获取所有SSH守护服务
            ssh_services, _ = self.check_and_handle_ssh_guard_services()
            
            success = True
            
            # 启动每个SSH守护服务
            for service_name in ssh_services:
                service_manager = self._get_service_manager(service_name)
                exists, _ = service_manager.get_service_status()
                if exists:
                    start_success, message = service_manager.start_service()
                    if start_success:
                        logger.info(f"✓ {service_name} 服务已启动")
                    else:
                        logger.error(f"✗ {service_name} 服务启动失败: {message}")
                        success = False
                else:
                    logger.info(f"{service_name} 服务不存在，无需启动")
            
            logger.info("=== SSH守护服务启动完成 ===")
            return success
            
        except Exception as e:
            logger.error(f"启动SSH守护服务时出错: {e}")
            return False
    
    def check_native_ssh_service(self):
        """
        检查系统原生SSH服务状态
        
        Returns:
            dict: 包含原生SSH服务信息的字典
        """
        # 直接检查原生SSH服务
        ssh_services = ['ssh', 'openssh-server']
        
        for service_name in ssh_services:
            service_manager = self._get_service_manager(service_name)
            exists, status_info = service_manager.get_service_status()
            if exists:
                # 使用ServiceManager的方法检查服务状态
                # 从状态信息中推断服务是否活跃和启用
                is_active = "Active: active" in status_info
                is_enabled = "enabled" in status_info.lower()
                
                return {
                    'exists': True,
                    'service_name': service_name,
                    'is_active': is_active,
                    'is_enabled': is_enabled,
                    'is_native': True
                }
        
        return {'exists': False, 'service_name': None, 'is_active': False, 'is_enabled': False, 'is_native': False}
    
    def disable_native_ssh_service(self):
        """
        禁用原生SSH服务，避免端口冲突
        
        Returns:
            bool: 禁用是否成功
        """
        ssh_info = self.check_native_ssh_service()
        
        if not ssh_info['exists']:
            logger.info("系统未安装原生SSH服务，无需禁用")
            return True
        
        service_name = ssh_info['service_name']
        logger.info(f"检测到原生SSH服务: {service_name}")
        
        success = True
        
        # 停止原生SSH服务
        if ssh_info['is_active']:
            service_manager = self._get_service_manager(service_name)
            stop_success, message = service_manager.stop_service()
            if not stop_success:
                logger.warning(f"警告: 原生SSH服务 {service_name} 停止失败: {message}")
                success = False
        
        # 禁用原生SSH服务开机自启
        if ssh_info['is_enabled']:
            service_manager = self._get_service_manager(service_name)
            disable_success, message = service_manager.disable_service()
            if not disable_success:
                logger.warning(f"警告: 原生SSH服务 {service_name} 禁用开机自启失败: {message}")
                success = False
        
        if success:
            logger.info("原生SSH服务已成功禁用")
        else:
            logger.warning("警告: 原生SSH服务禁用可能不完整")
        
        return success


def main():
    """测试函数"""
    manager = InstallerServiceManager()
    
    # 测试SSH防护服务检测
    ssh_services, should_continue = manager.check_and_handle_ssh_guard_services()
    logger.info(f"检测到的SSH防护服务: {ssh_services}")
    logger.info(f"是否继续安装流程: {should_continue}")
    
    # 测试统一的SSH守护服务管理
    logger.info("\n=== 测试SSH守护服务管理 ===")
    if ssh_services:
        stopped = manager.stop_ssh_guard_services()
        logger.info(f"SSH守护服务停止结果: {stopped}")
        
        started = manager.start_ssh_guard_services()
        logger.info(f"SSH守护服务启动结果: {started}")
    
    # 测试原生SSH服务管理
    logger.info("\n=== 测试原生SSH服务管理 ===")
    ssh_info = manager.check_native_ssh_service()
    logger.info(f"原生SSH服务信息: {ssh_info}")
    
    if ssh_info['exists']:
        disabled = manager.disable_native_ssh_service()
        logger.info(f"原生SSH服务禁用结果: {disabled}")


if __name__ == "__main__":
    main()