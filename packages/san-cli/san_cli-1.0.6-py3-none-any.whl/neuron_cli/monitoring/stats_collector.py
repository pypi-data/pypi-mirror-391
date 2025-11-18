"""Real-time system statistics collector"""

import psutil
from typing import Dict, Any
from datetime import datetime


class StatsCollector:
    """Collects real-time system statistics for billing and monitoring"""
    
    @staticmethod
    def collect_all() -> Dict[str, Any]:
        """Collect all system statistics"""
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "cpu": StatsCollector.collect_cpu(),
            "memory": StatsCollector.collect_memory(),
            "disk": StatsCollector.collect_disk(),
            "network": StatsCollector.collect_network(),
        }
    
    @staticmethod
    def collect_cpu() -> Dict[str, Any]:
        """Collect CPU statistics"""
        cpu_freq = psutil.cpu_freq()
        
        stats = {
            "usage_percent": psutil.cpu_percent(interval=0.1),
            "usage_per_core": psutil.cpu_percent(interval=0.1, percpu=True),
            "cores": psutil.cpu_count(logical=False),
            "threads": psutil.cpu_count(logical=True),
            "load_average": list(psutil.getloadavg()) if hasattr(psutil, 'getloadavg') else [0, 0, 0],
        }
        
        if cpu_freq:
            stats.update({
                "frequency_current_mhz": round(cpu_freq.current, 2),
                "frequency_min_mhz": round(cpu_freq.min, 2) if cpu_freq.min else 0,
                "frequency_max_mhz": round(cpu_freq.max, 2) if cpu_freq.max else 0,
            })
        
        # Try to get temperature
        temp = StatsCollector._get_cpu_temperature()
        if temp:
            stats["temperature_celsius"] = temp
        
        return stats
    
    @staticmethod
    def _get_cpu_temperature() -> float:
        """Get CPU temperature if available"""
        try:
            if hasattr(psutil, 'sensors_temperatures'):
                temps = psutil.sensors_temperatures()
                if 'coretemp' in temps and temps['coretemp']:
                    return round(temps['coretemp'][0].current, 1)
                elif 'cpu_thermal' in temps and temps['cpu_thermal']:
                    return round(temps['cpu_thermal'][0].current, 1)
        except:
            pass
        return None
    
    @staticmethod
    def collect_memory() -> Dict[str, Any]:
        """Collect memory statistics"""
        mem = psutil.virtual_memory()
        swap = psutil.swap_memory()
        
        return {
            "total_gb": round(mem.total / (1024**3), 2),
            "used_gb": round(mem.used / (1024**3), 2),
            "available_gb": round(mem.available / (1024**3), 2),
            "free_gb": round(mem.free / (1024**3), 2),
            "usage_percent": mem.percent,
            "swap_total_gb": round(swap.total / (1024**3), 2),
            "swap_used_gb": round(swap.used / (1024**3), 2),
            "swap_free_gb": round(swap.free / (1024**3), 2),
            "swap_percent": swap.percent,
        }
    
    @staticmethod
    def collect_disk() -> Dict[str, Any]:
        """Collect disk statistics"""
        disk_usage = psutil.disk_usage('/')
        disk_io = psutil.disk_io_counters()
        
        stats = {
            "root_total_gb": round(disk_usage.total / (1024**3), 2),
            "root_used_gb": round(disk_usage.used / (1024**3), 2),
            "root_free_gb": round(disk_usage.free / (1024**3), 2),
            "root_usage_percent": disk_usage.percent,
        }
        
        if disk_io:
            stats.update({
                "read_bytes": disk_io.read_bytes,
                "write_bytes": disk_io.write_bytes,
                "read_mb": round(disk_io.read_bytes / (1024**2), 2),
                "write_mb": round(disk_io.write_bytes / (1024**2), 2),
            })
        
        # Get all partitions
        partitions = []
        for partition in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                partitions.append({
                    "device": partition.device,
                    "mountpoint": partition.mountpoint,
                    "fstype": partition.fstype,
                    "total_gb": round(usage.total / (1024**3), 2),
                    "used_gb": round(usage.used / (1024**3), 2),
                    "free_gb": round(usage.free / (1024**3), 2),
                    "usage_percent": usage.percent,
                })
            except:
                continue
        
        stats["partitions"] = partitions
        return stats
    
    @staticmethod
    def collect_network() -> Dict[str, Any]:
        """Collect network statistics"""
        net_io = psutil.net_io_counters()
        
        stats = {
            "bytes_sent": net_io.bytes_sent,
            "bytes_recv": net_io.bytes_recv,
            "sent_mb": round(net_io.bytes_sent / (1024**2), 2),
            "recv_mb": round(net_io.bytes_recv / (1024**2), 2),
            "packets_sent": net_io.packets_sent,
            "packets_recv": net_io.packets_recv,
        }
        
        # Get interface stats
        interfaces = []
        net_if_addrs = psutil.net_if_addrs()
        net_if_stats = psutil.net_if_stats()
        
        for iface_name, addrs in net_if_addrs.items():
            iface_stat = net_if_stats.get(iface_name)
            
            iface_info = {
                "name": iface_name,
                "is_up": iface_stat.isup if iface_stat else False,
                "speed_mbps": iface_stat.speed if iface_stat else 0,
                "addresses": []
            }
            
            for addr in addrs:
                if addr.family == 2:  # AF_INET (IPv4)
                    iface_info["addresses"].append({
                        "type": "ipv4",
                        "address": addr.address,
                        "netmask": addr.netmask
                    })
                elif addr.family == 10:  # AF_INET6 (IPv6)
                    iface_info["addresses"].append({
                        "type": "ipv6",
                        "address": addr.address
                    })
            
            interfaces.append(iface_info)
        
        stats["interfaces"] = interfaces
        return stats
