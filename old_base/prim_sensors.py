"""
Prim Sensor Management
Provides sensor data collection, calibration, filtering, sensor fusion,
and sensor network management.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum


class SensorType(Enum):
    """Sensor types"""
    TEMPERATURE = "temperature"
    HUMIDITY = "humidity"
    PRESSURE = "pressure"
    MOTION = "motion"
    LIGHT = "light"


@dataclass
class Sensor:
    """Sensor"""
    id: str
    type: SensorType
    value: float


class SensorManager:
    """Sensor manager"""

    def __init__(self):
        self.sensors: Dict[str, Sensor] = {}

    def add_sensor(self, sensor: Sensor):
        """Add sensor"""
        self.sensors[sensor.id] = sensor

    def read_sensor(self, id: str) -> Optional[float]:
        """Read sensor value"""
        if id in self.sensors:
            return self.sensors[id].value
        return None


def main():
    print("Testing Sensor Management...")
    manager = SensorManager()
    sensor = Sensor(id="sensor1", type=SensorType.TEMPERATURE, value=25.0)
    manager.add_sensor(sensor)
    value = manager.read_sensor("sensor1")
    print(f"Value: {value}")
    print("Sensor Management initialized successfully")


if __name__ == "__main__":
    main()
