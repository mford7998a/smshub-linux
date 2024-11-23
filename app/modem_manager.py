import serial
import subprocess
import logging
from typing import Dict, List, Optional
import time
import json
from device_handler import DeviceHandler
from smshub_api import SMSHubAPI
import os

class ModemManager:
    def __init__(self):
        self.modems: Dict[str, 'ModemDevice'] = {}
        self.logger = logging.getLogger(__name__)
        self.device_handler = DeviceHandler()
        self.smshub_api = SMSHubAPI(os.getenv('SMSHUB_API_KEY'))
        
    def discover_modems(self) -> List[dict]:
        """Discover connected USB modems using ModemManager"""
        try:
            # Use mmcli to list modems
            result = subprocess.run(['mmcli', '-L'], capture_output=True, text=True)
            modems = []
            
            for line in result.stdout.splitlines():
                if '/org/freedesktop/ModemManager1/Modem/' in line:
                    modem_id = line.split()[-1]
                    modem_info = self._get_modem_info(modem_id)
                    if modem_info:
                        modems.append(modem_info)
                        
            return modems
        except Exception as e:
            self.logger.error(f"Error discovering modems: {e}")
            return []
            
    def _get_modem_info(self, modem_id: str) -> Optional[dict]:
        """Get detailed information about a specific modem"""
        try:
            result = subprocess.run(['mmcli', '-m', modem_id, '-J'], 
                                 capture_output=True, text=True)
            return json.loads(result.stdout)
        except Exception as e:
            self.logger.error(f"Error getting modem info: {e}")
            return None
            
    def send_at_command(self, device_path: str, command: str) -> str:
        """Send AT command to modem"""
        try:
            with serial.Serial(device_path, 115200, timeout=1) as ser:
                ser.write(f"{command}\r\n".encode())
                time.sleep(0.1)
                response = ser.read_all().decode()
                return response
        except Exception as e:
            self.logger.error(f"Error sending AT command: {e}")
            return f"Error: {str(e)}"
            
    def read_sms(self, device_path: str) -> List[dict]:
        """Read SMS messages from modem"""
        messages = []
        try:
            # Enable text mode
            self.send_at_command(device_path, "AT+CMGF=1")
            
            # Read all messages
            response = self.send_at_command(device_path, "AT+CMGL=\"ALL\"")
            
            # Parse messages (basic implementation)
            for line in response.split('\n'):
                if '+CMGL:' in line:
                    # Parse message header
                    msg_data = line.split(',')
                    msg_text = next(response.split('\n'))
                    
                    messages.append({
                        'index': msg_data[0].split()[-1],
                        'status': msg_data[1].strip('"'),
                        'sender': msg_data[2].strip('"'),
                        'timestamp': f"{msg_data[3].strip('"')} {msg_data[4].strip('"')}",
                        'text': msg_text.strip()
                    })
                    
            return messages
        except Exception as e:
            self.logger.error(f"Error reading SMS: {e}")
            return [] 
            
    def process_new_message(self, device_path: str, message: Dict):
        """Process and forward new SMS message"""
        try:
            # Forward message to SMSHub
            if self.smshub_api.forward_message(message):
                # Delete message after successful forwarding
                self.send_at_command(device_path, f"AT+CMGD={message['index']}")
                self.logger.info(f"Message {message['index']} processed and deleted")
            else:
                self.logger.error(f"Failed to forward message {message['index']}")
                
        except Exception as e:
            self.logger.error(f"Error processing message: {e}")
            
    def configure_modem(self, device_path: str, vendor_id: str, product_id: str) -> bool:
        """Configure newly connected modem"""
        model = self.device_handler.identify_device(vendor_id, product_id)
        if model:
            return self.device_handler.configure_device(device_path, model)
        return False 