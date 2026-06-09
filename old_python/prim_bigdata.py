"""
Prim Big Data Integration
Provides distributed computing framework, stream processing, data pipeline management,
cluster resource management, and fault tolerance.
"""

import threading
import queue
import time
from typing import List, Dict, Any, Optional, Callable, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json


class TaskStatus(Enum):
    """Task status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class TaskPriority(Enum):
    """Task priority"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class Task:
    """Distributed task"""
    id: str
    name: str
    function: Callable
    args: Tuple[Any, ...] = field(default_factory=tuple)
    kwargs: Dict[str, Any] = field(default_factory=dict)
    status: TaskStatus = TaskStatus.PENDING
    priority: TaskPriority = TaskPriority.MEDIUM
    result: Optional[Any] = None
    error: Optional[str] = None
    node_id: Optional[str] = None

    def execute(self):
        """Execute the task"""
        try:
            self.status = TaskStatus.RUNNING
            self.result = self.function(*self.args, **self.kwargs)
            self.status = TaskStatus.COMPLETED
        except Exception as e:
            self.status = TaskStatus.FAILED
            self.error = str(e)


@dataclass
class Node:
    """Cluster node"""
    id: str
    address: str
    port: int
    status: str = "active"
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task):
        """Add task to node"""
        self.tasks.append(task)
        task.node_id = self.id

    def remove_task(self, task_id: str):
        """Remove task from node"""
        self.tasks = [t for t in self.tasks if t.id != task_id]


class Cluster:
    """Distributed computing cluster"""

    def __init__(self, name: str = "cluster"):
        self.name = name
        self.nodes: Dict[str, Node] = {}
        self.tasks: Dict[str, Task] = {}
        self.task_queue: queue.Queue = queue.Queue()
        self.running = False
        self.lock = threading.Lock()

    def add_node(self, node: Node):
        """Add node to cluster"""
        with self.lock:
            self.nodes[node.id] = node

    def remove_node(self, node_id: str):
        """Remove node from cluster"""
        with self.lock:
            if node_id in self.nodes:
                del self.nodes[node_id]

    def submit_task(self, task: Task):
        """Submit task to cluster"""
        with self.lock:
            self.tasks[task.id] = task
            self.task_queue.put(task)

    def get_task(self, task_id: str) -> Optional[Task]:
        """Get task by ID"""
        return self.tasks.get(task_id)

    def schedule_tasks(self):
        """Schedule tasks to nodes"""
        while self.running:
            try:
                task = self.task_queue.get(timeout=1)
                if task.status == TaskStatus.PENDING:
                    # Find least loaded node
                    available_nodes = [n for n in self.nodes.values() if n.status == "active"]
                    if available_nodes:
                        node = min(available_nodes, key=lambda n: len(n.tasks))
                        node.add_task(task)
                        # Execute task in thread
                        thread = threading.Thread(target=self._execute_task, args=(task, node))
                        thread.start()
            except queue.Empty:
                continue

    def _execute_task(self, task: Task, node: Node):
        """Execute task on node"""
        task.execute()
        node.remove_task(task.id)

    def start(self):
        """Start cluster scheduler"""
        self.running = True
        self.scheduler_thread = threading.Thread(target=self.schedule_tasks)
        self.scheduler_thread.start()

    def stop(self):
        """Stop cluster"""
        self.running = False
        if hasattr(self, 'scheduler_thread'):
            self.scheduler_thread.join()

    def get_status(self) -> Dict[str, Any]:
        """Get cluster status"""
        return {
            "name": self.name,
            "nodes": len(self.nodes),
            "tasks": len(self.tasks),
            "pending": sum(1 for t in self.tasks.values() if t.status == TaskStatus.PENDING),
            "running": sum(1 for t in self.tasks.values() if t.status == TaskStatus.RUNNING),
            "completed": sum(1 for t in self.tasks.values() if t.status == TaskStatus.COMPLETED),
            "failed": sum(1 for t in self.tasks.values() if t.status == TaskStatus.FAILED)
        }


class StreamProcessor:
    """Stream processing framework"""

    def __init__(self, name: str = "stream"):
        self.name = name
        self.sources: List[Callable] = []
        self.transformations: List[Callable] = []
        self.sinks: List[Callable] = []
        self.running = False

    def add_source(self, source: Callable):
        """Add data source"""
        self.sources.append(source)

    def add_transformation(self, transform: Callable):
        """Add transformation"""
        self.transformations.append(transform)

    def add_sink(self, sink: Callable):
        """Add sink"""
        self.sinks.append(sink)

    def process(self):
        """Process stream"""
        while self.running:
            for source in self.sources:
                try:
                    data = source()
                    if data is None:
                        continue

                    # Apply transformations
                    for transform in self.transformations:
                        data = transform(data)

                    # Send to sinks
                    for sink in self.sinks:
                        sink(data)

                except Exception as e:
                    print(f"Stream processing error: {e}")

            time.sleep(0.1)

    def start(self):
        """Start stream processing"""
        self.running = True
        self.thread = threading.Thread(target=self.process)
        self.thread.start()

    def stop(self):
        """Stop stream processing"""
        self.running = False
        if hasattr(self, 'thread'):
            self.thread.join()


class Pipeline:
    """Data pipeline management"""

    def __init__(self, name: str = "pipeline"):
        self.name = name
        self.stages: List[Callable] = []
        self.status = "idle"

    def add_stage(self, stage: Callable):
        """Add pipeline stage"""
        self.stages.append(stage)

    def execute(self, data: Any) -> Any:
        """Execute pipeline"""
        self.status = "running"
        result = data

        for i, stage in enumerate(self.stages):
            try:
                result = stage(result)
                print(f"Stage {i + 1}/{len(self.stages)} completed")
            except Exception as e:
                self.status = "failed"
                print(f"Pipeline failed at stage {i + 1}: {e}")
                raise

        self.status = "completed"
        return result

    def get_status(self) -> str:
        """Get pipeline status"""
        return self.status


class ResourceManager:
    """Cluster resource management"""

    def __init__(self):
        self.resources: Dict[str, Dict[str, Any]] = {}
        self.allocations: Dict[str, Dict[str, Any]] = {}

    def register_resource(self, resource_id: str, capacity: float):
        """Register resource"""
        self.resources[resource_id] = {
            "capacity": capacity,
            "available": capacity,
            "allocated": 0
        }

    def allocate(self, resource_id: str, amount: float, task_id: str) -> bool:
        """Allocate resource"""
        if resource_id not in self.resources:
            return False

        resource = self.resources[resource_id]
        if resource["available"] >= amount:
            resource["available"] -= amount
            resource["allocated"] += amount

            if task_id not in self.allocations:
                self.allocations[task_id] = {}
            self.allocations[task_id][resource_id] = amount
            return True

        return False

    def release(self, resource_id: str, task_id: str):
        """Release resource"""
        if task_id in self.allocations and resource_id in self.allocations[task_id]:
            amount = self.allocations[task_id][resource_id]
            self.resources[resource_id]["available"] += amount
            self.resources[resource_id]["allocated"] -= amount
            del self.allocations[task_id][resource_id]

    def get_usage(self) -> Dict[str, Dict[str, float]]:
        """Get resource usage"""
        return {
            rid: {
                "capacity": r["capacity"],
                "available": r["available"],
                "allocated": r["allocated"],
                "utilization": r["allocated"] / r["capacity"] if r["capacity"] > 0 else 0
            }
            for rid, r in self.resources.items()
        }


class FaultTolerance:
    """Fault tolerance mechanisms"""

    def __init__(self):
        self.checkpoints: Dict[str, Any] = {}
        self.recovery_log: List[Dict[str, Any]] = []

    def create_checkpoint(self, task_id: str, state: Any):
        """Create checkpoint"""
        self.checkpoints[task_id] = {
            "state": state,
            "timestamp": time.time()
        }

    def restore_checkpoint(self, task_id: str) -> Optional[Any]:
        """Restore from checkpoint"""
        if task_id in self.checkpoints:
            return self.checkpoints[task_id]["state"]
        return None

    def log_recovery(self, task_id: str, action: str, details: Any):
        """Log recovery action"""
        self.recovery_log.append({
            "task_id": task_id,
            "action": action,
            "details": details,
            "timestamp": time.time()
        })

    def retry_task(self, task: Task, max_retries: int = 3) -> bool:
        """Retry failed task"""
        for attempt in range(max_retries):
            try:
                task.execute()
                if task.status == TaskStatus.COMPLETED:
                    self.log_recovery(task.id, "retry_success", f"Attempt {attempt + 1}")
                    return True
            except Exception as e:
                self.log_recovery(task.id, "retry_failed", f"Attempt {attempt + 1}: {e}")

        return False


class DistributedMapReduce:
    """MapReduce framework"""

    def __init__(self, cluster: Cluster):
        self.cluster = cluster

    def map(self, data: List[Any], mapper: Callable) -> List[Tuple[Any, Any]]:
        """Map phase"""
        results = []
        for item in data:
            results.extend(mapper(item))
        return results

    def shuffle(self, mapped: List[Tuple[Any, Any]]) -> Dict[Any, List[Any]]:
        """Shuffle phase"""
        shuffled = {}
        for key, value in mapped:
            if key not in shuffled:
                shuffled[key] = []
            shuffled[key].append(value)
        return shuffled

    def reduce(self, shuffled: Dict[Any, List[Any]], reducer: Callable) -> List[Tuple[Any, Any]]:
        """Reduce phase"""
        results = []
        for key, values in shuffled.items():
            results.append((key, reducer(key, values)))
        return results

    def execute(self, data: List[Any], mapper: Callable, reducer: Callable) -> List[Tuple[Any, Any]]:
        """Execute MapReduce"""
        mapped = self.map(data, mapper)
        shuffled = self.shuffle(mapped)
        reduced = self.reduce(shuffled, reducer)
        return reduced


def create_cluster(name: str = "cluster") -> Cluster:
    """Create a cluster"""
    return Cluster(name)


def create_stream(name: str = "stream") -> StreamProcessor:
    """Create a stream processor"""
    return StreamProcessor(name)


def create_pipeline(name: str = "pipeline") -> Pipeline:
    """Create a pipeline"""
    return Pipeline(name)


def main():
    """Main entry point for testing"""
    print("Testing Big Data Integration...")

    # Test Cluster
    cluster = create_cluster("test_cluster")
    node1 = Node(id="node1", address="localhost", port=8000)
    node2 = Node(id="node2", address="localhost", port=8001)
    cluster.add_node(node1)
    cluster.add_node(node2)

    # Submit tasks
    task1 = Task(id="task1", name="test_task", function=lambda: sum(range(100)))
    task2 = Task(id="task2", name="test_task2", function=lambda x: x * 2, args=(10,))

    cluster.submit_task(task1)
    cluster.submit_task(task2)

    cluster.start()
    time.sleep(1)
    cluster.stop()

    print(f"Cluster status: {cluster.get_status()}")

    # Test Stream Processing
    stream = create_stream("test_stream")
    counter = [0]

    def source():
        counter[0] += 1
        return counter[0] if counter[0] <= 10 else None

    def transform(data):
        return data * 2

    def sink(data):
        print(f"Sink received: {data}")

    stream.add_source(source)
    stream.add_transformation(transform)
    stream.add_sink(sink)

    stream.start()
    time.sleep(2)
    stream.stop()

    # Test Pipeline
    pipeline = create_pipeline("test_pipeline")

    def stage1(data):
        return [x * 2 for x in data]

    def stage2(data):
        return sum(data)

    pipeline.add_stage(stage1)
    pipeline.add_stage(stage2)

    result = pipeline.execute([1, 2, 3, 4, 5])
    print(f"Pipeline result: {result}")

    # Test MapReduce
    mapreduce = DistributedMapReduce(cluster)
    data = ["hello world", "hello prim", "world programming"]
    mapper = lambda text: [(word, 1) for word in text.split()]
    reducer = lambda key, values: (key, sum(values))

    results = mapreduce.execute(data, mapper, reducer)
    print(f"MapReduce results: {results}")

    print("\nBig Data Integration initialized successfully")


if __name__ == "__main__":
    main()
