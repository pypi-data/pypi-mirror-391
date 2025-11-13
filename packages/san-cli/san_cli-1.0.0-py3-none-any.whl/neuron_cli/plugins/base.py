"""Base plugin class for Neuron CLI plugins"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime


class NeuronPlugin(ABC):
    """Base class for all Neuron CLI plugins"""
    
    # Metadata (must be defined by plugin)
    name: str = ""
    version: str = "1.0.0"
    author: str = ""
    description: str = ""
    category: str = "general"
    
    # Pricing
    price: float = 0.0  # Monthly price (0 = free)
    price_model: str = "subscription"  # subscription, one_time, usage
    
    # Capabilities
    provides: List[str] = []  # What capabilities this plugin adds
    requires: List[str] = []  # What it needs from the system
    
    # System requirements
    min_cpu_cores: int = 1
    min_memory_gb: float = 1.0
    min_storage_gb: float = 1.0
    requires_gpu: bool = False
    requires_display: bool = False
    requires_network: bool = True
    
    def __init__(self):
        self.installed_at: Optional[datetime] = None
        self.started_at: Optional[datetime] = None
        self.is_running: bool = False
        self.config: Dict[str, Any] = {}
        self.state: Dict[str, Any] = {}
    
    @abstractmethod
    def install(self, config: Optional[Dict[str, Any]] = None) -> bool:
        """
        Install the plugin
        
        Args:
            config: Optional configuration dict
            
        Returns:
            True if installation successful
        """
        pass
    
    @abstractmethod
    def start(self) -> bool:
        """
        Start the plugin
        
        Returns:
            True if started successfully
        """
        pass
    
    @abstractmethod
    def stop(self) -> bool:
        """
        Stop the plugin
        
        Returns:
            True if stopped successfully
        """
        pass
    
    @abstractmethod
    def uninstall(self) -> bool:
        """
        Uninstall the plugin
        
        Returns:
            True if uninstalled successfully
        """
        pass
    
    def collect_data(self) -> Dict[str, Any]:
        """
        Collect data/metrics from the plugin
        
        Returns:
            Dict of metrics/data
        """
        return {}
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get plugin status
        
        Returns:
            Status dict
        """
        return {
            "name": self.name,
            "version": self.version,
            "is_running": self.is_running,
            "installed_at": self.installed_at.isoformat() if self.installed_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
        }
    
    def get_routes(self) -> List[Dict[str, Any]]:
        """
        Get API routes provided by this plugin
        
        Returns:
            List of route definitions
        """
        return []
    
    def validate_requirements(self, system_info: Dict[str, Any]) -> bool:
        """
        Validate that system meets plugin requirements
        
        Args:
            system_info: System capabilities
            
        Returns:
            True if requirements met
        """
        if system_info.get("cpu_cores", 0) < self.min_cpu_cores:
            return False
        if system_info.get("memory_gb", 0) < self.min_memory_gb:
            return False
        if system_info.get("storage_gb", 0) < self.min_storage_gb:
            return False
        if self.requires_gpu and not system_info.get("gpu_available", False):
            return False
        if self.requires_display and not system_info.get("display_available", False):
            return False
        
        return True
    
    def get_billing_info(self) -> Dict[str, Any]:
        """
        Get billing information for this plugin
        
        Returns:
            Billing info dict
        """
        return {
            "price": self.price,
            "price_model": self.price_model,
            "currency": "USD",
            "revenue_split": {
                "author": 0.70,
                "platform": 0.20,
                "device_owner": 0.10
            }
        }
