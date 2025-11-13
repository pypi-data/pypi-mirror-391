"""
参数验证模块
负责验证命令行参数的格式和逻辑一致性
"""

import argparse


def validate_time_format(time_str: str) -> bool:
    """
    验证时间格式是否正确
    
    Args:
        time_str: 时间字符串，格式应为 HH:MM:SS-HH:MM:SS
        
    Returns:
        bool: 时间格式是否正确
    """
    try:
        # 检查时间格式
        if "-" not in time_str:
            return False
            
        start_time, end_time = time_str.split("-")
        
        # 验证开始时间格式
        start_parts = start_time.split(":")
        if len(start_parts) != 3:
            return False
        
        hour, minute, second = map(int, start_parts)
        if not (0 <= hour <= 23 and 0 <= minute <= 59 and 0 <= second <= 59):
            return False
        
        # 验证结束时间格式
        end_parts = end_time.split(":")
        if len(end_parts) != 3:
            return False
        
        hour, minute, second = map(int, end_parts)
        if not (0 <= hour <= 23 and 0 <= minute <= 59 and 0 <= second <= 59):
            return False
            
        return True
    except (ValueError, AttributeError):
        return False





def validate_arguments(args: argparse.Namespace) -> bool:
    """
    验证所有命令行参数
    
    Args:
        args: 解析后的命令行参数
        
    Returns:
        bool: 所有参数是否有效
    """
    # 验证时间格式
    if args.upgrade_time:
        if not validate_time_format(args.upgrade_time):
            print("错误: 升级时间段格式无效")
            print("请使用格式: HH:MM:SS-HH:MM:SS")
            return False
    
    return True


def validate_arguments_early(parser: argparse.ArgumentParser) -> bool:
    """
    早期参数验证（在systemd检测之前调用）
    
    Args:
        parser: 参数解析器
        
    Returns:
        bool: 参数是否有效，如果无效则程序应该退出
    """
    try:
        # 解析参数但不进行完整的验证
        args, _ = parser.parse_known_args()
        
        # 验证时间格式
        if args.upgrade_time:
            if not validate_time_format(args.upgrade_time):
                print("错误: 升级时间段格式无效")
                print("请使用格式: HH:MM:SS-HH:MM:SS")
                return False
        
        return True
    except SystemExit:
        # 当用户使用--help或无效参数时，argparse会调用sys.exit()
        # 这种情况下我们不应该继续执行
        return False
    except Exception as e:
        print(f"参数解析错误: {e}")
        return False