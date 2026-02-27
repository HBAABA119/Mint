"""
Prim Scalability Engineering
Provides horizontal scaling, load balancing, auto-scaling, capacity planning,
and distributed system scaling.
"""

import time
import threading
from typing import List, Dict, Any, Optional, Callable, Tuple
from dataclasses import dataclass, field
from enum import Enum


class ScalingDirection(Enum):
    """Scaling directions"""
    HORIZONTAL = "horizontal"
    VERTICAL = "vertical"
    BOTH = "both"


class ScalingPolicy(Enum):
    """Scaling policies"""
    MANUAL = "manual"
    AUTO_SCALE = "auto_scale"
    SCHEDULED = "scheduled"
    EVENT_DRIVEN = "event_driven"


@dataclass
class ScalingMetric:
    """Scaling metric"""
    name: str
    current_value: float
    target_value: float
    threshold: float
    scale_up_threshold: float
    scale_down_threshold: float


@dataclass
class ScalingAction:
    """Scaling action"""
    direction: ScalingDirection
    target_instances: int
    reason: str
    timestamp: float = field(default_factory=time.time)


class LoadBalancer:
    """Load balancer"""

    def __init__(self, algorithm: str = "round_robin"):
        self.algorithm = algorithm
        self.backends: List[str] = []
        self.current_index = 0
        self.weights: Dict[str, int] = {}

    def add_backend(self, backend: str, weight: int = 1):
        """Add backend"""
        self.backends.append(backend)
        self.weights[backend] = weight

    def remove_backend(self, backend: str):
        """Remove backend"""
        if backend in self.backends:
            self.backends.remove(backend)
            del self.weights[backend]

    def get_backend(self) -> Optional[str]:
        """Get next backend"""
        if not self.backends:
            return None

        if self.algorithm == "round_robin":
            backend = self.backends[self.current_index]
            self.current_index = (self.current_index + 1) % len(self.backends)
            return backend
        elif self.algorithm == "least_connections":
            # Simplified - would track connections in practice
            return self.backends[0]
        elif self.algorithm == "weighted":
            total_weight = sum(self.weights.values())
            import random
            r = random.uniform(0, total_weight)
            cumulative = 0

            for backend, weight in self.weights.items():
                cumulative += weight
                if r <= cumulative:
                    return backend

        return self.backends[0]

    def get_stats(self) -> Dict[str, Any]:
        """Get load balancer statistics"""
        return {
            "backends": len(self.backends),
            "algorithm": self.algorithm,
            "current_index": self.current_index
        }


class AutoScaler:
    """Auto-scaling manager"""

    def __init__(self, min_instances: int = 1, max_instances: int = 10):
        self.min_instances = min_instances
        self.max_instances = max_instances
        self.current_instances = min_instances
        self.metrics: Dict[str, ScalingMetric] = {}
        self.scaling_actions: List[ScalingAction] = []

    def add_metric(self, metric: ScalingMetric):
        """Add scaling metric"""
        self.metrics[metric.name] = metric

    def update_metric(self, name: str, value: float):
        """Update metric value"""
        if name in self.metrics:
            self.metrics[name].current_value = value

    def check_scaling_needed(self) -> Optional[ScalingAction]:
        """Check if scaling is needed"""
        for metric in self.metrics.values():
            # Check scale up
            if metric.current_value > metric.scale_up_threshold:
                if self.current_instances < self.max_instances:
                    action = ScalingAction(
                        direction=ScalingDirection.HORIZONTAL,
                        target_instances=self.current_instances + 1,
                        reason=f"Scale up due to {metric.name}",
                        timestamp=time.time()
                    )
                    self.current_instances += 1
                    self.scaling_actions.append(action)
                    return action

            # Check scale down
            if metric.current_value < metric.scale_down_threshold:
                if self.current_instances > self.min_instances:
                    action = ScalingAction(
                        direction=ScalingDirection.HORIZONTAL,
                        target_instances=self.current_instances - 1,
                        reason=f"Scale down due to {metric.name}",
                        timestamp=time.time()
                    )
                    self.current_instances -= 1
                    self.scaling_actions.append(action)
                    return action

        return None

    def get_status(self) -> Dict[str, Any]:
        """Get scaler status"""
        return {
            "current_instances": self.current_instances,
            "min_instances": self.min_instances,
            "max_instances": self.max_instances,
            "scaling_actions": len(self.scaling_actions)
        }


class CapacityPlanner:
    """Capacity planning"""

    def __init__(self):
        self.capacity_history: List[Dict[str, Any]] = []
        self.forecasts: List[Dict[str, float]] = []

    def record_capacity(self, instances: int, load: float, throughput: float):
        """Record capacity metrics"""
        self.capacity_history.append({
            "timestamp": time.time(),
            "instances": instances,
            "load": load,
            "throughput": throughput
        })

    def forecast_capacity(self, horizon: int = 10) -> List[Dict[str, float]]:
        """Forecast capacity needs"""
        if len(self.capacity_history) < 10:
            return []

        # Simple linear forecast
        recent = self.capacity_history[-10:]
        avg_instances = sum(h["instances"] for h in recent) / len(recent)
        avg_load = sum(h["load"] for h in recent) / len(recent)

        forecasts = []
        for i in range(horizon):
            growth_rate = 0.01  # 1% growth per period
            forecast = {
                "instances": avg_instances * (1 + growth_rate) ** i,
                "load": avg_load * (1 + growth_rate) ** i,
                "throughput": avg_instances * (1 + growth_rate) ** i
            }
            forecasts.append(forecast)

        self.forecasts = forecasts
        return forecasts

    def get_recommendations(self) -> List[str]:
        """Get capacity recommendations"""
        if not self.forecasts:
            return []

        forecasts = self.forecasts[-1]
        recommendations = []

        if forecasts["load"] > 0.8:
            recommendations.append("Consider scaling up to handle increased load")
        elif forecasts["load"] < 0.2:
            recommendations.append("Consider scaling down to reduce costs")

        return recommendations


class HorizontalScaler:
    """Horizontal scaling"""

    def __init__(self, initial_instances: int = 1):
        self.instances = initial_instances
        self.load_balancer = LoadBalancer()

    def scale_up(self, target: int) -> bool:
        """Scale up to target instances"""
        if target <= self.instances:
            return False

        # Add new instances
        for i in range(self.instances, target):
            backend = f"instance_{i}"
            self.load_balancer.add_backend(backend)

        self.instances = target
        return True

    def scale_down(self, target: int) -> bool:
        """Scale down to target instances"""
        if target >= self.instances:
            return False

        # Remove instances
        for i in range(target, self.instances):
            backend = f"instance_{i}"
            self.load_balancer.remove_backend(backend)

        self.instances = target
        return True

    def get_status(self) -> Dict[str, Any]:
        """Get scaler status"""
        return {
            "instances": self.instances,
            "load_balancer": self.load_balancer.get_stats()
        }


class VerticalScaler:
    """Vertical scaling"""

    def __init__(self):
        self.resources: Dict[str, float] = {}
        self.limits: Dict[str, float] = {}

    def set_resource(self, resource: str, amount: float):
        """Set resource allocation"""
        self.resources[resource] = amount

    def scale_up(self, resource: str, target: float) -> bool:
        """Scale up resource"""
        if resource in self.limits and target > self.limits[resource]:
            return False

        self.resources[resource] = target
        return True

    def scale_down(self, resource: str, target: float) -> bool:
        """Scale down resource"""
        self.resources[resource] = target
        return True

    def get_status(self) -> Dict[str, Any]:
        """Get vertical scaler status"""
        return {
            "resources": self.resources,
            "utilization": {k: v / self.limits.get(k, v) for k, v in self.resources.items()}
        }


class DistributedScaler:
    """Distributed scaling coordinator"""

    def __init__(self):
        self.nodes: List[str] = []
        self.scalers: Dict[str, HorizontalScaler] = {}
        self.global_scaler = AutoScaler()

    def add_node(self, node_id: str):
        """Add node to cluster"""
        self.nodes.append(node_id)
        self.scalers[node_id] = HorizontalScaler(initial_instances=1)

    def scale_cluster(self, target_instances: int) -> bool:
        """Scale entire cluster"""
        per_node = target_instances // len(self.nodes)

        for node_id, scaler in self.scalers.items():
            scaler.scale_up(per_node)

        return True

    def get_cluster_status(self) -> Dict[str, Any]:
        """Get cluster status"""
        return {
            "nodes": len(self.nodes),
            "node_status": {nid: s.get_status() for nid, s in self.scalers.items()},
            "global_status": self.global_scaler.get_status()
        }


class ScalabilityManager:
    """Scalability management"""

    def __init__(self):
        self.horizontal = HorizontalScaler()
        self.vertical = VerticalScaler()
        self.distributed = DistributedScaler()
        self.capacity_planner = CapacityPlanner()

    def scale(self, direction: ScalingDirection, target: int) -> bool:
        """Scale in specified direction"""
        if direction == ScalingDirection.HORIZONTAL:
            return self.horizontal.scale_up(target)
        elif direction == ScalingDirection.VERTICAL:
            return self.vertical.scale_up("cpu", target)
        elif direction == ScalingDirection.BOTH:
            self.horizontal.scale_up(target)
            return self.vertical.scale_up("cpu", target)

        return False

    def get_recommendations(self) -> List[str]:
        """Get scaling recommendations"""
        return self.capacity_planner.get_recommendations()

    def get_status(self) -> Dict[str, Any]:
        """Get overall status"""
        return {
            "horizontal": self.horizontal.get_status(),
            "vertical": self.vertical.get_status(),
            "distributed": self.distributed.get_cluster_status()
        }


def create_scalability_manager() -> ScalabilityManager:
    """Create scalability manager"""
    return ScalabilityManager()


def main():
    """Main entry point for testing"""
    print("Testing Scalability Engineering...")

    # Create manager
    manager = create_scalability_manager()

    # Test horizontal scaling
    manager.horizontal.scale_up(5)
    status = manager.horizontal.get_status()
    print(f"Horizontal status: {status['instances']} instances")

    # Test auto-scaler
    scaler = AutoScaler()
    metric = ScalingMetric(
        name="cpu",
        current_value=50.0,
        target_value=70.0,
        threshold=80.0,
        scale_up_threshold=75.0,
        scale_down_threshold=25.0
    )
    scaler.add_metric(metric)

    scaler.update_metric("cpu", 80.0)
    action = scaler.check_scaling_needed()
    print(f"Scaling action: {action.reason if action else 'None'}")

    # Test capacity planning
    planner = CapacityPlanner()
    for i in range(20):
        planner.record_capacity(instances=10, load=0.5 + i * 0.01, throughput=100)

    forecasts = planner.forecast_capacity()
    print(f"Forecasts: {len(forecasts)} periods")

    # Get recommendations
    recommendations = planner.get_recommendations()
    print(f"Recommendations: {recommendations}")

    # Test load balancer
    lb = LoadBalancer()
    lb.add_backend("backend1")
    lb.add_backend("backend2")
    backend = lb.get_backend()
    print(f"Load balanced to: {backend}")

    # Get overall status
    overall_status = manager.get_status()
    print(f"Overall status: {list(overall_status.keys())}")

    print("\nScalability Engineering initialized successfully")


if __name__ == "__main__":
    main()
