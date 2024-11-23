import usb.core
import usb.util
from typing import Dict, Optional, List
import logging
from config.modem_configs import SUPPORTED_MODEMS

class DeviceHandler:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def identify_device(self, vendor_id: str, product_id: str) -> Optional[str]:
        """Identify modem model based on vendor and product IDs"""
        for model, config in SUPPORTED_MODEMS.items():
            if (config['vendor_id'] == vendor_id and 
                config['product_id'] == product_id):
                return model
        return None
        
    def configure_device(self, device_path: str, model: str) -> bool:
        """Configure device with model-specific settings"""
        try:
            if model not in SUPPORTED_MODEMS:
                self.logger.error(f"Unsupported model: {model}")
                return False
                
            config = SUPPORTED_MODEMS[model]
            
            # Execute initialization commands
            for command in config['init_commands']:
                response = self.send_at_command(device_path, command)
                if 'ERROR' in response:
                    self.logger.error(f"Command failed: {command}")
                    return False
                    
            return True
            
        except Exception as e:
            self.logger.error(f"Error configuring device: {e}")
            return False
            
    def get_device_status(self, device_path: str) -> Dict:
        """Get comprehensive device status"""
        status = {
            'connection': False,
            'signal_strength': None,
            'operator': None,
            'imei': None,
            'error': None
        }
        
        try:
            # Check connection
            csq = self.send_at_command(device_path, 'AT+CSQ')
            if 'CSQ:' in csq:
                status['connection'] = True
                status['signal_strength'] = csq.split(':')[1].strip()
                
            # Get operator
            cops = self.send_at_command(device_path, 'AT+COPS?')
            if 'COPS:' in cops:
                status['operator'] = cops.split(',')[-1].strip('"')
                
            # Get IMEI
            imei = self.send_at_command(device_path, 'AT+CGSN')
            if imei and imei.strip():
                status['imei'] = imei.strip()
                
        except Exception as e:
            status['error'] = str(e)
            
        return status 