"""Docker service management"""

import subprocess
from typing import List, Dict, Optional
from ..core.logger import logger


class DockerServiceManager:
    """Manage Docker services"""
    
    def list_services(self) -> List[Dict]:
        """List all Docker containers"""
        try:
            result = subprocess.run(
                ['docker', 'ps', '-a', '--format', '{{.Names}}|{{.Status}}|{{.Ports}}'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                return []
            
            services = []
            for line in result.stdout.strip().split('\n'):
                if not line:
                    continue
                
                parts = line.split('|')
                if len(parts) >= 2:
                    services.append({
                        'name': parts[0],
                        'status': parts[1],
                        'ports': parts[2] if len(parts) > 2 else '',
                        'running': 'Up' in parts[1],
                    })
            
            return services
        except Exception as e:
            logger.error(f"Error listing Docker services: {e}")
            return []
    
    def exists(self, service_name: str) -> bool:
        """Check if Docker container exists"""
        try:
            result = subprocess.run(
                ['docker', 'ps', '-a', '--filter', f'name={service_name}', '--format', '{{.Names}}'],
                capture_output=True,
                text=True,
                timeout=5
            )
            return service_name in result.stdout
        except:
            return False
    
    def get_status(self, service_name: str) -> Optional[Dict]:
        """Get Docker container status"""
        try:
            result = subprocess.run(
                ['docker', 'ps', '-a', '--filter', f'name={service_name}', '--format', '{{.Status}}'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0 and result.stdout.strip():
                status_str = result.stdout.strip()
                return {
                    'name': service_name,
                    'status': status_str,
                    'running': 'Up' in status_str,
                }
            
            return None
        except Exception as e:
            return {'error': str(e)}
    
    def start(self, service_name: str) -> bool:
        """Start Docker container"""
        try:
            logger.info(f"Starting {service_name}...")
            result = subprocess.run(
                ['docker', 'start', service_name],
                capture_output=True,
                timeout=30
            )
            
            if result.returncode == 0:
                logger.info(f"✅ {service_name} started")
                return True
            else:
                logger.error(f"❌ Failed to start {service_name}")
                return False
        except Exception as e:
            logger.error(f"❌ Error starting {service_name}: {e}")
            return False
    
    def stop(self, service_name: str) -> bool:
        """Stop Docker container"""
        try:
            logger.info(f"Stopping {service_name}...")
            result = subprocess.run(
                ['docker', 'stop', service_name],
                capture_output=True,
                timeout=30
            )
            
            if result.returncode == 0:
                logger.info(f"✅ {service_name} stopped")
                return True
            else:
                logger.error(f"❌ Failed to stop {service_name}")
                return False
        except Exception as e:
            logger.error(f"❌ Error stopping {service_name}: {e}")
            return False
    
    def restart(self, service_name: str) -> bool:
        """Restart Docker container"""
        try:
            logger.info(f"Restarting {service_name}...")
            result = subprocess.run(
                ['docker', 'restart', service_name],
                capture_output=True,
                timeout=30
            )
            
            if result.returncode == 0:
                logger.info(f"✅ {service_name} restarted")
                return True
            else:
                logger.error(f"❌ Failed to restart {service_name}")
                return False
        except Exception as e:
            logger.error(f"❌ Error restarting {service_name}: {e}")
            return False
    
    def logs(self, service_name: str, follow: bool = False, tail: int = 100) -> Optional[str]:
        """Get Docker container logs"""
        try:
            cmd = ['docker', 'logs']
            if follow:
                cmd.append('-f')
            if tail:
                cmd.extend(['--tail', str(tail)])
            cmd.append(service_name)
            
            if follow:
                # Stream logs (blocking)
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
        except Exception as e:
            logger.error(f"Error getting logs: {e}")
            return None
    
    def health_check(self, service_name: str) -> Dict:
        """Check Docker container health"""
        status = self.get_status(service_name)
        
        if not status:
            return {'healthy': False, 'error': 'Container not found'}
        
        if not status.get('running'):
            return {'healthy': False, 'error': 'Container not running'}
        
        # Check if container is actually responding
        # For now, just check if it's running
        return {'healthy': True, 'status': status['status']}
    
    def get_stats(self, service_name: str) -> Optional[Dict]:
        """Get Docker container resource usage"""
        try:
            result = subprocess.run(
                ['docker', 'stats', service_name, '--no-stream', '--format', '{{.CPUPerc}}|{{.MemUsage}}|{{.NetIO}}'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0 and result.stdout.strip():
                parts = result.stdout.strip().split('|')
                if len(parts) >= 3:
                    return {
                        'cpu': parts[0],
                        'memory': parts[1],
                        'network': parts[2],
                    }
            
            return None
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return None
