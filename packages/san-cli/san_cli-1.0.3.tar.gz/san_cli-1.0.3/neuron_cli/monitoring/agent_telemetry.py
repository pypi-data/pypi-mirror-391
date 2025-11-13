"""Agent Telemetry - Send logs, errors, and metrics to NexusCore Cloud"""

import logging
import json
import time
import traceback
from typing import Dict, Any, Optional
from datetime import datetime
from queue import Queue
from threading import Thread
import requests

from ..core.logger import logger


class TelemetryLevel:
    """Telemetry levels"""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AgentTelemetry:
    """Sends agent logs and metrics to NexusCore Cloud"""
    
    def __init__(self, api_url: str, device_id: str, jwt_token: str):
        self.api_url = api_url
        self.device_id = device_id
        self.jwt_token = jwt_token
        self.queue = Queue(maxsize=1000)
        self.running = False
        self.thread = None
        self.batch_size = 10
        self.flush_interval = 5  # seconds
        
        # Telemetry settings
        self.settings = {
            "send_logs": True,
            "send_errors": True,
            "send_warnings": True,
            "send_metrics": True,
            "send_benchmarks": True,
            "min_level": TelemetryLevel.INFO,
            "immediate_errors": True,  # Send errors immediately via callback
        }
    
    def start(self):
        """Start telemetry thread"""
        if self.running:
            return
        
        self.running = True
        self.thread = Thread(target=self._run, daemon=True)
        self.thread.start()
        logger.info("📊 Agent telemetry started")
    
    def stop(self):
        """Stop telemetry thread"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=10)
        logger.info("📊 Agent telemetry stopped")
    
    def log(self, level: str, message: str, context: Optional[Dict[str, Any]] = None):
        """
        Send log message
        
        Args:
            level: Log level (debug, info, warning, error, critical)
            message: Log message
            context: Additional context data
        """
        if not self.settings["send_logs"]:
            return
        
        log_entry = {
            "type": "log",
            "level": level,
            "message": message,
            "context": context or {},
            "timestamp": datetime.utcnow().isoformat(),
            "device_id": self.device_id
        }
        
        # Send immediately if error and immediate_errors enabled
        if level in [TelemetryLevel.ERROR, TelemetryLevel.CRITICAL] and self.settings["immediate_errors"]:
            self._send_immediate(log_entry)
        else:
            self._enqueue(log_entry)
    
    def error(self, error: Exception, context: Optional[Dict[str, Any]] = None):
        """
        Send error with full traceback
        
        Args:
            error: Exception object
            context: Additional context
        """
        if not self.settings["send_errors"]:
            return
        
        error_entry = {
            "type": "error",
            "error_type": type(error).__name__,
            "error_message": str(error),
            "traceback": traceback.format_exc(),
            "context": context or {},
            "timestamp": datetime.utcnow().isoformat(),
            "device_id": self.device_id
        }
        
        # Always send errors immediately
        self._send_immediate(error_entry)
    
    def metric(self, name: str, value: Any, tags: Optional[Dict[str, str]] = None):
        """
        Send metric
        
        Args:
            name: Metric name
            value: Metric value
            tags: Metric tags
        """
        if not self.settings["send_metrics"]:
            return
        
        metric_entry = {
            "type": "metric",
            "name": name,
            "value": value,
            "tags": tags or {},
            "timestamp": datetime.utcnow().isoformat(),
            "device_id": self.device_id
        }
        
        self._enqueue(metric_entry)
    
    def benchmark(self, benchmark_data: Dict[str, Any]):
        """
        Send benchmark results
        
        Args:
            benchmark_data: Benchmark results
        """
        if not self.settings["send_benchmarks"]:
            return
        
        benchmark_entry = {
            "type": "benchmark",
            "data": benchmark_data,
            "timestamp": datetime.utcnow().isoformat(),
            "device_id": self.device_id
        }
        
        self._enqueue(benchmark_entry)
    
    def job_event(self, job_id: str, event: str, data: Optional[Dict[str, Any]] = None):
        """
        Send job event
        
        Args:
            job_id: Job ID
            event: Event type (started, progress, completed, failed)
            data: Event data
        """
        event_entry = {
            "type": "job_event",
            "job_id": job_id,
            "event": event,
            "data": data or {},
            "timestamp": datetime.utcnow().isoformat(),
            "device_id": self.device_id
        }
        
        self._enqueue(event_entry)
    
    def _enqueue(self, entry: Dict[str, Any]):
        """Add entry to queue"""
        try:
            self.queue.put_nowait(entry)
        except:
            # Queue full, drop oldest
            try:
                self.queue.get_nowait()
                self.queue.put_nowait(entry)
            except:
                pass
    
    def _send_immediate(self, entry: Dict[str, Any]):
        """Send entry immediately (for errors)"""
        try:
            url = f"{self.api_url}/mesh/telemetry"
            headers = {
                "Authorization": f"Bearer {self.jwt_token}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "device_id": self.device_id,
                "entries": [entry]
            }
            
            requests.post(url, json=payload, headers=headers, timeout=5)
            logger.debug(f"📤 Sent immediate telemetry: {entry['type']}")
            
        except Exception as e:
            logger.debug(f"Failed to send immediate telemetry: {e}")
    
    def _run(self):
        """Telemetry thread - batch and send entries"""
        last_flush = time.time()
        batch = []
        
        while self.running:
            try:
                # Get entries from queue
                while len(batch) < self.batch_size:
                    try:
                        entry = self.queue.get(timeout=0.1)
                        batch.append(entry)
                    except:
                        break
                
                # Flush if batch full or interval elapsed
                current_time = time.time()
                should_flush = (
                    len(batch) >= self.batch_size or
                    (batch and current_time - last_flush >= self.flush_interval)
                )
                
                if should_flush and batch:
                    self._send_batch(batch)
                    batch = []
                    last_flush = current_time
                
                time.sleep(0.1)
                
            except Exception as e:
                logger.error(f"Telemetry thread error: {e}")
                time.sleep(1)
        
        # Flush remaining entries on shutdown
        if batch:
            self._send_batch(batch)
    
    def _send_batch(self, batch: list):
        """Send batch of entries"""
        try:
            url = f"{self.api_url}/mesh/telemetry"
            headers = {
                "Authorization": f"Bearer {self.jwt_token}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "device_id": self.device_id,
                "entries": batch
            }
            
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            
            if response.status_code == 200:
                logger.debug(f"📤 Sent {len(batch)} telemetry entries")
            else:
                logger.warning(f"Telemetry batch failed: {response.status_code}")
                
        except Exception as e:
            logger.error(f"Failed to send telemetry batch: {e}")


class TelemetryHandler(logging.Handler):
    """Logging handler that sends logs to telemetry"""
    
    def __init__(self, telemetry: AgentTelemetry):
        super().__init__()
        self.telemetry = telemetry
    
    def emit(self, record: logging.LogRecord):
        """Send log record to telemetry"""
        try:
            level_map = {
                logging.DEBUG: TelemetryLevel.DEBUG,
                logging.INFO: TelemetryLevel.INFO,
                logging.WARNING: TelemetryLevel.WARNING,
                logging.ERROR: TelemetryLevel.ERROR,
                logging.CRITICAL: TelemetryLevel.CRITICAL,
            }
            
            level = level_map.get(record.levelno, TelemetryLevel.INFO)
            
            context = {
                "module": record.module,
                "function": record.funcName,
                "line": record.lineno,
            }
            
            if record.exc_info:
                context["exception"] = self.format(record)
            
            self.telemetry.log(level, record.getMessage(), context)
            
        except Exception:
            self.handleError(record)
