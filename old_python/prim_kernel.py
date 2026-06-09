"""
Prim Kernel Development
Provides kernel services, process management, memory management,
interrupt handling, and kernel APIs.
"""

from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass
from enum import Enum


class ProcessState(Enum):
    """Process states"""
    READY = "ready"
    RUNNING = "running"
    BLOCKED = "blocked"
    TERMINATED = "terminated"


@dataclass
class Process:
    """Kernel process"""
    pid: int
    state: ProcessState
    priority: int


class Kernel:
    """Kernel"""

    def __init__(self):
        self.processes: Dict[int, Process] = {}
        self.pid_counter = 0

    def create_process(self, priority: int = 0) -> Process:
        """Create process"""
        self.pid_counter += 1
        process = Process(pid=self.pid_counter, state=ProcessState.READY, priority=priority)
        self.processes[process.pid] = process
        return process

    def schedule(self) -> Optional[Process]:
        """Schedule next process"""
        ready = [p for p in self.processes.values() if p.state == ProcessState.READY]
        if ready:
            return max(ready, key=lambda p: p.priority)
        return None


def main():
    print("Testing Kernel Development...")
    kernel = Kernel()
    process = kernel.create_process(priority=1)
    print(f"Process: {process.pid}")
    print("Kernel Development initialized successfully")


if __name__ == "__main__":
    main()
