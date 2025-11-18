"""Host service management (launchd/systemd)"""

import subprocess
from typing import List, Dict, Optional
from ..core.logger import logger


class HostServiceManager:
    """Manage host services (launchd on macOS, systemd on Linux)"""
    
    def __init__(self, os_type: str):
        self.os_type = os_type
        self.service_map = {
            'ollama': {
                'darwin': 'com.ollama.server',
                'linux': 'ollama',
            },
            'whisper': {
                'darwin': 'com.nexuscore.whisper',
                'linux': 'whisper-service',
            },
        }
    
    def list_services(self) -> List[Dict]:
        """List all host services"""
        services = []
        
        for service_name in self.service_map.keys():
            status = self.get_status(service_name)
            if status:
                services.append(status)
        
        return services
    
    def exists(self, service_name: str) -> bool:
        """Check if host service exists"""
        return service_name in self.service_map
    
    def _get_service_id(self, service_name: str) -> Optional[str]:
        """Get platform-specific service ID"""
        if service_name not in self.service_map:
            return None
        
        return self.service_map[service_name].get(self.os_type)
    
    def get_status(self, service_name: str) -> Optional[Dict]:
        """Get host service status"""
        service_id = self._get_service_id(service_name)
        if not service_id:
            return None
        
        try:
            if self.os_type == 'darwin':
                # macOS launchd
                result = subprocess.run(
                    ['launchctl', 'list', service_id],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                if result.returncode == 0:
                    # Parse launchctl output
                    running = 'PID' in result.stdout
                    return {
                        'name': service_name,
                        'status': 'running' if running else 'stopped',
                        'running': running,
                    }
                
            elif self.os_type == 'linux':
                # Linux systemd
                result = subprocess.run(
                    ['systemctl', 'is-active', service_id],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                status = result.stdout.strip()
                return {
                    'name': service_name,
                    'status': status,
                    'running': status == 'active',
                }
            
            return None
        except Exception as e:
            return {'name': service_name, 'error': str(e)}
    
    def start(self, service_name: str) -> bool:
        """Start host service"""
        service_id = self._get_service_id(service_name)
        if not service_id:
            logger.error(f"Service '{service_name}' not found")
            return False
        
        try:
            logger.info(f"Starting {service_name}...")
            
            if self.os_type == 'darwin':
                # macOS launchd
                plist_path = f'/Library/LaunchDaemons/{service_id}.plist'
                result = subprocess.run(
                    ['sudo', 'launchctl', 'load', plist_path],
                    capture_output=True,
                    timeout=10
                )
                
            elif self.os_type == 'linux':
                # Linux systemd
                result = subprocess.run(
                    ['sudo', 'systemctl', 'start', service_id],
                    capture_output=True,
                    timeout=10
                )
            else:
                return False
            
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
        """Stop host service"""
        service_id = self._get_service_id(service_name)
        if not service_id:
            logger.error(f"Service '{service_name}' not found")
            return False
        
        try:
            logger.info(f"Stopping {service_name}...")
            
            if self.os_type == 'darwin':
                # macOS launchd
                plist_path = f'/Library/LaunchDaemons/{service_id}.plist'
                result = subprocess.run(
                    ['sudo', 'launchctl', 'unload', plist_path],
                    capture_output=True,
                    timeout=10
                )
                
            elif self.os_type == 'linux':
                # Linux systemd
                result = subprocess.run(
                    ['sudo', 'systemctl', 'stop', service_id],
                    capture_output=True,
                    timeout=10
                )
            else:
                return False
            
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
        """Restart host service"""
        if self.stop(service_name):
            import time
            time.sleep(2)
            return self.start(service_name)
        return False
    
    def enable(self, service_name: str) -> bool:
        """Enable service (auto-start on boot)"""
        service_id = self._get_service_id(service_name)
        if not service_id:
            return False
        
        try:
            if self.os_type == 'linux':
                result = subprocess.run(
                    ['sudo', 'systemctl', 'enable', service_id],
                    capture_output=True,
                    timeout=10
                )
                return result.returncode == 0
            
            # macOS launchd services are enabled by default
            return True
        except:
            return False
    
    def disable(self, service_name: str) -> bool:
        """Disable service (don't auto-start)"""
        service_id = self._get_service_id(service_name)
        if not service_id:
            return False
        
        try:
            if self.os_type == 'linux':
                result = subprocess.run(
                    ['sudo', 'systemctl', 'disable', service_id],
                    capture_output=True,
                    timeout=10
                )
                return result.returncode == 0
            
            # For macOS, need to unload the plist
            return self.stop(service_name)
        except:
            return False
    
    def logs(self, service_name: str, follow: bool = False, tail: int = 100) -> Optional[str]:
        """Get host service logs"""
        service_id = self._get_service_id(service_name)
        if not service_id:
            return None
        
        try:
            if self.os_type == 'darwin':
                # macOS - read from log files
                log_file = f'/tmp/{service_name}.log'
                cmd = ['tail']
                if follow:
                    cmd.append('-f')
                cmd.extend(['-n', str(tail), log_file])
                
                if follow:
                    subprocess.run(cmd)
                    return None
                else:
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
                    return result.stdout if result.returncode == 0 else None
                    
            elif self.os_type == 'linux':
                # Linux systemd
                cmd = ['journalctl', '-u', service_id]
                if follow:
                    cmd.append('-f')
                cmd.extend(['-n', str(tail)])
                
                if follow:
                    subprocess.run(cmd)
                    return None
                else:
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
                    return result.stdout if result.returncode == 0 else None
            
            return None
        except Exception as e:
            logger.error(f"Error getting logs: {e}")
            return None
    
    def health_check(self, service_name: str) -> Dict:
        """Check host service health"""
        status = self.get_status(service_name)
        
        if not status:
            return {'healthy': False, 'error': 'Service not found'}
        
        if not status.get('running'):
            return {'healthy': False, 'error': 'Service not running'}
        
        # Check if service is actually responding
        if service_name == 'ollama':
            return self._check_ollama_health()
        elif service_name == 'whisper':
            return self._check_whisper_health()
        
        return {'healthy': True}
    
    def _check_ollama_health(self) -> Dict:
        """Check Ollama health"""
        try:
            result = subprocess.run(
                ['curl', '-s', 'http://localhost:11434/api/tags'],
                capture_output=True,
                timeout=5
            )
            return {'healthy': result.returncode == 0}
        except:
            return {'healthy': False, 'error': 'Health check failed'}
    
    def _check_whisper_health(self) -> Dict:
        """Check Whisper health"""
        try:
            result = subprocess.run(
                ['curl', '-s', 'http://localhost:8026/health'],
                capture_output=True,
                timeout=5
            )
            return {'healthy': result.returncode == 0}
        except:
            return {'healthy': False, 'error': 'Health check failed'}
