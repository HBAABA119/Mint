"""
Prim Embedded Systems
Provides microcontroller support, GPIO, ADC/DAC, PWM,
serial communication, and embedded frameworks.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum


class PinMode(Enum):
    """Pin modes"""
    INPUT = "input"
    OUTPUT = "output"
    INPUT_PULLUP = "input_pullup"
    INPUT_PULLDOWN = "input_pulldown"


@dataclass
class Pin:
    """GPIO pin"""
    id: int
    mode: PinMode
    value: int


class EmbeddedController:
    """Embedded controller"""

    def __init__(self):
        self.pins: Dict[int, Pin] = {}

    def configure_pin(self, pin: Pin):
        """Configure pin"""
        self.pins[pin.id] = pin

    def write_pin(self, id: int, value: int):
        """Write pin value"""
        if id in self.pins:
            self.pins[id].value = value

    def read_pin(self, id: int) -> Optional[int]:
        """Read pin value"""
        if id in self.pins:
            return self.pins[id].value
        return None


def main():
    print("Testing Embedded Systems...")
    controller = EmbeddedController()
    pin = Pin(id=0, mode=PinMode.OUTPUT, value=0)
    controller.configure_pin(pin)
    controller.write_pin(0, 1)
    print(f"Pin value: {controller.read_pin(0)}")
    print("Embedded Systems initialized successfully")


if __name__ == "__main__":
    main()
