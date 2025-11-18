"""Unified service management"""

import platform
from typing import Dict, List, Optional
from ..core.logger import logger
from .docker_manager import DockerServiceManager
from .host_manager import HostServiceManager


class ServiceManager:
    """Manage all services (Docker and host)"""
    
    def __init__(self):
        self.os_type = platform.system().lower()
        self.docker_manager = DockerServiceManager()
        self.host_manager = HostServiceManager(self.os_type)
    
    def list_all_services(self) -> Dict[str, List[Dict]]:
        """List all services"""
        return {
            'docker': self.docker_manager.list_services(),
            'host': self.host_manager.list_services(),
        }
    
    def get_service_status(self, service_name: str) -> Optional[Dict]:
        """Get status of a specific service"""
        # Try Docker first
        docker_status = self.docker_manager.get_status(service_name)
        if docker_status:
            return {**docker_status, 'type': 'docker'}
        
        # Try host service
        host_status = self.host_manager.get_status(service_name)
        if host_status:
            return {**host_status, 'type': 'host'}
        
        return None
    
    def start_service(self, service_name: str) -> bool:
        """Start a service"""
        # Try Docker first
        if self.docker_manager.exists(service_name):
            return self.docker_manager.start(service_name)
        
        # Try host service
        if self.host_manager.exists(service_name):
            return self.host_manager.start(service_name)
        
        logger.error(f"Service '{service_name}' not found")
        return False
    
    def stop_service(self, service_name: str) -> bool:
        """Stop a service"""
        if self.docker_manager.exists(service_name):
            return self.docker_manager.stop(service_name)
        
        if self.host_manager.exists(service_name):
            return self.host_manager.stop(service_name)
        
        logger.error(f"Service '{service_name}' not found")
        return False
    
    def restart_service(self, service_name: str) -> bool:
        """Restart a service"""
        if self.docker_manager.exists(service_name):
            return self.docker_manager.restart(service_name)
        
        if self.host_manager.exists(service_name):
            return self.host_manager.restart(service_name)
        
        logger.error(f"Service '{service_name}' not found")
        return False
    
    def get_logs(self, service_name: str, follow: bool = False, tail: int = 100) -> Optional[str]:
        """Get service logs"""
        if self.docker_manager.exists(service_name):
            return self.docker_manager.logs(service_name, follow, tail)
        
        if self.host_manager.exists(service_name):
            return self.host_manager.logs(service_name, follow, tail)
        
        logger.error(f"Service '{service_name}' not found")
        return None
    
    def enable_service(self, service_name: str) -> bool:
        """Enable service (auto-start on boot)"""
        if self.host_manager.exists(service_name):
            return self.host_manager.enable(service_name)
        
        logger.warning(f"Enable not supported for Docker services")
        return False
    
    def disable_service(self, service_name: str) -> bool:
        """Disable service (don't auto-start)"""
        if self.host_manager.exists(service_name):
            return self.host_manager.disable(service_name)
        
        logger.warning(f"Disable not supported for Docker services")
        return False
    
    def health_check(self, service_name: str) -> Dict:
        """Check service health"""
        status = self.get_service_status(service_name)
        
        if not status:
            return {'healthy': False, 'error': 'Service not found'}
        
        if status['type'] == 'docker':
            return self.docker_manager.health_check(service_name)
        else:
            return self.host_manager.health_check(service_name)
