"""
Prim Runtime Foundation
Provides core Prim runtime implementation, memory management primitives, basic I/O operations,
error handling system, and cross-platform compatibility layer.
"""

import os
import sys
import platform
import ctypes
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
import gc


class Platform(Enum):
    """Platform types"""
    WINDOWS = "windows"
    LINUX = "linux"
    MACOS = "macos"
    UNKNOWN = "unknown"


class MemoryErrorType(Enum):
    """Memory error types"""
    ALLOCATION_FAILED = "allocation_failed"
    OUT_OF_MEMORY = "out_of_memory"
    INVALID_ACCESS = "invalid_access"
    LEAK_DETECTED = "leak_detected"


@dataclass
class MemoryBlock:
    """Memory block representation"""
    address: int
    size: int
    data: bytes = b""
    allocated: bool = True


@dataclass
class MemoryStats:
    """Memory statistics"""
    total_allocated: int = 0
    total_freed: int = 0
    current_usage: int = 0
    peak_usage: int = 0
    allocation_count: int = 0
    deallocation_count: int = 0


class MemoryManager:
    """Memory management primitives"""

    def __init__(self):
        self.blocks: Dict[int, MemoryBlock] = {}
        self.stats = MemoryStats()
        self.next_address = 0x1000
        self.leak_detection_enabled = True

    def allocate(self, size: int) -> MemoryBlock:
        """Allocate a memory block"""
        if size <= 0:
            raise ValueError("Size must be positive")

        address = self.next_address
        self.next_address += size

        block = MemoryBlock(
            address=address,
            size=size,
            data=bytes(size)
        )

        self.blocks[address] = block
        self.stats.total_allocated += size
        self.stats.current_usage += size
        self.stats.allocation_count += 1
        self.stats.peak_usage = max(self.stats.peak_usage, self.stats.current_usage)

        return block

    def free(self, address: int) -> bool:
        """Free a memory block"""
        if address not in self.blocks:
            return False

        block = self.blocks[address]
        if not block.allocated:
            return False

        block.allocated = False
        self.stats.total_freed += block.size
        self.stats.current_usage -= block.size
        self.stats.deallocation_count += 1

        del self.blocks[address]
        return True

    def read(self, address: int, size: int) -> bytes:
        """Read from memory"""
        if address not in self.blocks:
            raise MemoryError(f"Invalid memory address: {address}")

        block = self.blocks[address]
        if not block.allocated:
            raise MemoryError(f"Memory block not allocated: {address}")

        return block.data[:size]

    def write(self, address: int, data: bytes):
        """Write to memory"""
        if address not in self.blocks:
            raise MemoryError(f"Invalid memory address: {address}")

        block = self.blocks[address]
        if not block.allocated:
            raise MemoryError(f"Memory block not allocated: {address}")

        block.data = data

    def get_stats(self) -> MemoryStats:
        """Get memory statistics"""
        return self.stats

    def detect_leaks(self) -> List[int]:
        """Detect memory leaks"""
        return [
            addr for addr, block in self.blocks.items()
            if block.allocated
        ]


class ErrorHandler:
    """Error handling system"""

    def __init__(self):
        self.error_handlers: Dict[str, Callable] = {}
        self.error_log: List[Dict] = []

    def register_handler(self, error_type: str, handler: Callable):
        """Register an error handler"""
        self.error_handlers[error_type] = handler

    def handle_error(
        self,
        error_type: str,
        message: str,
        context: Optional[Dict] = None
    ):
        """Handle an error"""
        error_info = {
            'type': error_type,
            'message': message,
            'context': context or {},
            'timestamp': None
        }

        self.error_log.append(error_info)

        # Call handler if registered
        if error_type in self.error_handlers:
            self.error_handlers[error_type](error_info)

    def get_error_log(self) -> List[Dict]:
        """Get error log"""
        return self.error_log.copy()

    def clear_error_log(self):
        """Clear error log"""
        self.error_log.clear()


class IOPrimitives:
    """Basic I/O operations"""

    def __init__(self, error_handler: ErrorHandler):
        self.error_handler = error_handler
        self.stdin = sys.stdin
        self.stdout = sys.stdout
        self.stderr = sys.stderr

    def read_line(self) -> str:
        """Read a line from stdin"""
        try:
            return self.stdin.readline()
        except Exception as e:
            self.error_handler.handle_error(
                'io_error',
                f"Failed to read input: {e}"
            )
            return ""

    def write(self, text: str):
        """Write text to stdout"""
        try:
            self.stdout.write(text)
            self.stdout.flush()
        except Exception as e:
            self.error_handler.handle_error(
                'io_error',
                f"Failed to write output: {e}"
            )

    def write_error(self, text: str):
        """Write text to stderr"""
        try:
            self.stderr.write(text)
            self.stderr.flush()
        except Exception as e:
            pass  # Can't do much if stderr fails

    def read_file(self, path: str) -> Optional[str]:
        """Read from a file"""
        try:
            with open(path, 'r') as f:
                return f.read()
        except Exception as e:
            self.error_handler.handle_error(
                'io_error',
                f"Failed to read file {path}: {e}",
                {'path': path}
            )
            return None

    def write_file(self, path: str, content: str) -> bool:
        """Write to a file"""
        try:
            with open(path, 'w') as f:
                f.write(content)
            return True
        except Exception as e:
            self.error_handler.handle_error(
                'io_error',
                f"Failed to write file {path}: {e}",
                {'path': path}
            )
            return False

    def file_exists(self, path: str) -> bool:
        """Check if a file exists"""
        return os.path.exists(path)


class PlatformLayer:
    """Cross-platform compatibility layer"""

    def __init__(self):
        self.platform = self._detect_platform()
        self.libc = None

    def _detect_platform(self) -> Platform:
        """Detect the current platform"""
        system = platform.system().lower()
        if system == 'windows':
            return Platform.WINDOWS
        elif system == 'linux':
            return Platform.LINUX
        elif system == 'darwin':
            return Platform.MACOS
        return Platform.UNKNOWN

    def get_platform(self) -> Platform:
        """Get current platform"""
        return self.platform

    def is_windows(self) -> bool:
        """Check if running on Windows"""
        return self.platform == Platform.WINDOWS

    def is_linux(self) -> bool:
        """Check if running on Linux"""
        return self.platform == Platform.LINUX

    def is_macos(self) -> bool:
        """Check if running on macOS"""
        return self.platform == Platform.MACOS

    def get_path_separator(self) -> str:
        """Get path separator for current platform"""
        return '\\' if self.is_windows() else '/'

    def get_environment_variable(self, name: str) -> Optional[str]:
        """Get an environment variable"""
        return os.environ.get(name)

    def set_environment_variable(self, name: str, value: str):
        """Set an environment variable"""
        os.environ[name] = value

    def get_cwd(self) -> str:
        """Get current working directory"""
        return os.getcwd()

    def set_cwd(self, path: str):
        """Set current working directory"""
        os.chdir(path)

    def get_system_info(self) -> Dict[str, Any]:
        """Get system information"""
        return {
            'platform': self.platform.value,
            'python_version': sys.version,
            'architecture': platform.architecture(),
            'processor': platform.processor(),
            'node': platform.node(),
            'release': platform.release(),
            'version': platform.version()
        }


class PrimRuntime:
    """Core Prim runtime"""

    def __init__(self):
        self.memory_manager = MemoryManager()
        self.error_handler = ErrorHandler()
        self.io_primitives = IOPrimitives(self.error_handler)
        self.platform_layer = PlatformLayer()
        self.running = False

        # Register default error handlers
        self.error_handler.register_handler('memory_error', self._handle_memory_error)
        self.error_handler.register_handler('io_error', self._handle_io_error)

    def _handle_memory_error(self, error_info: Dict):
        """Handle memory errors"""
        print(f"Memory Error: {error_info['message']}")

    def _handle_io_error(self, error_info: Dict):
        """Handle I/O errors"""
        print(f"I/O Error: {error_info['message']}")

    def initialize(self):
        """Initialize the runtime"""
        self.running = True

        # Set up error handlers
        sys.excepthook = self._exception_hook

    def shutdown(self):
        """Shutdown the runtime"""
        self.running = False

        # Detect memory leaks
        if self.memory_manager.leak_detection_enabled:
            leaks = self.memory_manager.detect_leaks()
            if leaks:
                print(f"Warning: {len(leaks)} memory leak(s) detected")

    def _exception_hook(self, exc_type, exc_value, exc_traceback):
        """Exception hook for unhandled exceptions"""
        self.error_handler.handle_error(
            'runtime_error',
            f"Unhandled exception: {exc_value}",
            {
                'type': exc_type.__name__,
                'traceback': exc_traceback
            }
        )

    def run(self, code: str) -> Any:
        """Run Prim code"""
        if not self.running:
            self.initialize()

        try:
            # In a real implementation, this would compile and execute Prim code
            # For now, just execute as Python
            result = eval(code, {}, {})
            return result
        except Exception as e:
            self.error_handler.handle_error(
                'runtime_error',
                f"Execution error: {e}"
            )
            return None

    def get_memory_stats(self) -> MemoryStats:
        """Get memory statistics"""
        return self.memory_manager.get_stats()

    def get_system_info(self) -> Dict[str, Any]:
        """Get system information"""
        return self.platform_layer.get_system_info()

    def is_running(self) -> bool:
        """Check if runtime is running"""
        return self.running


class RuntimeCLI:
    """Command-line interface for runtime"""

    def __init__(self):
        self.runtime = PrimRuntime()

    def run(self, args: List[str]):
        """Run CLI command"""
        if not args:
            self.show_help()
            return

        command = args[0]
        command_args = args[1:]

        if command == 'run':
            self.cmd_run(command_args)
        elif command == 'stats':
            self.cmd_stats()
        elif command == 'info':
            self.cmd_info()
        elif command == 'shell':
            self.cmd_shell()
        else:
            print(f"Unknown command: {command}")
            self.show_help()

    def cmd_run(self, args: List[str]):
        """Run Prim code"""
        if not args:
            print("Usage: run <code>")
            return

        code = ' '.join(args)
        result = self.runtime.run(code)
        print(f"Result: {result}")

    def cmd_stats(self):
        """Show memory statistics"""
        stats = self.runtime.get_memory_stats()
        print("Memory Statistics:")
        print(f"  Total Allocated: {stats.total_allocated}")
        print(f"  Total Freed: {stats.total_freed}")
        print(f"  Current Usage: {stats.current_usage}")
        print(f"  Peak Usage: {stats.peak_usage}")
        print(f"  Allocations: {stats.allocation_count}")
        print(f"  Deallocations: {stats.deallocation_count}")

    def cmd_info(self):
        """Show system information"""
        info = self.runtime.get_system_info()
        print("System Information:")
        for key, value in info.items():
            print(f"  {key}: {value}")

    def cmd_shell(self):
        """Interactive shell"""
        print("Prim Runtime Shell (type 'exit' to quit)")
        self.runtime.initialize()

        while True:
            try:
                line = input("prim> ").strip()
                if line.lower() == 'exit':
                    break
                if line:
                    result = self.runtime.run(line)
                    if result is not None:
                        print(f"=> {result}")
            except KeyboardInterrupt:
                print("\nInterrupted")
            except EOFError:
                break

        self.runtime.shutdown()

    def show_help(self):
        """Show help"""
        print("""
Prim Runtime Commands:
  run <code>       Execute Prim code
  stats            Show memory statistics
  info             Show system information
  shell            Interactive shell

Example:
  python prim_runtime.py run "1 + 2"
  python prim_runtime.py shell
""")


def main():
    """Main entry point"""
    import sys

    cli = RuntimeCLI()
    sys.exit(cli.run(sys.argv[1:]) or 0)


if __name__ == "__main__":
    main()
