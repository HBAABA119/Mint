"""
Prim Resource Management
Provides resource allocation, monitoring, scheduling, quotas,
and capacity planning.
"""

import time
import threading
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum


class ResourceType(Enum):
    """Resource types"""
    CPU = "cpu"
    MEMORY = "memory"
    DISK = "disk"
    NETWORK = "network"
    GPU = "gpu"
    CUSTOM = "custom"


class AllocationPolicy(Enum):
    """Allocation policies"""
    FIFO = "fifo"
    PRIORITY = "priority"
    FAIR_SHARE = "fair_share"
    PROPORTIONAL = "proportional"


@dataclass
class Resource:
    """Compute resource"""
    id: str
    type: ResourceType
    capacity: float
    allocated: float = 0.0
    available: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ResourceRequest:
    """Resource request"""
    id: str
    resources: Dict[ResourceType, float]
    priority: int = 0
    duration: Optional[float] = None


@dataclass
class ResourceAllocation:
    """Resource allocation"""
    id: str
    request_id: str
    resources: Dict[ResourceType, float]
    allocated_at: float
    expires_at: Optional[float] = None


class ResourcePool:
    """Resource pool"""

    def __init__(self, name: str, resource_type: ResourceType, capacity: float):
        self.name = name
        self.resource_type = resource_type
        self.capacity = capacity
        self.available = capacity
        self.allocated = 0.0
        self.allocations: Dict[str, float] = {}
        self.lock = threading.Lock()

    def allocate(self, request_id: str, amount: float) -> bool:
        """Allocate resource"""
        with self.lock:
            if amount > self.available:
                return False

            self.available -= amount
            self.allocated += amount
            self.allocations[request_id] = amount
            return True

    def release(self, request_id: str):
        """Release resource"""
        with self.lock:
            if request_id in self.allocations:
                amount = self.allocations[request_id]
                self.available += amount
                self.allocated -= amount
                del self.allocations[request_id]

    def get_utilization(self) -> float:
        """Get utilization percentage"""
        return (self.allocated / self.capacity) * 100 if self.capacity > 0 else 0

    def get_status(self) -> Dict[str, float]:
        """Get pool status"""
        return {
            "capacity": self.capacity,
            "allocated": self.allocated,
            "available": self.available,
            "utilization": self.get_utilization()
        }


class ResourceManager:
    """Resource manager"""

    def __init__(self):
        self.pools: Dict[str, ResourcePool] = {}
        self.allocations: Dict[str, ResourceAllocation] = {}
        self.requests: List[ResourceRequest] = []
        self.allocation_counter = 0
        self.policy = AllocationPolicy.FIFO

    def add_pool(self, name: str, resource_type: ResourceType, capacity: float):
        """Add resource pool"""
        pool = ResourcePool(name, resource_type, capacity)
        self.pools[name] = pool

    def allocate(self, request: ResourceRequest) -> Optional[ResourceAllocation]:
        """Allocate resources"""
        # Check if enough resources available
        for resource_type, amount in request.resources.items():
            pool = self._get_pool_for_type(resource_type)
            if not pool or pool.available < amount:
                return None

        # Allocate resources
        self.allocation_counter += 1
        allocation_id = f"alloc_{self.allocation_counter}"

        allocated_resources = {}
        for resource_type, amount in request.resources.items():
            pool = self._get_pool_for_type(resource_type)
            pool.allocate(allocation_id, amount)
            allocated_resources[resource_type] = amount

        allocation = ResourceAllocation(
            id=allocation_id,
            request_id=request.id,
            resources=allocated_resources,
            allocated_at=time.time(),
            expires_at=time.time() + request.duration if request.duration else None
        )

        self.allocations[allocation_id] = allocation
        return allocation

    def release(self, allocation_id: str):
        """Release allocation"""
        if allocation_id not in self.allocations:
            return

        allocation = self.allocations[allocation_id]

        for resource_type in allocation.resources:
            pool = self._get_pool_for_type(resource_type)
            if pool:
                pool.release(allocation_id)

        del self.allocations[allocation_id]

    def get_status(self) -> Dict[str, Any]:
        """Get resource manager status"""
        return {
            "pools": {name: pool.get_status() for name, pool in self.pools.items()},
            "allocations": len(self.allocations),
            "utilization": self._get_total_utilization()
        }

    def _get_pool_for_type(self, resource_type: ResourceType) -> Optional[ResourcePool]:
        """Get pool for resource type"""
        for pool in self.pools.values():
            if pool.resource_type == resource_type:
                return pool
        return None

    def _get_total_utilization(self) -> float:
        """Get total utilization"""
        if not self.pools:
            return 0.0

        total_util = 0
        for pool in self.pools.values():
            total_util += pool.get_utilization()

        return total_util / len(self.pools)


class ResourceMonitor:
    """Resource monitoring"""

    def __init__(self):
        self.metrics: Dict[str, List[float]] = {}
        self.thresholds: Dict[str, float] = {}
        self.alerts: List[Dict[str, Any]] = []
        self.running = False

    def start(self):
        """Start monitoring"""
        self.running = True

    def stop(self):
        """Stop monitoring"""
        self.running = False

    def collect_metrics(self, resource_manager: ResourceManager):
        """Collect resource metrics"""
        status = resource_manager.get_status()

        for pool_name, pool_status in status["pools"].items():
            if pool_name not in self.metrics:
                self.metrics[pool_name] = []

            self.metrics[pool_name].append(pool_status["utilization"])

            # Keep last 100 values
            if len(self.metrics[pool_name]) > 100:
                self.metrics[pool_name] = self.metrics[pool_name][-100:]

            # Check thresholds
            if pool_name in self.thresholds:
                if pool_status["utilization"] > self.thresholds[pool_name]:
                    self.alerts.append({
                        "pool": pool_name,
                        "utilization": pool_status["utilization"],
                        "threshold": self.thresholds[pool_name],
                        "timestamp": time.time()
                    })

    def get_metrics(self, pool_name: str) -> List[float]:
        """Get metrics for pool"""
        return self.metrics.get(pool_name, [])

    def set_threshold(self, pool_name: str, threshold: float):
        """Set alert threshold"""
        self.thresholds[pool_name] = threshold

    def get_alerts(self) -> List[Dict[str, Any]]:
        """Get alerts"""
        return self.alerts.copy()


class ResourceScheduler:
    """Resource scheduler"""

    def __init__(self, policy: AllocationPolicy = AllocationPolicy.FIFO):
        self.policy = policy
        self.queue: List[ResourceRequest] = []

    def submit(self, request: ResourceRequest):
        """Submit resource request"""
        self.queue.append(request)

    def schedule(self, resource_manager: ResourceManager) -> List[ResourceAllocation]:
        """Schedule pending requests"""
        allocations = []

        if self.policy == AllocationPolicy.PRIORITY:
            self.queue.sort(key=lambda r: r.priority, reverse=True)

        for request in self.queue[:]:
            allocation = resource_manager.allocate(request)
            if allocation:
                allocations.append(allocation)
                self.queue.remove(request)

        return allocations

    def get_queue_size(self) -> int:
        """Get queue size"""
        return len(self.queue)


class QuotaManager:
    """Quota management"""

    def __init__(self):
        self.quotas: Dict[str, Dict[ResourceType, float]] = {}
        self.usage: Dict[str, Dict[ResourceType, float]] = {}

    def set_quota(self, user_id: str, resource_type: ResourceType, limit: float):
        """Set quota for user"""
        if user_id not in self.quotas:
            self.quotas[user_id] = {}
        self.quotas[user_id][resource_type] = limit

    def check_quota(self, user_id: str, resource_type: ResourceType, amount: float) -> bool:
        """Check if request fits within quota"""
        if user_id not in self.quotas:
            return True

        if resource_type not in self.quotas[user_id]:
            return True

        limit = self.quotas[user_id][resource_type]
        usage = self.usage.get(user_id, {}).get(resource_type, 0)

        return (usage + amount) <= limit

    def record_usage(self, user_id: str, resource_type: ResourceType, amount: float):
        """Record resource usage"""
        if user_id not in self.usage:
            self.usage[user_id] = {}
        self.usage[user_id][resource_type] = self.usage[user_id].get(resource_type, 0) + amount

    def get_usage(self, user_id: str) -> Dict[ResourceType, float]:
        """Get usage for user"""
        return self.usage.get(user_id, {})

    def get_remaining(self, user_id: str, resource_type: ResourceType) -> float:
        """Get remaining quota"""
        if user_id not in self.quotas:
            return float('inf')

        if resource_type not in self.quotas[user_id]:
            return float('inf')

        limit = self.quotas[user_id][resource_type]
        usage = self.usage.get(user_id, {}).get(resource_type, 0)

        return max(0, limit - usage)


class CapacityPlanner:
    """Capacity planning"""

    def __init__(self):
        self.history: List[Dict[str, float]] = []
        self.forecasts: Dict[str, List[float]] = {}

    def record_usage(self, resource_manager: ResourceManager):
        """Record resource usage"""
        status = resource_manager.get_status()
        self.history.append({
            "timestamp": time.time(),
            "utilization": status["utilization"],
            **{f"pool_{name}": pool_status["utilization"]
               for name, pool_status in status["pools"].items()}
        })

    def forecast(self, pool_name: str, periods: int = 10) -> List[float]:
        """Forecast resource usage"""
        if pool_name not in self.history:
            return []

        # Simple moving average forecast
        values = [h.get(f"pool_{pool_name}", 0) for h in self.history[-10:]]
        forecast = []

        for _ in range(periods):
            avg = sum(values) / len(values) if values else 0
            forecast.append(avg)
            values.append(avg)
            values = values[-10:]

        self.forecasts[pool_name] = forecast
        return forecast

    def get_capacity_recommendations(self) -> Dict[str, str]:
        """Get capacity recommendations"""
        recommendations = {}

        for pool_name in self.forecasts:
            forecast = self.forecasts[pool_name]
            if forecast:
                avg_forecast = sum(forecast) / len(forecast)

                if avg_forecast > 90:
                    recommendations[pool_name] = "URGENT: Scale up immediately"
                elif avg_forecast > 75:
                    recommendations[pool_name] = "WARNING: Consider scaling up"
                elif avg_forecast < 20:
                    recommendations[pool_name] = "INFO: Consider scaling down"

        return recommendations


def create_resource_manager() -> ResourceManager:
    """Create resource manager"""
    return ResourceManager()


def main():
    """Main entry point for testing"""
    print("Testing Resource Management...")

    # Create resource manager
    rm = create_resource_manager()

    # Add resource pools
    rm.add_pool("cpu_pool", ResourceType.CPU, 100.0)
    rm.add_pool("memory_pool", ResourceType.MEMORY, 16.0)
    rm.add_pool("gpu_pool", ResourceType.GPU, 4.0)

    # Create resource request
    request = ResourceRequest(
        id="req1",
        resources={
            ResourceType.CPU: 10.0,
            ResourceType.MEMORY: 2.0
        },
        priority=1,
        duration=60.0
    )

    # Allocate resources
    allocation = rm.allocate(request)
    print(f"Allocation: {allocation.id if allocation else 'None'}")

    # Get status
    status = rm.get_status()
    print(f"Status: {status['allocations']} allocations")

    # Test resource monitor
    monitor = ResourceMonitor()
    monitor.start()
    monitor.collect_metrics(rm)
    metrics = monitor.get_metrics("cpu_pool")
    print(f"Metrics: {len(metrics)} samples")

    # Test scheduler
    scheduler = ResourceScheduler()
    scheduler.submit(request)
    scheduled = scheduler.schedule(rm)
    print(f"Scheduled: {len(scheduled)} allocations")

    # Test quota manager
    quota_mgr = QuotaManager()
    quota_mgr.set_quota("user1", ResourceType.CPU, 50.0)
    has_quota = quota_mgr.check_quota("user1", ResourceType.CPU, 30.0)
    print(f"Has quota: {has_quota}")

    # Test capacity planner
    planner = CapacityPlanner()
    for _ in range(20):
        planner.record_usage(rm)

    forecast = planner.forecast("cpu_pool", periods=5)
    print(f"Forecast: {len(forecast)} periods")

    recommendations = planner.get_capacity_recommendations()
    print(f"Recommendations: {len(recommendations)}")

    # Cleanup
    if allocation:
        rm.release(allocation.id)

    print("\nResource Management initialized successfully")


if __name__ == "__main__":
    main()
