"""Firewall management - Control traffic in/out"""

import subprocess
from typing import List, Dict, Any, Optional
from enum import Enum

from ..core.logger import logger


class Protocol(Enum):
    """Network protocols"""
    TCP = "tcp"
    UDP = "udp"
    BOTH = "both"


class Policy(Enum):
    """Firewall policies"""
    ACCEPT = "ACCEPT"
    DROP = "DROP"
    REJECT = "REJECT"


class Firewall:
    """Manages device firewall rules"""
    
    def __init__(self):
        self.rules = []
        self.default_policy = Policy.DROP
    
    def deny_all(self):
        """Set default policy to DENY ALL"""
        logger.info("🔒 Setting firewall to DENY ALL")
        
        try:
            # Set default policies to DROP
            subprocess.run(["iptables", "-P", "INPUT", "DROP"], check=True)
            subprocess.run(["iptables", "-P", "FORWARD", "DROP"], check=True)
            subprocess.run(["iptables", "-P", "OUTPUT", "DROP"], check=True)
            
            # Flush existing rules
            subprocess.run(["iptables", "-F"], check=True)
            
            self.default_policy = Policy.DROP
            logger.info("✅ Firewall set to DENY ALL")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Failed to set firewall: {e}")
            return False
        except FileNotFoundError:
            logger.warning("⚠️  iptables not found (not running as root or not on Linux)")
            return False
    
    def allow_vpn_only(self, vpn_interface: str = "wg0"):
        """
        Allow traffic only through VPN interface
        
        Args:
            vpn_interface: VPN interface name (default: wg0 for WireGuard)
        """
        logger.info(f"🔓 Allowing traffic only through {vpn_interface}")
        
        try:
            # Allow loopback
            subprocess.run(["iptables", "-A", "INPUT", "-i", "lo", "-j", "ACCEPT"], check=True)
            subprocess.run(["iptables", "-A", "OUTPUT", "-o", "lo", "-j", "ACCEPT"], check=True)
            
            # Allow VPN interface
            subprocess.run(["iptables", "-A", "INPUT", "-i", vpn_interface, "-j", "ACCEPT"], check=True)
            subprocess.run(["iptables", "-A", "OUTPUT", "-o", vpn_interface, "-j", "ACCEPT"], check=True)
            
            # Allow established connections
            subprocess.run([
                "iptables", "-A", "INPUT", "-m", "state",
                "--state", "ESTABLISHED,RELATED", "-j", "ACCEPT"
            ], check=True)
            
            logger.info(f"✅ VPN-only traffic enabled on {vpn_interface}")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Failed to configure VPN firewall: {e}")
            return False
        except FileNotFoundError:
            logger.warning("⚠️  iptables not found")
            return False
    
    def allow_service(self, port: int, protocol: Protocol = Protocol.TCP, source: Optional[str] = None):
        """
        Allow specific service
        
        Args:
            port: Port number
            protocol: TCP or UDP
            source: Source IP/network (optional, e.g., "10.9.0.0/16")
        """
        logger.info(f"🔓 Opening port {port}/{protocol.value}")
        
        try:
            cmd = ["iptables", "-A", "INPUT", "-p", protocol.value, "--dport", str(port)]
            
            if source:
                cmd.extend(["-s", source])
            
            cmd.extend(["-j", "ACCEPT"])
            
            subprocess.run(cmd, check=True)
            
            self.rules.append({
                "port": port,
                "protocol": protocol.value,
                "source": source,
                "action": "allow"
            })
            
            logger.info(f"✅ Port {port}/{protocol.value} opened")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Failed to open port: {e}")
            return False
        except FileNotFoundError:
            logger.warning("⚠️  iptables not found")
            return False
    
    def block_service(self, port: int, protocol: Protocol = Protocol.TCP):
        """
        Block specific service
        
        Args:
            port: Port number
            protocol: TCP or UDP
        """
        logger.info(f"🔒 Blocking port {port}/{protocol.value}")
        
        try:
            subprocess.run([
                "iptables", "-A", "INPUT", "-p", protocol.value,
                "--dport", str(port), "-j", "DROP"
            ], check=True)
            
            logger.info(f"✅ Port {port}/{protocol.value} blocked")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Failed to block port: {e}")
            return False
        except FileNotFoundError:
            logger.warning("⚠️  iptables not found")
            return False
    
    def allow_external_via_proxy(self, service_name: str, internal_port: int):
        """
        Allow external access via HybridConnect proxy
        
        Args:
            service_name: Service name
            internal_port: Internal port to expose
        """
        logger.info(f"🌐 Exposing {service_name} externally via HybridConnect")
        
        # This would register the service with HybridConnect proxy
        # For now, just log it
        logger.info(f"   Service: {service_name}")
        logger.info(f"   Internal port: {internal_port}")
        logger.info(f"   External URL: https://device-id.hybridconnect.cloud/{service_name}")
        
        return True
    
    def get_rules(self) -> List[Dict[str, Any]]:
        """Get current firewall rules"""
        return self.rules
    
    def list_rules(self):
        """List current iptables rules"""
        try:
            result = subprocess.run(
                ["iptables", "-L", "-n", "-v"],
                capture_output=True, text=True, check=True
            )
            print(result.stdout)
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Failed to list rules: {e}")
        except FileNotFoundError:
            logger.warning("⚠️  iptables not found")
    
    def save_rules(self, filepath: str = "/etc/iptables/rules.v4"):
        """
        Save current rules (persist across reboots)
        
        Args:
            filepath: Path to save rules
        """
        try:
            result = subprocess.run(
                ["iptables-save"],
                capture_output=True, text=True, check=True
            )
            
            with open(filepath, 'w') as f:
                f.write(result.stdout)
            
            logger.info(f"✅ Rules saved to {filepath}")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Failed to save rules: {e}")
            return False
        except FileNotFoundError:
            logger.warning("⚠️  iptables-save not found")
            return False
        except PermissionError:
            logger.error(f"❌ Permission denied: {filepath}")
            return False
