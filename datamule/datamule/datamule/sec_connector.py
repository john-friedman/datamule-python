import os
import json
import urllib.request
import websocket
import re
import logging

logger = logging.getLogger(__name__)

class SecConnector:
    def __init__(self, api_key=None, quiet=False):
        self.api_key = api_key or os.getenv('DATAMULE_API_KEY')
        if not self.api_key:
            raise ValueError("API key not found. Set DATAMULE_API_KEY or provide api_key parameter.")
        
        self.quiet = quiet
        self.auth_url = "https://sec-websocket-auth-worker.jgfriedman99.workers.dev/"
        
    def _get_jwt_token_and_ip(self):
        if not self.quiet:
            logger.info("Getting JWT token...")
            
        url = self.auth_url
        
        # Send API key in Authorization header instead of POST body
        req = urllib.request.Request(url, method='GET')
        req.add_header('Accept', 'application/json')
        req.add_header('Authorization', f'Bearer {self.api_key}')  # API key in header
        
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            
        if not data.get('success'):
            raise Exception(f"Auth failed: {data.get('error')}")
            
        if not self.quiet:
            logger.info("JWT token obtained")
            
        return data['token'], data['websocket_ip']
    
    def connect(self, data_callback=None):
        token, websocket_ip = self._get_jwt_token_and_ip()
        ws_url = f"ws://{websocket_ip}/ws"
        
        if not self.quiet:
            logger.info("Connecting to WebSocket...")
        
        def on_open(ws):
            if not self.quiet:
                logger.info("WebSocket connected")
        
        def on_message(ws, message):
            response = json.loads(message)
            data = response.get('data', [])
            if not self.quiet:
                logger.info(f"Received data: {len(data)} items")
            if data_callback:
                data_callback(data) 
        
        def on_error(ws, error):
            if not self.quiet:
                sanitized_error = self._sanitize_error_message(str(error))
                logger.info(f"WebSocket error: {sanitized_error}")
        
        def on_close(ws, close_status_code, close_msg):
            if not self.quiet:
                logger.info("WebSocket closed")
        
        # Use Authorization header for WebSocket connection
        headers = {'Authorization': f'Bearer {token}'}
        
        ws = websocket.WebSocketApp(
            ws_url,
            header=headers,
            on_open=on_open,
            on_message=on_message,
            on_error=on_error,
            on_close=on_close
        )
        
        ws.run_forever()
    
    def _sanitize_error_message(self, error_msg):
        sensitive_patterns = [
            r'Bearer\s+[A-Za-z0-9\-_\.]+',     # Bearer tokens
            r'api_key[=:]\s*[A-Za-z0-9\-_]+',  # API key patterns
            r'token[=:]\s*[A-Za-z0-9\-_\.]+',  # Token patterns
            r'jwt[=:]\s*[A-Za-z0-9\-_\.]+',    # JWT patterns
        ]
        
        sanitized = error_msg
        for pattern in sensitive_patterns:
            sanitized = re.sub(pattern, '[REDACTED]', sanitized, flags=re.IGNORECASE)
        
        return sanitized
