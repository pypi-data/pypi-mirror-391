"""Neuron CLI - Join the NexusCore MESH Network"""

from .version import __version__, __author__, __license__

# Core components
try:
    from .core.agent import NeuronAgent
    from .core.config import Config
except ImportError:
    NeuronAgent = None
    Config = None

# MESH IP Protocol (v2.0)
from .connection.mesh_ip import MeshIPProtocol, MeshAddress

# Plugin system (v2.0)
from .plugins.base import NeuronPlugin

__all__ = [
    '__version__', 
    '__author__', 
    'NeuronAgent',
    'NeuronAgent', 
    'Config',
    'MeshIPProtocol',
    'MeshAddress',
    'NeuronPlugin'
]
