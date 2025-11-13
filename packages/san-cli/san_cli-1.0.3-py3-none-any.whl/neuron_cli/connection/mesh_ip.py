"""MESH IP Protocol Implementation"""

import re
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass


@dataclass
class MeshAddress:
    """Represents a parsed MESH IP address"""
    node: str  # Primary device ID (8 hex chars)
    subnet: Optional[str] = None  # Sub-MESH ID (4 hex chars)
    vlan: Optional[str] = None  # VLAN ID (4 hex chars)
    segment: Optional[str] = None  # Segment ID (4 hex chars)
    device: Optional[str] = None  # Device ID (4 hex chars)
    domain: str = "nexus.cloud"  # Internal or external domain
    
    def __str__(self) -> str:
        """Convert to MESH IP string"""
        parts = [self.node]
        if self.subnet:
            parts.append(self.subnet)
        if self.vlan:
            parts.append(self.vlan)
        if self.segment:
            parts.append(self.segment)
        if self.device:
            parts.append(self.device)
        
        return f"mesh://{'.'.join(parts)}.{self.domain}"
    
    def to_external_url(self, protocol: str = "https") -> str:
        """
        Convert to external URL
        
        Args:
            protocol: Protocol to use (https, wss, mesh)
            
        Returns:
            External URL string
        """
        parts = [self.node]
        if self.subnet:
            parts.append(self.subnet)
        if self.vlan:
            parts.append(self.vlan)
        if self.segment:
            parts.append(self.segment)
        if self.device:
            parts.append(self.device)
        
        hostname = f"{'.'.join(parts)}.hybridconnect.cloud"
        
        if protocol == "mesh":
            return f"mesh://{hostname}"
        elif protocol == "wss":
            return f"wss://{hostname}"
        else:
            return f"https://{hostname}"
    
    def is_internal(self) -> bool:
        """Check if this is an internal (VPN) address"""
        return self.domain == "nexus.cloud" or self.domain.endswith(".local")
    
    def is_external(self) -> bool:
        """Check if this is an external (public) address"""
        return self.domain == "hybridconnect.cloud"


class MeshIPProtocol:
    """MESH IP Protocol handler"""
    
    # Regex patterns
    MESH_IP_PATTERN = re.compile(
        r'^mesh://([a-f0-9]{8})'  # node (required)
        r'(?:\.([a-f0-9]{4}))?'    # subnet (optional)
        r'(?:\.([a-f0-9]{4}))?'    # vlan (optional)
        r'(?:\.([a-f0-9]{4}))?'    # segment (optional)
        r'(?:\.([a-f0-9]{4}))?'    # device (optional)
        r'\.([a-z.]+)$'            # domain
    )
    
    EXTERNAL_URL_PATTERN = re.compile(
        r'^https?://([a-f0-9]{8})'  # node (required)
        r'(?:\.([a-f0-9]{4}))?'      # subnet (optional)
        r'(?:\.([a-f0-9]{4}))?'      # vlan (optional)
        r'(?:\.([a-f0-9]{4}))?'      # segment (optional)
        r'(?:\.([a-f0-9]{4}))?'      # device (optional)
        r'\.hybridconnect\.cloud'
    )
    
    @staticmethod
    def parse(address: str) -> Optional[MeshAddress]:
        """
        Parse a MESH IP address
        
        Args:
            address: MESH IP string (mesh://... or https://...)
            
        Returns:
            MeshAddress object or None if invalid
        """
        # Try MESH IP format
        match = MeshIPProtocol.MESH_IP_PATTERN.match(address)
        if match:
            return MeshAddress(
                node=match.group(1),
                subnet=match.group(2),
                vlan=match.group(3),
                segment=match.group(4),
                device=match.group(5),
                domain=match.group(6)
            )
        
        # Try external URL format
        match = MeshIPProtocol.EXTERNAL_URL_PATTERN.match(address)
        if match:
            return MeshAddress(
                node=match.group(1),
                subnet=match.group(2),
                vlan=match.group(3),
                segment=match.group(4),
                device=match.group(5),
                domain="hybridconnect.cloud"
            )
        
        return None
    
    @staticmethod
    def create(node: str, subnet: Optional[str] = None, vlan: Optional[str] = None,
               segment: Optional[str] = None, device: Optional[str] = None,
               internal: bool = True) -> MeshAddress:
        """
        Create a MESH IP address
        
        Args:
            node: Primary device ID (8 hex chars)
            subnet: Sub-MESH ID (4 hex chars)
            vlan: VLAN ID (4 hex chars)
            segment: Segment ID (4 hex chars)
            device: Device ID (4 hex chars)
            internal: True for internal (VPN), False for external
            
        Returns:
            MeshAddress object
        """
        domain = "nexus.cloud" if internal else "hybridconnect.cloud"
        return MeshAddress(node, subnet, vlan, segment, device, domain)
    
    @staticmethod
    def validate(address: str) -> bool:
        """
        Validate a MESH IP address
        
        Args:
            address: MESH IP string
            
        Returns:
            True if valid
        """
        return MeshIPProtocol.parse(address) is not None
    
    @staticmethod
    def resolve_to_ipv4(mesh_address: MeshAddress) -> Optional[str]:
        """
        Resolve MESH IP to IPv4 address
        
        Args:
            mesh_address: MeshAddress object
            
        Returns:
            IPv4 address or None
        """
        # TODO: Implement DNS resolution
        # For now, return None (will be implemented in network module)
        return None
    
    @staticmethod
    def get_vlan_for_address(mesh_address: MeshAddress) -> Optional[int]:
        """
        Get VLAN ID from MESH address
        
        Args:
            mesh_address: MeshAddress object
            
        Returns:
            VLAN ID (integer) or None
        """
        if mesh_address.vlan:
            return int(mesh_address.vlan, 16)
        return None
