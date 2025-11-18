"""Host service installation (Ollama, Whisper)"""

import subprocess
import os
import shutil
from typing import Dict
from ..core.logger import logger


class HostServiceInstaller:
    """Install services that run directly on host (for GPU access)"""
    
    def __init__(self, os_type: str):
        self.os_type = os_type
    
    def install_ollama(self, gpu_info: Dict) -> Dict:
        """Install Ollama on host"""
        logger.info("🤖 Installing Ollama...")
        
        try:
            # Step 1: Download Ollama binary
            logger.info("   Downloading Ollama...")
            if not self._download_ollama():
                return {'success': False, 'error': 'Failed to download Ollama'}
            
            # Step 2: Create service
            logger.info("   Creating service...")
            if not self._create_ollama_service(gpu_info):
                return {'success': False, 'error': 'Failed to create service'}
            
            # Step 3: Start service
            logger.info("   Starting service...")
            if not self._start_ollama_service():
                return {'success': False, 'error': 'Failed to start service'}
            
            # Step 4: Verify service
            logger.info("   Verifying service...")
            if not self._verify_ollama():
                return {'success': False, 'error': 'Service not responding'}
            
            logger.info("   ✅ Ollama installed successfully")
            return {
                'success': True,
                'port': 11434,
                'gpu_enabled': gpu_info.get('available', False),
                'gpu_type': gpu_info.get('type', 'none'),
            }
        
        except Exception as e:
            logger.error(f"   ❌ Installation failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def install_whisper(self, python_path: str = 'python3.12') -> Dict:
        """Install Whisper transcription service"""
        logger.info("🎤 Installing Whisper...")
        
        try:
            venv_dir = '/opt/whisper-service/venv'
            app_file = '/opt/whisper-service/app.py'
            
            # Step 1: Create directory
            logger.info("   Creating directory...")
            os.makedirs('/opt/whisper-service', exist_ok=True)
            
            # Step 2: Create Python venv
            logger.info("   Creating Python virtual environment...")
            if not self._create_python_venv(venv_dir, python_path):
                return {'success': False, 'error': 'Failed to create venv'}
            
            # Step 3: Install dependencies
            logger.info("   Installing dependencies...")
            if not self._install_whisper_dependencies(venv_dir):
                return {'success': False, 'error': 'Failed to install dependencies'}
            
            # Step 4: Create app.py
            logger.info("   Creating application...")
            if not self._create_whisper_app(app_file):
                return {'success': False, 'error': 'Failed to create app'}
            
            # Step 5: Create service
            logger.info("   Creating service...")
            if not self._create_whisper_service(venv_dir):
                return {'success': False, 'error': 'Failed to create service'}
            
            # Step 6: Start service
            logger.info("   Starting service...")
            if not self._start_whisper_service():
                return {'success': False, 'error': 'Failed to start service'}
            
            logger.info("   ✅ Whisper installed successfully")
            return {
                'success': True,
                'port': 8026,
                'venv': venv_dir,
            }
        
        except Exception as e:
            logger.error(f"   ❌ Installation failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def _download_ollama(self) -> bool:
        """Download Ollama binary"""
        try:
            if self.os_type == 'darwin':
                # macOS
                arch = 'arm64' if os.uname().machine in ['arm64', 'aarch64'] else 'amd64'
                url = f'https://ollama.ai/download/ollama-darwin-{arch}'
                install_path = '/usr/local/bin/ollama'
            elif self.os_type == 'linux':
                # Linux
                url = 'https://ollama.ai/download/ollama-linux-amd64'
                install_path = '/usr/local/bin/ollama'
            else:
                return False
            
            # Download
            result = subprocess.run(
                ['curl', '-fsSL', url, '-o', '/tmp/ollama'],
                capture_output=True,
                timeout=300
            )
            
            if result.returncode != 0:
                return False
            
            # Make executable and move
            subprocess.run(['chmod', '+x', '/tmp/ollama'], check=True)
            subprocess.run(['sudo', 'mv', '/tmp/ollama', install_path], check=True)
            
            return True
        except:
            return False
    
    def _create_ollama_service(self, gpu_info: Dict) -> bool:
        """Create Ollama service (launchd or systemd)"""
        try:
            if self.os_type == 'darwin':
                # macOS launchd
                plist_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.ollama.server</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/local/bin/ollama</string>
        <string>serve</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/tmp/ollama.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/ollama.error.log</string>
</dict>
</plist>'''
                
                plist_path = '/Library/LaunchDaemons/com.ollama.server.plist'
                with open('/tmp/ollama.plist', 'w') as f:
                    f.write(plist_content)
                
                subprocess.run(['sudo', 'mv', '/tmp/ollama.plist', plist_path], check=True)
                subprocess.run(['sudo', 'chown', 'root:wheel', plist_path], check=True)
                
            elif self.os_type == 'linux':
                # Linux systemd
                service_content = f'''[Unit]
Description=Ollama Service
After=network.target

[Service]
Type=simple
ExecStart=/usr/local/bin/ollama serve
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target'''
                
                service_path = '/etc/systemd/system/ollama.service'
                with open('/tmp/ollama.service', 'w') as f:
                    f.write(service_content)
                
                subprocess.run(['sudo', 'mv', '/tmp/ollama.service', service_path], check=True)
                subprocess.run(['sudo', 'systemctl', 'daemon-reload'], check=True)
            
            return True
        except:
            return False
    
    def _start_ollama_service(self) -> bool:
        """Start Ollama service"""
        try:
            if self.os_type == 'darwin':
                subprocess.run(['sudo', 'launchctl', 'load', '/Library/LaunchDaemons/com.ollama.server.plist'], check=True)
            elif self.os_type == 'linux':
                subprocess.run(['sudo', 'systemctl', 'enable', 'ollama'], check=True)
                subprocess.run(['sudo', 'systemctl', 'start', 'ollama'], check=True)
            return True
        except:
            return False
    
    def _verify_ollama(self) -> bool:
        """Verify Ollama is running"""
        try:
            import time
            time.sleep(3)  # Give it time to start
            
            result = subprocess.run(
                ['curl', '-s', 'http://localhost:11434/api/tags'],
                capture_output=True,
                timeout=10
            )
            return result.returncode == 0
        except:
            return False
    
    def _create_python_venv(self, venv_dir: str, python_path: str) -> bool:
        """Create Python virtual environment"""
        try:
            # Remove existing venv
            if os.path.exists(venv_dir):
                shutil.rmtree(venv_dir)
            
            # Create new venv
            result = subprocess.run(
                [python_path, '-m', 'venv', venv_dir],
                capture_output=True,
                timeout=60
            )
            
            return result.returncode == 0
        except:
            return False
    
    def _install_whisper_dependencies(self, venv_dir: str) -> bool:
        """Install Whisper dependencies in venv"""
        try:
            pip_path = f'{venv_dir}/bin/pip'
            
            # Upgrade pip
            subprocess.run([pip_path, 'install', '--upgrade', 'pip'], check=True, capture_output=True, timeout=60)
            
            # Install dependencies
            subprocess.run([pip_path, 'install', 'faster-whisper', 'flask', 'requests'], check=True, capture_output=True, timeout=300)
            
            return True
        except:
            return False
    
    def _create_whisper_app(self, app_file: str) -> bool:
        """Create Whisper Flask app"""
        app_content = '''#!/usr/bin/env python3
"""Whisper Transcription Service"""

import os
from flask import Flask, request, jsonify
from faster_whisper import WhisperModel

app = Flask(__name__)

# Initialize model
model_size = os.getenv("WHISPER_MODEL", "base")
model = WhisperModel(model_size, device="auto", compute_type="auto")

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy", "model": model_size})

@app.route('/transcribe', methods=['POST'])
def transcribe():
    try:
        data = request.json
        audio_url = data.get('audio_url')
        
        if not audio_url:
            return jsonify({"error": "audio_url required"}), 400
        
        # Download audio
        import requests
        import tempfile
        
        response = requests.get(audio_url)
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as f:
            f.write(response.content)
            audio_file = f.name
        
        # Transcribe
        segments, info = model.transcribe(audio_file, beam_size=5)
        
        text = " ".join([segment.text for segment in segments])
        
        # Cleanup
        os.unlink(audio_file)
        
        return jsonify({
            "text": text,
            "language": info.language,
            "duration": info.duration
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.getenv("PORT", 8026))
    app.run(host='0.0.0.0', port=port)
'''
        
        try:
            with open(app_file, 'w') as f:
                f.write(app_content)
            
            os.chmod(app_file, 0o755)
            return True
        except:
            return False
    
    def _create_whisper_service(self, venv_dir: str) -> bool:
        """Create Whisper service"""
        try:
            python_path = f'{venv_dir}/bin/python3'
            
            if self.os_type == 'darwin':
                # macOS launchd
                plist_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.nexuscore.whisper</string>
    <key>ProgramArguments</key>
    <array>
        <string>{python_path}</string>
        <string>/opt/whisper-service/app.py</string>
    </array>
    <key>EnvironmentVariables</key>
    <dict>
        <key>PORT</key>
        <string>8026</string>
        <key>WHISPER_MODEL</key>
        <string>base</string>
    </dict>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/tmp/whisper.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/whisper.error.log</string>
</dict>
</plist>'''
                
                plist_path = '/Library/LaunchDaemons/com.nexuscore.whisper.plist'
                with open('/tmp/whisper.plist', 'w') as f:
                    f.write(plist_content)
                
                subprocess.run(['sudo', 'mv', '/tmp/whisper.plist', plist_path], check=True)
                subprocess.run(['sudo', 'chown', 'root:wheel', plist_path], check=True)
                
            elif self.os_type == 'linux':
                # Linux systemd
                service_content = f'''[Unit]
Description=Whisper Transcription Service
After=network.target

[Service]
Type=simple
ExecStart={python_path} /opt/whisper-service/app.py
Environment="PORT=8026"
Environment="WHISPER_MODEL=base"
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target'''
                
                service_path = '/etc/systemd/system/whisper-service.service'
                with open('/tmp/whisper.service', 'w') as f:
                    f.write(service_content)
                
                subprocess.run(['sudo', 'mv', '/tmp/whisper.service', service_path], check=True)
                subprocess.run(['sudo', 'systemctl', 'daemon-reload'], check=True)
            
            return True
        except:
            return False
    
    def _start_whisper_service(self) -> bool:
        """Start Whisper service"""
        try:
            if self.os_type == 'darwin':
                subprocess.run(['sudo', 'launchctl', 'load', '/Library/LaunchDaemons/com.nexuscore.whisper.plist'], check=True)
            elif self.os_type == 'linux':
                subprocess.run(['sudo', 'systemctl', 'enable', 'whisper-service'], check=True)
                subprocess.run(['sudo', 'systemctl', 'start', 'whisper-service'], check=True)
            return True
        except:
            return False
