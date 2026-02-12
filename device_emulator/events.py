import random
from datetime import datetime, timezone
from typing import Optional


class EventGenerator:
    """Generates random device events"""

    def __init__(self):
        self.error_types = [
            'motor_jam',
            'low_food',
            'sensor_error',
            'wifi_disconnect'
        ]
        self.last_cat_event = None

    def check_error(self, error_probability: float) -> Optional[dict]:
        """Check if an error occurs based on probability"""
        if random.random() < error_probability:
            error_type = random.choice(self.error_types)
            return self.create_event('error', {
                'error_type': error_type,
                'message': self.get_error_message(error_type)
            })
        return None

    def create_cat_detected_event(self) -> dict:
        """Create cat detection event"""
        self.last_cat_event = datetime.now(timezone.utc)
        return self.create_event('cat_detected', {
            'message': 'Cat detected at bowl'
        })

    def create_cat_left_event(self) -> dict:
        """Create cat left event"""
        return self.create_event('cat_left', {
            'message': 'Cat left the bowl'
        })

    def create_feeding_complete_event(self, portion: int) -> dict:
        """Create feeding completed event"""
        return self.create_event('feeding_complete', {
            'portion_grams': portion,
            'message': f'Feeding completed: {portion}g dispensed'
        })

    def create_low_food_warning(self, level: int) -> dict:
        """Create low food warning event"""
        return self.create_event('low_food_warning', {
            'food_level': level,
            'message': f'Food running low: {level}% remaining'
        })

    def create_low_water_warning(self, level: int) -> dict:
        """Create low water warning event"""
        return self.create_event('low_water_warning', {
            'water_level': level,
            'message': f'Water running low: {level}% remaining'
        })

    def create_event(self, event_type: str, data: dict) -> dict:
        """Create a generic event structure"""
        return {
            'type': event_type,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'data': data
        }

    @staticmethod
    def get_error_message(error_type: str) -> str:
        """Get human-readable error message"""
        messages = {
            'motor_jam': 'Motor jam detected - check dispenser mechanism',
            'low_food': 'Food level critically low - refill needed',
            'sensor_error': 'Sensor malfunction detected',
            'wifi_disconnect': 'WiFi connection unstable'
        }
        return messages.get(error_type, 'Unknown error occurred')
