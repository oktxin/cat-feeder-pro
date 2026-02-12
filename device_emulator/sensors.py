import random
from datetime import datetime, timezone


class SensorSimulator:
    """Simulates various sensors on the cat feeder device"""

    def __init__(self):
        self.food_level = 75
        self.water_level = 60
        self.battery_level = 88
        self.temperature = 22.3
        self.wifi_signal = -65
        self.weight_bowl = 0.0
        self.last_decay_time = datetime.now(timezone.utc)

    def get_food_level(self) -> int:
        """Get current food level (0-100%)"""
        return max(0, min(100, int(self.food_level)))

    def get_water_level(self) -> int:
        """Get current water level (0-100%)"""
        return max(0, min(100, int(self.water_level)))

    def get_battery_level(self) -> int:
        """Get current battery level (0-100%)"""
        return max(0, min(100, int(self.battery_level)))

    def get_temperature(self) -> float:
        """Get temperature with slight random variation"""
        self.temperature += random.uniform(-0.2, 0.2)
        self.temperature = max(15.0, min(30.0, self.temperature))
        return round(self.temperature, 1)

    def get_wifi_signal(self) -> int:
        """Get WiFi signal strength in dBm"""
        self.wifi_signal += random.randint(-3, 3)
        self.wifi_signal = max(-90, min(-40, self.wifi_signal))
        return self.wifi_signal

    def get_weight_bowl(self) -> float:
        """Get weight of food in bowl (grams)"""
        # Bowl weight naturally decreases as cat eats
        if self.weight_bowl > 0:
            self.weight_bowl -= random.uniform(0, 0.5)
            self.weight_bowl = max(0, self.weight_bowl)
        return round(self.weight_bowl, 1)

    def apply_natural_decay(self):
        """Apply gradual food and water consumption over time"""
        now = datetime.now(timezone.utc)
        hours_passed = (now - self.last_decay_time).total_seconds() / 3600

        if hours_passed >= 0.1:  # Apply decay every 6 minutes minimum
            decay_rate = random.uniform(2, 5) * hours_passed
            self.food_level -= decay_rate
            self.water_level -= random.uniform(1, 3) * hours_passed

            # Battery slowly drains
            self.battery_level -= random.uniform(0.1, 0.3) * hours_passed

            self.last_decay_time = now

    def dispense_food(self, portion: int):
        """Simulate food dispensing"""
        # Decrease food level based on portion size
        food_decrease = random.uniform(10, 20)
        self.food_level -= food_decrease

        # Add weight to bowl
        self.weight_bowl += portion

        return food_decrease

    def refill_food(self):
        """Simulate manual food refill"""
        self.food_level = 100

    def refill_water(self):
        """Simulate manual water refill"""
        self.water_level = 100

    def tare_scale(self):
        """Reset bowl weight to zero"""
        self.weight_bowl = 0.0


class WeightSensor:
    """Dedicated weight sensor for the bowl"""

    def __init__(self):
        self.current_weight = 0.0
        self.tare_offset = 0.0

    def read(self) -> float:
        """Read current weight in grams"""
        # Add small random noise
        noise = random.uniform(-0.1, 0.1)
        return max(0, round(self.current_weight + noise - self.tare_offset, 1))

    def add_weight(self, grams: float):
        """Add weight (food dispensed)"""
        self.current_weight += grams

    def remove_weight(self, grams: float):
        """Remove weight (cat eating)"""
        self.current_weight = max(0, self.current_weight - grams)

    def tare(self):
        """Reset scale to zero"""
        self.tare_offset = self.current_weight
        self.current_weight = 0.0

    def simulate_eating(self):
        """Simulate cat eating from bowl"""
        if self.current_weight > 0:
            eat_amount = random.uniform(0, 1.5)
            self.remove_weight(eat_amount)


class IRSensor:
    """Infrared presence sensor for cat detection"""

    def __init__(self):
        self.cat_present = False
        self.presence_start_time = None
        self.presence_duration = 0

    def update(self, detection_probability: float, duration_range: tuple) -> bool:
        """Update sensor state based on probability"""
        if not self.cat_present:
            # Check if cat appears
            if random.random() < detection_probability:
                self.cat_present = True
                self.presence_start_time = datetime.now(timezone.utc)
                self.presence_duration = random.randint(*duration_range)
        else:
            # Check if cat leaves
            elapsed = (datetime.now(timezone.utc) - self.presence_start_time).total_seconds()
            if elapsed >= self.presence_duration:
                self.cat_present = False
                self.presence_start_time = None

        return self.cat_present

    def is_detected(self) -> bool:
        """Check if cat is currently detected"""
        return self.cat_present

    def force_state(self, present: bool):
        """Manually set cat presence state"""
        self.cat_present = present
        if present:
            self.presence_start_time = datetime.now(timezone.utc)
            self.presence_duration = 30  # 30 seconds default
        else:
            self.presence_start_time = None
            self.presence_duration = 0
