"""Ollama model management"""

import subprocess
import json
from typing import List, Dict, Optional
from ..core.logger import logger


class OllamaManager:
    """Manage Ollama models and operations"""
    
    def __init__(self, host: str = "http://localhost:11434"):
        self.host = host
    
    def list_models(self) -> List[Dict]:
        """List installed models"""
        try:
            result = subprocess.run(
                ['ollama', 'list'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                logger.error(f"Failed to list models: {result.stderr}")
                return []
            
            # Parse output
            models = []
            lines = result.stdout.strip().split('\n')
            
            # Skip header line
            for line in lines[1:]:
                if not line.strip():
                    continue
                
                parts = line.split()
                if len(parts) >= 3:
                    models.append({
                        'name': parts[0],
                        'id': parts[1] if len(parts) > 1 else '',
                        'size': parts[2] if len(parts) > 2 else '',
                        'modified': ' '.join(parts[3:]) if len(parts) > 3 else '',
                    })
            
            return models
        except Exception as e:
            logger.error(f"Error listing models: {e}")
            return []
    
    def pull_model(self, model_name: str) -> bool:
        """Pull a model from Ollama registry"""
        try:
            logger.info(f"📥 Pulling model: {model_name}")
            logger.info("   This may take a few minutes...")
            
            # Run ollama pull with real-time output
            process = subprocess.Popen(
                ['ollama', 'pull', model_name],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            
            # Stream output
            for line in process.stdout:
                print(f"   {line.rstrip()}")
            
            process.wait()
            
            if process.returncode == 0:
                logger.info(f"✅ Model {model_name} pulled successfully")
                return True
            else:
                logger.error(f"❌ Failed to pull model {model_name}")
                return False
                
        except Exception as e:
            logger.error(f"Error pulling model: {e}")
            return False
    
    def remove_model(self, model_name: str) -> bool:
        """Remove a model"""
        try:
            logger.info(f"🗑️  Removing model: {model_name}")
            
            result = subprocess.run(
                ['ollama', 'rm', model_name],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                logger.info(f"✅ Model {model_name} removed")
                return True
            else:
                logger.error(f"❌ Failed to remove model: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Error removing model: {e}")
            return False
    
    def show_model(self, model_name: str) -> Optional[Dict]:
        """Show model information"""
        try:
            result = subprocess.run(
                ['ollama', 'show', model_name],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                # Parse the output
                info = {}
                current_section = None
                
                for line in result.stdout.split('\n'):
                    line = line.strip()
                    if not line:
                        continue
                    
                    if line.endswith(':'):
                        current_section = line[:-1].lower()
                        info[current_section] = []
                    elif current_section:
                        info[current_section].append(line)
                    else:
                        # Key-value pair
                        if ':' in line:
                            key, value = line.split(':', 1)
                            info[key.strip().lower()] = value.strip()
                
                return info
            
            return None
        except Exception as e:
            logger.error(f"Error showing model: {e}")
            return None
    
    def list_running(self) -> List[Dict]:
        """List running models"""
        try:
            result = subprocess.run(
                ['ollama', 'ps'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                return []
            
            # Parse output
            models = []
            lines = result.stdout.strip().split('\n')
            
            # Skip header
            for line in lines[1:]:
                if not line.strip():
                    continue
                
                parts = line.split()
                if len(parts) >= 4:
                    models.append({
                        'name': parts[0],
                        'id': parts[1],
                        'size': parts[2],
                        'processor': parts[3],
                        'until': ' '.join(parts[4:]) if len(parts) > 4 else '',
                    })
            
            return models
        except Exception as e:
            logger.error(f"Error listing running models: {e}")
            return []
    
    def run_model(self, model_name: str, prompt: Optional[str] = None) -> bool:
        """Run a model interactively or with a prompt"""
        try:
            if prompt:
                # Run with prompt
                result = subprocess.run(
                    ['ollama', 'run', model_name, prompt],
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                
                if result.returncode == 0:
                    print(result.stdout)
                    return True
                else:
                    logger.error(f"Error: {result.stderr}")
                    return False
            else:
                # Interactive mode
                logger.info(f"🤖 Starting interactive session with {model_name}")
                logger.info("   Type your messages and press Enter")
                logger.info("   Press Ctrl+C to exit\n")
                
                subprocess.run(['ollama', 'run', model_name])
                return True
                
        except KeyboardInterrupt:
            logger.info("\n👋 Exiting interactive session")
            return True
        except Exception as e:
            logger.error(f"Error running model: {e}")
            return False
    
    def copy_model(self, source: str, destination: str) -> bool:
        """Copy a model"""
        try:
            logger.info(f"📋 Copying model: {source} → {destination}")
            
            result = subprocess.run(
                ['ollama', 'cp', source, destination],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                logger.info(f"✅ Model copied successfully")
                return True
            else:
                logger.error(f"❌ Failed to copy model: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Error copying model: {e}")
            return False
    
    def get_model_size(self, model_name: str) -> Optional[str]:
        """Get model size"""
        models = self.list_models()
        for model in models:
            if model['name'] == model_name:
                return model.get('size')
        return None
    
    def is_model_installed(self, model_name: str) -> bool:
        """Check if a model is installed"""
        models = self.list_models()
        return any(m['name'] == model_name for m in models)
    
    def get_recommended_models(self) -> List[Dict]:
        """Get list of recommended models"""
        return [
            {
                'name': 'llama3.2:3b',
                'size': '2.0GB',
                'description': 'Latest Llama 3.2 (3B parameters)',
                'speed': 'Fast',
                'quality': 'Good',
                'recommended': True,
            },
            {
                'name': 'llama3.1:8b',
                'size': '4.7GB',
                'description': 'Llama 3.1 (8B parameters)',
                'speed': 'Medium',
                'quality': 'Very Good',
                'recommended': True,
            },
            {
                'name': 'phi3:mini',
                'size': '2.3GB',
                'description': 'Microsoft Phi-3 Mini',
                'speed': 'Fast',
                'quality': 'Good',
                'recommended': False,
            },
            {
                'name': 'phi2:2.7b',
                'size': '1.7GB',
                'description': 'Microsoft Phi-2',
                'speed': 'Very Fast',
                'quality': 'Good',
                'recommended': True,
            },
            {
                'name': 'mistral:7b',
                'size': '4.1GB',
                'description': 'Mistral 7B',
                'speed': 'Medium',
                'quality': 'Very Good',
                'recommended': False,
            },
            {
                'name': 'codellama:7b',
                'size': '3.8GB',
                'description': 'Code Llama (7B)',
                'speed': 'Medium',
                'quality': 'Very Good (Code)',
                'recommended': False,
            },
        ]
