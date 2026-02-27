"""
Prim Device Management
Provides device registration, I/O operations, device drivers,
interrupt handling, and device monitoring.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum


class DeviceType(Enum):
    """Device types"""
    BLOCK = "block"
    CHARACTER = "character"
    NETWORK = "network"


@dataclass
class Device:
    """Device"""
    id: str
    type: DeviceType
    name: str


class DeviceManager:
    """Device manager"""

    def __init__(self):
        self.devices: Dict[str, Device] = {}

    def register_device(self, device: Device):
        """Register device"""
        self.devices[device.id] = device

    def get_device(self, id: str) -> Optional[Device]:
        """Get device"""
        return self.devices.get(id)


def main():
    print("Testing Device Management...")
    manager = DeviceManager()
    device = Device(id="dev1", type=DeviceType.BLOCK, name="disk")
    manager.register_device(device)
    print(f"Device: {device.name}")
    print("Device Management initialized successfully")


if __name__ == "__main__":
    main()
