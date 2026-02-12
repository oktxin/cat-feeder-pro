import logging
import asyncio
from datetime import datetime, timezone, timedelta
from typing import List
from sensors import SensorSimulator, WeightSensor, IRSensor
from events import EventGenerator
import config

logger = logging.getLogger(__name__)


class CatFeeder:
    """Main cat feeder device logic"""

    def __init__(self, device_id: str):
        self.device_id = device_id
        self.sensors = SensorSimulator()
        self.weight_sensor = WeightSensor()
        self.ir_sensor = IRSensor()
        self.event_generator = EventGenerator()

        # State
        self.motor_status = 'idle'
        self.door_open = False
        self.total_feedings_today = 0
        self.last_feeding_time = None
        self.next_feeding_time = None
        self.feeding_schedule = ['08:00', '14:00', '20:00']
        self.default_portion = 50  # grams

        # Internal tracking
        self.last_day = datetime.now(timezone.utc).date()
        self.cat_was_present = False
        self.low_food_warning_sent = False
        self.low_water_warning_sent = False

        self._calculate_next_feeding()

    def get_state(self) -> dict:
        """Get current device state"""
        # Apply natural decay
        self.sensors.apply_natural_decay()

        # Update weight as cat may be eating
        self.weight_sensor.simulate_eating()

        # Check if day changed, reset counters
        current_day = datetime.now(timezone.utc).date()
        if current_day != self.last_day:
            self.total_feedings_today = 0
            self.last_day = current_day
            self.low_food_warning_sent = False
            self.low_water_warning_sent = False

        state = {
            'device_id': self.device_id,
            'food_level': self.sensors.get_food_level(),
            'water_level': self.sensors.get_water_level(),
            'last_feeding_time': self.last_feeding_time.isoformat() if self.last_feeding_time else None,
            'next_feeding_time': self.next_feeding_time.isoformat() if self.next_feeding_time else None,
            'motor_status': self.motor_status,
            'cat_detected': self.ir_sensor.is_detected(),
            'weight_bowl': self.weight_sensor.read(),
            'door_open': self.door_open,
            'temperature': self.sensors.get_temperature(),
            'wifi_signal': self.sensors.get_wifi_signal(),
            'battery_level': self.sensors.get_battery_level(),
            'total_feedings_today': self.total_feedings_today,
            'firmware_version': config.FIRMWARE_VERSION,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }

        return state

    async def check_events(self) -> List[dict]:
        """Check for and generate events"""
        events = []

        # Check for errors
        error_event = self.event_generator.check_error(config.ERROR_PROBABILITY)
        if error_event:
            events.append(error_event)
            if error_event['data']['error_type'] == 'motor_jam':
                self.motor_status = 'error'

        # Check cat detection
        cat_detected = self.ir_sensor.update(
            config.CAT_DETECTION_PROBABILITY,
            config.CAT_PRESENCE_DURATION
        )

        if cat_detected and not self.cat_was_present:
            events.append(self.event_generator.create_cat_detected_event())
            self.cat_was_present = True
        elif not cat_detected and self.cat_was_present:
            events.append(self.event_generator.create_cat_left_event())
            self.cat_was_present = False

        # Check low food warning
        food_level = self.sensors.get_food_level()
        if food_level < 20 and not self.low_food_warning_sent:
            events.append(self.event_generator.create_low_food_warning(food_level))
            self.low_food_warning_sent = True
        elif food_level >= 20:
            self.low_food_warning_sent = False

        # Check low water warning
        water_level = self.sensors.get_water_level()
        if water_level < 20 and not self.low_water_warning_sent:
            events.append(self.event_generator.create_low_water_warning(water_level))
            self.low_water_warning_sent = True
        elif water_level >= 20:
            self.low_water_warning_sent = False

        # Check scheduled feeding
        if self.next_feeding_time and datetime.now(timezone.utc) >= self.next_feeding_time:
            await self.feed_now(self.default_portion)
            events.append(self.event_generator.create_feeding_complete_event(self.default_portion))

        return events

    async def feed_now(self, portion: int = None):
        """Execute immediate feeding"""
        if self.motor_status == 'error':
            logger.warning("Cannot feed - motor in error state")
            return False

        if portion is None:
            portion = self.default_portion

        logger.info(f"Starting feeding: {portion}g")

        # Activate motor
        self.motor_status = 'running'

        # Simulate motor running time
        motor_time = asyncio.create_task(
            asyncio.sleep(config.MOTOR_RUNNING_TIME[0])
        )
        await motor_time

        # Dispense food
        self.sensors.dispense_food(portion)
        self.weight_sensor.add_weight(portion)

        # Update state
        self.motor_status = 'idle'
        self.last_feeding_time = datetime.now(timezone.utc)
        self.total_feedings_today += 1
        self._calculate_next_feeding()

        logger.info(f"Feeding complete. Next feeding at {self.next_feeding_time}")
        return True

    def set_schedule(self, times: List[str]):
        """Update feeding schedule"""
        self.feeding_schedule = sorted(times)
        self._calculate_next_feeding()
        logger.info(f"Schedule updated: {self.feeding_schedule}")

    def set_portion(self, grams: int):
        """Set default portion size"""
        self.default_portion = max(10, min(100, grams))
        logger.info(f"Portion size set to {self.default_portion}g")

    def open_door(self):
        """Open feeder door (for maintenance)"""
        self.door_open = True
        logger.info("Door opened")

    def close_door(self):
        """Close feeder door"""
        self.door_open = False
        logger.info("Door closed")

    def tare_scale(self):
        """Reset bowl weight scale"""
        self.weight_sensor.tare()
        logger.info("Scale tared")

    def reboot(self):
        """Simulate device reboot"""
        logger.info("Device rebooting...")
        self.motor_status = 'idle'
        self.door_open = False

    def _calculate_next_feeding(self):
        """Calculate next scheduled feeding time"""
        now = datetime.now(timezone.utc)
        today = now.date()

        # Convert schedule times to datetime objects
        feeding_times = []
        for time_str in self.feeding_schedule:
            hour, minute = map(int, time_str.split(':'))
            feeding_time = datetime.combine(today, datetime.min.time().replace(hour=hour, minute=minute))
            feeding_time = feeding_time.replace(tzinfo=timezone.utc)

            # If time has passed today, schedule for tomorrow
            if feeding_time <= now:
                feeding_time += timedelta(days=1)

            feeding_times.append(feeding_time)

        # Get nearest feeding time
        if feeding_times:
            self.next_feeding_time = min(feeding_times)

    async def handle_command(self, command: dict):
        """Handle incoming MQTT command"""
        action = command.get('action')

        if not action:
            logger.warning(f"Command missing 'action' field: {command}")
            return

        logger.info(f"Handling command: {action}")

        if action == 'feed_now':
            portion = command.get('portion', self.default_portion)
            success = await self.feed_now(portion)
            if success:
                return self.event_generator.create_feeding_complete_event(portion)

        elif action == 'set_schedule':
            times = command.get('times', [])
            if times:
                self.set_schedule(times)

        elif action == 'set_portion':
            grams = command.get('grams')
            if grams:
                self.set_portion(grams)

        elif action == 'open_door':
            self.open_door()

        elif action == 'close_door':
            self.close_door()

        elif action == 'tare_scale':
            self.tare_scale()

        elif action == 'reboot':
            self.reboot()

        else:
            logger.warning(f"Unknown command action: {action}")

        return None
