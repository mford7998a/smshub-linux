SUPPORTED_MODEMS = {
    'Franklin T9': {
        'vendor_id': '1fac',
        'product_id': '0201',
        'init_commands': [
            'AT+CMGF=1',  # Set SMS text mode
            'AT+CNMI=2,1,0,0,0'  # Configure new message notifications
        ]
    },
    'Franklin T10': {
        'vendor_id': '1fac',
        'product_id': '0202',
        'init_commands': [
            'AT+CMGF=1',
            'AT+CNMI=2,1,0,0,0'
        ]
    },
    'Sierra EM7455': {
        'vendor_id': '1199',
        'product_id': '9079',
        'init_commands': [
            'AT+CMGF=1',
            'AT+CNMI=2,1,0,0,0'
        ]
    },
    'Fibocom L850GL': {
        'vendor_id': '2cb7',
        'product_id': '0001',
        'init_commands': [
            'AT+CMGF=1',
            'AT+CNMI=2,1,0,0,0'
        ]
    },
    'Pantech UML290': {
        'vendor_id': '106c',
        'product_id': '3b11',
        'init_commands': [
            'AT+CMGF=1',
            'AT+CNMI=2,1,0,0,0'
        ]
    }
} 