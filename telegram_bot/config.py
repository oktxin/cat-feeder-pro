import os

BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
BACKEND_URL = os.getenv('BACKEND_URL', 'http://backend:3001')
DEVICE_ID = os.getenv('DEVICE_ID', 'feeder_001')
POLL_INTERVAL = int(os.getenv('POLL_INTERVAL', '10'))
