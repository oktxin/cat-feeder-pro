@echo off
echo Starting Cat Feeder Device Emulator...
set MQTT_HOST=test.mosquitto.org
set MQTT_PORT=1883
set DEVICE_ID=feeder_001

"C:\Program Files\Python311\python.exe" main.py
pause
