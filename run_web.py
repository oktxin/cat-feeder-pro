"""
Entry point for running the web interface on Railway
"""
import os
import sys
import asyncio
import threading

# Add device_emulator to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'device_emulator'))

from device_emulator.main import DeviceEmulator
from device_emulator.web_interface import app, set_emulator

def run_emulator():
    """Run the device emulator in background thread"""
    emulator = DeviceEmulator()
    set_emulator(emulator)

    # Run emulator
    try:
        asyncio.run(emulator.start())
    except Exception as e:
        print(f"Emulator error: {e}")

if __name__ == "__main__":
    # Start emulator in background thread
    emulator_thread = threading.Thread(target=run_emulator, daemon=True)
    emulator_thread.start()

    # Get port from environment variable (Railway provides this)
    port = int(os.getenv('PORT', 5000))

    # Run Flask app
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)
