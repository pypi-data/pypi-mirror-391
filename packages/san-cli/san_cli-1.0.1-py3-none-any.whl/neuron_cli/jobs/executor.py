"""Job Executor - polls and executes MESH jobs"""

import time
import json
from typing import Optional, Dict, Any
import requests
from datetime import datetime

from ..core.logger import logger
from .package_manager import PackageManager
from ..monitoring.job_metrics import JobMetrics


class JobExecutor:
    """Executes jobs from the MESH network"""
    
    def __init__(self, api_url: str, device_id: str, jwt_token: str):
        self.api_url = api_url
        self.device_id = device_id
        self.jwt_token = jwt_token
        self.package_manager = PackageManager()
        self.current_job: Optional[Dict[str, Any]] = None
        self.running = False
    
    def start_polling(self, interval: int = 30) -> None:
        """Start polling for jobs"""
        self.running = True
        logger.info(f"🔄 Job executor started (polling every {interval}s)")
        
        while self.running:
            try:
                job = self._poll_next_job()
                if job:
                    self._execute_job(job)
                time.sleep(interval)
            except KeyboardInterrupt:
                logger.info("\n⚠️  Job executor interrupted")
                self.running = False
            except Exception as e:
                logger.error(f"❌ Job polling error: {e}")
                time.sleep(interval)
    
    def stop_polling(self) -> None:
        """Stop polling for jobs"""
        self.running = False
        logger.info("🛑 Job executor stopped")
    
    def _poll_next_job(self) -> Optional[Dict[str, Any]]:
        """Poll for next job in queue"""
        try:
            url = f"{self.api_url}/mesh/jobs/next/{self.device_id}"
            headers = {
                "Authorization": f"Bearer {self.jwt_token}",
                "Content-Type": "application/json"
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                job = response.json()
                logger.info(f"📦 New job received: {job['job_id']}")
                logger.info(f"   Package: {job['package']} v{job['version']}")
                logger.info(f"   Action: {job['action']}")
                return job
            elif response.status_code == 204:
                # No jobs available
                logger.debug("💤 No jobs in queue")
                return None
            else:
                logger.warning(f"⚠️  Failed to poll jobs: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Job polling error: {e}")
            return None
    
    def _execute_job(self, job: Dict[str, Any]) -> None:
        """Execute a job"""
        job_id = job['job_id']
        package_name = job['package']
        package_version = job['version']
        action = job['action']
        config = job.get('config', {})
        args = job.get('args', {})
        
        logger.info("=" * 60)
        logger.info(f"🚀 Executing job: {job_id}")
        logger.info(f"   Package: {package_name} v{package_version}")
        logger.info(f"   Action: {action}")
        logger.info("=" * 60)
        
        self.current_job = job
        start_time = datetime.now()
        
        # Initialize job metrics for billing
        metrics = JobMetrics(job_id)
        metrics.start()
        
        # Update job status to running
        self._update_job_status(job_id, "running", {
            "message": f"Starting {action} for {package_name}"
        })
        
        try:
            # Execute action based on type
            if action == "install":
                result = self.package_manager.install_package(
                    package_name, package_version, config
                )
            elif action == "start":
                result = self.package_manager.start_package(
                    package_name, config
                )
            elif action == "stop":
                result = self.package_manager.stop_package(
                    package_name
                )
            elif action == "uninstall":
                result = self.package_manager.uninstall_package(
                    package_name
                )
            elif action == "execute":
                # Direct command execution with full log capture
                command = args.get("command")
                if not command:
                    raise ValueError("command required for execute action")
                
                result = self._execute_command(
                    command,
                    cwd=args.get("cwd", "/tmp"),
                    env=args.get("env", {}),
                    timeout=args.get("timeout", 300)
                )
            elif action == "custom":
                result = self.package_manager.run_custom_action(
                    package_name, args, config
                )
            else:
                raise ValueError(f"Unknown action: {action}")
            
            # Stop metrics collection
            final_metrics = metrics.stop()
            billing_data = metrics.get_billing_data()
            
            # Calculate duration
            duration = (datetime.now() - start_time).total_seconds()
            
            # Update job status to completed with metrics
            self._update_job_status(job_id, "completed", {
                "message": f"Successfully completed {action}",
                "result": result,
                "duration_seconds": duration,
                "metrics": final_metrics,
                "billing": billing_data,
            })
            
            logger.info(f"✅ Job completed successfully in {duration:.2f}s")
            
        except Exception as e:
            # Stop metrics even on failure
            final_metrics = metrics.stop()
            billing_data = metrics.get_billing_data()
            
            duration = (datetime.now() - start_time).total_seconds()
            error_msg = str(e)
            
            logger.error(f"❌ Job failed: {error_msg}")
            
            # Update job status to failed with metrics
            self._update_job_status(job_id, "failed", {
                "error": error_msg,
                "duration_seconds": duration,
                "metrics": final_metrics,
                "billing": billing_data,
            }, error=error_msg)
        
        finally:
            self.current_job = None
            logger.info("=" * 60)
    
    def _update_job_status(
        self, 
        job_id: str, 
        status: str, 
        output: Dict[str, Any],
        error: Optional[str] = None
    ) -> None:
        """Update job status on server"""
        try:
            url = f"{self.api_url}/mesh/jobs/{job_id}/status"
            headers = {
                "Authorization": f"Bearer {self.jwt_token}",
                "Content-Type": "application/json"
            }
            
            data = {
                "status": status,
                "output": output,
                "logs": getattr(self, '_captured_logs', ''),
                "cpu_usage": getattr(self, '_cpu_usage', 0),
                "memory_mb": getattr(self, '_memory_mb', 0)
            }
            
            if error:
                data["error"] = error
            
            response = requests.post(url, json=data, headers=headers, timeout=10)
            
            if response.status_code == 200:
                logger.debug(f"📊 Job status updated: {status}")
            else:
                logger.warning(f"⚠️  Failed to update job status: {response.status_code}")
                
        except Exception as e:
            logger.error(f"❌ Failed to update job status: {e}")
    
    def _execute_command(
        self,
        command: str,
        cwd: str = "/tmp",
        env: Optional[Dict[str, str]] = None,
        timeout: int = 300
    ) -> Dict[str, Any]:
        """Execute command and capture all output"""
        import subprocess
        import os
        
        logger.info(f"🔧 Executing command: {command[:100]}...")
        logger.info(f"   Working directory: {cwd}")
        logger.info(f"   Timeout: {timeout}s")
        
        # Merge environment
        full_env = os.environ.copy()
        if env:
            full_env.update(env)
            logger.info(f"   Environment variables: {list(env.keys())}")
        
        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=cwd,
                env=full_env,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            # Store logs for status update
            log_output = f"=== COMMAND ===\n{command}\n\n"
            log_output += f"=== EXIT CODE ===\n{result.returncode}\n\n"
            log_output += f"=== STDOUT ({len(result.stdout)} bytes) ===\n{result.stdout}\n\n"
            log_output += f"=== STDERR ({len(result.stderr)} bytes) ===\n{result.stderr}"
            
            self._captured_logs = log_output
            
            logger.info(f"✅ Command completed with exit code: {result.returncode}")
            if result.stdout:
                logger.info(f"   stdout: {len(result.stdout)} bytes")
            if result.stderr:
                logger.info(f"   stderr: {len(result.stderr)} bytes")
            
            return {
                "exit_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "success": result.returncode == 0,
                "command": command
            }
            
        except subprocess.TimeoutExpired as e:
            error_msg = f"Command timed out after {timeout}s"
            self._captured_logs = f"=== ERROR ===\n{error_msg}\n\n"
            logger.error(f"❌ {error_msg}")
            raise ValueError(error_msg)
            
        except Exception as e:
            error_msg = f"Command execution failed: {str(e)}"
            self._captured_logs = f"=== ERROR ===\n{error_msg}\n\n"
            logger.error(f"❌ {error_msg}")
            raise
