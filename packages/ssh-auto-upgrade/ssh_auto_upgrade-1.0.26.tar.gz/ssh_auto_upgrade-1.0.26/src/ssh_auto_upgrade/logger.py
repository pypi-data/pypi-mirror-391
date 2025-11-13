"""
日志记录器模块
负责记录安装过程的日志
"""

import logging
import os
import sys
from datetime import datetime
from logging.handlers import RotatingFileHandler


class CircularFileHandler(logging.Handler):
    """
    循环日志文件处理器
    只保存两份日志，一份最大1MB，当第一个达到1MB则创建第二个，当第二个达到1MB则重写第一个
    """
    
    def __init__(self, log_dir, max_bytes=1024*1024, backup_count=1):
        """
        初始化循环文件处理器
        
        Args:
            log_dir: 日志目录路径
            max_bytes: 每个日志文件的最大字节数（默认1MB）
            backup_count: 备份文件数量（默认1个，总共2个文件）
        """
        super().__init__()
        self.log_dir = log_dir
        self.max_bytes = max_bytes
        self.backup_count = backup_count
        self.current_file_index = 0
        
        # 创建日志目录
        os.makedirs(log_dir, exist_ok=True)
        
        # 生成基础日志文件名
        self.base_filename = os.path.join(log_dir, "ssh_upgrade")
        self.file_paths = []
        
        # 初始化日志文件路径
        for i in range(backup_count + 1):
            if i == 0:
                file_path = f"{self.base_filename}.log"
            else:
                file_path = f"{self.base_filename}.{i}.log"
            self.file_paths.append(file_path)
        
        # 找到当前应该使用的文件
        self._find_current_file()
        
        # 打开当前文件
        self._open_current_file()
    
    def _find_current_file(self):
        """找到当前应该使用的日志文件"""
        # 检查每个文件的大小，找到第一个未满的文件
        for i, file_path in enumerate(self.file_paths):
            if os.path.exists(file_path):
                file_size = os.path.getsize(file_path)
                if file_size < self.max_bytes:
                    self.current_file_index = i
                    return
        
        # 如果所有文件都满了，从第一个开始重写
        self.current_file_index = 0
    
    def _open_current_file(self):
        """打开当前日志文件"""
        if hasattr(self, '_file'):
            self._file.close()
        
        current_path = self.file_paths[self.current_file_index]
        self._file = open(current_path, 'a', encoding='utf-8')
        
        # 记录当前文件路径，供get_log_file_path使用
        self._current_log_path = current_path
    
    def _should_rollover(self):
        """检查是否需要滚动到下一个文件"""
        if not hasattr(self, '_file'):
            return False
        
        # 检查当前文件大小
        current_pos = self._file.tell()
        return current_pos >= self.max_bytes
    
    def _do_rollover(self):
        """执行日志文件滚动"""
        if hasattr(self, '_file'):
            self._file.close()
        
        # 移动到下一个文件
        self.current_file_index = (self.current_file_index + 1) % (self.backup_count + 1)
        
        # 如果回到第一个文件，清空它
        if self.current_file_index == 0:
            # 清空所有文件，重新开始
            for file_path in self.file_paths:
                if os.path.exists(file_path):
                    os.remove(file_path)
        
        # 打开新的当前文件
        self._open_current_file()
    
    def emit(self, record):
        """
        发送日志记录到文件
        
        Args:
            record: 日志记录
        """
        try:
            # 格式化日志消息
            msg = self.format(record)
            
            # 检查是否需要滚动
            if self._should_rollover():
                self._do_rollover()
            
            # 写入日志
            self._file.write(msg + '\n')
            self._file.flush()
            
        except Exception:
            self.handleError(record)
    
    def close(self):
        """关闭处理器"""
        if hasattr(self, '_file'):
            self._file.close()
        super().close()
    
    def get_current_log_path(self):
        """
        获取当前日志文件路径
        
        Returns:
            str: 当前日志文件路径
        """
        return getattr(self, '_current_log_path', None)


def setup_logger(log_dir="/var/log/ssh-auto-upgrade"):
    """
    设置日志记录器
    
    Args:
        log_dir: 日志目录路径
        
    Returns:
        logging.Logger: 配置好的日志记录器
    """
    # 创建日志记录器
    logger = logging.getLogger("ssh_auto_upgrade")
    logger.setLevel(logging.INFO)
    
    # 避免重复添加处理器
    if logger.handlers:
        return logger
    
    # 创建循环文件处理器（2个文件，每个最大1MB）
    file_handler = CircularFileHandler(log_dir, max_bytes=1024*1024, backup_count=1)
    file_handler.setLevel(logging.INFO)
    
    # 创建控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    
    # 创建格式化器（包含文件名、行号和函数名信息）
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] %(funcName)s() - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # 添加处理器到记录器
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger


def log_installation_start(logger, version_info):
    """
    记录安装开始信息
    
    Args:
        logger: 日志记录器
        version_info: 版本信息
    """
    logger.info("=" * 60)
    logger.info("OpenSSH自动升级开始")
    logger.info(f"目标版本: {version_info.get('version', '未知')}")
    logger.info(f"下载URL: {version_info.get('download_url', '未知')}")
    logger.info("=" * 60)


def log_installation_step(logger, step_name, status="开始"):
    """
    记录安装步骤信息
    
    Args:
        logger: 日志记录器
        step_name: 步骤名称
        status: 步骤状态
    """
    logger.info(f"[{step_name}] {status}")


def log_installation_success(logger, version_info):
    """
    记录安装成功信息
    
    Args:
        logger: 日志记录器
        version_info: 版本信息
    """
    logger.info("=" * 60)
    logger.info("OpenSSH自动升级成功完成")
    logger.info(f"安装版本: {version_info.get('version', '未知')}")
    logger.info("=" * 60)


def log_installation_error(logger, error_message, step_name=None):
    """
    记录安装错误信息
    
    Args:
        logger: 日志记录器
        error_message: 错误信息
        step_name: 发生错误的步骤名称
    """
    if step_name:
        logger.error(f"[{step_name}] 失败: {error_message}")
    else:
        logger.error(f"安装失败: {error_message}")


def log_verification_result(logger, verification_result):
    """
    记录验证结果
    
    Args:
        logger: 日志记录器
        verification_result: 验证结果字典
    """
    logger.info("安装验证结果:")
    logger.info(f"  成功: {verification_result.get('success', False)}")
    logger.info(f"  SSH服务状态: {verification_result.get('ssh_service_active', False)}")
    logger.info(f"  当前版本: {verification_result.get('current_version', '未知')}")
    
    if not verification_result.get('success', False):
        logger.warning("安装验证发现问题，建议手动检查")


def get_log_file_path(logger):
    """
    获取当前日志文件路径
    
    Args:
        logger: 日志记录器
        
    Returns:
        str: 日志文件路径，如果没有文件处理器则返回None
    """
    for handler in logger.handlers:
        if isinstance(handler, CircularFileHandler):
            return handler.get_current_log_path()
        elif isinstance(handler, logging.FileHandler):
            return handler.baseFilename
    return None