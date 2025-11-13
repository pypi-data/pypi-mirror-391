"""Installation module for SPACE Agent and services"""

from .system_detector import SystemDetector
from .dependency_installer import DependencyInstaller
from .space_agent import SpaceAgentInstaller
from .host_service import HostServiceInstaller

__all__ = [
    'SystemDetector',
    'DependencyInstaller',
    'SpaceAgentInstaller',
    'HostServiceInstaller',
]
