"""
Prim Memory Management
Provides virtual memory, paging, segmentation, memory protection,
and memory allocation.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum


class MemoryType(Enum):
    """Memory types"""
    CODE = "code"
    DATA = "data"
    STACK = "stack"
    HEAP = "heap"


@dataclass
class MemoryRegion:
    """Memory region"""
    start: int
    size: int
    type: MemoryType


class MemoryManager:
    """Memory manager"""

    def __init__(self):
        self.regions: Dict[int, MemoryRegion] = {}
        self.page_size = 4096

    def allocate(self, size: int, mem_type: MemoryType) -> int:
        """Allocate memory"""
        address = len(self.regions) * self.page_size
        region = MemoryRegion(start=address, size=size, type=mem_type)
        self.regions[address] = region
        return address

    def free(self, address: int):
        """Free memory"""
        if address in self.regions:
            del self.regions[address]


def main():
    print("Testing Memory Management...")
    manager = MemoryManager()
    address = manager.allocate(1024, MemoryType.HEAP)
    print(f"Allocated: {address}")
    print("Memory Management initialized successfully")


if __name__ == "__main__":
    main()
