"""System detection for installation"""

import platform
import subprocess
import shutil
import os
from typing import Dict, Optional


class SystemDetector:
    """Detect system capabilities for installation"""
    
    def __init__(self):
        self.os_type = platform.system().lower()
        self.arch = platform.machine().lower()
        self.python_version = platform.python_version()
    
    def detect_all(self) -> Dict:
        """Detect all system capabilities"""
        return {
            'os': self.detect_os(),
            'arch': self.detect_architecture(),
            'python': self.detect_python(),
            'docker': self.detect_docker(),
            'gpu': self.detect_gpu(),
            'dependencies': self.detect_dependencies(),
        }
    
    def detect_os(self) -> Dict:
        """Detect operating system"""
        os_info = {
            'type': self.os_type,
            'version': platform.version(),
            'release': platform.release(),
        }
        
        if self.os_type == 'darwin':
            os_info['name'] = 'macOS'
            # Detect if Apple Silicon
            if self.arch in ['arm64', 'aarch64']:
                os_info['chip'] = 'Apple Silicon'
            else:
                os_info['chip'] = 'Intel'
        elif self.os_type == 'linux':
            os_info['name'] = 'Linux'
            # Try to detect distribution
            try:
                with open('/etc/os-release', 'r') as f:
                    for line in f:
                        if line.startswith('PRETTY_NAME='):
                            os_info['distro'] = line.split('=')[1].strip().strip('"')
                            break
            except:
                os_info['distro'] = 'Unknown'
        elif self.os_type == 'windows':
            os_info['name'] = 'Windows'
        
        return os_info
    
    def detect_architecture(self) -> Dict:
        """Detect CPU architecture"""
        return {
            'machine': self.arch,
            'processor': platform.processor(),
            'bits': platform.architecture()[0],
        }
    
    def detect_python(self) -> Dict:
        """Detect Python installation"""
        python_info = {
            'version': self.python_version,
            'executable': shutil.which('python3') or shutil.which('python'),
            'compatible': self._check_python_version(),
        }
        
        # Check for python3.12 specifically (recommended)
        python312 = shutil.which('python3.12')
        if python312:
            python_info['python3.12'] = python312
            python_info['recommended'] = True
        else:
            python_info['recommended'] = False
        
        return python_info
    
    def _check_python_version(self) -> bool:
        """Check if Python version is compatible (>=3.11, <3.14)"""
        major, minor, _ = self.python_version.split('.')
        version_tuple = (int(major), int(minor))
        return (3, 11) <= version_tuple < (3, 14)
    
    def detect_docker(self) -> Dict:
        """Detect Docker installation"""
        docker_info = {
            'installed': False,
            'running': False,
            'version': None,
        }
        
        # Check if Docker is installed
        docker_path = shutil.which('docker')
        if docker_path:
            docker_info['installed'] = True
            docker_info['path'] = docker_path
            
            # Check Docker version
            try:
                result = subprocess.run(
                    ['docker', '--version'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    docker_info['version'] = result.stdout.strip()
            except:
                pass
            
            # Check if Docker is running
            try:
                result = subprocess.run(
                    ['docker', 'ps'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    docker_info['running'] = True
            except:
                pass
        
        return docker_info
    
    def detect_gpu(self) -> Dict:
        """Detect GPU capabilities"""
        gpu_info = {
            'available': False,
            'type': None,
            'memory_gb': 0,
            'devices': [],
        }
        
        if self.os_type == 'darwin':
            # macOS - detect Metal GPU
            gpu_info.update(self._detect_metal_gpu())
        elif self.os_type == 'linux':
            # Linux - detect NVIDIA GPU
            gpu_info.update(self._detect_nvidia_gpu())
        elif self.os_type == 'windows':
            # Windows - detect CUDA GPU
            gpu_info.update(self._detect_cuda_gpu())
        
        return gpu_info
    
    def _detect_metal_gpu(self) -> Dict:
        """Detect Metal GPU on macOS"""
        gpu_info = {}
        
        try:
            # Get system memory (unified memory on Apple Silicon)
            result = subprocess.run(
                ['sysctl', '-n', 'hw.memsize'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                memory_bytes = int(result.stdout.strip())
                memory_gb = memory_bytes // (1024 ** 3)
                
                gpu_info['available'] = True
                gpu_info['type'] = 'metal'
                gpu_info['memory_gb'] = memory_gb
                gpu_info['devices'] = [f'Apple Metal GPU ({memory_gb}GB unified memory)']
        except:
            pass
        
        return gpu_info
    
    def _detect_nvidia_gpu(self) -> Dict:
        """Detect NVIDIA GPU on Linux"""
        gpu_info = {}
        
        # Check if nvidia-smi is available
        nvidia_smi = shutil.which('nvidia-smi')
        if nvidia_smi:
            try:
                result = subprocess.run(
                    ['nvidia-smi', '--query-gpu=name,memory.total', '--format=csv,noheader'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    devices = []
                    total_memory = 0
                    
                    for line in result.stdout.strip().split('\n'):
                        if line:
                            name, memory = line.split(',')
                            memory_mb = int(memory.strip().split()[0])
                            memory_gb = memory_mb // 1024
                            devices.append(f'{name.strip()} ({memory_gb}GB)')
                            total_memory += memory_gb
                    
                    gpu_info['available'] = True
                    gpu_info['type'] = 'cuda'
                    gpu_info['memory_gb'] = total_memory
                    gpu_info['devices'] = devices
            except:
                pass
        
        return gpu_info
    
    def _detect_cuda_gpu(self) -> Dict:
        """Detect CUDA GPU on Windows"""
        # Similar to NVIDIA detection but for Windows
        return self._detect_nvidia_gpu()
    
    def detect_dependencies(self) -> Dict:
        """Detect required dependencies"""
        deps = {
            'cmake': shutil.which('cmake') is not None,
            'rust': shutil.which('rustc') is not None or shutil.which('cargo') is not None,
            'pkg-config': shutil.which('pkg-config') is not None,
            'ffmpeg': shutil.which('ffmpeg') is not None,
        }
        
        # Add platform-specific dependencies
        if self.os_type == 'darwin':
            deps['homebrew'] = shutil.which('brew') is not None
        elif self.os_type == 'linux':
            deps['apt'] = shutil.which('apt') is not None or shutil.which('apt-get') is not None
            deps['yum'] = shutil.which('yum') is not None
        
        return deps
    
    def get_package_manager(self) -> Optional[str]:
        """Get the system package manager"""
        if self.os_type == 'darwin':
            return 'brew' if shutil.which('brew') else None
        elif self.os_type == 'linux':
            if shutil.which('apt') or shutil.which('apt-get'):
                return 'apt'
            elif shutil.which('yum'):
                return 'yum'
            elif shutil.which('dnf'):
                return 'dnf'
        elif self.os_type == 'windows':
            return 'choco' if shutil.which('choco') else None
        
        return None
    
    def is_compatible(self) -> tuple[bool, list[str]]:
        """Check if system is compatible for installation"""
        issues = []
        
        # Check Python version
        if not self._check_python_version():
            issues.append(f'Python version {self.python_version} not compatible (need >=3.11, <3.14)')
        
        # Check Docker
        docker = self.detect_docker()
        if not docker['installed']:
            issues.append('Docker not installed')
        elif not docker['running']:
            issues.append('Docker not running')
        
        # Check package manager
        pkg_mgr = self.get_package_manager()
        if not pkg_mgr:
            issues.append(f'No package manager found for {self.os_type}')
        
        return (len(issues) == 0, issues)
