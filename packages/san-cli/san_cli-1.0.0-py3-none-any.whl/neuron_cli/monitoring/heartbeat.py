"""Enhanced heartbeat - Sends comprehensive device stats to API"""

import requests
from typing import Dict, Any
from datetime import datetime

from .stats_collector import StatsCollector
from .device_scanner import DeviceScanner
from .network_monitor import NetworkMonitor
from ..core.logger import logger


class EnhancedHeartbeat:
    """Sends enhanced heartbeat with full device stats"""
    
    def __init__(self, api_url: str, device_id: str, jwt_token: str):
        self.api_url = api_url
        self.device_id = device_id
        self.jwt_token = jwt_token
        self.last_full_scan = 0
        self.full_scan_interval = 300  # Full scan every 5 minutes
    
    def send(self, include_full_scan: bool = False) -> bool:
        """Send heartbeat with device stats"""
        try:
            current_time = datetime.utcnow().timestamp()
            
            # Always include basic stats
            payload = {
                "status": "active",
                "timestamp": datetime.utcnow().isoformat(),
                "stats": StatsCollector.collect_all(),
            }
            
            # Include full device scan periodically
            if include_full_scan or (current_time - self.last_full_scan) > self.full_scan_interval:
                payload["devices"] = DeviceScanner.scan_all()
                payload["network_info"] = NetworkMonitor.get_network_info()
                payload["display_capabilities"] = DeviceScanner.get_display_control_capabilities()
                self.last_full_scan = current_time
            
            # Send to API
            url = f"{self.api_url}/mesh/devices/{self.device_id}/heartbeat"
            headers = {
                "Authorization": f"Bearer {self.jwt_token}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            
            if response.status_code == 200:
                logger.debug("💓 Enhanced heartbeat sent successfully")
                return True
            else:
                logger.warning(f"⚠️  Heartbeat failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Heartbeat error: {e}")
            return False
    
    def send_stats_update(self) -> bool:
        """Send just stats update (lightweight)"""
        try:
            payload = {
                "timestamp": datetime.utcnow().isoformat(),
                "stats": StatsCollector.collect_all(),
            }
            
            url = f"{self.api_url}/mesh/devices/{self.device_id}/stats"
            headers = {
                "Authorization": f"Bearer {self.jwt_token}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            return response.status_code == 200
            
        except Exception as e:
            logger.error(f"❌ Stats update error: {e}")
            return False
