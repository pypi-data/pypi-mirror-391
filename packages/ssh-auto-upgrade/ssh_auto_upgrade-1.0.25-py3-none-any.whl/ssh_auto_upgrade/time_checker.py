"""
时间段检测模块
用于检测当前时间是否在指定的升级时间段内
"""

import logging
from datetime import datetime
from typing import Tuple, Optional

logger = logging.getLogger(__name__)


class TimeChecker:
    """时间段检测器"""
    
    def __init__(self):
        """初始化时间段检测器"""
        pass
    
    def parse_time_range(self, time_range_str: str) -> Tuple[str, str]:
        """
        解析时间段字符串
        
        Args:
            time_range_str: 时间段字符串，格式为 HH:MM:SS-HH:MM:SS
            
        Returns:
            Tuple[str, str]: (开始时间字符串, 结束时间字符串)
            
        Raises:
            ValueError: 时间段格式错误
        """
        try:
            time_parts = time_range_str.split('-')
            if len(time_parts) != 2:
                raise ValueError("时间段格式错误，请使用格式: HH:MM:SS-HH:MM:SS")
            
            start_time_str = time_parts[0]
            end_time_str = time_parts[1]
            
            # 验证时间格式
            datetime.strptime(start_time_str, '%H:%M:%S')
            datetime.strptime(end_time_str, '%H:%M:%S')
            
            return start_time_str, end_time_str
            
        except ValueError as e:
            logger.error(f"时间段解析失败: {str(e)}")
            raise
    
    def is_time_in_range(self, start_time_str: str, end_time_str: str) -> bool:
        """
        检查当前时间是否在指定时间段内
        
        Args:
            start_time_str: 开始时间字符串，格式为 HH:MM:SS
            end_time_str: 结束时间字符串，格式为 HH:MM:SS
            
        Returns:
            bool: 当前时间是否在时间段内
        """
        # 获取当前时间
        now = datetime.now()
        current_time = now.time()
        
        # 解析开始和结束时间
        start_time = datetime.strptime(start_time_str, '%H:%M:%S').time()
        end_time = datetime.strptime(end_time_str, '%H:%M:%S').time()
        
        # 检查时间范围（支持跨天）
        if start_time <= end_time:
            # 不跨天的情况
            return start_time <= current_time <= end_time
        else:
            # 跨天的情况（如 22:00:00 到 06:00:00）
            return current_time >= start_time or current_time <= end_time
    
    def get_current_time_str(self) -> str:
        """
        获取当前时间字符串
        
        Returns:
            str: 当前时间字符串，格式为 HH:MM:SS
        """
        return datetime.now().strftime('%H:%M:%S')
    
    def validate_and_check_time_range(self, time_range_str: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        验证时间段格式并检查当前时间是否在时间段内
        
        Args:
            time_range_str: 时间段字符串
            
        Returns:
            Tuple[bool, Optional[str], Optional[str]]: 
                (是否在时间段内, 开始时间字符串, 结束时间字符串)
                如果时间段格式错误，返回 (False, None, None)
        """
        try:
            start_time_str, end_time_str = self.parse_time_range(time_range_str)
            in_range = self.is_time_in_range(start_time_str, end_time_str)
            return in_range, start_time_str, end_time_str
            
        except ValueError:
            return False, None, None


def is_time_in_range(start_time_str: str, end_time_str: str) -> bool:
    """
    便捷函数：检查当前时间是否在指定时间段内
    
    Args:
        start_time_str: 开始时间字符串，格式为 HH:MM:SS
        end_time_str: 结束时间字符串，格式为 HH:MM:SS
        
    Returns:
        bool: 当前时间是否在时间段内
    """
    checker = TimeChecker()
    return checker.is_time_in_range(start_time_str, end_time_str)


def parse_time_range(time_range_str: str) -> Tuple[str, str]:
    """
    便捷函数：解析时间段字符串
    
    Args:
        time_range_str: 时间段字符串，格式为 HH:MM:SS-HH:MM:SS
        
    Returns:
        Tuple[str, str]: (开始时间字符串, 结束时间字符串)
        
    Raises:
        ValueError: 时间段格式错误
    """
    checker = TimeChecker()
    return checker.parse_time_range(time_range_str)


def validate_and_check_time_range(time_range_str: str) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    便捷函数：验证时间段格式并检查当前时间是否在时间段内
    
    Args:
        time_range_str: 时间段字符串
        
    Returns:
        Tuple[bool, Optional[str], Optional[str]]: 
            (是否在时间段内, 开始时间字符串, 结束时间字符串)
            如果时间段格式错误，返回 (False, None, None)
    """
    checker = TimeChecker()
    return checker.validate_and_check_time_range(time_range_str)


if __name__ == "__main__":
    # 测试代码
    import sys
    
    if len(sys.argv) > 1:
        test_time_range = sys.argv[1]
    else:
        test_time_range = "00:00:00-08:00:00"
    
    print(f"测试时间段: {test_time_range}")
    
    checker = TimeChecker()
    
    try:
        in_range, start_time, end_time = checker.validate_and_check_time_range(test_time_range)
        
        if start_time and end_time:
            print(f"时间段解析成功: {start_time} - {end_time}")
            print(f"当前时间: {checker.get_current_time_str()}")
            print(f"是否在时间段内: {'是' if in_range else '否'}")
        else:
            print("时间段格式错误")
            
    except ValueError as e:
        print(f"错误: {str(e)}")
        sys.exit(1)