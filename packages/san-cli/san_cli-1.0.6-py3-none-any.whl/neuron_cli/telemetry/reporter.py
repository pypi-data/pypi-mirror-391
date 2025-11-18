"""Telemetry reporting to Nexus Core Cloud"""

import json
import requests
import time
import threading
from pathlib import Path
from typing import Dict, Optional
from ..core.logger import logger
from .collector import TelemetryCollector


class TelemetryReporter:
    """Report telemetry data to Nexus Core Cloud"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.collector = TelemetryCollector()
        self.api_url = config.get('api_url', 'https://api.support.nexuscore.cloud')
        self.device_id = config.get('device_id', '')
        self.jwt_token = config.get('jwt_token', '')
        self.enabled = self._load_enabled_state()
        self.interval = 60  # Report every 60 seconds
        self.thread = None
        self.running = False
    
    def _load_enabled_state(self) -> bool:
        """Load telemetry enabled state"""
        state_file = Path.home() / '.neuron' / 'telemetry.json'
        if state_file.exists():
            try:
                with open(state_file, 'r') as f:
                    data = json.load(f)
                    return data.get('enabled', True)
            except:
                pass
        return True  # Enabled by default
    
    def _save_enabled_state(self):
        """Save telemetry enabled state"""
        state_file = Path.home() / '.neuron' / 'telemetry.json'
        state_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(state_file, 'w') as f:
            json.dump({'enabled': self.enabled}, f)
    
    def enable(self):
        """Enable telemetry"""
        self.enabled = True
        self._save_enabled_state()
        logger.info("✅ Telemetry enabled")
    
    def disable(self):
        """Disable telemetry"""
        self.enabled = False
        self._save_enabled_state()
        logger.info("✅ Telemetry disabled")
    
    def status(self) -> Dict:
        """Get telemetry status"""
        return {
            'enabled': self.enabled,
            'running': self.running,
            'interval': self.interval,
            'api_url': self.api_url,
            'device_id': self.device_id,
        }
    
    def start_background(self):
        """Start background telemetry reporting"""
        if self.running:
            logger.warning("Telemetry already running")
            return
        
        if not self.enabled:
            logger.info("Telemetry disabled, not starting")
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._background_loop, daemon=True)
        self.thread.start()
        logger.info("✅ Telemetry background reporting started")
    
    def stop_background(self):
        """Stop background telemetry reporting"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        logger.info("✅ Telemetry background reporting stopped")
    
    def _background_loop(self):
        """Background reporting loop"""
        while self.running:
            try:
                self.report_once()
            except Exception as e:
                logger.error(f"Telemetry error: {e}")
            
            # Sleep in small increments to allow quick shutdown
            for _ in range(self.interval):
                if not self.running:
                    break
                time.sleep(1)
    
    def report_once(self) -> bool:
        """Report telemetry once"""
        if not self.enabled:
            return False
        
        try:
            # Collect data
            data = self.collector.collect_all()
            
            # Add device info
            data['device_id'] = self.device_id
            
            # Send to API
            response = requests.post(
                f'{self.api_url}/api/v1/telemetry',
                headers={
                    'Authorization': f'Bearer {self.jwt_token}',
                    'Content-Type': 'application/json',
                },
                json=data,
                timeout=10
            )
            
            if response.status_code == 200:
                logger.debug("Telemetry reported successfully")
                return True
            else:
                logger.warning(f"Telemetry report failed: {response.status_code}")
                return False
        
        except Exception as e:
            logger.error(f"Telemetry report error: {e}")
            return False
    
    def view_recent(self, limit: int = 100) -> Optional[list]:
        """View recent telemetry data"""
        try:
            response = requests.get(
                f'{self.api_url}/api/v1/telemetry/{self.device_id}',
                headers={
                    'Authorization': f'Bearer {self.jwt_token}',
                },
                params={'limit': limit},
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to fetch telemetry: {response.status_code}")
                return None
        
        except Exception as e:
            logger.error(f"Error fetching telemetry: {e}")
            return None
