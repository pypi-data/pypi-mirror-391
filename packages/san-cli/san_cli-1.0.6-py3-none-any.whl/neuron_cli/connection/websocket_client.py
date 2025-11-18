"""WebSocket client for real-time communication"""

import json
import threading
import time
from typing import Callable, Dict, Any, Optional
import websocket

from ..core.logger import logger


class WebSocketClient:
    """WebSocket client for real-time MESH communication"""
    
    def __init__(self, ws_url: str, device_id: str, jwt_token: str):
        self.ws_url = ws_url
        self.device_id = device_id
        self.jwt_token = jwt_token
        self.ws = None
        self.connected = False
        self.running = False
        self.thread = None
        self.message_handlers = {}
        self.reconnect_delay = 5
    
    def connect(self):
        """Connect to WebSocket server"""
        try:
            logger.info(f"🔌 Connecting to WebSocket: {self.ws_url}")
            
            # Create WebSocket with authentication
            headers = {
                "Authorization": f"Bearer {self.jwt_token}",
                "X-Device-ID": self.device_id
            }
            
            self.ws = websocket.WebSocketApp(
                self.ws_url,
                header=headers,
                on_open=self._on_open,
                on_message=self._on_message,
                on_error=self._on_error,
                on_close=self._on_close
            )
            
            # Run in separate thread
            self.running = True
            self.thread = threading.Thread(target=self._run, daemon=True)
            self.thread.start()
            
            return True
            
        except Exception as e:
            logger.error(f"❌ WebSocket connection failed: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from WebSocket server"""
        self.running = False
        if self.ws:
            self.ws.close()
        if self.thread:
            self.thread.join(timeout=5)
        logger.info("🔌 WebSocket disconnected")
    
    def send(self, message_type: str, data: Dict[str, Any]):
        """
        Send message to server
        
        Args:
            message_type: Type of message (job_status, heartbeat, etc.)
            data: Message data
        """
        if not self.connected:
            logger.warning("⚠️  WebSocket not connected, cannot send message")
            return False
        
        try:
            message = {
                "type": message_type,
                "device_id": self.device_id,
                "timestamp": time.time(),
                "data": data
            }
            
            self.ws.send(json.dumps(message))
            logger.debug(f"📤 Sent: {message_type}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to send message: {e}")
            return False
    
    def on(self, message_type: str, handler: Callable):
        """
        Register message handler
        
        Args:
            message_type: Type of message to handle
            handler: Callback function
        """
        self.message_handlers[message_type] = handler
    
    def _run(self):
        """Run WebSocket connection with auto-reconnect"""
        while self.running:
            try:
                self.ws.run_forever()
            except Exception as e:
                logger.error(f"❌ WebSocket error: {e}")
            
            if self.running:
                logger.info(f"🔄 Reconnecting in {self.reconnect_delay}s...")
                time.sleep(self.reconnect_delay)
    
    def _on_open(self, ws):
        """WebSocket opened"""
        self.connected = True
        logger.info("✅ WebSocket connected")
        
        # Send initial handshake
        self.send("handshake", {
            "device_id": self.device_id,
            "agent_version": "2.0.0"
        })
    
    def _on_message(self, ws, message):
        """Received message from server"""
        try:
            data = json.loads(message)
            message_type = data.get("type")
            
            logger.debug(f"📥 Received: {message_type}")
            
            # Call registered handler
            if message_type in self.message_handlers:
                self.message_handlers[message_type](data)
            else:
                logger.debug(f"⚠️  No handler for message type: {message_type}")
                
        except Exception as e:
            logger.error(f"❌ Failed to process message: {e}")
    
    def _on_error(self, ws, error):
        """WebSocket error"""
        logger.error(f"❌ WebSocket error: {error}")
    
    def _on_close(self, ws, close_status_code, close_msg):
        """WebSocket closed"""
        self.connected = False
        logger.info(f"🔌 WebSocket closed: {close_status_code} - {close_msg}")
