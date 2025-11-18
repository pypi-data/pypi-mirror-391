"""Network connection detector - VPN vs Public"""

import socket
from typing import Tuple, Optional
from ..core.logger import logger


class ConnectionDetector:
    """Detects best connection method (VPN or Public)"""
    
    # VPN endpoint
    VPN_HOST = "10.9.0.1"
    VPN_PORT = 8080
    VPN_API = f"http://{VPN_HOST}:{VPN_PORT}/api/v1"
    VPN_WS = f"ws://{VPN_HOST}:{VPN_PORT}/api/v1/mesh/connect"
    
    # Public endpoint
    PUBLIC_API = "https://api.support.nexuscore.cloud/api/v1"
    PUBLIC_WS = "wss://api.support.nexuscore.cloud/api/v1/mesh/connect"
    
    @staticmethod
    def detect() -> Tuple[str, str, str]:
        """
        Detect best connection method
        
        Returns:
            Tuple of (connection_type, api_url, ws_url)
            connection_type: "vpn" or "public"
        """
        if ConnectionDetector.check_vpn_available():
            logger.info("✅ VPN connection available - using internal endpoint")
            return ("vpn", ConnectionDetector.VPN_API, ConnectionDetector.VPN_WS)
        else:
            logger.info("🌐 VPN not available - using public HTTPS endpoint")
            return ("public", ConnectionDetector.PUBLIC_API, ConnectionDetector.PUBLIC_WS)
    
    @staticmethod
    def check_vpn_available(timeout: float = 2.0) -> bool:
        """
        Check if VPN endpoint is reachable
        
        Args:
            timeout: Connection timeout in seconds
            
        Returns:
            True if VPN is available, False otherwise
        """
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((ConnectionDetector.VPN_HOST, ConnectionDetector.VPN_PORT))
            sock.close()
            return result == 0
        except Exception as e:
            logger.debug(f"VPN check failed: {e}")
            return False
    
    @staticmethod
    def get_local_ip() -> Optional[str]:
        """Get local IP address"""
        try:
            # Create a socket to determine local IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            return local_ip
        except:
            return None
    
    @staticmethod
    def is_vpn_network(ip: str) -> bool:
        """Check if IP is in VPN network range"""
        return ip.startswith("10.8.") or ip.startswith("10.9.")
