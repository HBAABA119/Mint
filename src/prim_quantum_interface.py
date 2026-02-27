"""
Prim Quantum Interface
Provides quantum device interface, hardware abstraction, calibration,
device management, and quantum hardware control.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum


class DeviceType(Enum):
    """Quantum device types"""
    SIMULATOR = "simulator"
    SUPERCONDUCTING = "superconducting"
    ION_TRAP = "ion_trap"
    PHOTONIC = "photonic"


@dataclass
class QuantumDevice:
    """Quantum device"""
    id: str
    type: DeviceType
    qubits: int


class QuantumInterface:
    """Quantum hardware interface"""

    def __init__(self):
        self.devices: Dict[str, QuantumDevice] = {}

    def add_device(self, device: QuantumDevice):
        """Add quantum device"""
        self.devices[device.id] = device

    def get_device(self, id: str) -> Optional[QuantumDevice]:
        """Get device"""
        return self.devices.get(id)


def main():
    print("Testing Quantum Interface...")
    interface = QuantumInterface()
    device = QuantumDevice(id="dev1", type=DeviceType.SIMULATOR, qubits=5)
    interface.add_device(device)
    print(f"Device: {device.id}")
    print("Quantum Interface initialized successfully")


if __name__ == "__main__":
    main()
