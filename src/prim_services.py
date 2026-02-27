"""
Prim System Services
Provides service management, daemon processes, system monitoring,
logging services, and service discovery.
"""

import time
import threading
import logging
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum


class ServiceState(Enum):
    """Service states"""
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    FAILED = "failed"


class ServiceType(Enum):
    """Service types"""
    DAEMON = "daemon"
    SYSTEMD = "systemd"
    INIT = "init"
    WINDOWS_SERVICE = "windows_service"
    CUSTOM = "custom"


@dataclass
class Service:
    """System service"""
    name: str
    service_type: ServiceType
    command: str
    state: ServiceState = ServiceState.STOPPED
    pid: Optional[int] = None
    auto_start: bool = False
    dependencies: List[str] = field(default_factory=list)


class ServiceManager:
    """Service manager"""

    def __init__(self):
        self.services: Dict[str, Service] = {}
        self.running: Dict[str, bool] = {}

    def register_service(self, service: Service):
        """Register service"""
        self.services[service.name] = service

    def start_service(self, name: str) -> bool:
        """Start service"""
        if name not in self.services:
            return False

        service = self.services[name]

        # Check dependencies
        for dep in service.dependencies:
            if dep in self.services and not self.running.get(dep, False):
                return False

        service.state = ServiceState.STARTING

        # Start service (simplified)
        import subprocess
        try:
            process = subprocess.Popen(service.command, shell=True)
            service.pid = process.pid
            service.state = ServiceState.RUNNING
            self.running[name] = True
            return True
        except Exception as e:
            service.state = ServiceState.FAILED
            return False

    def stop_service(self, name: str) -> bool:
        """Stop service"""
        if name not in self.services:
            return False

        service = self.services[name]

        if service.pid:
            try:
                import signal
                import os
                os.kill(service.pid, signal.SIGTERM)
                service.state = ServiceState.STOPPED
                self.running[name] = False
                return True
            except Exception as e:
                return False

        return False

    def restart_service(self, name: str) -> bool:
        """Restart service"""
        self.stop_service(name)
        time.sleep(1)
        return self.start_service(name)

    def get_service_status(self, name: str) -> Optional[ServiceState]:
        """Get service status"""
        if name in self.services:
            return self.services[name].state
        return None

    def list_services(self) -> List[Service]:
        """List all services"""
        return list(self.services.values())


class Daemon:
    """Daemon process"""

    def __init__(self, name: str, func: Callable):
        self.name = name
        self.func = func
        self.running = False
        self.thread: Optional[threading.Thread] = None

    def start(self):
        """Start daemon"""
        self.running = True
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()

    def stop(self):
        """Stop daemon"""
        self.running = False
        if self.thread:
            self.thread.join()

    def _run_loop(self):
        """Daemon main loop"""
        while self.running:
            try:
                self.func()
            except Exception as e:
                print(f"Daemon error: {e}")

            time.sleep(1)


class ServiceDiscovery:
    """Service discovery"""

    def __init__(self):
        self.services: Dict[str, Dict[str, Any]] = {}

    def register_service(self, name: str, address: str, port: int, metadata: Optional[Dict] = None):
        """Register service"""
        self.services[name] = {
            "address": address,
            "port": port,
            "metadata": metadata or {},
            "registered_at": time.time()
        }

    def discover_service(self, name: str) -> Optional[Dict[str, Any]]:
        """Discover service"""
        return self.services.get(name)

    def list_services(self) -> List[str]:
        """List available services"""
        return list(self.services.keys())

    def health_check(self, name: str) -> bool:
        """Health check for service"""
        service = self.services.get(name)
        if not service:
            return False

        # Simplified health check
        return True


class LoggingService:
    """Logging service"""

    def __init__(self, name: str = "logger"):
        self.name = name
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        # File handler
        file_handler = logging.FileHandler(f"{name}.log")
        file_handler.setLevel(logging.INFO)

        # Formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)

        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)

    def log(self, level: str, message: str):
        """Log message"""
        if level == "info":
            self.logger.info(message)
        elif level == "warning":
            self.logger.warning(message)
        elif level == "error":
            self.logger.error(message)
        elif level == "debug":
            self.logger.debug(message)

    def info(self, message: str):
        """Log info message"""
        self.log("info", message)

    def warning(self, message: str):
        """Log warning message"""
        self.log("warning", message)

    def error(self, message: str):
        """Log error message"""
        self.log("error", message)

    def debug(self, message: str):
        """Log debug message"""
        self.log("debug", message)


class SystemMonitor:
    """System monitoring service"""

    def __init__(self):
        self.metrics: Dict[str, List[float]] = {}
        self.running = False

    def start(self):
        """Start monitoring"""
        self.running = True
        threading.Thread(target=self._monitor_loop, daemon=True).start()

    def stop(self):
        """Stop monitoring"""
        self.running = False

    def _monitor_loop(self):
        """Monitoring loop"""
        while self.running:
            self._collect_metrics()
            time.sleep(1)

    def _collect_metrics(self):
        """Collect system metrics"""
        import psutil

        # CPU
        cpu = psutil.cpu_percent()
        if "cpu" not in self.metrics:
            self.metrics["cpu"] = []
        self.metrics["cpu"].append(cpu)

        # Memory
        mem = psutil.virtual_memory().percent
        if "memory" not in self.metrics:
            self.metrics["memory"] = []
        self.metrics["memory"].append(mem)

        # Keep last 100 values
        for key in self.metrics:
            if len(self.metrics[key]) > 100:
                self.metrics[key] = self.metrics[key][-100:]

    def get_metrics(self) -> Dict[str, List[float]]:
        """Get collected metrics"""
        return self.metrics.copy()


class ServiceManagerExtended:
    """Extended service manager"""

    def __init__(self):
        self.service_manager = ServiceManager()
        self.discovery = ServiceDiscovery()
        self.logger = LoggingService("service_manager")
        self.monitor = SystemMonitor()

    def start_all(self):
        """Start all auto-start services"""
        for name, service in self.service_manager.services.items():
            if service.auto_start:
                self.service_manager.start_service(name)
                self.logger.info(f"Started service: {name}")

    def stop_all(self):
        """Stop all services"""
        for name in self.service_manager.services:
            self.service_manager.stop_service(name)
            self.logger.info(f"Stopped service: {name}")

    def get_status(self) -> Dict[str, Any]:
        """Get overall status"""
        services = self.service_manager.list_services()

        return {
            "services": len(services),
            "running": sum(1 for s in services if s.state == ServiceState.RUNNING),
            "stopped": sum(1 for s in services if s.state == ServiceState.STOPPED),
            "discovered_services": len(self.discovery.list_services())
        }


def create_service_manager() -> ServiceManagerExtended:
    """Create service manager"""
    return ServiceManagerExtended()


def main():
    """Main entry point for testing"""
    print("Testing System Services...")

    # Create service manager
    manager = create_service_manager()

    # Register services
    service1 = Service(
        name="service1",
        service_type=ServiceType.CUSTOM,
        command="echo 'test'",
        auto_start=True
    )

    manager.service_manager.register_service(service1)

    # Start service
    started = manager.service_manager.start_service("service1")
    print(f"Service started: {started}")

    # Test daemon
    def daemon_func():
        print("Daemon running")

    daemon = Daemon("test_daemon", daemon_func)
    daemon.start()
    time.sleep(1)
    daemon.stop()

    # Test service discovery
    manager.discovery.register_service("test_service", "localhost", 8080)
    discovered = manager.discovery.discover_service("test_service")
    print(f"Discovered service: {discovered is not None}")

    # Test logging
    manager.logger.info("Test message")
    print("Logged message")

    # Get status
    status = manager.get_status()
    print(f"Status: {status}")

    print("\nSystem Services initialized successfully")


if __name__ == "__main__":
    main()
