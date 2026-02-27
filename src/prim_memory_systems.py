"""
Prim Memory Systems
Provides working memory, long-term memory, episodic memory,
semantic memory, and memory management.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum


class MemoryType(Enum):
    """Memory types"""
    WORKING = "working"
    EPISODIC = "episodic"
    SEMANTIC = "semantic"
    PROCEDURAL = "procedural"


@dataclass
class Memory:
    """Memory"""
    id: str
    type: MemoryType
    content: Any
    timestamp: float


class MemorySystem:
    """Memory system"""

    def __init__(self):
        self.memories: Dict[str, Memory] = {}

    def store(self, memory: Memory):
        """Store memory"""
        self.memories[memory.id] = memory

    def retrieve(self, id: str) -> Optional[Memory]:
        """Retrieve memory"""
        return self.memories.get(id)


def main():
    print("Testing Memory Systems...")
    system = MemorySystem()
    memory = Memory(id="mem1", type=MemoryType.WORKING, content="data", timestamp=0.0)
    system.store(memory)
    retrieved = system.retrieve("mem1")
    print(f"Retrieved: {retrieved.id if retrieved else 'None'}")
    print("Memory Systems initialized successfully")


if __name__ == "__main__":
    main()
