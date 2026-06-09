"""
Prim Hardware Abstraction Layer
Provides hardware abstraction, device drivers, interrupt handling,
memory-mapped I/O, and platform abstraction.
"""

import ctypes
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass
from enum import Enum


class DeviceType(Enum):
    """Device types"""
    CPU = "cpu"
    GPU = "gpu"
    MEMORY = "memory"
    STORAGE = "storage"
    NETWORK = "network"
    INPUT = "input"
    OUTPUT = "output"


class InterruptType(Enum):
    """Interrupt types"""
    HARDWARE = "hardware"
    SOFTWARE = "software"
    EXCEPTION = "exception"
    TIMER = "timer"


@dataclass
class Device:
    """Hardware device"""
    id: str
    type: DeviceType
    name: str
    base_address: int
    registers: Dict[str, int]
    interrupt_line: Optional[int] = None


class HAL:
    """Hardware Abstraction Layer"""

    def __init__(self):
        self.devices: Dict[str, Device] = {}
        self.memory_map: Dict[int, Any] = {}
        self.interrupt_handlers: Dict[int, Callable] = {}
        self.io_ports: Dict[int, Callable] = {}

    def register_device(self, device: Device):
        """Register hardware device"""
        self.devices[device.id] = device

    def read_register(self, device_id: str, register: str) -> int:
        """Read device register"""
        if device_id not in self.devices:
            raise ValueError(f"Device {device_id} not found")

        device = self.devices[device_id]
        if register not in device.registers:
            raise ValueError(f"Register {register} not found")

        # Simulated register read
        return device.registers[register]

    def write_register(self, device_id: str, register: str, value: int):
        """Write device register"""
        if device_id not in self.devices:
            raise ValueError(f"Device {device_id} not found")

        device = self.devices[device_id]
        if register not in device.registers:
            raise ValueError(f"Register {register} not found")

        device.registers[register] = value

    def map_memory(self, address: int, size: int) -> Any:
        """Map physical memory to virtual address"""
        if address in self.memory_map:
            return self.memory_map[address]

        # Simulated memory mapping
        memory = bytearray(size)
        self.memory_map[address] = memory
        return memory

    def unmap_memory(self, address: int):
        """Unmap memory"""
        if address in self.memory_map:
            del self.memory_map[address]

    def register_interrupt_handler(self, interrupt_line: int, handler: Callable):
        """Register interrupt handler"""
        self.interrupt_handlers[interrupt_line] = handler

    def trigger_interrupt(self, interrupt_line: int):
        """Trigger interrupt"""
        if interrupt_line in self.interrupt_handlers:
            self.interrupt_handlers[interrupt_line]()

    def register_io_port(self, port: int, handler: Callable):
        """Register I/O port handler"""
        self.io_ports[port] = handler

    def read_io_port(self, port: int) -> int:
        """Read from I/O port"""
        if port in self.io_ports:
            return self.io_ports[port]()
        return 0

    def write_io_port(self, port: int, value: int):
        """Write to I/O port"""
        if port in self.io_ports:
            self.io_ports[port](value)


class DeviceDriver:
    """Device driver"""

    def __init__(self, hal: HAL, device: Device):
        self.hal = hal
        self.device = device
        self.enabled = False

    def initialize(self):
        """Initialize device"""
        self.enabled = True

    def shutdown(self):
        """Shutdown device"""
        self.enabled = False

    def read(self, register: str) -> int:
        """Read from device register"""
        return self.hal.read_register(self.device.id, register)

    def write(self, register: str, value: int):
        """Write to device register"""
        self.hal.write_register(self.device.id, register, value)


class InterruptController:
    """Interrupt controller"""

    def __init__(self, hal: HAL):
        self.hal = hal
        self.priority_levels = 16
        self.current_priority = 0
        self.interrupt_queue: List[int] = []

    def enable_interrupt(self, line: int, priority: int):
        """Enable interrupt line"""
        self.hal.register_interrupt_handler(line, lambda: self._handle_interrupt(line, priority))

    def disable_interrupt(self, line: int):
        """Disable interrupt line"""
        if line in self.hal.interrupt_handlers:
            del self.hal.interrupt_handlers[line]

    def _handle_interrupt(self, line: int, priority: int):
        """Handle interrupt"""
        if priority >= self.current_priority:
            self.interrupt_queue.append(line)
            self.interrupt_queue.sort(key=lambda x: x)

    def process_interrupts(self):
        """Process queued interrupts"""
        while self.interrupt_queue:
            line = self.interrupt_queue.pop(0)
            if line in self.hal.interrupt_handlers:
                self.hal.interrupt_handlers[line]()


class MemoryManager:
    """Memory management"""

    def __init__(self):
        self.pages: Dict[int, bool] = {}
        self.page_size = 4096
        self.total_pages = 1024

    def allocate_page(self) -> Optional[int]:
        """Allocate memory page"""
        for page_num in range(self.total_pages):
            if page_num not in self.pages or not self.pages[page_num]:
                self.pages[page_num] = True
                return page_num * self.page_size

        return None

    def free_page(self, address: int):
        """Free memory page"""
        page_num = address // self.page_size
        if page_num in self.pages:
            self.pages[page_num] = False

    def get_status(self) -> Dict[str, int]:
        """Get memory status"""
        used = sum(1 for p in self.pages.values() if p)
        return {
            "total_pages": self.total_pages,
            "used_pages": used,
            "free_pages": self.total_pages - used
        }


class PlatformAbstraction:
    """Platform abstraction layer"""

    def __init__(self):
        self.hal = HAL()
        self.memory_manager = MemoryManager()
        self.interrupt_controller = InterruptController(self.hal)

    def get_platform_info(self) -> Dict[str, str]:
        """Get platform information"""
        import platform
        return {
            "system": platform.system(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "architecture": platform.architecture()[0]
        }

    def initialize_device(self, device: Device) -> DeviceDriver:
        """Initialize device driver"""
        self.hal.register_device(device)
        driver = DeviceDriver(self.hal, device)
        driver.initialize()
        return driver

    def get_hal(self) -> HAL:
        """Get HAL instance"""
        return self.hal


def create_hal() -> HAL:
    """Create HAL instance"""
    return HAL()


def main():
    """Main entry point for testing"""
    print("Testing Hardware Abstraction Layer...")

    # Create HAL
    hal = create_hal()

    # Create device
    device = Device(
        id="test_device",
        type=DeviceType.CPU,
        name="Test Device",
        base_address=0x1000,
        registers={"control": 0, "status": 0, "data": 0}
    )

    # Register device
    hal.register_device(device)

    # Test register operations
    hal.write_register("test_device", "control", 1)
    value = hal.read_register("test_device", "control")
    print(f"Register value: {value}")

    # Test memory mapping
    memory = hal.map_memory(0x1000, 4096)
    print(f"Memory mapped: {len(memory)} bytes")

    # Test interrupt handler
    def handler():
        print("Interrupt handled")

    hal.register_interrupt_handler(1, handler)
    hal.trigger_interrupt(1)

    # Test platform abstraction
    platform = PlatformAbstraction()
    platform_info = platform.get_platform_info()
    print(f"Platform: {platform_info['system']}")

    # Test memory manager
    mem_mgr = MemoryManager()
    page = mem_mgr.allocate_page()
    print(f"Allocated page: {page}")

    status = mem_mgr.get_status()
    print(f"Memory status: {status}")

    print("\nHardware Abstraction Layer initialized successfully")


if __name__ == "__main__":
    main()
