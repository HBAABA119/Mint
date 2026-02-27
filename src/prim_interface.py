"""
Prim Hardware Interface
Provides hardware abstraction, device interfaces, protocol support,
hardware discovery, and interface management.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum


class InterfaceType(Enum):
    """Interface types"""
    GPIO = "gpio"
    I2C = "i2c"
    SPI = "spi"
    UART = "uart"


@dataclass
class Interface:
    """Hardware interface"""
    id: str
    type: InterfaceType
    address: str


class InterfaceManager:
    """Interface manager"""

    def __init__(self):
        self.interfaces: Dict[str, Interface] = {}

    def add_interface(self, interface: Interface):
        """Add interface"""
        self.interfaces[interface.id] = interface

    def get_interfaces(self) -> List[Interface]:
        """Get all interfaces"""
        return list(self.interfaces.values())


def main():
    print("Testing Hardware Interface...")
    manager = InterfaceManager()
    interface = Interface(id="iface1", type=InterfaceType.GPIO, address="0x1000")
    manager.add_interface(interface)
    print(f"Interfaces: {len(manager.get_interfaces())}")
    print("Hardware Interface initialized successfully")


if __name__ == "__main__":
    main()
