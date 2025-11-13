"""Package manifest parser"""

import yaml
from typing import Dict, List, Optional
from pathlib import Path


class PackageManifest:
    """Parse and validate package manifests"""
    
    def __init__(self, manifest_path: str):
        self.manifest_path = Path(manifest_path)
        self.data = {}
        self.load()
    
    def load(self):
        """Load manifest from YAML file"""
        if not self.manifest_path.exists():
            raise FileNotFoundError(f"Manifest not found: {self.manifest_path}")
        
        with open(self.manifest_path, 'r') as f:
            self.data = yaml.safe_load(f)
    
    @property
    def name(self) -> str:
        """Package name"""
        return self.data.get('name', '')
    
    @property
    def version(self) -> str:
        """Package version"""
        return self.data.get('version', '1.0.0')
    
    @property
    def type(self) -> str:
        """Package type: docker, host, or conditional"""
        return self.data.get('type', 'docker')
    
    @property
    def description(self) -> str:
        """Package description"""
        return self.data.get('description', '')
    
    @property
    def docker_config(self) -> Optional[Dict]:
        """Docker configuration"""
        return self.data.get('docker')
    
    @property
    def host_config(self) -> Optional[Dict]:
        """Host service configuration"""
        return self.data.get('host')
    
    @property
    def macos_config(self) -> Optional[Dict]:
        """macOS-specific configuration"""
        return self.data.get('macos')
    
    @property
    def linux_config(self) -> Optional[Dict]:
        """Linux-specific configuration"""
        return self.data.get('linux')
    
    @property
    def dependencies(self) -> List[str]:
        """Package dependencies"""
        deps = self.data.get('dependencies', {})
        if isinstance(deps, dict):
            return [k for k, v in deps.items() if v == 'required']
        return []
    
    @property
    def healthcheck(self) -> Optional[Dict]:
        """Health check configuration"""
        return self.data.get('healthcheck')
    
    @property
    def telemetry(self) -> Optional[Dict]:
        """Telemetry configuration"""
        return self.data.get('telemetry')
    
    def get_config_for_os(self, os_type: str) -> Optional[Dict]:
        """Get configuration for specific OS"""
        if os_type == 'darwin':
            return self.macos_config
        elif os_type == 'linux':
            return self.linux_config
        return None
    
    def validate(self) -> tuple[bool, List[str]]:
        """Validate manifest"""
        errors = []
        
        if not self.name:
            errors.append("Missing required field: name")
        
        if not self.type:
            errors.append("Missing required field: type")
        
        if self.type not in ['docker', 'host', 'conditional']:
            errors.append(f"Invalid type: {self.type}")
        
        if self.type == 'docker' and not self.docker_config:
            errors.append("Docker type requires docker configuration")
        
        if self.type == 'host' and not self.host_config:
            errors.append("Host type requires host configuration")
        
        return (len(errors) == 0, errors)
