"""
端口检查和进程清理模块
负责检查指定端口的占用情况并结束占用进程
"""

import os
import logging
import subprocess
import time

# 设置日志记录器
logger = logging.getLogger(__name__)


class PortChecker:
    """端口检查器"""
    
    def __init__(self):
        """初始化端口检查器"""
        pass
    
    def check_port_occupied(self, port=22):
        """
        检查指定端口是否被占用
        
        Args:
            port: 要检查的端口号，默认为22
            
        Returns:
            bool: 端口是否被占用
        """
        try:
            # 使用ss命令检查端口占用（推荐）
            result = subprocess.run(
                ['ss', '-tlnp'], 
                capture_output=True, 
                text=True, 
                timeout=10
            )
            
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if f':{port}' in line and 'LISTEN' in line:
                        logger.info(f"检测到端口 {port} 被占用: {line.strip()}")
                        return True
            
            # 如果ss命令不可用，尝试使用netstat
            result = subprocess.run(
                ['netstat', '-tlnp'], 
                capture_output=True, 
                text=True, 
                timeout=10
            )
            
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if f':{port}' in line and 'LISTEN' in line:
                        logger.info(f"检测到端口 {port} 被占用: {line.strip()}")
                        return True
                        
            # 如果都不可用，尝试使用lsof
            result = subprocess.run(
                ['lsof', '-i', f':{port}'], 
                capture_output=True, 
                text=True, 
                timeout=10
            )
            
            if result.returncode == 0 and result.stdout.strip():
                logger.info(f"检测到端口 {port} 被占用: {result.stdout.strip()}")
                return True
            
            logger.info(f"端口 {port} 当前未被占用")
            return False
            
        except subprocess.TimeoutExpired:
            logger.warning(f"检查端口 {port} 占用情况时超时")
            return False
        except FileNotFoundError as e:
            logger.warning(f"端口检查工具不可用: {e}")
            return False
        except Exception as e:
            logger.warning(f"检查端口 {port} 占用情况时出错: {e}")
            return False
    
    def get_processes_using_port(self, port=22):
        """
        获取占用指定端口的进程信息
        
        Args:
            port: 要检查的端口号，默认为22
            
        Returns:
            list: 占用端口的进程信息列表
        """
        processes = []
        
        try:
            # 尝试使用ss命令
            result = subprocess.run(
                ['ss', '-tlnp'], 
                capture_output=True, 
                text=True, 
                timeout=10
            )
            
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if f':{port}' in line and 'LISTEN' in line:
                        # 解析ss输出格式
                        # 例如: "tcp    0    0 0.0.0.0:22    0.0.0.0:*    users:(("sshd",pid=1234,fd=3))"
                        parts = line.split()
                        if len(parts) >= 6:
                            pid_info = parts[5] if len(parts) > 5 else ""
                            if 'pid=' in pid_info:
                                try:
                                    pid = int(pid_info.split('pid=')[1].split(',')[0])
                                    processes.append({
                                        'pid': pid,
                                        'command': 'sshd',
                                        'port': port,
                                        'source': 'ss'
                                    })
                                except (ValueError, IndexError):
                                    pass
            
            # 如果ss命令没有找到进程信息，尝试lsof
            if not processes:
                result = subprocess.run(
                    ['lsof', '-i', f':{port}'], 
                    capture_output=True, 
                    text=True, 
                    timeout=10
                )
                
                if result.returncode == 0 and result.stdout.strip():
                    lines = result.stdout.split('\n')[1:]  # 跳过标题行
                    for line in lines:
                        parts = line.split()
                        if len(parts) >= 2:
                            try:
                                pid = int(parts[1])
                                processes.append({
                                    'pid': pid,
                                    'command': parts[0],
                                    'port': port,
                                    'source': 'lsof'
                                })
                            except (ValueError, IndexError):
                                continue
                                
        except subprocess.TimeoutExpired:
            logger.warning(f"获取端口 {port} 占用进程信息时超时")
        except FileNotFoundError:
            logger.warning("端口检查工具（ss/lsof）不可用")
        except Exception as e:
            logger.warning(f"获取端口 {port} 占用进程信息时出错: {e}")
        
        return processes
    
    def terminate_processes_using_port(self, port=22, max_attempts=3, wait_seconds=2):
        """
        结束占用指定端口的进程
        
        Args:
            port: 要释放的端口号，默认为22
            max_attempts: 最大尝试次数
            wait_seconds: 每次尝试间隔秒数
            
        Returns:
            tuple: (success, message)
        """
        logger.info(f"开始清理端口 {port} 的占用进程...")
        
        for attempt in range(max_attempts):
            logger.info(f"第 {attempt + 1} 次尝试清理端口 {port}...")
            
            # 获取占用端口的进程
            processes = self.get_processes_using_port(port)
            
            if not processes:
                logger.info(f"第 {attempt + 1} 次尝试: 端口 {port} 当前未被占用")
                if attempt > 0:  # 如果不是第一次尝试，说明已经成功清理
                    break
                else:
                    return True, f"端口 {port} 当前未被占用"
            
            # 结束每个进程
            terminated_pids = []
            failed_pids = []
            
            for process_info in processes:
                pid = process_info['pid']
                command = process_info['command']
                
                try:
                    # 先尝试温和的SIGTERM
                    logger.info(f"尝试结束进程 PID={pid} ({command}) 使用SIGTERM...")
                    os.kill(pid, 15)  # SIGTERM
                    terminated_pids.append(pid)
                    
                except ProcessLookupError:
                    logger.info(f"进程 PID={pid} 已经不存在")
                    terminated_pids.append(pid)
                except PermissionError:
                    logger.warning(f"没有权限结束进程 PID={pid}")
                    failed_pids.append(pid)
                except Exception as e:
                    logger.warning(f"结束进程 PID={pid} 时出错: {e}")
                    failed_pids.append(pid)
            
            # 等待进程结束
            time.sleep(wait_seconds)
            
            # 检查是否还有进程占用端口
            if not self.check_port_occupied(port):
                logger.info(f"端口 {port} 已成功释放")
                
                # 记录终止的进程
                if terminated_pids:
                    logger.info(f"成功终止进程: {terminated_pids}")
                
                # 处理失败的进程
                if failed_pids:
                    logger.warning(f"无法终止的进程 (权限不足): {failed_pids}")
                    return False, f"部分进程因权限不足无法终止: {failed_pids}"
                
                return True, f"端口 {port} 已成功释放"
            else:
                # 如果还有进程占用，强制结束它们
                if failed_pids:
                    logger.warning("尝试强制结束剩余进程...")
                    for pid in failed_pids:
                        try:
                            logger.info(f"尝试强制结束进程 PID={pid} 使用SIGKILL...")
                            os.kill(pid, 9)  # SIGKILL
                        except Exception as e:
                            logger.warning(f"强制结束进程 PID={pid} 时出错: {e}")
                
                # 等待并重新检查
                time.sleep(wait_seconds)
        
        # 最终检查
        if self.check_port_occupied(port):
            processes = self.get_processes_using_port(port)
            remaining_pids = [p['pid'] for p in processes]
            return False, f"经过 {max_attempts} 次尝试后，端口 {port} 仍被占用，剩余进程: {remaining_pids}"
        else:
            return True, f"端口 {port} 已成功释放"
    
    def stop_ssh_service_with_port_cleanup(self, service_manager, ssh_port=22):
        """
        停止SSH服务并清理指定端口占用
        
        Args:
            service_manager: ServiceManager实例
            ssh_port: SSH服务端口号，默认22
            
        Returns:
            tuple: (success, message)
        """
        logger.info(f"开始停止SSH服务并清理端口 {ssh_port}...")
        
        # 首先停止SSH服务
        logger.info("停止SSH服务...")
        success, message = service_manager.stop_service()
        
        if not success:
            logger.error(f"停止SSH服务失败: {message}")
            return False, f"停止SSH服务失败: {message}"
        
        logger.info("SSH服务已停止，等待服务完全停止...")
        time.sleep(3)  # 等待服务停止
        
        # 检查指定端口是否被占用
        if self.check_port_occupied(ssh_port):
            logger.info(f"检测到端口 {ssh_port} 仍被占用，开始清理...")
            success, cleanup_message = self.terminate_processes_using_port(ssh_port)
            
            if success:
                logger.info(f"SSH服务已停止，端口 {ssh_port} 已清理")
                return True, f"SSH服务已停止，端口 {ssh_port} 已清理"
            else:
                logger.warning(f"SSH服务已停止，但端口 {ssh_port} 清理遇到问题: {cleanup_message}")
                return True, f"SSH服务已停止，但端口 {ssh_port} 清理遇到问题: {cleanup_message}"
        else:
            logger.info(f"SSH服务已停止，端口 {ssh_port} 当前未被占用")
            return True, f"SSH服务已停止，端口 {ssh_port} 未被占用"


def main():
    """测试函数"""
    checker = PortChecker()
    
    # 测试端口占用检查
    print("=== 测试22端口占用检查 ===")
    occupied = checker.check_port_occupied(22)
    print(f"端口22是否被占用: {occupied}")
    
    # 获取占用进程
    print("\n=== 获取占用进程信息 ===")
    processes = checker.get_processes_using_port(22)
    print(f"占用进程: {processes}")
    
    # 测试端口清理（谨慎使用）
    print("\n=== 测试端口清理 ===")
    if occupied:
        print("⚠️  检测到22端口被占用，但跳过清理测试以避免影响SSH服务")


if __name__ == "__main__":
    # 配置日志
    import sys
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler(sys.stdout)]
    )
    
    main()