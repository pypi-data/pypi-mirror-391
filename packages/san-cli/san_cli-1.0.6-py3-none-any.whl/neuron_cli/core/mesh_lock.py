"""MESH Lock File - Permanent device identity"""

import json
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional


class MeshLock:
    """Manages device MESH ID lock file - permanent, non-rotating identity"""
    
    LOCK_FILE = Path.home() / ".neuron" / "mesh.lock"
    
    @staticmethod
    def create(mesh_id: str, vpn_ip: str, public_key: str, vpn_cert: Optional[str] = None) -> Dict[str, Any]:
        """
        Create lock file (one time only during registration)
        
        Args:
            mesh_id: Permanent MESH ID (UUID)
            vpn_ip: VPN IP address (10.9.0.X)
            public_key: Device public key
            vpn_cert: VPN certificate (optional)
            
        Returns:
            Lock data dict
            
        Raises:
            Exception: If lock file already exists
        """
        if MeshLock.exists():
            raise Exception("❌ Lock file already exists! Device already registered.")
        
        # Extract node ID from MESH ID (first 8 hex chars)
        node_id = mesh_id.replace("-", "")[:8]
        
        lock_data = {
            "mesh_id": mesh_id,
            "node_id": node_id,
            "mesh_ip": f"mesh://{node_id}.nexus.cloud",
            "vpn_ip": vpn_ip,
            "public_key": public_key,
            "vpn_cert": vpn_cert,
            "created_at": datetime.utcnow().isoformat(),
            "locked": True,
            "rotation": False,  # NEVER rotates!
            "version": "2.0.0",
            "firewall": {
                "default_policy": "deny",
                "protocol": "udp",
                "vpn_only": True,
                "exposed_services": []
            }
        }
        
        # Sign the lock file
        signature = MeshLock._sign(lock_data)
        lock_data["signature"] = signature
        
        # Write lock file
        MeshLock.LOCK_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(MeshLock.LOCK_FILE, 'w') as f:
            json.dump(lock_data, f, indent=2)
        
        # Make read-only (owner only)
        MeshLock.LOCK_FILE.chmod(0o400)
        
        print(f"✅ Lock file created: {MeshLock.LOCK_FILE}")
        print(f"   MESH ID: {mesh_id}")
        print(f"   MESH IP: mesh://{node_id}.nexus.cloud")
        print(f"   VPN IP: {vpn_ip}")
        print(f"   Locked: True (permanent)")
        
        return lock_data
    
    @staticmethod
    def read() -> Optional[Dict[str, Any]]:
        """
        Read and verify lock file
        
        Returns:
            Lock data dict or None if doesn't exist
            
        Raises:
            Exception: If signature is invalid (tampered)
        """
        if not MeshLock.exists():
            return None
        
        with open(MeshLock.LOCK_FILE, 'r') as f:
            lock_data = json.load(f)
        
        # Verify signature
        if not MeshLock._verify(lock_data):
            raise Exception("❌ Lock file tampered! Signature invalid.")
        
        return lock_data
    
    @staticmethod
    def exists() -> bool:
        """Check if lock file exists"""
        return MeshLock.LOCK_FILE.exists()
    
    @staticmethod
    def get_mesh_id() -> Optional[str]:
        """Get MESH ID from lock file"""
        lock_data = MeshLock.read()
        return lock_data.get("mesh_id") if lock_data else None
    
    @staticmethod
    def get_mesh_ip() -> Optional[str]:
        """Get MESH IP from lock file"""
        lock_data = MeshLock.read()
        return lock_data.get("mesh_ip") if lock_data else None
    
    @staticmethod
    def get_vpn_ip() -> Optional[str]:
        """Get VPN IP from lock file"""
        lock_data = MeshLock.read()
        return lock_data.get("vpn_ip") if lock_data else None
    
    @staticmethod
    def is_locked() -> bool:
        """Check if device is locked (registered)"""
        lock_data = MeshLock.read()
        return lock_data.get("locked", False) if lock_data else False
    
    @staticmethod
    def update_firewall_rules(exposed_services: list):
        """
        Update firewall rules in lock file
        
        Args:
            exposed_services: List of exposed services
        """
        if not MeshLock.exists():
            raise Exception("❌ Lock file doesn't exist")
        
        lock_data = MeshLock.read()
        lock_data["firewall"]["exposed_services"] = exposed_services
        
        # Re-sign
        signature = MeshLock._sign(lock_data)
        lock_data["signature"] = signature
        
        # Temporarily make writable
        MeshLock.LOCK_FILE.chmod(0o600)
        
        # Write updated lock file
        with open(MeshLock.LOCK_FILE, 'w') as f:
            json.dump(lock_data, f, indent=2)
        
        # Make read-only again
        MeshLock.LOCK_FILE.chmod(0o400)
    
    @staticmethod
    def _sign(data: Dict[str, Any]) -> str:
        """
        Sign lock data with SHA-256
        
        Args:
            data: Lock data dict
            
        Returns:
            Hex signature
        """
        # Remove signature if present
        data_copy = {k: v for k, v in data.items() if k != "signature"}
        # Create deterministic string
        data_str = json.dumps(data_copy, sort_keys=True)
        # Hash it
        return hashlib.sha256(data_str.encode()).hexdigest()
    
    @staticmethod
    def _verify(data: Dict[str, Any]) -> bool:
        """
        Verify lock file signature
        
        Args:
            data: Lock data dict with signature
            
        Returns:
            True if signature is valid
        """
        stored_sig = data.get("signature")
        if not stored_sig:
            return False
        calculated_sig = MeshLock._sign(data)
        return stored_sig == calculated_sig
    
    @staticmethod
    def delete():
        """
        Delete lock file (DANGEROUS - only for testing/unregistration)
        """
        if MeshLock.exists():
            MeshLock.LOCK_FILE.unlink()
            print(f"⚠️  Lock file deleted: {MeshLock.LOCK_FILE}")
