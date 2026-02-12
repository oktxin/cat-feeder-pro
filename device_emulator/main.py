import asyncio
import logging
import signal
import sys
import threading
from feeder import CatFeeder
from mqtt_client import MQTTClient
import config
from web_interface import run_web_interface, set_emulator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DeviceEmulator:
    """Main device emulator orchestrator"""

    def __init__(self):
        self.feeder = CatFeeder(config.DEVICE_ID)
        self.mqtt_client = MQTTClient(config.MQTT_HOST, config.MQTT_PORT, config.DEVICE_ID)
        self.running = False
        self.telemetry_task = None
        self.event_task = None

    async def start(self):
        """Start the device emulator"""
        logger.info("Starting Cat Feeder Device Emulator")
        logger.info(f"Device ID: {config.DEVICE_ID}")
        logger.info(f"MQTT Broker: {config.MQTT_HOST}:{config.MQTT_PORT}")

        # Connect to MQTT broker
        if not self.mqtt_client.connect():
            logger.warning("Failed to connect to MQTT broker. Continuing without MQTT telemetry.")
        else:
            # Set command callback only if connected
            self.mqtt_client.set_command_callback(self._handle_command)

        # Start telemetry and event loops
        self.running = True
        self.telemetry_task = asyncio.create_task(self._telemetry_loop())
        self.event_task = asyncio.create_task(self._event_loop())

        logger.info("Device emulator started successfully")

        # Wait for tasks to complete
        await asyncio.gather(self.telemetry_task, self.event_task)

    async def stop(self):
        """Stop the device emulator"""
        logger.info("Stopping device emulator...")
        self.running = False

        # Cancel tasks
        if self.telemetry_task:
            self.telemetry_task.cancel()
        if self.event_task:
            self.event_task.cancel()

        # Disconnect from MQTT
        self.mqtt_client.disconnect()

        logger.info("Device emulator stopped")

    async def _telemetry_loop(self):
        """Publish telemetry data at regular intervals"""
        while self.running:
            try:
                # Only publish if MQTT is connected
                if self.mqtt_client.connected:
                    state = self.feeder.get_state()
                    self.mqtt_client.publish_telemetry(state)
                    logger.debug(f"Published telemetry: food={state['food_level']}%, water={state['water_level']}%")
                await asyncio.sleep(config.TELEMETRY_INTERVAL)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in telemetry loop: {e}")
                await asyncio.sleep(1)

    async def _event_loop(self):
        """Check for and publish events"""
        while self.running:
            try:
                events = await self.feeder.check_events()
                # Only publish events if MQTT is connected
                if self.mqtt_client.connected:
                    for event in events:
                        self.mqtt_client.publish_event(event)

                await asyncio.sleep(config.EVENT_CHECK_INTERVAL)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in event loop: {e}")
                await asyncio.sleep(1)

    def _handle_command(self, command: dict):
        """Handle incoming MQTT command (sync wrapper)"""
        asyncio.create_task(self._async_handle_command(command))

    async def _async_handle_command(self, command: dict):
        """Handle incoming MQTT command (async)"""
        try:
            event = await self.feeder.handle_command(command)
            if event:
                self.mqtt_client.publish_event(event)
        except Exception as e:
            logger.error(f"Error handling command: {e}")


async def main():
    """Main entry point"""
    emulator = DeviceEmulator()

    # Set emulator reference for web interface
    set_emulator(emulator)

    # Start web interface in separate thread
    web_thread = threading.Thread(
        target=run_web_interface,
        kwargs={'port': 5000},
        daemon=True
    )
    web_thread.start()
    logger.info("Web interface started on http://0.0.0.0:5000")

    # Set up signal handlers for graceful shutdown (not supported on Windows)
    loop = asyncio.get_event_loop()

    def signal_handler():
        logger.info("Received shutdown signal")
        asyncio.create_task(emulator.stop())

    # Signal handlers are not supported on Windows
    if sys.platform != 'win32':
        for sig in (signal.SIGTERM, signal.SIGINT):
            loop.add_signal_handler(sig, signal_handler)

    try:
        await emulator.start()
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received")
    finally:
        await emulator.stop()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        sys.exit(0)
