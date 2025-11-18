"""Telemetry data collection"""

import psutil
import platform
import subprocess
from typing import Dict, List
from datetime import datetime


class TelemetryCollector:
    """Collect system, service, and usage metrics"""
    
    def __init__(self):
        self.os_type = platform.system().lower()
    
    def collect_all(self) -> Dict:
        """Collect all telemetry data"""
        return {
            'timestamp': datetime.utcnow().isoformat(),
            'system': self.collect_system_metrics(),
            'services': self.collect_service_metrics(),
            'network': self.collect_network_metrics(),
            'gpu': self.collect_gpu_metrics(),
        }
    
    def collect_system_metrics(self) -> Dict:
        """Collect system metrics"""
        cpu_percent = psutil.cpu_percent(interval=1, percpu=True)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        return {
            'cpu': {
                'percent_total': sum(cpu_percent) / len(cpu_percent),
                'percent_per_core': cpu_percent,
                'count': psutil.cpu_count(),
                'load_avg': psutil.getloadavg() if hasattr(psutil, 'getloadavg') else None,
            },
            'memory': {
                'total': memory.total,
                'used': memory.used,
                'available': memory.available,
                'percent': memory.percent,
            },
            'disk': {
                'total': disk.total,
                'used': disk.used,
                'free': disk.free,
                'percent': disk.percent,
            },
            'uptime': self._get_uptime(),
        }
    
    def collect_service_metrics(self) -> List[Dict]:
        """Collect service metrics"""
        services = []
        
        # Docker services
        try:
            result = subprocess.run(
                ['docker', 'ps', '--format', '{{.Names}}|{{.Status}}|{{.ID}}'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                for line in result.stdout.strip().split('\n'):
                    if not line:
                        continue
                    
                    parts = line.split('|')
                    if len(parts) >= 3:
                        name, status, container_id = parts[0], parts[1], parts[2]
                        
                        # Get container stats
                        stats = self._get_container_stats(container_id)
                        
                        services.append({
                            'name': name,
                            'type': 'docker',
                            'status': status,
                            'running': 'Up' in status,
                            'stats': stats,
                        })
        except:
            pass
        
        # Host services (ollama, whisper)
        for service_name in ['ollama', 'whisper']:
            status = self._get_host_service_status(service_name)
            if status:
                services.append(status)
        
        return services
    
    def collect_network_metrics(self) -> Dict:
        """Collect network metrics"""
        net_io = psutil.net_io_counters()
        
        return {
            'bytes_sent': net_io.bytes_sent,
            'bytes_recv': net_io.bytes_recv,
            'packets_sent': net_io.packets_sent,
            'packets_recv': net_io.packets_recv,
            'errin': net_io.errin,
            'errout': net_io.errout,
            'dropin': net_io.dropin,
            'dropout': net_io.dropout,
        }
    
    def collect_gpu_metrics(self) -> Dict:
        """Collect GPU metrics"""
        if self.os_type == 'darwin':
            return self._collect_metal_metrics()
        elif self.os_type == 'linux':
            return self._collect_cuda_metrics()
        return {}
    
    def _collect_metal_metrics(self) -> Dict:
        """Collect Metal GPU metrics (macOS)"""
        try:
            # Get system memory (unified on Apple Silicon)
            result = subprocess.run(
                ['sysctl', '-n', 'hw.memsize'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                memory_bytes = int(result.stdout.strip())
                memory_gb = memory_bytes // (1024 ** 3)
                
                return {
                    'available': True,
                    'type': 'metal',
                    'memory_total': memory_gb,
                    'memory_used': None,  # Not easily available on macOS
                }
        except:
            pass
        
        return {'available': False}
    
    def _collect_cuda_metrics(self) -> Dict:
        """Collect CUDA GPU metrics (Linux)"""
        try:
            result = subprocess.run(
                ['nvidia-smi', '--query-gpu=utilization.gpu,utilization.memory,memory.total,memory.used,temperature.gpu', '--format=csv,noheader,nounits'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                values = result.stdout.strip().split(',')
                if len(values) >= 5:
                    return {
                        'available': True,
                        'type': 'cuda',
                        'utilization': float(values[0]),
                        'memory_utilization': float(values[1]),
                        'memory_total': int(values[2]),
                        'memory_used': int(values[3]),
                        'temperature': int(values[4]),
                    }
        except:
            pass
        
        return {'available': False}
    
    def _get_container_stats(self, container_id: str) -> Dict:
        """Get Docker container stats"""
        try:
            result = subprocess.run(
                ['docker', 'stats', container_id, '--no-stream', '--format', '{{.CPUPerc}}|{{.MemUsage}}|{{.NetIO}}'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                parts = result.stdout.strip().split('|')
                if len(parts) >= 3:
                    return {
                        'cpu': parts[0],
                        'memory': parts[1],
                        'network': parts[2],
                    }
        except:
            pass
        
        return {}
    
    def _get_host_service_status(self, service_name: str) -> Dict:
        """Get host service status"""
        try:
            if self.os_type == 'darwin':
                # macOS launchd
                service_id = f'com.ollama.server' if service_name == 'ollama' else f'com.nexuscore.whisper'
                result = subprocess.run(
                    ['launchctl', 'list', service_id],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                if result.returncode == 0:
                    running = 'PID' in result.stdout
                    return {
                        'name': service_name,
                        'type': 'host',
                        'status': 'running' if running else 'stopped',
                        'running': running,
                    }
            
            elif self.os_type == 'linux':
                # Linux systemd
                service_id = 'ollama' if service_name == 'ollama' else 'whisper-service'
                result = subprocess.run(
                    ['systemctl', 'is-active', service_id],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                status = result.stdout.strip()
                return {
                    'name': service_name,
                    'type': 'host',
                    'status': status,
                    'running': status == 'active',
                }
        except:
            pass
        
        return None
    
    def _get_uptime(self) -> float:
        """Get system uptime in seconds"""
        try:
            return psutil.boot_time()
        except:
            return 0
