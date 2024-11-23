from threading import Thread
import time
import logging
from typing import Dict
from modem_manager import ModemManager

class MessageMonitor:
    def __init__(self, modem_manager: ModemManager):
        self.modem_manager = modem_manager
        self.logger = logging.getLogger(__name__)
        self.running = False
        self.monitor_thread = None
        
    def start(self):
        """Start message monitoring"""
        self.running = True
        self.monitor_thread = Thread(target=self._monitor_loop)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        
    def stop(self):
        """Stop message monitoring"""
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join()
            
    def _monitor_loop(self):
        """Continuous monitoring loop"""
        while self.running:
            try:
                modems = self.modem_manager.discover_modems()
                
                for modem in modems:
                    device_path = modem.get('device_path')
                    if device_path:
                        messages = self.modem_manager.read_sms(device_path)
                        for message in messages:
                            self.modem_manager.process_new_message(device_path, message)
                            
                time.sleep(5)  # Check every 5 seconds
                
            except Exception as e:
                self.logger.error(f"Error in monitor loop: {e}")
                time.sleep(30)  # Wait longer on error 