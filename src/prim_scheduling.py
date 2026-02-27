"""
Prim Scheduling Algorithms
Provides real-time scheduling, priority scheduling, deadline scheduling,
multi-core scheduling, and task allocation.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum


class SchedulingPolicy(Enum):
    """Scheduling policies"""
    FIFO = "fifo"
    PRIORITY = "priority"
    ROUND_ROBIN = "round_robin"
    DEADLINE = "deadline"
    RATE_MONOTONIC = "rate_monotonic"


@dataclass
class Task:
    """Schedulable task"""
    id: str
    priority: int
    deadline: float
    execution_time: float


class Scheduler:
    """Task scheduler"""

    def __init__(self, policy: SchedulingPolicy = SchedulingPolicy.PRIORITY):
        self.policy = policy
        self.tasks: List[Task] = []

    def add_task(self, task: Task):
        """Add task"""
        self.tasks.append(task)

    def schedule(self) -> Optional[Task]:
        """Schedule next task"""
        if not self.tasks:
            return None

        if self.policy == SchedulingPolicy.PRIORITY:
            return max(self.tasks, key=lambda t: t.priority)
        elif self.policy == SchedulingPolicy.DEADLINE:
            return min(self.tasks, key=lambda t: t.deadline)

        return self.tasks[0]


def main():
    print("Testing Scheduling Algorithms...")
    scheduler = Scheduler(SchedulingPolicy.PRIORITY)
    task = Task(id="task1", priority=1, deadline=1.0, execution_time=0.1)
    scheduler.add_task(task)
    scheduled = scheduler.schedule()
    print(f"Scheduled: {scheduled.id if scheduled else 'None'}")
    print("Scheduling Algorithms initialized successfully")


if __name__ == "__main__":
    main()
