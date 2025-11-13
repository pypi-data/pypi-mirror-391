"""Agent Benchmarking - Test device capabilities"""

import time
import psutil
import subprocess
from typing import Dict, Any
from datetime import datetime

from ..core.logger import logger


class AgentBenchmark:
    """Benchmark agent capabilities"""
    
    @staticmethod
    def run_full_benchmark() -> Dict[str, Any]:
        """
        Run complete benchmark suite
        
        Returns:
            Benchmark results
        """
        logger.info("🏁 Starting agent benchmark...")
        
        results = {
            "timestamp": datetime.utcnow().isoformat(),
            "cpu": AgentBenchmark.benchmark_cpu(),
            "memory": AgentBenchmark.benchmark_memory(),
            "disk": AgentBenchmark.benchmark_disk(),
            "network": AgentBenchmark.benchmark_network(),
            "overall_score": 0
        }
        
        # Calculate overall score (0-100)
        results["overall_score"] = AgentBenchmark._calculate_score(results)
        
        logger.info(f"✅ Benchmark complete! Score: {results['overall_score']}/100")
        
        return results
    
    @staticmethod
    def benchmark_cpu() -> Dict[str, Any]:
        """Benchmark CPU performance"""
        logger.info("   Testing CPU...")
        
        # Test 1: Single-core performance
        start = time.time()
        result = 0
        for i in range(1000000):
            result += i * i
        single_core_time = time.time() - start
        
        # Test 2: Multi-core performance
        cpu_count = psutil.cpu_count()
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_freq = psutil.cpu_freq()
        
        # Score: Lower time = better
        single_core_score = max(0, 100 - (single_core_time * 100))
        
        return {
            "cores": cpu_count,
            "frequency_mhz": cpu_freq.current if cpu_freq else 0,
            "usage_percent": cpu_percent,
            "single_core_time": round(single_core_time, 4),
            "single_core_score": round(single_core_score, 2),
            "capable_of": AgentBenchmark._cpu_capabilities(cpu_count, cpu_freq)
        }
    
    @staticmethod
    def benchmark_memory() -> Dict[str, Any]:
        """Benchmark memory performance"""
        logger.info("   Testing Memory...")
        
        mem = psutil.virtual_memory()
        
        # Test: Memory allocation speed
        start = time.time()
        data = [0] * 10000000  # 10M integers
        alloc_time = time.time() - start
        del data
        
        # Score: More available memory = better
        memory_score = (mem.available / mem.total) * 100
        
        return {
            "total_gb": round(mem.total / (1024**3), 2),
            "available_gb": round(mem.available / (1024**3), 2),
            "usage_percent": mem.percent,
            "allocation_time": round(alloc_time, 4),
            "memory_score": round(memory_score, 2),
            "capable_of": AgentBenchmark._memory_capabilities(mem.total)
        }
    
    @staticmethod
    def benchmark_disk() -> Dict[str, Any]:
        """Benchmark disk performance"""
        logger.info("   Testing Disk...")
        
        disk = psutil.disk_usage('/')
        
        # Test: Write speed (1MB test file)
        test_file = "/tmp/neuron_benchmark_test"
        data = b"0" * (1024 * 1024)  # 1MB
        
        start = time.time()
        try:
            with open(test_file, 'wb') as f:
                f.write(data)
                f.flush()
            write_time = time.time() - start
            write_speed = 1 / write_time  # MB/s
        except:
            write_time = 0
            write_speed = 0
        
        # Test: Read speed
        start = time.time()
        try:
            with open(test_file, 'rb') as f:
                _ = f.read()
            read_time = time.time() - start
            read_speed = 1 / read_time  # MB/s
        except:
            read_time = 0
            read_speed = 0
        
        # Cleanup
        try:
            import os
            os.remove(test_file)
        except:
            pass
        
        # Score: More free space + faster speed = better
        disk_score = ((disk.free / disk.total) * 50) + (min(write_speed, 100) / 2)
        
        return {
            "total_gb": round(disk.total / (1024**3), 2),
            "free_gb": round(disk.free / (1024**3), 2),
            "usage_percent": disk.percent,
            "write_speed_mbps": round(write_speed, 2),
            "read_speed_mbps": round(read_speed, 2),
            "disk_score": round(disk_score, 2),
            "capable_of": AgentBenchmark._disk_capabilities(disk.total, write_speed)
        }
    
    @staticmethod
    def benchmark_network() -> Dict[str, Any]:
        """Benchmark network performance"""
        logger.info("   Testing Network...")
        
        net = psutil.net_io_counters()
        
        # Test: Latency to API
        start = time.time()
        try:
            import requests
            response = requests.get("https://api.support.nexuscore.cloud/api/v1/health", timeout=5)
            latency = (time.time() - start) * 1000  # ms
            api_reachable = response.status_code == 200
        except:
            latency = 9999
            api_reachable = False
        
        # Score: Lower latency = better
        network_score = max(0, 100 - latency)
        
        return {
            "bytes_sent_mb": round(net.bytes_sent / (1024**2), 2),
            "bytes_recv_mb": round(net.bytes_recv / (1024**2), 2),
            "api_latency_ms": round(latency, 2),
            "api_reachable": api_reachable,
            "network_score": round(network_score, 2),
            "capable_of": AgentBenchmark._network_capabilities(latency, api_reachable)
        }
    
    @staticmethod
    def _calculate_score(results: Dict[str, Any]) -> float:
        """Calculate overall score (0-100)"""
        scores = [
            results["cpu"].get("single_core_score", 0),
            results["memory"].get("memory_score", 0),
            results["disk"].get("disk_score", 0),
            results["network"].get("network_score", 0),
        ]
        return round(sum(scores) / len(scores), 2)
    
    @staticmethod
    def _cpu_capabilities(cores: int, freq) -> list:
        """Determine CPU capabilities"""
        capabilities = []
        
        if cores >= 8:
            capabilities.append("ai_training")
            capabilities.append("video_encoding")
        if cores >= 4:
            capabilities.append("ai_inference")
            capabilities.append("compute_jobs")
        if cores >= 2:
            capabilities.append("web_server")
            capabilities.append("iot_gateway")
        
        capabilities.append("monitoring")
        
        return capabilities
    
    @staticmethod
    def _memory_capabilities(total_bytes: int) -> list:
        """Determine memory capabilities"""
        total_gb = total_bytes / (1024**3)
        capabilities = []
        
        if total_gb >= 16:
            capabilities.append("large_models")
            capabilities.append("database")
        if total_gb >= 8:
            capabilities.append("medium_models")
            capabilities.append("caching")
        if total_gb >= 4:
            capabilities.append("small_models")
            capabilities.append("web_apps")
        
        capabilities.append("basic_tasks")
        
        return capabilities
    
    @staticmethod
    def _disk_capabilities(total_bytes: int, write_speed: float) -> list:
        """Determine disk capabilities"""
        total_gb = total_bytes / (1024**3)
        capabilities = []
        
        if total_gb >= 500:
            capabilities.append("media_storage")
            capabilities.append("cdn")
        if total_gb >= 100:
            capabilities.append("file_storage")
            capabilities.append("backups")
        if total_gb >= 50:
            capabilities.append("logs")
            capabilities.append("cache")
        
        if write_speed >= 100:
            capabilities.append("fast_io")
        
        return capabilities
    
    @staticmethod
    def _network_capabilities(latency: float, api_reachable: bool) -> list:
        """Determine network capabilities"""
        capabilities = []
        
        if api_reachable:
            capabilities.append("cloud_connected")
        
        if latency < 50:
            capabilities.append("real_time")
            capabilities.append("gaming")
            capabilities.append("streaming")
        elif latency < 100:
            capabilities.append("web_services")
            capabilities.append("api_server")
        elif latency < 200:
            capabilities.append("batch_processing")
        
        return capabilities
