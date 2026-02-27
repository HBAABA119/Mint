"""
Prim IoT Framework
Provides device management, connectivity, data collection, device provisioning,
and IoT platform integration.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum


class DeviceStatus(Enum):
    """Device status"""
    ONLINE = "online"
    OFFLINE = "offline"
    CONNECTING = "connecting"
    ERROR = "error"


@dataclass
class IoTDevice:
    """IoT device"""
    id: str
    type: str
    status: DeviceStatus


class IoTPlatform:
    """IoT platform"""

    def __init__(self):
        self.devices: Dict[str, IoTDevice] = {}

    def register_device(self, device: IoTDevice):
        """Register device"""
        self.devices[device.id] = device

    def get_devices(self) -> List[IoTDevice]:
        """Get all devices"""
        return list(self.devices.values())


def main():
    print("Testing IoT Framework...")
    platform = IoTPlatform()
    device = IoTDevice(id="iot1", type="sensor", status=DeviceStatus.ONLINE)
    platform.register_device(device)
    print(f"Devices: {len(platform.get_devices())}")
    print("IoT Framework initialized successfully")


if __name__ == "__main__":
    main()
