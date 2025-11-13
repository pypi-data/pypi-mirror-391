#!/usr/bin/env python3
"""
Neuron CLI - Usage Metering System
Tracks billable usage on deployed devices for accurate billing
"""

import json
import time
import psutil
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import requests


class UsageMeter:
    """
    Tracks all billable usage on the device:
    - Network traffic (upload/download)
    - Job execution time
    - CPU hours consumed
    - Storage used
    - Package installations
    - API calls made
    """
    
    def __init__(self, config_path: str = "~/.neuron/config.json"):
        self.config_path = Path(config_path).expanduser()
        self.config = self._load_config()
        self.db_path = Path("~/.neuron/usage.db").expanduser()
        self._init_database()
        
        # Track network baseline
        self.network_baseline = self._get_network_stats()
        self.last_sync = time.time()
        
    def _load_config(self) -> dict:
        """Load Neuron CLI configuration"""
        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                return json.load(f)
        return {}
    
    def _init_database(self):
        """Initialize local usage tracking database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Network usage table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS network_usage (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp INTEGER,
                bytes_sent INTEGER,
                bytes_received INTEGER,
                synced BOOLEAN DEFAULT 0
            )
        """)
        
        # Job execution table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS job_usage (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_id TEXT,
                package TEXT,
                started_at INTEGER,
                completed_at INTEGER,
                duration_seconds REAL,
                cpu_cores_used INTEGER,
                cpu_hours REAL,
                memory_mb_avg REAL,
                exit_code INTEGER,
                synced BOOLEAN DEFAULT 0
            )
        """)
        
        # Storage usage table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS storage_usage (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp INTEGER,
                total_gb REAL,
                used_gb REAL,
                packages_gb REAL,
                logs_gb REAL,
                synced BOOLEAN DEFAULT 0
            )
        """)
        
        # API calls table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS api_usage (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp INTEGER,
                endpoint TEXT,
                method TEXT,
                status_code INTEGER,
                response_size_bytes INTEGER,
                synced BOOLEAN DEFAULT 0
            )
        """)
        
        # Package installations table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS package_usage (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp INTEGER,
                package_name TEXT,
                version TEXT,
                action TEXT,
                size_mb REAL,
                synced BOOLEAN DEFAULT 0
            )
        """)
        
        # Billing summary table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS billing_summary (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                period_start INTEGER,
                period_end INTEGER,
                network_gb REAL,
                cpu_hours REAL,
                storage_gb_hours REAL,
                job_count INTEGER,
                api_calls INTEGER,
                estimated_cost REAL,
                synced BOOLEAN DEFAULT 0
            )
        """)
        
        conn.commit()
        conn.close()
    
    def _get_network_stats(self) -> Dict:
        """Get current network statistics"""
        net = psutil.net_io_counters()
        return {
            'bytes_sent': net.bytes_sent,
            'bytes_received': net.bytes_recv,
            'timestamp': time.time()
        }
    
    def track_network_usage(self):
        """Track network usage since last check"""
        current = self._get_network_stats()
        
        bytes_sent = current['bytes_sent'] - self.network_baseline['bytes_sent']
        bytes_received = current['bytes_received'] - self.network_baseline['bytes_received']
        
        # Only track if significant usage (> 1KB to avoid noise)
        if bytes_sent > 1024 or bytes_received > 1024:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO network_usage (timestamp, bytes_sent, bytes_received)
                VALUES (?, ?, ?)
            """, (int(time.time()), bytes_sent, bytes_received))
            conn.commit()
            conn.close()
        
        # Update baseline
        self.network_baseline = current
    
    def track_job_execution(self, job_id: str, package: str, started_at: float, 
                           completed_at: float, cpu_cores: int, 
                           memory_mb_avg: float, exit_code: int):
        """Track job execution for billing"""
        duration = completed_at - started_at
        cpu_hours = (duration / 3600) * cpu_cores
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO job_usage (
                job_id, package, started_at, completed_at, 
                duration_seconds, cpu_cores_used, cpu_hours, 
                memory_mb_avg, exit_code
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (job_id, package, int(started_at), int(completed_at), 
              duration, cpu_cores, cpu_hours, memory_mb_avg, exit_code))
        conn.commit()
        conn.close()
    
    def track_storage_usage(self):
        """Track storage usage"""
        disk = psutil.disk_usage('/')
        
        # Calculate package storage
        packages_dir = Path("~/.neuron/packages").expanduser()
        packages_size = sum(f.stat().st_size for f in packages_dir.rglob('*') if f.is_file()) if packages_dir.exists() else 0
        
        # Calculate logs storage
        logs_dir = Path("~/.neuron/logs").expanduser()
        logs_size = sum(f.stat().st_size for f in logs_dir.rglob('*') if f.is_file()) if logs_dir.exists() else 0
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO storage_usage (
                timestamp, total_gb, used_gb, packages_gb, logs_gb
            ) VALUES (?, ?, ?, ?, ?)
        """, (
            int(time.time()),
            disk.total / (1024**3),
            disk.used / (1024**3),
            packages_size / (1024**3),
            logs_size / (1024**3)
        ))
        conn.commit()
        conn.close()
    
    def track_api_call(self, endpoint: str, method: str, 
                       status_code: int, response_size: int):
        """Track API calls for billing"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO api_usage (
                timestamp, endpoint, method, status_code, response_size_bytes
            ) VALUES (?, ?, ?, ?, ?)
        """, (int(time.time()), endpoint, method, status_code, response_size))
        conn.commit()
        conn.close()
    
    def track_package_installation(self, package_name: str, version: str, 
                                   action: str, size_mb: float):
        """Track package installations"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO package_usage (
                timestamp, package_name, version, action, size_mb
            ) VALUES (?, ?, ?, ?, ?)
        """, (int(time.time()), package_name, version, action, size_mb))
        conn.commit()
        conn.close()
    
    def calculate_period_usage(self, start_time: Optional[float] = None, 
                              end_time: Optional[float] = None) -> Dict:
        """Calculate usage for a billing period"""
        if start_time is None:
            # Default to current month
            now = datetime.now()
            start_time = datetime(now.year, now.month, 1).timestamp()
        
        if end_time is None:
            end_time = time.time()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Network usage (GB)
        cursor.execute("""
            SELECT 
                SUM(bytes_sent + bytes_received) / (1024.0 * 1024.0 * 1024.0) as total_gb
            FROM network_usage
            WHERE timestamp BETWEEN ? AND ?
        """, (start_time, end_time))
        network_gb = cursor.fetchone()[0] or 0.0
        
        # CPU hours
        cursor.execute("""
            SELECT SUM(cpu_hours) as total_cpu_hours
            FROM job_usage
            WHERE started_at BETWEEN ? AND ?
        """, (start_time, end_time))
        cpu_hours = cursor.fetchone()[0] or 0.0
        
        # Storage GB-hours (average storage * hours in period)
        cursor.execute("""
            SELECT AVG(used_gb) as avg_storage_gb
            FROM storage_usage
            WHERE timestamp BETWEEN ? AND ?
        """, (start_time, end_time))
        avg_storage_gb = cursor.fetchone()[0] or 0.0
        hours_in_period = (end_time - start_time) / 3600
        storage_gb_hours = avg_storage_gb * hours_in_period
        
        # Job count
        cursor.execute("""
            SELECT COUNT(*) as job_count
            FROM job_usage
            WHERE started_at BETWEEN ? AND ?
        """, (start_time, end_time))
        job_count = cursor.fetchone()[0] or 0
        
        # API calls
        cursor.execute("""
            SELECT COUNT(*) as api_calls
            FROM api_usage
            WHERE timestamp BETWEEN ? AND ?
        """, (start_time, end_time))
        api_calls = cursor.fetchone()[0] or 0
        
        conn.close()
        
        # Calculate estimated cost
        estimated_cost = self._calculate_cost(
            network_gb, cpu_hours, storage_gb_hours, job_count, api_calls
        )
        
        return {
            'period_start': start_time,
            'period_end': end_time,
            'network_gb': round(network_gb, 3),
            'cpu_hours': round(cpu_hours, 3),
            'storage_gb_hours': round(storage_gb_hours, 3),
            'job_count': job_count,
            'api_calls': api_calls,
            'estimated_cost': round(estimated_cost, 2)
        }
    
    def _calculate_cost(self, network_gb: float, cpu_hours: float, 
                       storage_gb_hours: float, job_count: int, 
                       api_calls: int) -> float:
        """
        Calculate estimated cost based on usage
        
        Pricing:
        - Network: $0.05/GB
        - CPU: $0.10/hour per core
        - Storage: $0.02/GB/month (730 hours)
        - Jobs: $0.01 per job
        - API calls: $0.0001 per call
        """
        network_cost = network_gb * 0.05
        cpu_cost = cpu_hours * 0.10
        storage_cost = (storage_gb_hours / 730) * 0.02  # Convert to monthly
        job_cost = job_count * 0.01
        api_cost = api_calls * 0.0001
        
        return network_cost + cpu_cost + storage_cost + job_cost + api_cost
    
    def sync_to_api(self) -> bool:
        """Sync usage data to API for billing"""
        api_url = self.config.get('api_url', 'https://api.support.nexuscore.cloud/api/v1')
        device_id = self.config.get('device_id')
        api_token = self.config.get('api_token')
        
        if not all([device_id, api_token]):
            return False
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get unsynced data
        cursor.execute("SELECT * FROM network_usage WHERE synced = 0 LIMIT 100")
        network_data = cursor.fetchall()
        
        cursor.execute("SELECT * FROM job_usage WHERE synced = 0 LIMIT 100")
        job_data = cursor.fetchall()
        
        cursor.execute("SELECT * FROM storage_usage WHERE synced = 0 LIMIT 100")
        storage_data = cursor.fetchall()
        
        cursor.execute("SELECT * FROM api_usage WHERE synced = 0 LIMIT 100")
        api_data = cursor.fetchall()
        
        cursor.execute("SELECT * FROM package_usage WHERE synced = 0 LIMIT 100")
        package_data = cursor.fetchall()
        
        # Prepare payload
        payload = {
            'device_id': device_id,
            'timestamp': int(time.time()),
            'usage_data': {
                'network': [
                    {
                        'timestamp': row[1],
                        'bytes_sent': row[2],
                        'bytes_received': row[3]
                    } for row in network_data
                ],
                'jobs': [
                    {
                        'job_id': row[1],
                        'package': row[2],
                        'started_at': row[3],
                        'completed_at': row[4],
                        'duration_seconds': row[5],
                        'cpu_cores_used': row[6],
                        'cpu_hours': row[7],
                        'memory_mb_avg': row[8],
                        'exit_code': row[9]
                    } for row in job_data
                ],
                'storage': [
                    {
                        'timestamp': row[1],
                        'total_gb': row[2],
                        'used_gb': row[3],
                        'packages_gb': row[4],
                        'logs_gb': row[5]
                    } for row in storage_data
                ],
                'api_calls': [
                    {
                        'timestamp': row[1],
                        'endpoint': row[2],
                        'method': row[3],
                        'status_code': row[4],
                        'response_size_bytes': row[5]
                    } for row in api_data
                ],
                'packages': [
                    {
                        'timestamp': row[1],
                        'package_name': row[2],
                        'version': row[3],
                        'action': row[4],
                        'size_mb': row[5]
                    } for row in package_data
                ]
            }
        }
        
        try:
            # Send to API
            response = requests.post(
                f"{api_url}/mesh/usage",
                json=payload,
                headers={'Authorization': f'Bearer {api_token}'},
                timeout=30
            )
            
            if response.status_code == 200:
                # Mark as synced
                cursor.execute("UPDATE network_usage SET synced = 1 WHERE synced = 0")
                cursor.execute("UPDATE job_usage SET synced = 1 WHERE synced = 0")
                cursor.execute("UPDATE storage_usage SET synced = 1 WHERE synced = 0")
                cursor.execute("UPDATE api_usage SET synced = 1 WHERE synced = 0")
                cursor.execute("UPDATE package_usage SET synced = 1 WHERE synced = 0")
                conn.commit()
                
                self.last_sync = time.time()
                return True
            
        except Exception as e:
            print(f"Failed to sync usage data: {e}")
        
        finally:
            conn.close()
        
        return False
    
    def get_current_month_summary(self) -> Dict:
        """Get usage summary for current month"""
        now = datetime.now()
        start_of_month = datetime(now.year, now.month, 1).timestamp()
        return self.calculate_period_usage(start_of_month)
    
    def get_usage_report(self, days: int = 30) -> Dict:
        """Get detailed usage report for last N days"""
        end_time = time.time()
        start_time = end_time - (days * 86400)
        
        usage = self.calculate_period_usage(start_time, end_time)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Top packages by CPU usage
        cursor.execute("""
            SELECT package, SUM(cpu_hours) as total_cpu_hours, COUNT(*) as job_count
            FROM job_usage
            WHERE started_at BETWEEN ? AND ?
            GROUP BY package
            ORDER BY total_cpu_hours DESC
            LIMIT 10
        """, (start_time, end_time))
        top_packages = [
            {'package': row[0], 'cpu_hours': row[1], 'job_count': row[2]}
            for row in cursor.fetchall()
        ]
        
        # Daily breakdown
        cursor.execute("""
            SELECT 
                DATE(started_at, 'unixepoch') as date,
                SUM(cpu_hours) as cpu_hours,
                COUNT(*) as job_count
            FROM job_usage
            WHERE started_at BETWEEN ? AND ?
            GROUP BY date
            ORDER BY date DESC
        """, (start_time, end_time))
        daily_breakdown = [
            {'date': row[0], 'cpu_hours': row[1], 'job_count': row[2]}
            for row in cursor.fetchall()
        ]
        
        conn.close()
        
        usage['top_packages'] = top_packages
        usage['daily_breakdown'] = daily_breakdown
        
        return usage


# Background usage tracking daemon
def run_usage_meter_daemon():
    """Run usage meter as background daemon"""
    meter = UsageMeter()
    
    print("🔍 Usage Meter started")
    print(f"📊 Tracking: Network, CPU, Storage, Jobs, API calls")
    
    while True:
        try:
            # Track network every 60 seconds
            meter.track_network_usage()
            
            # Track storage every 5 minutes
            if int(time.time()) % 300 == 0:
                meter.track_storage_usage()
            
            # Sync to API every 15 minutes
            if int(time.time()) % 900 == 0:
                if meter.sync_to_api():
                    print(f"✅ Usage data synced at {datetime.now()}")
                else:
                    print(f"⚠️  Failed to sync usage data")
            
            # Show monthly summary every hour
            if int(time.time()) % 3600 == 0:
                summary = meter.get_current_month_summary()
                print(f"\n📊 Monthly Usage Summary:")
                print(f"   Network: {summary['network_gb']:.2f} GB")
                print(f"   CPU: {summary['cpu_hours']:.2f} hours")
                print(f"   Jobs: {summary['job_count']}")
                print(f"   Estimated cost: ${summary['estimated_cost']:.2f}\n")
            
            time.sleep(60)
            
        except KeyboardInterrupt:
            print("\n👋 Usage Meter stopped")
            break
        except Exception as e:
            print(f"❌ Error in usage meter: {e}")
            time.sleep(60)


if __name__ == "__main__":
    run_usage_meter_daemon()
