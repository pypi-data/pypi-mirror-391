"""
依赖管理模块
负责检测和安装编译OpenSSH所需的系统依赖
使用plpm模块进行包管理检测
"""

import subprocess
import platform
import sys
import logging
from typing import List, Dict, Tuple

try:
    import plpm
    PLPM_MODULE = plpm
    PLPM_AVAILABLE = True
except ImportError:
    PLPM_MODULE = None
    PLPM_AVAILABLE = False

logger = logging.getLogger(__name__)

from .dependency_constants import (
    REQUIRED_DEPENDENCIES,
    PACKAGE_MANAGERS,
    PACKAGE_MANAGER_UPDATE_COMMANDS,
    PACKAGE_MANAGER_INSTALL_COMMANDS,
    DEPENDENCY_DESCRIPTIONS
)

# 统一模块导入管理
class ModuleManager:
    """模块管理器，统一处理外部模块导入"""
    
    def __init__(self):
        self.plpm_available = PLPM_AVAILABLE
        self.plpm_module = PLPM_MODULE
        self._init_modules()
    
    def _init_modules(self):
        """初始化外部模块"""
        # 使用顶部导入的模块
        if self.plpm_available:
            logger.info("plpm模块已成功加载")
        else:
            logger.warning("plpm模块未安装，将使用传统检测方法")
    
    def get_package_manager(self):
        """获取包管理器实例"""
        if self.plpm_available and self.plpm_module:
            try:
                # 使用plpm模块检测包管理器
                return self.plpm_module.get_package_manager()
            except Exception as e:
                logger.warning(f"创建包管理器实例失败: {e}")
        return None
    
    def is_plpm_available(self):
        """检查plpm模块是否可用"""
        return self.plpm_available


class DependencyManager:
    """依赖管理器类"""
    
    def __init__(self):
        """初始化依赖管理器"""
        self.system_info = self._detect_system_info()
        self.package_manager = self._detect_package_manager()
        
        # 使用常量定义中的依赖配置
        self.required_dependencies = REQUIRED_DEPENDENCIES
        
        # 初始化模块管理器
        self.module_manager = ModuleManager()
    
    def _detect_system_info(self) -> Dict[str, str]:
        """检测系统信息"""
        system_info = {
            'system': platform.system(),
            'release': platform.release(),
            'version': platform.version(),
            'machine': platform.machine(),
            'distro': self._get_linux_distro()
        }
        return system_info
    
    def _get_linux_distro(self) -> str:
        """获取Linux发行版信息"""
        try:
            # 尝试读取/etc/os-release文件
            with open('/etc/os-release', 'r') as f:
                for line in f:
                    if line.startswith('ID='):
                        return line.split('=')[1].strip().strip('"')
        except:
            pass
        return 'unknown'
    
    def _detect_package_manager(self) -> str:
        """检测包管理器"""
        # 使用常量定义中的包管理器列表
        for pm in PACKAGE_MANAGERS:
            try:
                result = subprocess.run([pm, '--version'], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    return pm
            except (subprocess.SubprocessError, FileNotFoundError):
                continue
        
        return 'unknown'
    
    def check_dependency(self, package_name: str) -> bool:
        """检查单个依赖是否已安装"""
        try:
            # 优先使用plpm模块进行包检测
            if self.module_manager.is_plpm_available():
                try:
                    pm = self.module_manager.get_package_manager()
                    # 使用plpm模块检查包是否已安装
                    if pm and hasattr(pm, 'check_package_installed'):
                        return pm.check_package_installed(package_name)
                    elif pm and hasattr(pm, 'is_installed'):
                        return pm.is_installed(package_name)
                except Exception as e:
                    logger.debug(f"plpm模块检测失败 {package_name}: {e}")
            
            # 备用检测方法：使用包管理器检查包是否已安装
            if self.package_manager == 'apt':
                result = subprocess.run(['dpkg', '-l', package_name], 
                                      capture_output=True, text=True)
                if result.returncode == 0 and package_name in result.stdout:
                    return True
            elif self.package_manager in ['yum', 'dnf']:
                result = subprocess.run(['rpm', '-q', package_name], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    return True
            
            # 对于特定工具，使用which命令检查可执行文件是否存在
            tool_mapping = {
                'make': 'make',
                'gcc': 'gcc',
                'g++': 'g++',
                'clang': 'clang',
                'autoconf': 'autoconf',
                'automake': 'automake',
                'libtool': 'libtool',
                'pkg-config': 'pkg-config',
                'pkgconfig': 'pkg-config',
                'pkgconf': 'pkg-config',
                'curl': 'curl',
                'wget': 'wget',
                'tar': 'tar',
                'gzip': 'gzip'
            }
            
            if package_name in tool_mapping:
                result = subprocess.run(['which', tool_mapping[package_name]], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    return True
            
            # 对于开发库，尝试使用pkg-config检查
            if package_name.endswith('-dev') or package_name.endswith('-devel'):
                lib_name = package_name.replace('-dev', '').replace('-devel', '')
                result = subprocess.run(['pkg-config', '--exists', lib_name], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    return True
            
            return False
            
        except (subprocess.SubprocessError, FileNotFoundError):
            return False
    
    def check_all_dependencies(self) -> Tuple[bool, List[str]]:
        """检查所有必需的依赖"""
        if self.package_manager == 'unknown':
            return False, ["无法检测到支持的包管理器"]
        
        missing_deps = []
        
        # 获取当前包管理器对应的依赖列表
        deps = self.required_dependencies.get(self.package_manager, [])
        
        for dep in deps:
            if not self.check_dependency(dep):
                missing_deps.append(dep)
        
        return len(missing_deps) == 0, missing_deps
    
    def install_dependencies(self, update_first: bool = True) -> Tuple[bool, str]:
        """安装缺失的依赖"""
        if self.package_manager == 'unknown':
            return False, "无法检测到支持的包管理器"
        
        try:
            # 优先使用plpm模块进行包安装
            if self.module_manager.is_plpm_available():
                try:
                    pm = self.module_manager.get_package_manager()
                    
                    # 检查缺失的依赖
                    all_installed, missing_deps = self.check_all_dependencies()
                    
                    if all_installed:
                        return True, "所有依赖已安装"
                    
                    # 首先更新包管理器缓存
                    if update_first:
                        logger.info("正在更新包管理器缓存...")
                        if hasattr(pm, 'update_package_cache'):
                            if not pm.update_package_cache():
                                logger.warning("包管理器缓存更新失败，继续安装...")
                        elif hasattr(pm, 'update'):
                            if not pm.update():
                                logger.warning("包管理器缓存更新失败，继续安装...")
                    
                    # 安装缺失的依赖
                    logger.info(f"正在安装缺失的依赖: {', '.join(missing_deps)}")
                    
                    for dep in missing_deps:
                        logger.info(f"安装依赖: {dep}")
                        if hasattr(pm, 'install_package'):
                            if not pm.install_package(dep):
                                logger.error(f"安装依赖失败: {dep}")
                                return False, f"安装依赖失败: {dep}"
                        elif hasattr(pm, 'install'):
                            if not pm.install(dep):
                                logger.error(f"安装依赖失败: {dep}")
                                return False, f"安装依赖失败: {dep}"
                    
                    logger.info("依赖安装成功")
                    return True, "依赖安装成功"
                    
                except Exception as e:
                    logger.warning(f"plpm模块安装失败，使用传统方法: {e}")
            
            # 备用安装方法：使用传统包管理器
            # 首先更新包管理器缓存
            if update_first:
                logger.info("正在更新包管理器缓存...")
                update_cmd = PACKAGE_MANAGER_UPDATE_COMMANDS.get(self.package_manager)
                if update_cmd:
                    result = subprocess.run(update_cmd, capture_output=True, text=True)
                    if result.returncode != 0:
                        return False, f"包管理器缓存更新失败: {result.stderr}"
            
            # 检查缺失的依赖
            all_installed, missing_deps = self.check_all_dependencies()
            
            if all_installed:
                return True, "所有依赖已安装"
            
            # 安装缺失的依赖
            logger.info(f"正在安装缺失的依赖: {', '.join(missing_deps)}")
            
            install_cmd = PACKAGE_MANAGER_INSTALL_COMMANDS.get(self.package_manager)
            if install_cmd:
                cmd = install_cmd + missing_deps
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                if result.returncode == 0:
                    logger.info("依赖安装成功")
                    return True, "依赖安装成功"
                else:
                    logger.error(f"依赖安装失败: {result.stderr}")
                    return False, f"依赖安装失败: {result.stderr}"
            else:
                logger.error(f"不支持的包管理器: {self.package_manager}")
                return False, f"不支持的包管理器: {self.package_manager}"
            
        except Exception as e:
            return False, f"安装依赖时出错: {str(e)}"
    
    def ensure_dependencies(self, auto_install: bool = True) -> Tuple[bool, str]:
        """确保所有依赖已安装"""
        logger.info("检查编译依赖...")
        logger.info(f"检测到系统: {self.system_info['distro']}")
        logger.info(f"检测到包管理器: {self.package_manager}")
        
        # 检查依赖状态
        all_installed, missing_deps = self.check_all_dependencies()
        
        if all_installed:
            logger.info("✓ 所有编译依赖已安装")
            return True, "所有依赖已安装"
        
        logger.info(f"缺失的依赖: {', '.join(missing_deps)}")
        
        if not auto_install:
            return False, "存在缺失的依赖，请手动安装"
        
        # 自动安装缺失的依赖
        logger.info("开始自动安装缺失的依赖...")
        success, message = self.install_dependencies()
        
        if success:
            logger.info("✓ 依赖安装成功")
            return True, message
        else:
            logger.error(f"✗ 依赖安装失败: {message}")
            # 安装失败时直接终止程序
            sys.exit(f"依赖安装失败: {message}")


def main():
    """测试函数"""
    manager = DependencyManager()
    
    logger.info("系统信息:")
    for key, value in manager.system_info.items():
        logger.info(f"  {key}: {value}")
    
    logger.info(f"包管理器: {manager.package_manager}")
    
    # 检查依赖状态
    all_installed, missing_deps = manager.check_all_dependencies()
    
    if all_installed:
        logger.info("✓ 所有依赖已安装")
    else:
        logger.info(f"缺失的依赖: {', '.join(missing_deps)}")
        
        # 询问是否安装
        response = input("是否自动安装缺失的依赖? (y/n): ")
        if response.lower() == 'y':
            success, message = manager.install_dependencies()
            logger.info(message)


if __name__ == "__main__":
    main()