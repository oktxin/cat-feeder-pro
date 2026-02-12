import os

# MQTT Configuration
MQTT_HOST = os.getenv('MQTT_HOST', 'localhost')
MQTT_PORT = int(os.getenv('MQTT_PORT', 1883))
DEVICE_ID = os.getenv('DEVICE_ID', 'feeder_001')

# Topics
TOPIC_TELEMETRY = f"feeder/{DEVICE_ID.split('_')[1]}/telemetry"
TOPIC_COMMANDS = f"feeder/{DEVICE_ID.split('_')[1]}/commands"
TOPIC_EVENTS = f"feeder/{DEVICE_ID.split('_')[1]}/events"
TOPIC_STATUS = f"feeder/{DEVICE_ID.split('_')[1]}/status"

# Timing
TELEMETRY_INTERVAL = 5  # seconds
EVENT_CHECK_INTERVAL = 1  # seconds

# Device Configuration
FIRMWARE_VERSION = "1.2.4"
INITIAL_FOOD_LEVEL = 75
INITIAL_WATER_LEVEL = 60
INITIAL_BATTERY_LEVEL = 88

# Simulation Parameters
FOOD_DECAY_PER_HOUR = (2, 5)  # Random range in percent
FOOD_DROP_PER_FEEDING = (10, 20)  # Random range in percent
CAT_DETECTION_PROBABILITY = 0.005  # Per second (approx 30% per minute)
CAT_PRESENCE_DURATION = (30, 120)  # Seconds
ERROR_PROBABILITY = 0.0002  # Per cycle (approx 2% per 100 cycles)
MOTOR_RUNNING_TIME = (3, 5)  # Seconds
