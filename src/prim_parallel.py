"""
Prim Parallel Runtime
Provides parallel execution, task scheduling, work stealing,
synchronization primitives, and distributed computing.
"""

import concurrent.futures
import threading
import multiprocessing
import queue
import time
from typing import List, Dict, Any, Optional, Callable, Tuple
from dataclasses import dataclass, field
from enum import Enum


class SchedulingPolicy(Enum):
    """Task scheduling policies"""
    FIFO = "fifo"
    LIFO = "lifo"
    PRIORITY = "priority"
    WORK_STEALING = "work_stealing"


class ExecutionMode(Enum):
    """Execution modes"""
    THREAD_POOL = "thread_pool"
    PROCESS_POOL = "process_pool"
    ASYNC = "async"
    HYBRID = "hybrid"


@dataclass
class Task:
    """Parallel task"""
    id: int
    function: Callable
    args: Tuple[Any, ...] = field(default_factory=tuple)
    kwargs: Dict[str, Any] = field(default_factory=dict)
    priority: int = 0
    result: Optional[Any] = None
    exception: Optional[Exception] = None
    completed: bool = False


class TaskQueue:
    """Thread-safe task queue"""

    def __init__(self, policy: SchedulingPolicy = SchedulingPolicy.FIFO):
        self.queue = queue.PriorityQueue() if policy == SchedulingPolicy.PRIORITY else queue.Queue()
        self.policy = policy
        self.lock = threading.Lock()

    def put(self, task: Task):
        """Add task to queue"""
        if self.policy == SchedulingPolicy.PRIORITY:
            self.queue.put((-task.priority, task))
        else:
            self.queue.put(task)

    def get(self, timeout: Optional[float] = None) -> Optional[Task]:
        """Get task from queue"""
        try:
            item = self.queue.get(timeout=timeout)
            if self.policy == SchedulingPolicy.PRIORITY:
                return item[1]
            return item
        except queue.Empty:
            return None

    def task_done(self):
        """Mark task as done"""
        self.queue.task_done()

    def join(self):
        """Wait for all tasks to complete"""
        self.queue.join()

    def qsize(self) -> int:
        """Get queue size"""
        return self.queue.qsize()


class Worker:
    """Worker thread/process"""

    def __init__(self, worker_id: int, task_queue: TaskQueue, mode: ExecutionMode = ExecutionMode.THREAD_POOL):
        self.worker_id = worker_id
        self.task_queue = task_queue
        self.mode = mode
        self.running = False
        self.thread: Optional[threading.Thread] = None
        self.process: Optional[multiprocessing.Process] = None
        self.tasks_completed = 0

    def start(self):
        """Start worker"""
        self.running = True

        if self.mode == ExecutionMode.THREAD_POOL:
            self.thread = threading.Thread(target=self._run, daemon=True)
            self.thread.start()
        elif self.mode == ExecutionMode.PROCESS_POOL:
            self.process = multiprocessing.Process(target=self._run, daemon=True)
            self.process.start()

    def stop(self):
        """Stop worker"""
        self.running = False

        if self.thread:
            self.thread.join()
        if self.process:
            self.process.join()

    def _run(self):
        """Worker main loop"""
        while self.running:
            task = self.task_queue.get(timeout=0.1)

            if task is None:
                continue

            try:
                task.result = task.function(*task.args, **task.kwargs)
                task.completed = True
            except Exception as e:
                task.exception = e
                task.completed = True

            self.tasks_completed += 1
            self.task_queue.task_done()


class ParallelRuntime:
    """Parallel execution runtime"""

    def __init__(self, num_workers: int = 4, mode: ExecutionMode = ExecutionMode.THREAD_POOL,
                 scheduling: SchedulingPolicy = SchedulingPolicy.FIFO):
        self.num_workers = num_workers
        self.mode = mode
        self.scheduling = scheduling
        self.task_queue = TaskQueue(scheduling)
        self.workers: List[Worker] = []
        self.task_counter = 0
        self.stats = {
            "tasks_submitted": 0,
            "tasks_completed": 0,
            "tasks_failed": 0
        }

    def start(self):
        """Start parallel runtime"""
        for i in range(self.num_workers):
            worker = Worker(i, self.task_queue, self.mode)
            worker.start()
            self.workers.append(worker)

    def stop(self):
        """Stop parallel runtime"""
        for worker in self.workers:
            worker.stop()

        self.workers = []

    def submit(self, function: Callable, *args, priority: int = 0, **kwargs) -> Task:
        """Submit task for execution"""
        self.task_counter += 1

        task = Task(
            id=self.task_counter,
            function=function,
            args=args,
            kwargs=kwargs,
            priority=priority
        )

        self.task_queue.put(task)
        self.stats["tasks_submitted"] += 1

        return task

    def submit_batch(self, tasks: List[Tuple[Callable, Tuple, Dict]]) -> List[Task]:
        """Submit batch of tasks"""
        submitted = []

        for function, args, kwargs in tasks:
            task = self.submit(function, *args, **kwargs)
            submitted.append(task)

        return submitted

    def map(self, function: Callable, iterable: List[Any]) -> List[Any]:
        """Map function over iterable"""
        futures = []

        for item in iterable:
            future = self.submit(function, item)
            futures.append(future)

        results = []
        for future in futures:
            results.append(future.result)

        return results

    def wait_all(self, timeout: Optional[float] = None):
        """Wait for all tasks to complete"""
        self.task_queue.join()

    def get_stats(self) -> Dict[str, int]:
        """Get runtime statistics"""
        completed = sum(w.tasks_completed for w in self.workers)
        self.stats["tasks_completed"] = completed
        return self.stats.copy()


class WorkStealingRuntime:
    """Work-stealing parallel runtime"""

    def __init__(self, num_workers: int = 4):
        self.num_workers = num_workers
        self.queues: List[TaskQueue] = [TaskQueue(SchedulingPolicy.WORK_STEALING) for _ in range(num_workers)]
        self.workers: List[Worker] = []
        self.current_worker = 0

    def start(self):
        """Start work-stealing runtime"""
        for i in range(self.num_workers):
            worker = Worker(i, self.queues[i], ExecutionMode.THREAD_POOL)
            worker.start()
            self.workers.append(worker)

    def stop(self):
        """Stop work-stealing runtime"""
        for worker in self.workers:
            worker.stop()

    def submit(self, function: Callable, *args, **kwargs) -> Task:
        """Submit task to current worker's queue"""
        self.current_worker = (self.current_worker + 1) % self.num_workers

        self.task_counter = getattr(self, 'task_counter', 0) + 1

        task = Task(
            id=self.task_counter,
            function=function,
            args=args,
            kwargs=kwargs
        )

        self.queues[self.current_worker].put(task)
        return task

    def _steal_task(self, from_worker: int, to_worker: int) -> Optional[Task]:
        """Steal task from another worker"""
        task = self.queues[from_worker].get(timeout=0.01)
        if task:
            self.queues[to_worker].put(task)
        return task


class Barrier:
    """Barrier synchronization primitive"""

    def __init__(self, num_threads: int):
        self.num_threads = num_threads
        self.count = 0
        self.lock = threading.Lock()
        self.condition = threading.Condition(self.lock)

    def wait(self):
        """Wait for all threads to reach barrier"""
        with self.lock:
            self.count += 1

            if self.count == self.num_threads:
                # Last thread to reach barrier
                self.condition.notify_all()
                self.count = 0
                return True

            # Wait for other threads
            self.condition.wait()
            return False


class Future:
    """Future for async results"""

    def __init__(self):
        self._result = None
        self._exception = None
        self._completed = False
        self._condition = threading.Condition()

    def set_result(self, result: Any):
        """Set result"""
        with self._condition:
            self._result = result
            self._completed = True
            self._condition.notify_all()

    def set_exception(self, exception: Exception):
        """Set exception"""
        with self._condition:
            self._exception = exception
            self._completed = True
            self._condition.notify_all()

    def result(self, timeout: Optional[float] = None) -> Any:
        """Get result"""
        with self._condition:
            if self._completed:
                if self._exception:
                    raise self._exception
                return self._result

            self._condition.wait(timeout)

            if not self._completed:
                raise TimeoutError("Future not completed")

            if self._exception:
                raise self._exception

            return self._result

    def done(self) -> bool:
        """Check if completed"""
        with self._condition:
            return self._completed


class AsyncExecutor:
    """Async task executor"""

    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=max_workers)
        self.futures: List[concurrent.futures.Future] = []

    def submit(self, function: Callable, *args, **kwargs) -> concurrent.futures.Future:
        """Submit async task"""
        future = self.executor.submit(function, *args, **kwargs)
        self.futures.append(future)
        return future

    def map(self, function: Callable, iterable: List[Any]) -> List[Any]:
        """Map function over iterable"""
        return list(self.executor.map(function, iterable))

    def wait_all(self, timeout: Optional[float] = None):
        """Wait for all tasks"""
        for future in self.futures:
            future.result(timeout=timeout)

    def shutdown(self):
        """Shutdown executor"""
        self.executor.shutdown()


def create_parallel_runtime(num_workers: int = 4, mode: ExecutionMode = ExecutionMode.THREAD_POOL) -> ParallelRuntime:
    """Create parallel runtime"""
    return ParallelRuntime(num_workers, mode)


def create_work_stealing_runtime(num_workers: int = 4) -> WorkStealingRuntime:
    """Create work-stealing runtime"""
    return WorkStealingRuntime(num_workers)


def main():
    """Main entry point for testing"""
    print("Testing Parallel Runtime...")

    # Test Parallel Runtime
    runtime = create_parallel_runtime(num_workers=4, mode=ExecutionMode.THREAD_POOL)
    runtime.start()

    # Submit tasks
    def task(x):
        time.sleep(0.1)
        return x * 2

    futures = []
    for i in range(10):
        future = runtime.submit(task, i)
        futures.append(future)

    runtime.wait_all()

    results = [f.result for f in futures]
    print(f"Results: {len(results)} tasks completed")

    stats = runtime.get_stats()
    print(f"Stats: {stats}")

    runtime.stop()

    # Test Work Stealing
    ws_runtime = create_work_stealing_runtime(num_workers=4)
    ws_runtime.start()

    for i in range(10):
        ws_runtime.submit(task, i)

    ws_runtime.stop()
    print("Work stealing runtime stopped")

    # Test Barrier
    barrier = Barrier(2)
    results = []

    def worker1():
        barrier.wait()
        results.append(1)

    def worker2():
        time.sleep(0.1)
        barrier.wait()
        results.append(2)

    t1 = threading.Thread(target=worker1)
    t2 = threading.Thread(target=worker2)
    t1.start()
    t2.start()
    t1.join()
    t2.join()

    print(f"Barrier results: {sorted(results)}")

    # Test Async Executor
    async_exec = AsyncExecutor(max_workers=4)
    async_futures = []

    for i in range(5):
        future = async_exec.submit(task, i)
        async_futures.append(future)

    async_exec.wait_all()
    async_results = [f.result() for f in async_futures]
    print(f"Async results: {len(async_results)} completed")

    async_exec.shutdown()

    print("\nParallel Runtime initialized successfully")


if __name__ == "__main__":
    main()
