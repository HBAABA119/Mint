# Prim Language Concurrency Guide

## Table of Contents

- [Async/Await](#asyncawait)
- [Parallel Processing](#parallel-processing)
- [Thread Safety](#thread-safety)
- [Synchronization](#synchronization)
- [Deadlock Prevention](#deadlock-prevention)

---

## Async/Await

### Basic Async Functions

```prim
async fn fetch_data(url: string) -> string {
    let response = await http.get(url);
    return response.data;
}
```

### Async Main

```prim
async fn main() {
    let data = await fetch_data("https://api.example.com");
    print(data);
}
```

### Parallel Execution

```prim
async fn fetch_all(urls: list) -> list {
    let tasks = [];
    for url in urls {
        tasks.push(http.get(url));
    }
    return await Promise.all(tasks);
}
```

### Error Handling in Async

```prim
async fn safe_fetch(url: string) -> Result<string> {
    try {
        let data = await http.get(url);
        return Ok(data);
    } catch (error) {
        return Error(error);
    }
}
```

---

## Parallel Processing

### Thread Pools

```prim
import threadpool;

fn parallel_process(items: list, func: Callable) -> list {
    let pool = threadpool.new(4);
    return pool.map(items, func);
}
```

### Parallel Map

```prim
fn parallel_map(items: list, func: Callable) -> list {
    let results = [];
    for item in items {
        results.push(func(item));
    }
    return results;
}
```

### Parallel Reduce

```prim
fn parallel_reduce(items: list, func: Callable, init: any) -> any {
    let result = init;
    for item in items {
        result = func(result, item);
    }
    return result;
}
```

---

## Thread Safety

### Mutex

```prim
import mutex;

fn main() {
    let lock = mutex.new();
    let counter = 0;

    fn increment() {
        lock.acquire();
        counter = counter + 1;
        lock.release();
    }
}
```

### Atomic Operations

```prim
import atomic;

fn main() {
    let counter = atomic.new(0);

    fn increment() {
        counter.increment();
    }

    fn get_value() -> int {
        return counter.get();
    }
}
```

### Thread-Local Storage

```prim
import thread_local;

fn main() {
    let local = thread_local.new(0);

    fn process() {
        let value = local.get();
        local.set(value + 1);
    }
}
```

---

## Synchronization

### Barriers

```prim
import barrier;

fn parallel_computation() {
    let b = barrier.new(3);

    async fn worker(id: int) {
        // Do work
        await b.wait();  // Wait for all workers
        // Continue
    }

    let tasks = [
        worker(1),
        worker(2),
        worker(3)
    ];

    await Promise.all(tasks);
}
```

### Semaphores

```prim
import semaphore;

fn limited_concurrency() {
    let sem = semaphore.new(3);  // Max 3 concurrent

    async fn worker() {
        sem.acquire();
        // Do work
        sem.release();
    }
}
```

### Conditions

```prim
import condition;

fn producer_consumer() {
    let mutex = mutex.new();
    let cond = condition.new(mutex);
    let queue = [];

    async fn producer() {
        mutex.acquire();
        while queue.length() >= 10 {
            cond.wait();
        }
        queue.push("item");
        cond.signal();
        mutex.release();
    }

    async fn consumer() {
        mutex.acquire();
        while queue.length() == 0 {
            cond.wait();
        }
        let item = queue.pop();
        cond.signal();
        mutex.release();
        return item;
    }
}
```

---

## Deadlock Prevention

### Avoid Circular Dependencies

```prim
// Bad - Can deadlock
fn deadlock_example() {
    let lock1 = mutex.new();
    let lock2 = mutex.new();

    fn thread1() {
        lock1.acquire();
        lock2.acquire();
        // ...
        lock2.release();
        lock1.release();
    }

    fn thread2() {
        lock2.acquire();
        lock1.acquire();
        // ...
        lock1.release();
        lock2.release();
    }
}

// Good - Always acquire locks in same order
fn safe_example() {
    let lock1 = mutex.new();
    let lock2 = mutex.new();

    fn thread1() {
        lock1.acquire();
        lock2.acquire();
        // ...
        lock2.release();
        lock1.release();
    }

    fn thread2() {
        lock1.acquire();
        lock2.acquire();
        // ...
        lock2.release();
        lock1.release();
    }
}
```

### Use Timeouts

```prim
fn acquire_with_timeout(lock: Mutex, timeout: int) -> bool {
    if lock.try_acquire(timeout) {
        return true;
    }
    return false;
}
```

---

## Summary

Concurrency in Prim involves:

1. **Async/Await**: Non-blocking I/O
2. **Parallel Processing**: Multi-threaded execution
3. **Thread Safety**: Protect shared state
4. **Synchronization**: Coordinate threads
5. **Deadlock Prevention**: Avoid circular waits

For more information, see the [Best Practices](./best_practices.md).
