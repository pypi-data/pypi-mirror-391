"""Device scanner - USB, HDMI, displays, peripherals"""

import subprocess
import re
from typing import Dict, Any, List


class DeviceScanner:
    """Scans for connected devices (USB, HDMI, displays)"""
    
    @staticmethod
    def scan_all() -> Dict[str, Any]:
        """Scan all connected devices"""
        return {
            "usb": DeviceScanner.scan_usb(),
            "displays": DeviceScanner.scan_displays(),
            "hdmi": DeviceScanner.scan_hdmi(),
            "audio": DeviceScanner.scan_audio(),
        }
    
    @staticmethod
    def scan_usb() -> List[Dict[str, Any]]:
        """Scan USB devices"""
        devices = []
        
        try:
            # Try lsusb (Linux)
            result = subprocess.run(['lsusb'], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                for line in result.stdout.strip().split('\n'):
                    if line:
                        # Parse: Bus 001 Device 002: ID 8087:0024 Intel Corp. Integrated Rate Matching Hub
                        match = re.match(r'Bus (\d+) Device (\d+): ID ([0-9a-f:]+) (.+)', line)
                        if match:
                            devices.append({
                                "bus": match.group(1),
                                "device": match.group(2),
                                "id": match.group(3),
                                "name": match.group(4).strip(),
                                "type": "usb"
                            })
        except:
            pass
        
        # Try system_profiler (macOS)
        try:
            result = subprocess.run(
                ['system_profiler', 'SPUSBDataType', '-json'],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                import json
                data = json.loads(result.stdout)
                # Parse macOS USB data
                # (simplified - would need full parser)
        except:
            pass
        
        return devices
    
    @staticmethod
    def scan_displays() -> List[Dict[str, Any]]:
        """Scan connected displays"""
        displays = []
        
        try:
            # Try xrandr (Linux with X11)
            result = subprocess.run(['xrandr'], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                current_display = None
                for line in result.stdout.split('\n'):
                    # Connected display line
                    if ' connected' in line:
                        parts = line.split()
                        current_display = {
                            "name": parts[0],
                            "connected": True,
                            "primary": 'primary' in line,
                            "resolutions": [],
                            "current_resolution": None,
                            "type": "display"
                        }
                        
                        # Extract current resolution
                        res_match = re.search(r'(\d+x\d+)\+', line)
                        if res_match:
                            current_display["current_resolution"] = res_match.group(1)
                        
                        displays.append(current_display)
                    
                    # Resolution lines
                    elif current_display and line.startswith('   '):
                        res_match = re.match(r'\s+(\d+x\d+)\s+', line)
                        if res_match:
                            resolution = res_match.group(1)
                            current_display["resolutions"].append(resolution)
        except:
            pass
        
        # Try system_profiler (macOS)
        try:
            result = subprocess.run(
                ['system_profiler', 'SPDisplaysDataType', '-json'],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                import json
                data = json.loads(result.stdout)
                # Parse macOS display data
        except:
            pass
        
        return displays
    
    @staticmethod
    def scan_hdmi() -> Dict[str, Any]:
        """Scan HDMI capabilities and connections"""
        hdmi_info = {
            "ports": [],
            "cec_available": False,
            "audio_supported": False,
        }
        
        try:
            # Check for HDMI CEC support (Linux)
            result = subprocess.run(
                ['cec-client', '-l'],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                hdmi_info["cec_available"] = True
                # Parse CEC devices
                for line in result.stdout.split('\n'):
                    if 'device #' in line.lower():
                        hdmi_info["ports"].append({
                            "type": "hdmi_cec",
                            "info": line.strip()
                        })
        except:
            pass
        
        # Check displays for HDMI connections
        displays = DeviceScanner.scan_displays()
        for display in displays:
            if 'HDMI' in display.get('name', '').upper():
                hdmi_info["ports"].append({
                    "type": "hdmi_display",
                    "name": display['name'],
                    "connected": display.get('connected', False),
                    "resolution": display.get('current_resolution')
                })
        
        return hdmi_info
    
    @staticmethod
    def scan_audio() -> List[Dict[str, Any]]:
        """Scan audio devices"""
        audio_devices = []
        
        try:
            # Try aplay (Linux ALSA)
            result = subprocess.run(
                ['aplay', '-l'],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if 'card' in line.lower():
                        audio_devices.append({
                            "type": "audio",
                            "info": line.strip()
                        })
        except:
            pass
        
        return audio_devices
    
    @staticmethod
    def get_display_control_capabilities() -> Dict[str, Any]:
        """Check what display control is possible"""
        capabilities = {
            "brightness_control": False,
            "power_control": False,
            "input_switching": False,
            "cec_control": False,
            "ddcci_control": False,
        }
        
        # Check for ddcutil (DDC/CI control)
        try:
            result = subprocess.run(
                ['ddcutil', 'detect'],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                capabilities["ddcci_control"] = True
                capabilities["brightness_control"] = True
                capabilities["input_switching"] = True
        except:
            pass
        
        # Check for CEC control
        try:
            result = subprocess.run(
                ['cec-client', '-l'],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                capabilities["cec_control"] = True
                capabilities["power_control"] = True
                capabilities["input_switching"] = True
        except:
            pass
        
        # Check for xrandr (basic control)
        try:
            result = subprocess.run(
                ['xrandr', '--version'],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                capabilities["brightness_control"] = True
        except:
            pass
        
        return capabilities
