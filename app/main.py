from flask import Flask, jsonify, request, render_template
from modem_manager import ModemManager
from message_monitor import MessageMonitor
import logging
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

app = Flask(__name__)
modem_manager = ModemManager()
message_monitor = MessageMonitor(modem_manager)

# Start message monitoring on app startup
@app.before_first_request
def start_monitor():
    message_monitor.start()

@app.route('/')
def dashboard():
    """Render main dashboard"""
    return render_template('dashboard.html')

@app.route('/api/modems', methods=['GET'])
def get_modems():
    """Get list of connected modems with status"""
    modems = modem_manager.discover_modems()
    return jsonify({'modems': modems})

@app.route('/api/modem/<path:device_path>/sms', methods=['GET'])
def get_sms(device_path):
    """Get SMS messages from specific modem"""
    messages = modem_manager.read_sms(device_path)
    return jsonify({'messages': messages})

@app.route('/api/modem/<path:device_path>/command', methods=['POST'])
def send_command(device_path):
    """Send AT command to modem"""
    command = request.json.get('command')
    if not command:
        return jsonify({'error': 'No command provided'}), 400
        
    response = modem_manager.send_at_command(device_path, command)
    return jsonify({'response': response})

@app.route('/api/messages/recent', methods=['GET'])
def get_recent_messages():
    """Get recent messages from all modems"""
    messages = []
    modems = modem_manager.discover_modems()
    
    for modem in modems:
        device_path = modem.get('device_path')
        if device_path:
            modem_messages = modem_manager.read_sms(device_path)
            for msg in modem_messages:
                msg['device'] = modem.get('model', 'Unknown Device')
            messages.extend(modem_messages)
    
    # Sort by timestamp and limit to 10 most recent
    messages.sort(key=lambda x: x['timestamp'], reverse=True)
    return jsonify({'messages': messages[:10]})

@app.route('/api/modem/<path:device_path>/configure', methods=['POST'])
def configure_device(device_path):
    """Configure a specific modem"""
    vendor_id = request.json.get('vendor_id')
    product_id = request.json.get('product_id')
    
    if not (vendor_id and product_id):
        return jsonify({'error': 'Vendor ID and Product ID required'}), 400
        
    success = modem_manager.configure_modem(device_path, vendor_id, product_id)
    return jsonify({'success': success})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000) 