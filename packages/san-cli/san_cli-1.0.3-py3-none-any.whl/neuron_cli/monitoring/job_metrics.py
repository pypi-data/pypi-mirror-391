"""Job metrics - Track job execution for billing"""

import psutil
import time
from typing import Dict, Any, Optional
from datetime import datetime


class JobMetrics:
    """Tracks metrics for job execution (for billing)"""
    
    def __init__(self, job_id: str):
        self.job_id = job_id
        self.start_time = None
        self.end_time = None
        self.process = None
        self.initial_cpu_times = None
        self.initial_io_counters = None
        self.metrics = {
            "job_id": job_id,
            "start_time": None,
            "end_time": None,
            "duration_seconds": 0,
            "cpu_usage_avg": 0,
            "cpu_usage_peak": 0,
            "memory_usage_avg_mb": 0,
            "memory_usage_peak_mb": 0,
            "disk_read_mb": 0,
            "disk_write_mb": 0,
            "network_sent_mb": 0,
            "network_recv_mb": 0,
            "samples": [],
        }
    
    def start(self, process_id: Optional[int] = None):
        """Start tracking metrics"""
        self.start_time = datetime.utcnow()
        self.metrics["start_time"] = self.start_time.isoformat()
        
        if process_id:
            try:
                self.process = psutil.Process(process_id)
                self.initial_cpu_times = self.process.cpu_times()
                self.initial_io_counters = self.process.io_counters() if hasattr(self.process, 'io_counters') else None
            except:
                pass
        
        # Get initial system counters
        self.initial_net_io = psutil.net_io_counters()
    
    def sample(self) -> Dict[str, Any]:
        """Take a sample of current metrics"""
        sample = {
            "timestamp": datetime.utcnow().isoformat(),
            "cpu_percent": 0,
            "memory_mb": 0,
        }
        
        if self.process:
            try:
                sample["cpu_percent"] = self.process.cpu_percent(interval=0.1)
                sample["memory_mb"] = round(self.process.memory_info().rss / (1024**2), 2)
            except:
                pass
        else:
            # System-wide metrics
            sample["cpu_percent"] = psutil.cpu_percent(interval=0.1)
            sample["memory_mb"] = round(psutil.virtual_memory().used / (1024**2), 2)
        
        self.metrics["samples"].append(sample)
        
        # Update peak values
        if sample["cpu_percent"] > self.metrics["cpu_usage_peak"]:
            self.metrics["cpu_usage_peak"] = sample["cpu_percent"]
        
        if sample["memory_mb"] > self.metrics["memory_usage_peak_mb"]:
            self.metrics["memory_usage_peak_mb"] = sample["memory_mb"]
        
        return sample
    
    def stop(self) -> Dict[str, Any]:
        """Stop tracking and calculate final metrics"""
        self.end_time = datetime.utcnow()
        self.metrics["end_time"] = self.end_time.isoformat()
        self.metrics["duration_seconds"] = (self.end_time - self.start_time).total_seconds()
        
        # Calculate averages
        if self.metrics["samples"]:
            cpu_samples = [s["cpu_percent"] for s in self.metrics["samples"]]
            memory_samples = [s["memory_mb"] for s in self.metrics["samples"]]
            
            self.metrics["cpu_usage_avg"] = round(sum(cpu_samples) / len(cpu_samples), 2)
            self.metrics["memory_usage_avg_mb"] = round(sum(memory_samples) / len(memory_samples), 2)
        
        # Calculate I/O if we have a process
        if self.process and self.initial_io_counters:
            try:
                final_io = self.process.io_counters()
                self.metrics["disk_read_mb"] = round(
                    (final_io.read_bytes - self.initial_io_counters.read_bytes) / (1024**2), 2
                )
                self.metrics["disk_write_mb"] = round(
                    (final_io.write_bytes - self.initial_io_counters.write_bytes) / (1024**2), 2
                )
            except:
                pass
        
        # Calculate network usage
        final_net_io = psutil.net_io_counters()
        self.metrics["network_sent_mb"] = round(
            (final_net_io.bytes_sent - self.initial_net_io.bytes_sent) / (1024**2), 2
        )
        self.metrics["network_recv_mb"] = round(
            (final_net_io.bytes_recv - self.initial_net_io.bytes_recv) / (1024**2), 2
        )
        
        return self.metrics
    
    def get_billing_data(self) -> Dict[str, Any]:
        """Get data formatted for billing"""
        return {
            "job_id": self.job_id,
            "start_time": self.metrics["start_time"],
            "end_time": self.metrics["end_time"],
            "duration_seconds": self.metrics["duration_seconds"],
            "duration_hours": round(self.metrics["duration_seconds"] / 3600, 4),
            "cpu_usage_avg_percent": self.metrics["cpu_usage_avg"],
            "cpu_usage_peak_percent": self.metrics["cpu_usage_peak"],
            "memory_usage_avg_mb": self.metrics["memory_usage_avg_mb"],
            "memory_usage_peak_mb": self.metrics["memory_usage_peak_mb"],
            "disk_io_mb": self.metrics["disk_read_mb"] + self.metrics["disk_write_mb"],
            "network_io_mb": self.metrics["network_sent_mb"] + self.metrics["network_recv_mb"],
            # Billing calculations (example rates)
            "compute_cost": round(self.metrics["duration_seconds"] / 3600 * 0.10, 4),  # $0.10/hour
            "network_cost": round((self.metrics["network_sent_mb"] + self.metrics["network_recv_mb"]) * 0.05 / 1024, 4),  # $0.05/GB
        }
    
    @staticmethod
    def calculate_cost(metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate cost based on metrics"""
        duration_hours = metrics.get("duration_seconds", 0) / 3600
        network_gb = (metrics.get("network_sent_mb", 0) + metrics.get("network_recv_mb", 0)) / 1024
        
        # Pricing (from revenue model)
        compute_cost = duration_hours * 0.10  # $0.10/hour per core
        network_cost = network_gb * 0.05      # $0.05/GB
        
        total_cost = compute_cost + network_cost
        
        # Revenue split (70% to device owner, 20% to platform, 10% to package author)
        device_owner_revenue = total_cost * 0.70
        platform_revenue = total_cost * 0.20
        package_author_revenue = total_cost * 0.10
        
        return {
            "total_cost": round(total_cost, 4),
            "compute_cost": round(compute_cost, 4),
            "network_cost": round(network_cost, 4),
            "revenue_split": {
                "device_owner": round(device_owner_revenue, 4),
                "platform": round(platform_revenue, 4),
                "package_author": round(package_author_revenue, 4),
            }
        }
