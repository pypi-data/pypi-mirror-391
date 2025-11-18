"""Marketplace package manager"""

import subprocess
import platform
import requests
from typing import List, Dict, Optional
from ..core.logger import logger
from ..core.config import Config
from ..installer import HostServiceInstaller, SystemDetector
from ..services import DockerServiceManager


class MarketplaceManager:
    """Manage marketplace packages"""
    
    def __init__(self):
        self.os_type = platform.system().lower()
        self.docker_manager = DockerServiceManager()
        self.detector = SystemDetector()
        self.config = Config()
        self.api_url = self.config.data.get('api_url', 'https://support.nexuscore.cloud')
        self.packages = self._get_builtin_packages()
    
    def _get_builtin_packages(self) -> Dict[str, Dict]:
        """Get built-in package definitions"""
        return {
            'mesh-ai-chat_mesh': {
                'name': 'mesh-ai-chat_mesh',
                'version': '1.0.0',
                'type': 'docker',
                'description': 'AI chat service with Ollama integration',
                'category': 'AI Services',
                'docker': {
                    'image': 'registry.nexuscore.cloud/mesh-ai-chat:latest',
                    'container_name': 'mesh-ai-chat_mesh',
                    'network': 'cave_mesh',
                    'ports': ['8024:8000'],
                    'environment': {
                        'OLLAMA_HOST': 'http://host.docker.internal:11434',
                        'DEFAULT_MODEL': 'llama3.1:8b',
                        'BRAND_API_KEY': 'nexuscore-support-api-key-44444',
                    },
                },
                'dependencies': ['ollama', 'space-agent'],
                'healthcheck': {'url': 'http://localhost:8024/health'},
            },
            'mesh-ai-rag_mesh': {
                'name': 'mesh-ai-rag_mesh',
                'version': '1.0.0',
                'type': 'docker',
                'description': 'RAG (Retrieval-Augmented Generation) service',
                'category': 'AI Services',
                'docker': {
                    'image': 'registry.nexuscore.cloud/mesh-ai-rag:latest',
                    'container_name': 'mesh-ai-rag_mesh',
                    'network': 'cave_mesh',
                    'ports': ['8025:8000'],
                    'environment': {
                        'OLLAMA_HOST': 'http://host.docker.internal:11434',
                        'DEFAULT_MODEL': 'llama3.1:8b',
                    },
                },
                'dependencies': ['ollama', 'space-agent'],
                'healthcheck': {'url': 'http://localhost:8025/health'},
            },
            'ai-flow-control_mesh': {
                'name': 'ai-flow-control_mesh',
                'version': '1.0.0',
                'type': 'docker',
                'description': 'AI-powered workflow orchestration',
                'category': 'AI Services',
                'docker': {
                    'image': 'registry.nexuscore.cloud/ai-flow-control:latest',
                    'container_name': 'ai-flow-control_mesh',
                    'network': 'cave_mesh',
                    'ports': ['8027:8000'],
                    'environment': {
                        'OLLAMA_HOST': 'http://ollama_mesh:11434',
                        'MESH_AI_CHAT_URL': 'http://mesh-ai-chat_mesh:8000',
                        'WHISPER_URL': 'http://host.docker.internal:8026',
                    },
                },
                'dependencies': ['ollama', 'space-agent'],
                'healthcheck': {'url': 'http://localhost:8027/health'},
            },
            'redis_mesh': {
                'name': 'redis_mesh',
                'version': '7.2.0',
                'type': 'docker',
                'description': 'Redis cache and message broker',
                'category': 'Infrastructure',
                'docker': {
                    'image': 'redis:7.2-alpine',
                    'container_name': 'redis_mesh',
                    'network': 'cave_mesh',
                    'ports': ['6379:6379'],
                },
                'dependencies': ['space-agent'],
                'healthcheck': {'command': 'redis-cli ping'},
            },
            'postgres_mesh': {
                'name': 'postgres_mesh',
                'version': '16.0',
                'type': 'docker',
                'description': 'PostgreSQL database',
                'category': 'Infrastructure',
                'docker': {
                    'image': 'postgres:16-alpine',
                    'container_name': 'postgres_mesh',
                    'network': 'cave_mesh',
                    'ports': ['5432:5432'],
                    'environment': {
                        'POSTGRES_PASSWORD': 'postgres',
                        'POSTGRES_DB': 'nexuscore',
                    },
                    'volumes': ['postgres_data:/var/lib/postgresql/data'],
                },
                'dependencies': ['space-agent'],
                'healthcheck': {'command': 'pg_isready'},
            },
        }
    
    def list_packages(self, category: Optional[str] = None) -> List[Dict]:
        """List available packages from API"""
        try:
            # Try to fetch from API first
            url = f"{self.api_url}/api/v1/marketplace/packages"
            params = {}
            if category:
                params['category'] = category
            
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                # API returns {"packages": [...], "total": N}
                # Return API response even if empty (don't fallback to built-in)
                return data.get('packages', [])
        except Exception as e:
            logger.debug(f"Failed to fetch from API, using built-in packages: {e}")
        
        # Fallback to built-in packages only on error
        packages = list(self.packages.values())
        
        if category:
            packages = [p for p in packages if p.get('category') == category]
        
        return packages
    
    def search_packages(self, query: str) -> List[Dict]:
        """Search packages"""
        query = query.lower()
        results = []
        
        for pkg in self.packages.values():
            if (query in pkg['name'].lower() or 
                query in pkg['description'].lower() or
                query in pkg.get('category', '').lower()):
                results.append(pkg)
        
        return results
    
    def get_package(self, name: str) -> Optional[Dict]:
        """Get package by name from API"""
        try:
            # Try to fetch from API first
            url = f"{self.api_url}/api/v1/marketplace/packages/{name}"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            logger.debug(f"Failed to fetch from API, using built-in packages: {e}")
        
        # Fallback to built-in packages
        return self.packages.get(name)
    
    def install_package(self, name: str) -> bool:
        """Install a package"""
        pkg = self.get_package(name)
        if not pkg:
            logger.error(f"Package '{name}' not found")
            return False
        
        logger.info(f"📦 Installing {pkg['name']}")
        logger.info(f"   {pkg['description']}")
        
        # Check dependencies
        if not self._check_dependencies(pkg):
            return False
        
        # Install based on type
        if pkg['type'] == 'docker':
            return self._install_docker_package(pkg)
        elif pkg['type'] == 'host':
            return self._install_host_package(pkg)
        
        return False
    
    def _check_dependencies(self, pkg: Dict) -> bool:
        """Check package dependencies"""
        deps = pkg.get('dependencies', [])
        
        if not deps:
            return True
        
        logger.info(f"   Checking dependencies...")
        
        for dep in deps:
            if dep == 'space-agent':
                if not self.docker_manager.exists('space-agent'):
                    logger.error(f"   ❌ Dependency missing: {dep}")
                    logger.info(f"   Install with: san-cli install")
                    return False
            elif dep == 'ollama':
                # Check if Ollama is installed
                try:
                    result = subprocess.run(['ollama', '--version'], capture_output=True, timeout=5)
                    if result.returncode != 0:
                        logger.error(f"   ❌ Dependency missing: {dep}")
                        logger.info(f"   Install with: san-cli install")
                        return False
                except FileNotFoundError:
                    logger.error(f"   ❌ Dependency missing: {dep}")
                    logger.info(f"   Install with: san-cli install")
                    return False
        
        logger.info(f"   ✅ All dependencies satisfied")
        return True
    
    def _install_docker_package(self, pkg: Dict) -> bool:
        """Install Docker package"""
        docker_config = pkg['docker']
        
        try:
            # Pull image
            logger.info(f"   Pulling Docker image...")
            result = subprocess.run(
                ['docker', 'pull', docker_config['image']],
                capture_output=True,
                timeout=300
            )
            
            if result.returncode != 0:
                logger.error(f"   ❌ Failed to pull image")
                return False
            
            # Stop existing container
            container_name = docker_config['container_name']
            subprocess.run(['docker', 'stop', container_name], capture_output=True)
            subprocess.run(['docker', 'rm', container_name], capture_output=True)
            
            # Build docker run command
            cmd = ['docker', 'run', '-d']
            cmd.extend(['--name', container_name])
            cmd.extend(['--network', docker_config['network']])
            cmd.append('--restart=unless-stopped')
            
            # Add ports
            for port in docker_config.get('ports', []):
                cmd.extend(['-p', port])
            
            # Add environment variables
            for key, value in docker_config.get('environment', {}).items():
                cmd.extend(['-e', f'{key}={value}'])
            
            # Add volumes
            for volume in docker_config.get('volumes', []):
                cmd.extend(['-v', volume])
            
            # Add image
            cmd.append(docker_config['image'])
            
            # Run container
            logger.info(f"   Starting container...")
            result = subprocess.run(cmd, capture_output=True, timeout=30)
            
            if result.returncode != 0:
                logger.error(f"   ❌ Failed to start container: {result.stderr.decode()}")
                return False
            
            # Verify health
            if pkg.get('healthcheck'):
                logger.info(f"   Verifying health...")
                import time
                time.sleep(3)
                
                healthcheck = pkg['healthcheck']
                if 'url' in healthcheck:
                    try:
                        result = subprocess.run(
                            ['curl', '-s', healthcheck['url']],
                            capture_output=True,
                            timeout=10
                        )
                        if result.returncode != 0:
                            logger.warning(f"   ⚠️  Health check failed (service may still be starting)")
                    except FileNotFoundError:
                        logger.warning(f"   ⚠️  curl not found, skipping health check")
                elif 'command' in healthcheck:
                    # Command-based health check (like redis-cli ping)
                    try:
                        result = subprocess.run(
                            ['docker', 'exec', container_name] + healthcheck['command'].split(),
                            capture_output=True,
                            timeout=10
                        )
                        if result.returncode != 0:
                            logger.warning(f"   ⚠️  Health check failed (service may still be starting)")
                    except Exception:
                        logger.warning(f"   ⚠️  Health check failed")
            
            logger.info(f"   ✅ {pkg['name']} installed successfully")
            return True
            
        except Exception as e:
            logger.error(f"   ❌ Installation failed: {e}")
            return False
    
    def _install_host_package(self, pkg: Dict) -> bool:
        """Install host package"""
        logger.error("Host package installation not yet implemented")
        return False
    
    def uninstall_package(self, name: str) -> bool:
        """Uninstall a package"""
        pkg = self.get_package(name)
        if not pkg:
            logger.error(f"Package '{name}' not found")
            return False
        
        logger.info(f"🗑️  Uninstalling {pkg['name']}")
        
        if pkg['type'] == 'docker':
            container_name = pkg['docker']['container_name']
            
            # Stop and remove container
            subprocess.run(['docker', 'stop', container_name], capture_output=True)
            subprocess.run(['docker', 'rm', container_name], capture_output=True)
            
            logger.info(f"   ✅ {pkg['name']} uninstalled")
            return True
        
        return False
    
    def update_package(self, name: str) -> bool:
        """Update a package"""
        pkg = self.get_package(name)
        if not pkg:
            logger.error(f"Package '{name}' not found")
            return False
        
        logger.info(f"🔄 Updating {pkg['name']}")
        
        # For Docker packages, pull latest and restart
        if pkg['type'] == 'docker':
            docker_config = pkg['docker']
            
            # Pull latest image
            logger.info(f"   Pulling latest image...")
            result = subprocess.run(
                ['docker', 'pull', docker_config['image']],
                capture_output=True,
                timeout=300
            )
            
            if result.returncode != 0:
                logger.error(f"   ❌ Failed to pull image")
                return False
            
            # Restart container
            container_name = docker_config['container_name']
            logger.info(f"   Restarting container...")
            
            subprocess.run(['docker', 'stop', container_name], capture_output=True)
            subprocess.run(['docker', 'rm', container_name], capture_output=True)
            
            # Reinstall
            return self._install_docker_package(pkg)
        
        return False
    
    def get_categories(self) -> List[str]:
        """Get all package categories"""
        categories = set()
        for pkg in self.packages.values():
            if 'category' in pkg:
                categories.add(pkg['category'])
        return sorted(list(categories))
