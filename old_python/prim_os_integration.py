"""
Prim OS Integration
Provides OS-level integration, process management, system calls,
file system operations, and platform-specific features.
"""

import os
import sys
import platform
import subprocess
import time
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass
from enum import Enum


class OSType(Enum):
    """OS types"""
    WINDOWS = "windows"
    LINUX = "linux"
    MACOS = "macos"
    UNIX = "unix"


class ProcessState(Enum):
    """Process states"""
    RUNNING = "running"
    STOPPED = "stopped"
    BLOCKED = "blocked"
    ZOMBIE = "zombie"


@dataclass
class Process:
    """Process information"""
    pid: int
    name: str
    state: ProcessState
    cpu_usage: float
    memory_usage: float


class OSManager:
    """OS integration manager"""

    def __init__(self):
        self.os_type = self._detect_os()
        self.processes: Dict[int, Process] = {}

    def _detect_os(self) -> OSType:
        """Detect OS type"""
        system = platform.system().lower()

        if system == "windows":
            return OSType.WINDOWS
        elif system == "linux":
            return OSType.LINUX
        elif system == "darwin":
            return OSType.MACOS
        else:
            return OSType.UNIX

    def get_os_info(self) -> Dict[str, str]:
        """Get OS information"""
        return {
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "python_version": sys.version
        }

    def execute_command(self, command: str, shell: bool = True) -> subprocess.CompletedProcess:
        """Execute shell command"""
        return subprocess.run(command, shell=shell, capture_output=True, text=True)

    def get_processes(self) -> List[Process]:
        """Get running processes"""
        processes = []

        try:
            if self.os_type == OSType.WINDOWS:
                result = self.execute_command("tasklist")
                lines = result.stdout.split('\n')[3:]  # Skip header

                for line in lines:
                    if not line.strip():
                        continue

                    parts = line.split()
                    if len(parts) >= 2:
                        name = parts[0]
                        pid = int(parts[1]) if parts[1].isdigit() else 0

                        processes.append(Process(
                            pid=pid,
                            name=name,
                            state=ProcessState.RUNNING,
                            cpu_usage=0.0,
                            memory_usage=0.0
                        ))

            elif self.os_type in [OSType.LINUX, OSType.MACOS]:
                result = self.execute_command("ps aux")
                lines = result.stdout.split('\n')[1:]  # Skip header

                for line in lines:
                    if not line.strip():
                        continue

                    parts = line.split(None, 10)
                    if len(parts) >= 11:
                        name = parts[10]
                        pid = int(parts[1])
                        cpu = float(parts[2])
                        mem = float(parts[3])

                        processes.append(Process(
                            pid=pid,
                            name=name,
                            state=ProcessState.RUNNING,
                            cpu_usage=cpu,
                            memory_usage=mem
                        ))

        except Exception as e:
            print(f"Error getting processes: {e}")

        return processes

    def kill_process(self, pid: int) -> bool:
        """Kill process by PID"""
        try:
            if self.os_type == OSType.WINDOWS:
                self.execute_command(f"taskkill /F /PID {pid}")
            else:
                self.execute_command(f"kill {pid}")
            return True
        except Exception as e:
            print(f"Error killing process: {e}")
            return False


class FileSystem:
    """File system operations"""

    def __init__(self):
        self.current_directory = os.getcwd()

    def list_directory(self, path: Optional[str] = None) -> List[Dict[str, Any]]:
        """List directory contents"""
        target_path = path or self.current_directory

        try:
            entries = []
            for entry in os.listdir(target_path):
                full_path = os.path.join(target_path, entry)
                stat = os.stat(full_path)

                entries.append({
                    "name": entry,
                    "path": full_path,
                    "is_file": os.path.isfile(full_path),
                    "is_dir": os.path.isdir(full_path),
                    "size": stat.st_size,
                    "modified": stat.st_mtime
                })

            return entries
        except Exception as e:
            print(f"Error listing directory: {e}")
            return []

    def read_file(self, path: str) -> Optional[str]:
        """Read file contents"""
        try:
            with open(path, 'r') as f:
                return f.read()
        except Exception as e:
            print(f"Error reading file: {e}")
            return None

    def write_file(self, path: str, content: str):
        """Write file contents"""
        try:
            with open(path, 'w') as f:
                f.write(content)
        except Exception as e:
            print(f"Error writing file: {e}")

    def create_directory(self, path: str):
        """Create directory"""
        try:
            os.makedirs(path, exist_ok=True)
        except Exception as e:
            print(f"Error creating directory: {e}")

    def delete_file(self, path: str):
        """Delete file"""
        try:
            os.remove(path)
        except Exception as e:
            print(f"Error deleting file: {e}")

    def get_file_info(self, path: str) -> Optional[Dict[str, Any]]:
        """Get file information"""
        try:
            stat = os.stat(path)
            return {
                "size": stat.st_size,
                "created": stat.st_ctime,
                "modified": stat.st_mtime,
                "accessed": stat.st_atime,
                "is_file": os.path.isfile(path),
                "is_dir": os.path.isdir(path)
            }
        except Exception as e:
            print(f"Error getting file info: {e}")
            return None


class SystemMonitor:
    """System monitoring"""

    def __init__(self):
        self.os_manager = OSManager()

    def get_cpu_usage(self) -> float:
        """Get CPU usage"""
        try:
            if self.os_manager.os_type == OSType.WINDOWS:
                result = self.os_manager.execute_command("wmic cpu get loadpercentage")
                lines = result.stdout.split('\n')
                for line in lines:
                    if line.strip().isdigit():
                        return float(line.strip())
            else:
                result = self.os_manager.execute_command("top -bn1 | grep 'Cpu(s)'")
                # Parse CPU usage from output
                lines = result.stdout.split('\n')
                for line in lines:
                    if 'us' in line:
                        parts = line.split(',')
                        for part in parts:
                            if 'us' in part:
                                return float(part.strip().replace('us', '').strip())
        except Exception as e:
            print(f"Error getting CPU usage: {e}")

        return 0.0

    def get_memory_usage(self) -> Dict[str, int]:
        """Get memory usage"""
        try:
            if self.os_manager.os_type == OSType.WINDOWS:
                result = self.os_manager.execute_command("wmic OS get TotalVisibleMemorySize,FreePhysicalMemory")
                lines = result.stdout.split('\n')
                for line in lines:
                    parts = line.split()
                    if len(parts) >= 2 and parts[0].isdigit():
                        total = int(parts[0])
                        free = int(parts[1])
                        return {
                            "total": total,
                            "used": total - free,
                            "free": free
                        }
            else:
                result = self.os_manager.execute_command("free -b")
                lines = result.stdout.split('\n')
                for line in lines:
                    if line.startswith('Mem:'):
                        parts = line.split()
                        if len(parts) >= 3:
                            total = int(parts[1])
                            used = int(parts[2])
                            free = int(parts[3])
                            return {
                                "total": total,
                                "used": used,
                                "free": free
                            }
        except Exception as e:
            print(f"Error getting memory usage: {e}")

        return {"total": 0, "used": 0, "free": 0}

    def get_disk_usage(self, path: str = "/") -> Dict[str, int]:
        """Get disk usage"""
        try:
            stat = os.statvfs(path)
            total = stat.f_blocks * stat.f_frsize
            free = stat.f_bavail * stat.f_frsize
            used = total - free

            return {
                "total": total,
                "used": used,
                "free": free
            }
        except Exception as e:
            print(f"Error getting disk usage: {e}")

        return {"total": 0, "used": 0, "free": 0}


class EnvironmentManager:
    """Environment variable management"""

    def __init__(self):
        self.variables: Dict[str, str] = dict(os.environ)

    def get_variable(self, name: str) -> Optional[str]:
        """Get environment variable"""
        return os.environ.get(name)

    def set_variable(self, name: str, value: str):
        """Set environment variable"""
        os.environ[name] = value
        self.variables[name] = value

    def unset_variable(self, name: str):
        """Unset environment variable"""
        if name in os.environ:
            del os.environ[name]
        if name in self.variables:
            del self.variables[name]

    def get_all_variables(self) -> Dict[str, str]:
        """Get all environment variables"""
        return self.variables.copy()


def create_os_manager() -> OSManager:
    """Create OS manager"""
    return OSManager()


def main():
    """Main entry point for testing"""
    print("Testing OS Integration...")

    # Create OS manager
    os_manager = create_os_manager()

    # Get OS info
    os_info = os_manager.get_os_info()
    print(f"OS: {os_info['system']} {os_info['release']}")

    # Test file system
    fs = FileSystem()
    entries = fs.list_directory()
    print(f"Directory entries: {len(entries)}")

    # Test system monitor
    monitor = SystemMonitor()
    cpu = monitor.get_cpu_usage()
    print(f"CPU usage: {cpu:.1f}%")

    memory = monitor.get_memory_usage()
    print(f"Memory: {memory['used'] / 1024 / 1024:.1f} MB used")

    # Test environment manager
    env = EnvironmentManager()
    test_var = env.get_variable("PATH")
    print(f"PATH length: {len(test_var) if test_var else 0}")

    # Test process management
    processes = os_manager.get_processes()
    print(f"Processes: {len(processes)}")

    print("\nOS Integration initialized successfully")


if __name__ == "__main__":
    main()
