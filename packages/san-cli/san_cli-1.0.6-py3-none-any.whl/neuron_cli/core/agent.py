"""Main Neuron Agent - orchestrates all components"""

import time
import sys
import threading
from typing import Optional, Dict, Any
import requests

from .config import Config
from .logger import logger
from ..hardware.detector import HardwareDetector
from ..connection.detector import ConnectionDetector
from ..jobs.executor import JobExecutor
from ..monitoring.usage_metering import UsageMeter


class NeuronAgent:
    """Main Neuron CLI Agent"""
    
    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config()
        self.connection_type: Optional[str] = None
        self.api_url: Optional[str] = None
        self.ws_url: Optional[str] = None
        self.running = False
        self.hardware_info: Optional[Dict[str, Any]] = None
        self.job_executor: Optional[JobExecutor] = None
        self.job_thread: Optional[threading.Thread] = None
        self.usage_meter: Optional[UsageMeter] = None
        self.usage_thread: Optional[threading.Thread] = None
    
    def start(self, daemon: bool = False) -> None:
        """Start the agent"""
        logger.info("🚀 Starting Neuron CLI Agent...")
        
        # Check if configured
        if not self.config.is_configured():
            logger.error("❌ Agent not configured. Run 'neuron-cli register' first.")
            sys.exit(1)
        
        # Detect connection method
        self.connection_type, self.api_url, self.ws_url = ConnectionDetector.detect()
        logger.info(f"📡 Connection type: {self.connection_type}")
        logger.info(f"🔗 API URL: {self.api_url}")
        
        # Detect hardware
        logger.info("🔍 Detecting hardware capabilities...")
        self.hardware_info = HardwareDetector.detect_all()
        self._log_hardware_summary()
        
        # Update device with hardware info
        self._update_device_capabilities()
        
        # Initialize job executor
        self.job_executor = JobExecutor(
            api_url=self.api_url,
            device_id=self.config.device_id,
            jwt_token=self.config.jwt_token
        )
        
        # Start job executor in separate thread
        self.job_thread = threading.Thread(
            target=self.job_executor.start_polling,
            args=(30,),  # Poll every 30 seconds
            daemon=True
        )
        self.job_thread.start()
        logger.info("🔄 Job executor started")
        
        # Initialize and start usage meter
        self.usage_meter = UsageMeter()
        self.usage_thread = threading.Thread(
            target=self._run_usage_meter,
            daemon=True
        )
        self.usage_thread.start()
        logger.info("📊 Usage meter started")
        
        # Start heartbeat loop
        self.running = True
        logger.info("✅ Agent started successfully!")
        
        if daemon:
            logger.info("🔄 Running in daemon mode...")
            self._run_daemon()
        else:
            logger.info("🔄 Running in foreground mode (Ctrl+C to stop)...")
            self._run_foreground()
    
    def stop(self) -> None:
        """Stop the agent"""
        logger.info("🛑 Stopping Neuron CLI Agent...")
        self.running = False
        
        # Stop job executor
        if self.job_executor:
            self.job_executor.stop_polling()
        
        # Wait for job thread to finish
        if self.job_thread and self.job_thread.is_alive():
            self.job_thread.join(timeout=5)
        
        # Stop usage meter
        if self.usage_meter:
            logger.info("📊 Syncing final usage data...")
            self.usage_meter.sync_to_api()
        
        # Wait for usage thread to finish
        if self.usage_thread and self.usage_thread.is_alive():
            self.usage_thread.join(timeout=5)
    
    def status(self) -> Dict[str, Any]:
        """Get agent status"""
        return {
            "configured": self.config.is_configured(),
            "device_id": self.config.device_id,
            "connection_type": self.connection_type,
            "api_url": self.api_url,
            "running": self.running
        }
    
    def _run_foreground(self) -> None:
        """Run in foreground with heartbeat loop"""
        try:
            while self.running:
                self._send_heartbeat()
                time.sleep(60)  # Heartbeat every minute
        except KeyboardInterrupt:
            logger.info("\n⚠️  Interrupted by user")
            self.stop()
    
    def _run_daemon(self) -> None:
        """Run as daemon (background process)"""
        # TODO: Implement proper daemonization
        # For now, just run in foreground
        self._run_foreground()
    
    def _send_heartbeat(self) -> None:
        """Send heartbeat to server"""
        try:
            url = f"{self.api_url}/mesh/devices/{self.config.device_id}/heartbeat"
            headers = {
                "Authorization": f"Bearer {self.config.jwt_token}",
                "Content-Type": "application/json"
            }
            data = {
                "status": "active",
                "connection_type": self.connection_type
            }
            
            response = requests.post(url, json=data, headers=headers, timeout=10)
            
            if response.status_code == 200:
                logger.debug("💓 Heartbeat sent successfully")
            else:
                logger.warning(f"⚠️  Heartbeat failed: {response.status_code}")
                
        except Exception as e:
            logger.error(f"❌ Heartbeat error: {e}")
    
    def _update_device_capabilities(self) -> None:
        """Update device with detected hardware capabilities"""
        try:
            url = f"{self.api_url}/mesh/devices/{self.config.device_id}/stats"
            headers = {
                "Authorization": f"Bearer {self.config.jwt_token}",
                "Content-Type": "application/json"
            }
            
            # Prepare capabilities payload
            capabilities = {
                "cpu_cores": self.hardware_info["cpu"]["cores"],
                "cpu_threads": self.hardware_info["cpu"]["threads"],
                "memory_gb": self.hardware_info["memory"]["total_gb"],
                "storage_gb": self.hardware_info["storage"]["total_gb"],
                "gpu_available": self.hardware_info["gpu"]["available"],
                "gpu_count": len(self.hardware_info["gpu"]["gpus"]),
                "display_available": self.hardware_info["display"]["available"],
                "display_count": len(self.hardware_info["display"]["displays"]),
                "os": self.hardware_info["os"]["system"],
                "architecture": self.hardware_info["os"]["architecture"],
                "connection_type": self.connection_type
            }
            
            response = requests.post(url, json=capabilities, headers=headers, timeout=10)
            
            if response.status_code == 200:
                logger.info("✅ Hardware capabilities updated")
            else:
                logger.warning(f"⚠️  Failed to update capabilities: {response.status_code}")
                
        except Exception as e:
            logger.warning(f"⚠️  Could not update capabilities: {e}")
    
    def _log_hardware_summary(self) -> None:
        """Log hardware detection summary"""
        hw = self.hardware_info
        logger.info("=" * 50)
        logger.info("📊 Hardware Detection Summary:")
        logger.info(f"  CPU: {hw['cpu']['cores']} cores, {hw['cpu']['threads']} threads")
        logger.info(f"  RAM: {hw['memory']['total_gb']} GB")
        logger.info(f"  Storage: {hw['storage']['total_gb']} GB")
        logger.info(f"  GPU: {'✅ ' + str(len(hw['gpu']['gpus'])) + ' GPU(s)' if hw['gpu']['available'] else '❌ No GPU'}")
        logger.info(f"  Network: {len(hw['network']['interfaces'])} interface(s)")
        logger.info("=" * 50)
    
    def _run_usage_meter(self) -> None:
        """Run usage meter in background"""
        logger.info("📊 Usage meter daemon started")
        
        while self.running:
            try:
                # Track network every 60 seconds
                self.usage_meter.track_network_usage()
                
                # Track storage every 5 minutes
                if int(time.time()) % 300 == 0:
                    self.usage_meter.track_storage_usage()
                
                # Sync to API every 15 minutes
                if int(time.time()) % 900 == 0:
                    if self.usage_meter.sync_to_api():
                        logger.debug("✅ Usage data synced")
                    else:
                        logger.warning("⚠️  Failed to sync usage data")
                
                # Show monthly summary every hour
                if int(time.time()) % 3600 == 0:
                    summary = self.usage_meter.get_current_month_summary()
                    logger.info(f"📊 Monthly Usage: Network={summary['network_gb']:.2f}GB, "
                              f"CPU={summary['cpu_hours']:.2f}h, Jobs={summary['job_count']}, "
                              f"Cost=${summary['estimated_cost']:.2f}")
                
                time.sleep(60)
                
            except Exception as e:
                logger.error(f"❌ Usage meter error: {e}")
                time.sleep(60)
