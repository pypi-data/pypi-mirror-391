"""Hardware detection module - detects CPU, RAM, GPU, storage, displays"""

import platform
import subprocess
from typing import Dict, Any, List, Optional
import psutil


class HardwareDetector:
    """Detects hardware capabilities of the system"""
    
    @staticmethod
    def detect_all() -> Dict[str, Any]:
        """Detect all hardware capabilities"""
        return {
            "cpu": HardwareDetector.detect_cpu(),
            "memory": HardwareDetector.detect_memory(),
            "storage": HardwareDetector.detect_storage(),
            "gpu": HardwareDetector.detect_gpu(),
            "display": HardwareDetector.detect_display(),
            "network": HardwareDetector.detect_network(),
            "os": HardwareDetector.detect_os()
        }
    
    @staticmethod
    def detect_cpu() -> Dict[str, Any]:
        """Detect CPU information"""
        cpu_info = {
            "cores": psutil.cpu_count(logical=False) or 1,
            "threads": psutil.cpu_count(logical=True) or 1,
            "model": "Unknown",
            "architecture": platform.machine(),
        }
        
        # Get CPU frequency
        try:
            freq = psutil.cpu_freq()
            if freq:
                cpu_info["freq_mhz"] = int(freq.max) if freq.max else int(freq.current)
        except:
            cpu_info["freq_mhz"] = 0
        
        # Get CPU model (Linux)
        if platform.system() == "Linux":
            try:
                with open("/proc/cpuinfo") as f:
                    for line in f:
                        if line.startswith("model name"):
                            cpu_info["model"] = line.split(":")[1].strip()
                            break
            except:
                pass
        
        return cpu_info
    
    @staticmethod
    def detect_memory() -> Dict[str, Any]:
        """Detect memory information"""
        mem = psutil.virtual_memory()
        return {
            "total_gb": round(mem.total / (1024 ** 3), 2),
            "available_gb": round(mem.available / (1024 ** 3), 2),
            "used_percent": mem.percent
        }
    
    @staticmethod
    def detect_storage() -> Dict[str, Any]:
        """Detect storage information"""
        storage_info = {
            "disks": [],
            "total_gb": 0
        }
        
        for partition in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                disk = {
                    "device": partition.device,
                    "mountpoint": partition.mountpoint,
                    "fstype": partition.fstype,
                    "total_gb": round(usage.total / (1024 ** 3), 2),
                    "used_gb": round(usage.used / (1024 ** 3), 2),
                    "free_gb": round(usage.free / (1024 ** 3), 2),
                    "used_percent": usage.percent
                }
                storage_info["disks"].append(disk)
                storage_info["total_gb"] += disk["total_gb"]
            except:
                continue
        
        storage_info["total_gb"] = round(storage_info["total_gb"], 2)
        return storage_info
    
    @staticmethod
    def detect_gpu() -> Dict[str, Any]:
        """Detect GPU information"""
        gpu_info = {
            "available": False,
            "gpus": []
        }
        
        # Try NVIDIA
        try:
            result = subprocess.run(
                ["nvidia-smi", "--query-gpu=name,memory.total", "--format=csv,noheader"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                for line in result.stdout.strip().split("\n"):
                    if line:
                        parts = line.split(",")
                        gpu_info["gpus"].append({
                            "vendor": "NVIDIA",
                            "model": parts[0].strip(),
                            "memory_mb": int(parts[1].strip().split()[0]) if len(parts) > 1 else 0
                        })
                gpu_info["available"] = True
        except:
            pass
        
        # Try AMD (lspci)
        if not gpu_info["available"] and platform.system() == "Linux":
            try:
                result = subprocess.run(
                    ["lspci"], capture_output=True, text=True, timeout=5
                )
                for line in result.stdout.split("\n"):
                    if "VGA" in line or "3D" in line:
                        if "AMD" in line or "ATI" in line:
                            gpu_info["gpus"].append({
                                "vendor": "AMD",
                                "model": line.split(":")[-1].strip(),
                                "memory_mb": 0
                            })
                            gpu_info["available"] = True
                        elif "Intel" in line:
                            gpu_info["gpus"].append({
                                "vendor": "Intel",
                                "model": line.split(":")[-1].strip(),
                                "memory_mb": 0
                            })
            except:
                pass
        
        return gpu_info
    
    @staticmethod
    def detect_display() -> Dict[str, Any]:
        """Detect display/HDMI outputs"""
        display_info = {
            "available": False,
            "displays": []
        }
        
        if platform.system() == "Linux":
            # Check for X11 displays
            try:
                result = subprocess.run(
                    ["xrandr", "--query"],
                    capture_output=True,
                    text=True,
                    timeout=5,
                    env={"DISPLAY": ":0"}
                )
                if result.returncode == 0:
                    for line in result.stdout.split("\n"):
                        if " connected" in line:
                            parts = line.split()
                            display_info["displays"].append({
                                "name": parts[0],
                                "connected": True,
                                "resolution": parts[2] if len(parts) > 2 else "unknown"
                            })
                    display_info["available"] = len(display_info["displays"]) > 0
            except:
                pass
        
        return display_info
    
    @staticmethod
    def detect_network() -> Dict[str, Any]:
        """Detect network interfaces"""
        network_info = {
            "interfaces": []
        }
        
        for interface, addrs in psutil.net_if_addrs().items():
            for addr in addrs:
                if addr.family == 2:  # AF_INET (IPv4)
                    network_info["interfaces"].append({
                        "name": interface,
                        "ip": addr.address,
                        "netmask": addr.netmask
                    })
                    break
        
        return network_info
    
    @staticmethod
    def detect_os() -> Dict[str, Any]:
        """Detect operating system information"""
        return {
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "architecture": platform.machine(),
            "hostname": platform.node()
        }
