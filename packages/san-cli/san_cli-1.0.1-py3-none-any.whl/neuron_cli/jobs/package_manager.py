"""Package Manager - installs and manages MESH packages"""

import os
import subprocess
import yaml
import shutil
import tempfile
import tarfile
from pathlib import Path
from typing import Dict, Any, Optional, List
import requests

from ..core.logger import logger

# Package Store API Configuration
PACKAGE_STORE_API = os.getenv(
    'PACKAGE_STORE_API',
    'https://api.support.nexuscore.cloud/api/v1/packages'
)
PACKAGE_STORE_TOKEN = os.getenv('NEXUSCORE_API_KEY', '')


class PackageManager:
    """Manages MESH packages installation and execution"""
    
    def __init__(self):
        self.packages_dir = Path.home() / ".neuron" / "packages"
        self.packages_dir.mkdir(parents=True, exist_ok=True)
        self.installed_packages: Dict[str, Dict[str, Any]] = {}
        self._load_installed_packages()
    
    def install_package(
        self, 
        package_name: str, 
        version: str = "latest",
        config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Install a package from the Package Store"""
        logger.info(f"📦 Installing package: {package_name} v{version}")
        
        package_dir = self.packages_dir / package_name
        
        # Check if already installed
        if package_dir.exists():
            logger.info(f"⚠️  Package already installed, reinstalling...")
            shutil.rmtree(package_dir)
        
        package_dir.mkdir(parents=True, exist_ok=True)
        
        # Download package from store
        package_file = self._download_package_file(package_name, version)
        
        if not package_file:
            logger.error(f"❌ Failed to download package: {package_name}")
            return {
                "package": package_name,
                "status": "failed",
                "error": "Download failed"
            }
        
        # Extract package
        logger.info(f"📂 Extracting package to {package_dir}...")
        try:
            with tarfile.open(package_file, 'r:gz') as tar:
                tar.extractall(path=package_dir)
        except Exception as e:
            logger.error(f"❌ Failed to extract package: {e}")
            return {
                "package": package_name,
                "status": "failed",
                "error": str(e)
            }
        finally:
            # Clean up downloaded file
            if package_file.exists():
                package_file.unlink()
        
        # Load manifest
        manifest_path = package_dir / "package.yaml"
        if not manifest_path.exists():
            logger.error(f"❌ No package.yaml found in package")
            return {
                "package": package_name,
                "status": "failed",
                "error": "Missing package.yaml"
            }
        
        with open(manifest_path, 'r') as f:
            manifest = yaml.safe_load(f)
        
        # Run installation steps
        install_result = self._run_install_steps(package_name, manifest, config)
        
        # Mark as installed
        import time
        self.installed_packages[package_name] = {
            "version": manifest.get('version', version),
            "installed_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "manifest": manifest,
            "config": config or {}
        }
        self._save_installed_packages()
        
        logger.info(f"✅ Package installed: {package_name}")
        
        return {
            "package": package_name,
            "version": manifest.get('version', version),
            "status": "installed",
            "install_result": install_result
        }
    
    def start_package(
        self, 
        package_name: str,
        config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Start a package"""
        logger.info(f"▶️  Starting package: {package_name}")
        
        if package_name not in self.installed_packages:
            raise ValueError(f"Package not installed: {package_name}")
        
        package_info = self.installed_packages[package_name]
        manifest = package_info["manifest"]
        
        # Get execution command
        exec_cmd = manifest.get("execution", {}).get("command")
        if not exec_cmd:
            raise ValueError(f"No execution command defined for {package_name}")
        
        # Run in background
        package_dir = self.packages_dir / package_name
        log_file = package_dir / "output.log"
        
        # Replace config placeholders
        if config:
            for key, value in config.items():
                exec_cmd = exec_cmd.replace(f"${{{key}}}", str(value))
        
        logger.info(f"🚀 Running: {exec_cmd}")
        
        # Start process in background
        with open(log_file, 'w') as f:
            process = subprocess.Popen(
                exec_cmd,
                shell=True,
                cwd=package_dir,
                stdout=f,
                stderr=subprocess.STDOUT,
                start_new_session=True
            )
        
        # Save PID
        pid_file = package_dir / "process.pid"
        with open(pid_file, 'w') as f:
            f.write(str(process.pid))
        
        logger.info(f"✅ Package started with PID: {process.pid}")
        
        return {
            "package": package_name,
            "status": "running",
            "pid": process.pid,
            "log_file": str(log_file)
        }
    
    def stop_package(self, package_name: str) -> Dict[str, Any]:
        """Stop a package"""
        logger.info(f"⏹️  Stopping package: {package_name}")
        
        if package_name not in self.installed_packages:
            raise ValueError(f"Package not installed: {package_name}")
        
        package_dir = self.packages_dir / package_name
        pid_file = package_dir / "process.pid"
        
        if not pid_file.exists():
            logger.warning(f"⚠️  No PID file found, package may not be running")
            return {"package": package_name, "status": "not_running"}
        
        # Read PID and kill process
        with open(pid_file, 'r') as f:
            pid = int(f.read().strip())
        
        try:
            os.kill(pid, 15)  # SIGTERM
            logger.info(f"✅ Package stopped (PID: {pid})")
            pid_file.unlink()
            
            return {
                "package": package_name,
                "status": "stopped",
                "pid": pid
            }
        except ProcessLookupError:
            logger.warning(f"⚠️  Process not found (PID: {pid})")
            pid_file.unlink()
            return {"package": package_name, "status": "not_running"}
    
    def uninstall_package(self, package_name: str) -> Dict[str, Any]:
        """Uninstall a package"""
        logger.info(f"🗑️  Uninstalling package: {package_name}")
        
        # Stop if running
        try:
            self.stop_package(package_name)
        except:
            pass
        
        # Remove package directory
        package_dir = self.packages_dir / package_name
        if package_dir.exists():
            shutil.rmtree(package_dir)
        
        # Remove from installed packages
        if package_name in self.installed_packages:
            del self.installed_packages[package_name]
            self._save_installed_packages()
        
        logger.info(f"✅ Package uninstalled: {package_name}")
        
        return {
            "package": package_name,
            "status": "uninstalled"
        }
    
    def run_custom_action(
        self, 
        package_name: str,
        args: Dict[str, Any],
        config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Run a custom action"""
        logger.info(f"⚡ Running custom action for: {package_name}")
        
        if package_name not in self.installed_packages:
            raise ValueError(f"Package not installed: {package_name}")
        
        # For now, just log the action
        logger.info(f"   Args: {args}")
        logger.info(f"   Config: {config}")
        
        return {
            "package": package_name,
            "action": "custom",
            "status": "completed",
            "args": args,
            "config": config
        }
    
    def list_available_packages(self) -> List[Dict[str, Any]]:
        """List all available packages from the store"""
        try:
            logger.info("📦 Fetching available packages...")
            response = requests.get(PACKAGE_STORE_API, timeout=10)
            response.raise_for_status()
            
            # Debug: print response
            logger.info(f"Response status: {response.status_code}")
            logger.info(f"Response length: {len(response.text)} bytes")
            
            data = response.json()
            packages = data.get('packages', [])
            
            logger.info(f"✅ Found {len(packages)} available packages")
            return packages
        except requests.exceptions.JSONDecodeError as e:
            logger.error(f"❌ Failed to parse JSON response: {e}")
            logger.error(f"Response text: {response.text[:200]}")
            return []
        except Exception as e:
            logger.error(f"❌ Failed to list packages: {e}")
            return []
    
    def get_package_info(self, package_name: str) -> Optional[Dict[str, Any]]:
        """Get package information from the store"""
        try:
            logger.info(f"📄 Fetching package info: {package_name}")
            response = requests.get(f"{PACKAGE_STORE_API}/{package_name}", timeout=10)
            response.raise_for_status()
            
            data = response.json()
            return data.get('package')
        except Exception as e:
            logger.error(f"❌ Failed to get package info: {e}")
            return None
    
    def _download_package_file(
        self,
        package_name: str,
        version: str = "latest"
    ) -> Optional[Path]:
        """Download package tarball from the store"""
        try:
            logger.info(f"⬇️  Downloading {package_name} v{version}...")
            
            # Check for API token
            if not PACKAGE_STORE_TOKEN:
                logger.warning("⚠️  No API token found, set NEXUSCORE_API_KEY environment variable")
                return None
            
            # Download package
            url = f"{PACKAGE_STORE_API}/{package_name}/download"
            if version != "latest":
                url += f"?version={version}"
            
            headers = {'Authorization': f'Bearer {PACKAGE_STORE_TOKEN}'}
            response = requests.get(url, headers=headers, stream=True, timeout=60)
            response.raise_for_status()
            
            # Save to temporary file
            temp_file = Path(tempfile.gettempdir()) / f"{package_name}-{version}.tar.gz"
            
            # Download with progress
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(temp_file, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            progress = (downloaded / total_size) * 100
                            logger.info(f"   Progress: {progress:.1f}%")
            
            logger.info(f"✅ Downloaded {downloaded} bytes")
            return temp_file
            
        except Exception as e:
            logger.error(f"❌ Failed to download package: {e}")
            return None
    
    def _create_demo_manifest(self, package_name: str, version: str) -> Dict[str, Any]:
        """Create a demo manifest for testing"""
        return {
            "name": package_name,
            "version": version,
            "description": f"Demo package: {package_name}",
            "author": "NexusCore",
            "installation": {
                "steps": [
                    f"echo 'Installing {package_name} v{version}'",
                    "echo 'Installation complete'"
                ]
            },
            "execution": {
                "command": f"echo 'Running {package_name}' && sleep 5"
            }
        }
    
    def _run_install_steps(
        self, 
        package_name: str,
        manifest: Dict[str, Any],
        config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Run installation steps from manifest"""
        steps = manifest.get("installation", {}).get("steps", [])
        
        if not steps:
            logger.info("ℹ️  No installation steps defined")
            return {"status": "no_steps"}
        
        package_dir = self.packages_dir / package_name
        results = []
        
        for i, step in enumerate(steps, 1):
            logger.info(f"   Step {i}/{len(steps)}: {step[:60]}...")
            
            try:
                # Replace config placeholders
                if config:
                    for key, value in config.items():
                        step = step.replace(f"${{{key}}}", str(value))
                
                result = subprocess.run(
                    step,
                    shell=True,
                    cwd=package_dir,
                    capture_output=True,
                    text=True,
                    timeout=300  # 5 minute timeout per step
                )
                
                results.append({
                    "step": i,
                    "command": step,
                    "exit_code": result.returncode,
                    "stdout": result.stdout[:500],  # Limit output
                    "stderr": result.stderr[:500]
                })
                
                if result.returncode != 0:
                    logger.warning(f"⚠️  Step {i} failed with exit code {result.returncode}")
                    logger.warning(f"   stderr: {result.stderr[:200]}")
                else:
                    logger.info(f"   ✅ Step {i} completed")
                    
            except subprocess.TimeoutExpired:
                logger.error(f"❌ Step {i} timed out")
                results.append({
                    "step": i,
                    "command": step,
                    "error": "timeout"
                })
            except Exception as e:
                logger.error(f"❌ Step {i} failed: {e}")
                results.append({
                    "step": i,
                    "command": step,
                    "error": str(e)
                })
        
        return {
            "total_steps": len(steps),
            "results": results
        }
    
    def _load_installed_packages(self) -> None:
        """Load installed packages from disk"""
        registry_file = self.packages_dir / "registry.json"
        if registry_file.exists():
            import json
            with open(registry_file, 'r') as f:
                self.installed_packages = json.load(f)
    
    def _save_installed_packages(self) -> None:
        """Save installed packages to disk"""
        registry_file = self.packages_dir / "registry.json"
        import json
        with open(registry_file, 'w') as f:
            json.dump(self.installed_packages, f, indent=2)
