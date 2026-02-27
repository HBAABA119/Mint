"""
Prim Real-time Concurrency
Provides real-time scheduling, priority inversion handling,
deadline management, real-time monitoring, and latency guarantees.
"""

import time
import threading
import heapq
from typing import List, Dict, Any, Optional, Callable, Tuple
from dataclasses import dataclass, field
from enum import Enum


class SchedulingPolicy(Enum):
    """Scheduling policies"""
    FIFO = "fifo"
    PRIORITY = "priority"
    DEADLINE = "deadline"
    ROUND_ROBIN = "round_robin"
    RATE_MONOTONIC = "rate_monotonic"


class TaskState(Enum):
    """Task states"""
    READY = "ready"
    RUNNING = "running"
    BLOCKED = "blocked"
    COMPLETED = "completed"
    MISSED_DEADLINE = "missed_deadline"


@dataclass
class RealTimeTask:
    """Real-time task"""
    id: str
    period: float
    execution_time: float
    deadline: float
    priority: int = 0
    state: TaskState = TaskState.READY
    remaining_time: float = 0.0
    next_release: float = 0.0
    deadline_time: float = 0.0


class RealTimeScheduler:
    """Real-time task scheduler"""

    def __init__(self, policy: SchedulingPolicy = SchedulingPolicy.PRIORITY):
        self.policy = policy
        self.tasks: Dict[str, RealTimeTask] = []
        self.ready_queue: List[Tuple[int, RealTimeTask]] = []
        self.current_task: Optional[RealTimeTask] = None
        self.clock = 0.0
        self.missed_deadlines = 0
        self.preemptions = 0

    def add_task(self, task: RealTimeTask):
        """Add task to scheduler"""
        task.next_release = self.clock
        task.deadline_time = self.clock + task.deadline
        task.remaining_time = task.execution_time

        self.tasks[task.id] = task

    def schedule(self) -> Optional[RealTimeTask]:
        """Schedule next task"""
        # Update ready queue
        self._update_ready_queue()

        if not self.ready_queue:
            return None

        # Select task based on policy
        if self.policy == SchedulingPolicy.PRIORITY:
            self.ready_queue.sort(key=lambda x: x[0], reverse=True)
        elif self.policy == SchedulingPolicy.DEADLINE:
            self.ready_queue.sort(key=lambda x: x[1].deadline_time)
        elif self.policy == SchedulingPolicy.RATE_MONOTONIC:
            self.ready_queue.sort(key=lambda x: x[1].period)

        if self.ready_queue:
            priority, task = self.ready_queue[0]
            self.ready_queue.pop(0)

            # Check preemption
            if self.current_task and task.priority > self.current_task.priority:
                if self.current_task.state == TaskState.RUNNING:
                    self.current_task.state = TaskState.READY
                    self.preemptions += 1

            return task

        return None

    def _update_ready_queue(self):
        """Update ready queue"""
        for task in self.tasks.values():
            if task.state == TaskState.COMPLETED:
                continue

            # Check for new release
            if self.clock >= task.next_release:
                task.state = TaskState.READY
                task.next_release = self.clock + task.period
                task.deadline_time = task.next_release + task.deadline

            # Check deadline
            if self.clock > task.deadline_time and task.remaining_time > 0:
                task.state = TaskState.MISSED_DEADLINE
                self.missed_deadlines += 1

            # Add to ready queue
            if task.state == TaskState.READY:
                heapq.heappush(self.ready_queue, (task.priority, task))

    def tick(self, dt: float = 0.001):
        """Advance clock by dt"""
        self.clock += dt

        # Check deadlines
        for task in self.tasks.values():
            if task.state == TaskState.RUNNING:
                task.remaining_time -= dt

                if task.remaining_time <= 0:
                    task.state = TaskState.COMPLETED
                    task.remaining_time = task.execution_time

    def get_stats(self) -> Dict[str, Any]:
        """Get scheduler statistics"""
        return {
            "clock": self.clock,
            "tasks": len(self.tasks),
            "missed_deadlines": self.missed_deadlines,
            "preemptions": self.preemptions
        }


class PriorityInheritance:
    """Priority inheritance for avoiding priority inversion"""

    def __init__(self):
        self.locks: Dict[str, List[str]] = {}
        self.task_priorities: Dict[str, int] = {}

    def acquire_lock(self, task_id: str, lock_name: str):
        """Acquire lock with priority inheritance"""
        if lock_name not in self.locks:
            self.locks[lock_name] = []

        # Inherit priority from blocked tasks
        if self.locks[lock_name]:
            highest_blocked = max(self.locks[lock_name])
            if highest_blocked > self.task_priorities.get(task_id, 0):
                self.task_priorities[task_id] = highest_blocked

        self.locks[lock_name].append(task_id)

    def release_lock(self, task_id: str, lock_name: str):
        """Release lock"""
        if lock_name in self.locks and task_id in self.locks[lock_name]:
            self.locks[lock_name].remove(task_id)


class DeadlineMonitor:
    """Deadline monitoring"""

    def __init__(self):
        self.deadlines: Dict[str, float] = {}
        self.missed: List[str] = []
        self.met: List[str] = []

    def set_deadline(self, task_id: str, deadline: float):
        """Set deadline for task"""
        self.deadlines[task_id] = deadline

    def check_deadlines(self, current_time: float) -> List[str]:
        """Check for missed deadlines"""
        missed = []

        for task_id, deadline in self.deadlines.items():
            if current_time > deadline:
                missed.append(task_id)
                if task_id not in self.missed:
                    self.missed.append(task_id)
            else:
                if task_id not in self.met:
                    self.met.append(task_id)

        return missed

    def get_stats(self) -> Dict[str, int]:
        """Get deadline statistics"""
        return {
            "total": len(self.deadlines),
            "met": len(self.met),
            "missed": len(self.missed)
        }


class LatencyTracker:
    """Latency tracking"""

    def __init__(self):
        self.latencies: Dict[str, List[float]] = {}
        self.timestamps: Dict[str, float] = {}

    def start_task(self, task_id: str):
        """Record task start"""
        self.timestamps[task_id] = time.time()

    def end_task(self, task_id: str):
        """Record task end"""
        if task_id in self.timestamps:
            latency = time.time() - self.timestamps[task_id]

            if task_id not in self.latencies:
                self.latencies[task_id] = []

            self.latencies[task_id].append(latency)
            del self.timestamps[task_id]

    def get_latency(self, task_id: str) -> Optional[float]:
        """Get average latency for task"""
        if task_id not in self.latencies or not self.latencies[task_id]:
            return None

        return sum(self.latencies[task_id]) / len(self.latencies[task_id])

    def get_stats(self) -> Dict[str, float]:
        """Get latency statistics"""
        all_latencies = []

        for latencies in self.latencies.values():
            all_latencies.extend(latencies)

        if not all_latencies:
            return {"min": 0, "max": 0, "avg": 0}

        return {
            "min": min(all_latencies),
            "max": max(all_latencies),
            "avg": sum(all_latencies) / len(all_latencies)
        }


class RealTimeExecutor:
    """Real-time task executor"""

    def __init__(self, policy: SchedulingPolicy = SchedulingPolicy.PRIORITY):
        self.scheduler = RealTimeScheduler(policy)
        self.priority_inheritance = PriorityInheritance()
        self.deadline_monitor = DeadlineMonitor()
        self.latency_tracker = LatencyTracker()
        self.running = False

    def add_task(self, task: RealTimeTask):
        """Add real-time task"""
        self.scheduler.add_task(task)
        self.deadline_monitor.set_deadline(task.id, task.deadline_time)

    def start(self):
        """Start executor"""
        self.running = True

        while self.running:
            # Schedule task
            task = self.scheduler.schedule()

            if task:
                # Execute task
                self._execute_task(task)
            else:
                # Idle
                time.sleep(0.001)

            # Advance clock
            self.scheduler.tick()

            # Check deadlines
            missed = self.deadline_monitor.check_deadlines(self.scheduler.clock)

    def stop(self):
        """Stop executor"""
        self.running = False

    def _execute_task(self, task: RealTimeTask):
        """Execute task"""
        task.state = TaskState.RUNNING
        self.latency_tracker.start_task(task.id)

        # Simulate execution
        time.sleep(min(task.remaining_time, 0.01))

        self.latency_tracker.end_task(task.id)

    def get_stats(self) -> Dict[str, Any]:
        """Get executor statistics"""
        return {
            "scheduler": self.scheduler.get_stats(),
            "deadlines": self.deadline_monitor.get_stats(),
            "latency": self.latency_tracker.get_stats()
        }


def create_realtime_executor(policy: SchedulingPolicy = SchedulingPolicy.PRIORITY) -> RealTimeExecutor:
    """Create real-time executor"""
    return RealTimeExecutor(policy)


def main():
    """Main entry point for testing"""
    print("Testing Real-time Concurrency...")

    # Create executor
    executor = create_realtime_executor(SchedulingPolicy.PRIORITY)

    # Add tasks
    task1 = RealTimeTask(
        id="task1",
        period=1.0,
        execution_time=0.1,
        deadline=0.5,
        priority=1
    )

    task2 = RealTimeTask(
        id="task2",
        period=2.0,
        execution_time=0.2,
        deadline=1.0,
        priority=2
    )

    executor.add_task(task1)
    executor.add_task(task2)

    # Run for a short time
    def run_executor():
        for _ in range(100):
            executor.scheduler.tick()
            executor.scheduler.schedule()
            time.sleep(0.001)

    thread = threading.Thread(target=run_executor)
    thread.start()
    thread.join()

    # Get stats
    stats = executor.get_stats()
    print(f"Executor stats: {stats}")

    print("\nReal-time Concurrency initialized successfully")


if __name__ == "__main__":
    main()
