import json
import logging
import time
from typing import Callable, Optional
import paho.mqtt.client as mqtt

logger = logging.getLogger(__name__)


class MQTTClient:
    """MQTT client wrapper for device communication"""

    def __init__(self, host: str, port: int, device_id: str):
        self.host = host
        self.port = port
        self.device_id = device_id
        self.client = mqtt.Client(client_id=device_id, clean_session=True)
        self.connected = False
        self.command_callback: Optional[Callable] = None

        # Set up callbacks
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.on_message = self._on_message

        # Set Last Will and Testament
        self.client.will_set(
            self._get_status_topic(),
            payload=json.dumps({'online': False}),
            qos=1,
            retain=True
        )

    def _on_connect(self, client, userdata, flags, rc):
        """Callback for when connected to MQTT broker"""
        if rc == 0:
            self.connected = True
            logger.info(f"Connected to MQTT broker at {self.host}:{self.port}")

            # Publish online status
            self.publish_status(True)

            # Subscribe to command topic
            command_topic = self._get_command_topic()
            self.client.subscribe(command_topic)
            logger.info(f"Subscribed to {command_topic}")
        else:
            logger.error(f"Failed to connect to MQTT broker, return code {rc}")
            self.connected = False

    def _on_disconnect(self, client, userdata, rc):
        """Callback for when disconnected from MQTT broker"""
        self.connected = False
        if rc != 0:
            logger.warning(f"Unexpected disconnection from MQTT broker, code {rc}")
        else:
            logger.info("Disconnected from MQTT broker")

    def _on_message(self, client, userdata, msg):
        """Callback for when a message is received"""
        try:
            payload = json.loads(msg.payload.decode())
            logger.info(f"Received message on {msg.topic}: {payload}")

            if self.command_callback:
                self.command_callback(payload)
        except json.JSONDecodeError:
            logger.error(f"Failed to decode JSON message: {msg.payload}")
        except Exception as e:
            logger.error(f"Error processing message: {e}")

    def connect(self, retry_interval: int = 5, max_retries: int = 10) -> bool:
        """Connect to MQTT broker with retry logic"""
        retries = 0
        while retries < max_retries:
            try:
                logger.info(f"Attempting to connect to MQTT broker at {self.host}:{self.port}")
                self.client.connect(self.host, self.port, keepalive=60)
                self.client.loop_start()

                # Wait for connection to establish
                wait_time = 0
                while not self.connected and wait_time < 10:
                    time.sleep(1)
                    wait_time += 1

                if self.connected:
                    return True
                else:
                    logger.warning(f"Connection timeout, retrying...")
                    retries += 1
            except Exception as e:
                logger.error(f"Connection error: {e}")
                retries += 1

            if retries < max_retries:
                logger.info(f"Retrying in {retry_interval} seconds... ({retries}/{max_retries})")
                time.sleep(retry_interval)

        logger.error(f"Failed to connect after {max_retries} attempts")
        return False

    def disconnect(self):
        """Disconnect from MQTT broker"""
        if self.connected:
            self.publish_status(False)
            self.client.loop_stop()
            self.client.disconnect()

    def publish_telemetry(self, data: dict):
        """Publish telemetry data"""
        if self.connected:
            topic = self._get_telemetry_topic()
            payload = json.dumps(data)
            self.client.publish(topic, payload, qos=0)

    def publish_event(self, event: dict):
        """Publish an event"""
        if self.connected:
            topic = self._get_event_topic()
            payload = json.dumps(event)
            self.client.publish(topic, payload, qos=1)
            logger.info(f"Published event: {event['type']}")

    def publish_status(self, online: bool):
        """Publish device online/offline status"""
        topic = self._get_status_topic()
        payload = json.dumps({'online': online})
        self.client.publish(topic, payload, qos=1, retain=True)

    def set_command_callback(self, callback: Callable):
        """Set callback function for incoming commands"""
        self.command_callback = callback

    def _get_telemetry_topic(self) -> str:
        """Get telemetry topic for this device"""
        device_num = self.device_id.split('_')[1]
        return f"feeder/{device_num}/telemetry"

    def _get_command_topic(self) -> str:
        """Get command topic for this device"""
        device_num = self.device_id.split('_')[1]
        return f"feeder/{device_num}/commands"

    def _get_event_topic(self) -> str:
        """Get event topic for this device"""
        device_num = self.device_id.split('_')[1]
        return f"feeder/{device_num}/events"

    def _get_status_topic(self) -> str:
        """Get status topic for this device"""
        device_num = self.device_id.split('_')[1]
        return f"feeder/{device_num}/status"
