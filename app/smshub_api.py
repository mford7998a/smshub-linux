import requests
import logging
from typing import Dict, Optional
from datetime import datetime

class SMSHubAPI:
    def __init__(self, api_key: str, base_url: str = "https://smshub.org/api/v1"):
        self.api_key = api_key
        self.base_url = base_url
        self.logger = logging.getLogger(__name__)
        
    def forward_message(self, message: Dict) -> bool:
        """Forward SMS message to SMSHub.org"""
        try:
            payload = {
                'api_key': self.api_key,
                'sender': message['sender'],
                'message': message['text'],
                'timestamp': message['timestamp'],
                'device_id': message.get('device_id', 'unknown')
            }
            
            response = requests.post(
                f"{self.base_url}/messages",
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                self.logger.info(f"Message forwarded successfully: {message['index']}")
                return True
            else:
                self.logger.error(f"Failed to forward message: {response.text}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error forwarding message: {e}")
            return False 