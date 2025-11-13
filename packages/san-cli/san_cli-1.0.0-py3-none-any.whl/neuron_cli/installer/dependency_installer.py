"""Install system dependencies"""

import subprocess
import shutil
from typing import List, Dict
from ..core.logger import logger


class DependencyInstaller:
    """Install system dependencies required for services"""
    
    def __init__(self, os_type: str, package_manager: str):
        self.os_type = os_type
        self.package_manager = package_manager
    
    def install_build_tools(self) -> Dict:
        """Install build tools (cmake, rust, pkg-config, ffmpeg)"""
        logger.info("📦 Installing build tools...")
        
        packages = self._get_build_tool_packages()
        results = {}
        
        for package in packages:
            logger.info(f"   Installing {package}...")
            success = self._install_package(package)
            results[package] = success
            
            if success:
                logger.info(f"   ✅ {package} installed")
            else:
                logger.warning(f"   ⚠️  Failed to install {package}")
        
        return results
    
    def install_python312(self) -> bool:
        """Install Python 3.12"""
        logger.info("🐍 Installing Python 3.12...")
        
        if self.os_type == 'darwin':
            return self._install_package('python@3.12')
        elif self.os_type == 'linux':
            if self.package_manager == 'apt':
                # Add deadsnakes PPA for Python 3.12
                try:
                    subprocess.run(
                        ['sudo', 'add-apt-repository', '-y', 'ppa:deadsnakes/ppa'],
                        check=True,
                        capture_output=True
                    )
                    subprocess.run(
                        ['sudo', 'apt', 'update'],
                        check=True,
                        capture_output=True
                    )
                except:
                    logger.warning("   ⚠️  Failed to add Python PPA")
                
                return self._install_package('python3.12')
            elif self.package_manager in ['yum', 'dnf']:
                return self._install_package('python312')
        
        return False
    
    def _get_build_tool_packages(self) -> List[str]:
        """Get list of build tool packages for the OS"""
        if self.os_type == 'darwin':
            return ['cmake', 'rust', 'pkg-config', 'ffmpeg']
        elif self.os_type == 'linux':
            if self.package_manager == 'apt':
                return ['cmake', 'cargo', 'pkg-config', 'libavcodec-dev', 'ffmpeg']
            elif self.package_manager in ['yum', 'dnf']:
                return ['cmake', 'cargo', 'pkgconfig', 'ffmpeg-devel', 'ffmpeg']
        
        return []
    
    def _install_package(self, package: str) -> bool:
        """Install a single package"""
        try:
            if self.package_manager == 'brew':
                cmd = ['brew', 'install', package]
            elif self.package_manager == 'apt':
                cmd = ['sudo', 'apt', 'install', '-y', package]
            elif self.package_manager in ['yum', 'dnf']:
                cmd = ['sudo', self.package_manager, 'install', '-y', package]
            elif self.package_manager == 'choco':
                cmd = ['choco', 'install', '-y', package]
            else:
                return False
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes timeout
            )
            
            return result.returncode == 0
        except Exception as e:
            logger.error(f"   ❌ Error installing {package}: {e}")
            return False
    
    def check_dependency(self, command: str) -> bool:
        """Check if a dependency is installed"""
        return shutil.which(command) is not None
    
    def verify_installation(self) -> Dict[str, bool]:
        """Verify all dependencies are installed"""
        return {
            'cmake': self.check_dependency('cmake'),
            'rust': self.check_dependency('rustc') or self.check_dependency('cargo'),
            'pkg-config': self.check_dependency('pkg-config'),
            'ffmpeg': self.check_dependency('ffmpeg'),
            'python3.12': self.check_dependency('python3.12'),
        }
