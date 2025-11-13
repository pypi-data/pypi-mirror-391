"""Network monitor - Public IP, location, bandwidth tracking"""

import socket
import requests
from typing import Dict, Any, Optional
import time


class NetworkMonitor:
    """Monitors network connectivity and collects network data"""
    
    # Cache for location data (don't query too often)
    _location_cache = None
    _location_cache_time = 0
    _cache_ttl = 3600  # 1 hour
    
    @staticmethod
    def get_network_info() -> Dict[str, Any]:
        """Get complete network information"""
        return {
            "public_ip": NetworkMonitor.get_public_ip(),
            "location": NetworkMonitor.get_location(),
            "connectivity": NetworkMonitor.check_connectivity(),
            "bandwidth": NetworkMonitor.estimate_bandwidth(),
        }
    
    @staticmethod
    def get_public_ip() -> Optional[str]:
        """Get public IP address"""
        try:
            # Try multiple services for reliability
            services = [
                'https://api.ipify.org?format=json',
                'https://ifconfig.me/ip',
                'https://icanhazip.com',
            ]
            
            for service in services:
                try:
                    response = requests.get(service, timeout=5)
                    if response.status_code == 200:
                        if 'json' in service:
                            return response.json().get('ip')
                        else:
                            return response.text.strip()
                except:
                    continue
        except:
            pass
        return None
    
    @staticmethod
    def get_location() -> Dict[str, Any]:
        """Get geolocation based on IP address"""
        # Check cache
        current_time = time.time()
        if NetworkMonitor._location_cache and (current_time - NetworkMonitor._location_cache_time) < NetworkMonitor._cache_ttl:
            return NetworkMonitor._location_cache
        
        location = {
            "ip": None,
            "country": None,
            "country_code": None,
            "region": None,
            "city": None,
            "latitude": None,
            "longitude": None,
            "timezone": None,
            "isp": None,
        }
        
        try:
            # Use ipapi.co (free, no API key needed)
            response = requests.get('https://ipapi.co/json/', timeout=10)
            if response.status_code == 200:
                data = response.json()
                location.update({
                    "ip": data.get('ip'),
                    "country": data.get('country_name'),
                    "country_code": data.get('country_code'),
                    "region": data.get('region'),
                    "city": data.get('city'),
                    "latitude": data.get('latitude'),
                    "longitude": data.get('longitude'),
                    "timezone": data.get('timezone'),
                    "isp": data.get('org'),
                })
                
                # Cache the result
                NetworkMonitor._location_cache = location
                NetworkMonitor._location_cache_time = current_time
        except:
            pass
        
        return location
    
    @staticmethod
    def check_connectivity() -> Dict[str, Any]:
        """Check network connectivity to various services"""
        connectivity = {
            "internet": False,
            "api": False,
            "vpn": False,
            "dns": False,
        }
        
        # Check internet (Google DNS)
        try:
            socket.create_connection(("8.8.8.8", 53), timeout=3)
            connectivity["internet"] = True
        except:
            pass
        
        # Check DNS
        try:
            socket.gethostbyname("google.com")
            connectivity["dns"] = True
        except:
            pass
        
        # Check API
        try:
            response = requests.get(
                "https://api.support.nexuscore.cloud/api/v1/health",
                timeout=5
            )
            connectivity["api"] = response.status_code == 200
        except:
            pass
        
        # Check VPN
        try:
            socket.create_connection(("10.9.0.1", 8080), timeout=3)
            connectivity["vpn"] = True
        except:
            pass
        
        return connectivity
    
    @staticmethod
    def estimate_bandwidth() -> Dict[str, Any]:
        """Estimate network bandwidth (simple test)"""
        bandwidth = {
            "download_mbps": None,
            "upload_mbps": None,
            "latency_ms": None,
        }
        
        try:
            # Simple latency test
            start = time.time()
            response = requests.get("https://api.support.nexuscore.cloud/api/v1/health", timeout=5)
            latency = (time.time() - start) * 1000
            bandwidth["latency_ms"] = round(latency, 2)
            
            # Simple download test (1MB file)
            # Note: This is a rough estimate, not accurate bandwidth test
            # For production, use speedtest-cli or similar
            start = time.time()
            response = requests.get(
                "https://speed.cloudflare.com/__down?bytes=1000000",
                timeout=10
            )
            if response.status_code == 200:
                duration = time.time() - start
                bytes_downloaded = len(response.content)
                mbps = (bytes_downloaded * 8) / (duration * 1_000_000)
                bandwidth["download_mbps"] = round(mbps, 2)
        except:
            pass
        
        return bandwidth
    
    @staticmethod
    def track_bandwidth_usage(interval: int = 1) -> Dict[str, Any]:
        """Track bandwidth usage over interval"""
        import psutil
        
        # Get initial counters
        net_io_start = psutil.net_io_counters()
        time.sleep(interval)
        net_io_end = psutil.net_io_counters()
        
        # Calculate rates
        bytes_sent = net_io_end.bytes_sent - net_io_start.bytes_sent
        bytes_recv = net_io_end.bytes_recv - net_io_start.bytes_recv
        
        return {
            "interval_seconds": interval,
            "bytes_sent": bytes_sent,
            "bytes_recv": bytes_recv,
            "sent_mbps": round((bytes_sent * 8) / (interval * 1_000_000), 2),
            "recv_mbps": round((bytes_recv * 8) / (interval * 1_000_000), 2),
            "total_mbps": round(((bytes_sent + bytes_recv) * 8) / (interval * 1_000_000), 2),
        }
