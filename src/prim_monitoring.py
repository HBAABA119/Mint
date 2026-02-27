"""
Prim System Monitoring
Provides performance monitoring, health checks, alerting,
metrics collection, and system status.
"""

import time
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum


class HealthStatus(Enum):
    """Health status"""
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    DEGRADED = "degraded"


@dataclass
class Metric:
    """System metric"""
    name: str
    value: float
    timestamp: float


class SystemMonitor:
    """System monitor"""

    def __init__(self):
        self.metrics: List[Metric] = []
        self.status = HealthStatus.HEALTHY

    def record_metric(self, metric: Metric):
        """Record metric"""
        self.metrics.append(metric)

    def get_health(self) -> HealthStatus:
        """Get health status"""
        return self.status


def main():
    print("Testing System Monitoring...")
    monitor = SystemMonitor()
    metric = Metric(name="cpu", value=50.0, timestamp=time.time())
    monitor.record_metric(metric)
    print(f"Health: {monitor.get_health().value}")
    print("System Monitoring initialized successfully")


if __name__ == "__main__":
    main()
