"""
镜像地址连接检测模块
用于检测传入的镜像地址是否可用
"""

import requests
import urllib3
from urllib.parse import urljoin
import logging
import time

# 禁用不安全的HTTPS请求警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logger = logging.getLogger(__name__)


class MirrorChecker:
    """镜像地址连接检测器"""
    
    def __init__(self, timeout: int = 10, retry_count: int = 3):
        """
        初始化镜像检测器
        
        Args:
            timeout: 请求超时时间（秒）
            retry_count: 重试次数
        """
        self.timeout = timeout
        self.retry_count = retry_count
        self.session = requests.Session()
        # 设置请求头，模拟浏览器访问
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def check_mirror_availability(self, mirror_url: str) -> bool:
        """
        检测镜像地址是否可用
        
        Args:
            mirror_url: 镜像地址
            
        Returns:
            bool: 镜像地址是否可用
        """
        logger.info(f"开始检测镜像地址可用性: {mirror_url}")
        
        # 验证URL格式
        if not self._validate_url_format(mirror_url):
            logger.error(f"镜像地址格式无效: {mirror_url}")
            return False
        
        # 检测镜像地址连接
        for attempt in range(self.retry_count):
            try:
                logger.debug(f"第 {attempt + 1} 次尝试连接镜像地址...")
                
                # 测试基础连接
                if not self._test_connection(mirror_url):
                    continue
                
                # 测试目录访问（检查是否存在openssh目录）
                if not self._test_directory_access(mirror_url):
                    continue
                
                logger.info(f"✓ 镜像地址可用: {mirror_url}")
                return True
                
            except requests.exceptions.RequestException as e:
                logger.warning(f"第 {attempt + 1} 次连接失败: {e}")
                if attempt < self.retry_count - 1:
                    time.sleep(1)  # 等待1秒后重试
                else:
                    logger.error(f"镜像地址连接失败: {mirror_url}, 错误: {e}")
                    return False
            except Exception as e:
                logger.error(f"检测镜像地址时发生未知错误: {e}")
                return False
        
        return False
    
    def _validate_url_format(self, url: str) -> bool:
        """验证URL格式"""
        if not url:
            return False
        
        # 检查URL是否以http://或https://开头
        if not url.startswith(('http://', 'https://')):
            return False
        
        # 检查URL是否包含有效的主机名
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            if not parsed.netloc:
                return False
        except Exception:
            return False
        
        return True
    
    def _test_connection(self, url: str) -> bool:
        """测试基础连接"""
        try:
            response = self.session.head(url, timeout=self.timeout, verify=False)
            return response.status_code in [200, 301, 302]
        except requests.exceptions.RequestException:
            # 如果HEAD请求失败，尝试GET请求
            try:
                response = self.session.get(url, timeout=self.timeout, verify=False)
                return response.status_code in [200, 301, 302]
            except requests.exceptions.RequestException:
                return False
    
    def _test_directory_access(self, mirror_url: str) -> bool:
        """测试目录访问（检查镜像地址是否包含OpenSSH文件）"""
        # 首先检查根目录是否可访问
        try:
            response = self.session.head(mirror_url, timeout=self.timeout, verify=False)
            if response.status_code == 200:
                return True
            
            # 如果HEAD失败，尝试GET
            response = self.session.get(mirror_url, timeout=self.timeout, verify=False)
            if response.status_code == 200:
                return True
                
        except requests.exceptions.RequestException:
            return False
        
        # 如果根目录访问失败，尝试检查常见的OpenSSH文件
        # 构造可能的OpenSSH文件URL
        test_files = [
            'openssh-9.8p1.tar.gz',  # 常见的OpenSSH版本文件
            'README',
            'index.html'
        ]
        
        for test_file in test_files:
            test_url = urljoin(mirror_url, test_file)
            try:
                response = self.session.head(test_url, timeout=self.timeout, verify=False)
                if response.status_code == 200:
                    return True
            except requests.exceptions.RequestException:
                continue
        
        return False
    
    def get_mirror_status(self, mirror_url: str) -> dict:
        """
        获取镜像地址的详细状态信息
        
        Args:
            mirror_url: 镜像地址
            
        Returns:
            dict: 包含状态信息的字典
        """
        status = {
            'mirror_url': mirror_url,
            'available': False,
            'response_time': None,
            'status_code': None,
            'error_message': None
        }
        
        start_time = time.time()
        
        try:
            response = self.session.get(mirror_url, timeout=self.timeout, verify=False)
            status['response_time'] = round((time.time() - start_time) * 1000, 2)  # 毫秒
            status['status_code'] = response.status_code
            status['available'] = response.status_code == 200
            
            if not status['available']:
                status['error_message'] = f"HTTP状态码: {response.status_code}"
                
        except requests.exceptions.RequestException as e:
            status['error_message'] = str(e)
        
        return status


def check_mirror_url(mirror_url: str, timeout: int = 10) -> bool:
    """
    快速检查镜像地址是否可用的便捷函数
    
    Args:
        mirror_url: 镜像地址
        timeout: 超时时间（秒）
        
    Returns:
        bool: 镜像地址是否可用
    """
    checker = MirrorChecker(timeout=timeout)
    return checker.check_mirror_availability(mirror_url)


def validate_mirror_url(mirror_url: str):
    """
    验证镜像地址并返回结果和消息
    
    Args:
        mirror_url: 镜像地址
        
    Returns:
        tuple: (是否可用, 消息)
    """
    if not mirror_url:
        return False, "镜像地址不能为空"
    
    checker = MirrorChecker()
    
    # 验证URL格式
    if not checker._validate_url_format(mirror_url):
        return False, f"镜像地址格式无效: {mirror_url}"
    
    # 检查可用性
    if checker.check_mirror_availability(mirror_url):
        return True, f"镜像地址可用: {mirror_url}"
    else:
        return False, f"镜像地址不可用: {mirror_url}"


if __name__ == "__main__":
    # 测试代码
    import sys
    
    if len(sys.argv) > 1:
        test_url = sys.argv[1]
    else:
        test_url = "https://mirrors.aliyun.com/openssh/portable/"
    
    print(f"测试镜像地址: {test_url}")
    
    checker = MirrorChecker()
    result, message = validate_mirror_url(test_url)
    
    if result:
        print(f"✓ {message}")
        sys.exit(0)
    else:
        print(f"✗ {message}")
        sys.exit(1)