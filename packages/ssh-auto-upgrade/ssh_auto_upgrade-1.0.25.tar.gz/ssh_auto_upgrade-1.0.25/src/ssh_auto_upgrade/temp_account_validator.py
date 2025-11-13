#!/usr/bin/env python3
"""
临时账号验证模块
用于SSH升级完成后的连接验证
"""

import os
import sys
import subprocess
import logging
import time
import random
import string
import paramiko

logger = logging.getLogger("ssh_auto_upgrade")


class TempAccountValidator:
    """临时账号验证器"""
    
    def __init__(self):
        self.temp_username = None
        self.temp_password = None
        self.temp_home_dir = None
        
    def generate_temp_credentials(self):
        """生成临时账号凭据"""
        # 生成随机的用户名
        timestamp = str(int(time.time()))
        self.temp_username = f"ssh_test_{timestamp}"
        
        # 生成随机密码
        chars = string.ascii_letters + string.digits
        self.temp_password = ''.join(random.choice(chars) for _ in range(16))
        
        logger.info(f"生成临时账号: {self.temp_username}")
        
    def create_temp_user(self):
        """创建临时用户账号"""
        if not self.temp_username or not self.temp_password:
            self.generate_temp_credentials()
            
        try:
            # 创建系统用户
            cmd_create = [
                'useradd', '-m', '-s', '/bin/bash', 
                '-d', f'/home/{self.temp_username}',
                self.temp_username
            ]
            
            result = subprocess.run(cmd_create, 
                                  capture_output=True, text=True)
            if result.returncode != 0:
                logger.error(f"创建临时用户失败: {result.stderr}")
                return False
            
            # 设置密码
            cmd_passwd = f"echo '{self.temp_username}:{self.temp_password}' | chpasswd"
            result = subprocess.run(cmd_passwd, shell=True, 
                                  capture_output=True, text=True)
            if result.returncode != 0:
                logger.error(f"设置临时用户密码失败: {result.stderr}")
                # 清理已创建的用户
                self._cleanup_temp_user()
                return False
            
            # 获取用户主目录
            result = subprocess.run(['getent', 'passwd', self.temp_username],
                                  capture_output=True, text=True)
            if result.returncode == 0:
                self.temp_home_dir = result.stdout.split(':')[5]
                
            logger.info(f"临时用户创建成功: {self.temp_username}")
            return True
            
        except Exception as e:
            logger.error(f"创建临时用户异常: {str(e)}")
            self._cleanup_temp_user()
            return False
    
    def _cleanup_temp_user(self):
        """清理临时用户"""
        if self.temp_username:
            try:
                # 删除用户和主目录
                subprocess.run(['userdel', '-r', '-f', self.temp_username], 
                             capture_output=True)
                logger.info(f"已清理临时用户: {self.temp_username}")
            except Exception as e:
                logger.warning(f"清理临时用户失败: {str(e)}")
    
    def wait_for_ssh_ready(self, max_wait=30):
        """等待SSH服务准备就绪"""
        logger.info("等待SSH服务准备就绪...")
        
        for i in range(max_wait):
            try:
                # 检查SSH端口
                result = subprocess.run(['nc', '-z', 'localhost', '22'], 
                                      capture_output=True)
                if result.returncode == 0:
                    logger.info("SSH服务端口已开放")
                    return True
                    
            except FileNotFoundError:
                # nc命令不存在，使用其他方法检查
                try:
                    result = subprocess.run(['ss', '-tlnp'], 
                                          capture_output=True, text=True)
                    if '22' in result.stdout:
                        logger.info("SSH服务端口已开放")
                        return True
                except:
                    pass
                    
            time.sleep(1)
            if i % 5 == 0:
                logger.info(f"等待SSH服务... ({i}/{max_wait}秒)")
        
        logger.warning("SSH服务准备超时")
        return False
    
    def test_ssh_connection(self):
        """测试SSH连接"""
        if not self.temp_username or not self.temp_password:
            logger.error("临时账号凭据未生成")
            return False
        
        # 等待SSH服务准备就绪
        if not self.wait_for_ssh_ready():
            logger.error("SSH服务未准备就绪，连接测试失败")
            return False
        
        try:
            # 尝试连接
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            logger.info("尝试连接SSH服务...")
            client.connect('localhost', username=self.temp_username, 
                          password=self.temp_password, timeout=10)
            
            # 测试基本命令执行
            stdin, stdout, stderr = client.exec_command('echo "SSH连接测试成功"')
            output = stdout.read().decode().strip()
            
            if "SSH连接测试成功" in output:
                logger.info("SSH连接验证成功")
                return True
            else:
                logger.error("SSH连接验证失败: 命令执行异常")
                return False
                
        except paramiko.AuthenticationException:
            logger.error("SSH连接验证失败: 认证失败")
            return False
        except paramiko.SSHException as e:
            logger.error(f"SSH连接验证失败: SSH错误 - {str(e)}")
            return False
        except Exception as e:
            logger.error(f"SSH连接验证失败: 连接异常 - {str(e)}")
            return False
        finally:
            try:
                client.close()
            except:
                pass
    
    def restart_ssh_and_retry(self, ssh_port=22):
        """重启SSH服务并重试连接（使用D-Bus API）
        
        Args:
            ssh_port: SSH端口号，默认为22
        """
        logger.info("尝试重启SSH服务...")
        
        try:
            # 导入ServiceManager模块进行SSH服务重启
            from .service_manager import ServiceManager
            
            # 使用D-Bus API重启SSH服务
            service_manager = ServiceManager(service_name="ssh-auto-upgrade")
            success = service_manager.restart_ssh_service(ssh_port=ssh_port)
            
            if not success:
                logger.error("重启SSH服务失败")
                return False
            
            # 等待服务启动
            time.sleep(5)
            logger.info("SSH服务已重启")
            
            # 重试连接测试
            logger.info("重启后重试连接测试...")
            if self.test_ssh_connection():
                logger.info("重启后连接验证成功")
                return True
            else:
                logger.error("重启后连接验证仍然失败")
                return False
                
        except Exception as e:
            logger.error(f"重启SSH服务异常: {str(e)}")
            return False
    
    def validate_ssh_upgrade(self, ssh_port=22):
        """执行完整的SSH升级验证流程
        
        Args:
            ssh_port: SSH端口号，默认为22
        """
        logger.info("开始SSH升级验证流程")
        
        # 创建临时账号
        if not self.create_temp_user():
            logger.error("创建临时账号失败，验证中止")
            return False
        
        try:
            # 第一次连接测试
            logger.info("执行第一次SSH连接测试")
            if self.test_ssh_connection():
                logger.info("SSH升级验证成功")
                return True
            
            # 第一次连接失败，尝试重启SSH服务
            logger.warning("首次连接失败，尝试重启SSH服务")
            if self.restart_ssh_and_retry(ssh_port=ssh_port):
                logger.info("SSH升级验证成功（重启后）")
                return True
            else:
                logger.error("SSH升级验证失败")
                return False
                
        except Exception as e:
            logger.error(f"SSH升级验证过程异常: {str(e)}")
            return False
        finally:
            # 清理临时账号
            self._cleanup_temp_user()
            logger.info("临时账号验证完成，已清理临时账号")


def validate_ssh_connection_after_upgrade(ssh_port=22):
    """
    验证SSH升级后的连接
    
    Args:
        ssh_port: SSH端口号，默认为22
        
    Returns:
        bool: 验证成功返回True，否则返回False
    """
    try:
        validator = TempAccountValidator()
        return validator.validate_ssh_upgrade(ssh_port=ssh_port)
    except Exception as e:
        logger.error(f"SSH升级验证过程发生异常: {str(e)}")
        return False


if __name__ == "__main__":
    # 测试函数
    logging.basicConfig(level=logging.INFO)
    
    # 检查是否以root权限运行
    if os.geteuid() != 0:
        print("需要root权限运行临时账号验证")
        sys.exit(1)
    
    # 执行验证
    result = validate_ssh_connection_after_upgrade()
    print(f"SSH升级验证结果: {'成功' if result else '失败'}")
    sys.exit(0 if result else 1)