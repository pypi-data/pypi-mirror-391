"""SPACE Agent Docker installation"""

import subprocess
import json
import time
from typing import Dict, Optional
from ..core.logger import logger


class SpaceAgentInstaller:
    """Install and manage SPACE Agent Docker container"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.container_name = 'space-agent'
        self.network_name = 'cave_mesh'
        self.image = 'registry.nexuscore.cloud/space-agent:latest'
    
    def install(self) -> Dict:
        """Install SPACE Agent"""
        logger.info("🚀 Installing SPACE Agent...")
        
        try:
            # Step 1: Create Docker network
            logger.info("   Creating Docker network...")
            if not self._create_network():
                return {'success': False, 'error': 'Failed to create Docker network'}
            
            # Step 2: Pull Docker image
            logger.info("   Pulling Docker image...")
            if not self._pull_image():
                return {'success': False, 'error': 'Failed to pull Docker image'}
            
            # Step 3: Stop existing container (if any)
            logger.info("   Checking for existing container...")
            self._stop_existing()
            
            # Step 4: Create and start container
            logger.info("   Starting container...")
            if not self._start_container():
                return {'success': False, 'error': 'Failed to start container'}
            
            # Step 5: Verify container is running
            logger.info("   Verifying container...")
            if not self._verify_running():
                return {'success': False, 'error': 'Container not running'}
            
            logger.info("   ✅ SPACE Agent installed successfully")
            return {
                'success': True,
                'container_name': self.container_name,
                'network': self.network_name,
                'image': self.image,
            }
        
        except Exception as e:
            logger.error(f"   ❌ Installation failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def _create_network(self) -> bool:
        """Create Docker network"""
        try:
            # Check if network exists
            result = subprocess.run(
                ['docker', 'network', 'ls', '--format', '{{.Name}}'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if self.network_name in result.stdout:
                logger.info(f"   Network '{self.network_name}' already exists")
                return True
            
            # Create network
            result = subprocess.run(
                ['docker', 'network', 'create', self.network_name],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            return result.returncode == 0
        except Exception as e:
            logger.error(f"   ❌ Error creating network: {e}")
            return False
    
    def _pull_image(self) -> bool:
        """Pull Docker image"""
        try:
            result = subprocess.run(
                ['docker', 'pull', self.image],
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes
            )
            
            return result.returncode == 0
        except Exception as e:
            logger.error(f"   ❌ Error pulling image: {e}")
            return False
    
    def _stop_existing(self):
        """Stop and remove existing container"""
        try:
            # Stop container
            subprocess.run(
                ['docker', 'stop', self.container_name],
                capture_output=True,
                timeout=30
            )
            
            # Remove container
            subprocess.run(
                ['docker', 'rm', self.container_name],
                capture_output=True,
                timeout=10
            )
        except:
            pass  # Container might not exist
    
    def _start_container(self) -> bool:
        """Start SPACE Agent container"""
        try:
            # Build docker run command
            cmd = [
                'docker', 'run', '-d',
                '--name', self.container_name,
                '--network', self.network_name,
                '--restart', 'unless-stopped',
                '-p', '8080:8080',
                '-v', '/var/run/docker.sock:/var/run/docker.sock',
            ]
            
            # Add environment variables
            env_vars = self._get_environment_variables()
            for key, value in env_vars.items():
                cmd.extend(['-e', f'{key}={value}'])
            
            # Add image
            cmd.append(self.image)
            
            # Run container
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                logger.error(f"   ❌ Docker run failed: {result.stderr}")
                return False
            
            return True
        except Exception as e:
            logger.error(f"   ❌ Error starting container: {e}")
            return False
    
    def _get_environment_variables(self) -> Dict[str, str]:
        """Get environment variables for container"""
        env = {
            'API_URL': self.config.get('api_url', 'https://api.support.nexuscore.cloud'),
            'GATEWAY_URL': self.config.get('gateway_url', 'wss://gateway.nexuscore.cloud'),
            'DEVICE_ID': self.config.get('device_id', ''),
            'JWT_TOKEN': self.config.get('jwt_token', ''),
        }
        
        # Add GPU info if available
        if 'gpu' in self.config:
            gpu = self.config['gpu']
            env['GPU_AVAILABLE'] = str(gpu.get('available', False)).lower()
            env['GPU_TYPE'] = gpu.get('type', '')
            env['GPU_MEMORY_GB'] = str(gpu.get('memory_gb', 0))
        
        return env
    
    def _verify_running(self, timeout: int = 30) -> bool:
        """Verify container is running"""
        try:
            start_time = time.time()
            
            while time.time() - start_time < timeout:
                result = subprocess.run(
                    ['docker', 'ps', '--filter', f'name={self.container_name}', '--format', '{{.Status}}'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                if result.returncode == 0 and 'Up' in result.stdout:
                    return True
                
                time.sleep(2)
            
            return False
        except Exception as e:
            logger.error(f"   ❌ Error verifying container: {e}")
            return False
    
    def status(self) -> Dict:
        """Get SPACE Agent status"""
        try:
            result = subprocess.run(
                ['docker', 'ps', '--filter', f'name={self.container_name}', '--format', '{{.Status}}'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0 and result.stdout.strip():
                return {
                    'running': True,
                    'status': result.stdout.strip(),
                }
            
            return {'running': False}
        except Exception as e:
            return {'running': False, 'error': str(e)}
    
    def stop(self) -> bool:
        """Stop SPACE Agent"""
        try:
            result = subprocess.run(
                ['docker', 'stop', self.container_name],
                capture_output=True,
                timeout=30
            )
            return result.returncode == 0
        except:
            return False
    
    def restart(self) -> bool:
        """Restart SPACE Agent"""
        try:
            result = subprocess.run(
                ['docker', 'restart', self.container_name],
                capture_output=True,
                timeout=30
            )
            return result.returncode == 0
        except:
            return False
    
    def logs(self, follow: bool = False, tail: int = 100) -> Optional[str]:
        """Get SPACE Agent logs"""
        try:
            cmd = ['docker', 'logs']
            if follow:
                cmd.append('-f')
            if tail:
                cmd.extend(['--tail', str(tail)])
            cmd.append(self.container_name)
            
            if follow:
                # Stream logs
                subprocess.run(cmd)
                return None
            else:
                # Get logs
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                return result.stdout if result.returncode == 0 else None
        except:
            return None
