"""Configuration management for Neuron CLI"""

import json
from pathlib import Path
from typing import Optional, Dict, Any


class Config:
    """Manages Neuron CLI configuration"""
    
    DEFAULT_CONFIG_DIR = Path.home() / ".neuron"
    DEFAULT_CONFIG_FILE = DEFAULT_CONFIG_DIR / "config.json"
    
    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path or self.DEFAULT_CONFIG_FILE
        self.data: Dict[str, Any] = {}
        self.load()
    
    def load(self) -> None:
        """Load configuration from file"""
        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                self.data = json.load(f)
        else:
            # Create default config
            self.data = {
                "api_url": "https://api.support.nexuscore.cloud/api/v1",
                "device_id": "",
                "jwt_token": "",
                "brand_key": ""
            }
    
    def save(self) -> None:
        """Save configuration to file"""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        return self.data.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value"""
        self.data[key] = value
    
    def is_configured(self) -> bool:
        """Check if device is configured"""
        return bool(self.data.get("device_id") and self.data.get("jwt_token"))
    
    @property
    def device_id(self) -> str:
        return self.data.get("device_id", "")
    
    @property
    def jwt_token(self) -> str:
        return self.data.get("jwt_token", "")
    
    @property
    def api_url(self) -> str:
        return self.data.get("api_url", "https://api.support.nexuscore.cloud/api/v1")
    
    @property
    def brand_key(self) -> str:
        return self.data.get("brand_key", "")
