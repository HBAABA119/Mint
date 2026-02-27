# Prim Language Performance Guide

## Table of Contents

- [Profiling](#profiling)
- [Optimization Techniques](#optimization-techniques)
- [Memory Management](#memory-management)
- [Concurrency](#concurrency)
- [Benchmarking](#benchmarking)

---

## Profiling

### CPU Profiling

```prim
import profiler;

fn main() {
    profiler.start();

    // ... application code ...

    profiler.stop();
    profiler.print_report();
}
```

### Memory Profiling

```prim
import memory;

fn profile_memory() {
    let before = memory.get_usage();

    // ... application code ...

    let after = memory.get_usage();
    let delta = after - before;

    print("Memory delta: " + delta + " MB");
}
```

### Function Timing

```prim
fn time_function(func: Callable) -> float {
    let start = time.now();
    func();
    return time.now() - start;
}
```

---

## Optimization Techniques

### Algorithm Optimization

#### Use Efficient Algorithms

```prim
// Bad - O(n^2)
fn contains_duplicate(list: list) -> bool {
    for i in 0..list.length() {
        for j in (i + 1)..list.length() {
            if list[i] == list[j] {
                return true;
            }
        }
    }
    return false;
}

// Good - O(n)
fn contains_duplicate(list: list) -> bool {
    let seen = set([]);
    for item in list {
        if seen.has(item) {
            return true;
        }
        seen.add(item);
    }
    return false;
}
```

#### Use Built-in Functions

```prim
// Bad
let sum = 0;
for n in numbers {
    sum = sum + n;
}

// Good
let sum = numbers.reduce(fn(a, b) -> int { a + b }, 0);
```

### Data Structure Optimization

#### Choose Right Data Structure

```prim
// Use set for membership tests
let s = set([1, 2, 3]);
if s.has(5) { ... }

// Use dict for lookups
let m = {"key": "value"};
if m.has("key") { ... }
```

#### Pre-allocate Capacity

```prim
// Bad
let list = [];
for i in 0..10000 {
    list.push(i);  // Multiple allocations
}

// Good
let list = list.with_capacity(10000);
for i in 0..10000 {
    list.push(i);  // Single allocation
}
```

### String Optimization

#### Use StringBuilder for Concatenation

```prim
// Bad
let result = "";
for i in 0..1000 {
    result = result + "item";  // O(n^2)
}

// Good
let builder = StringBuilder.new();
for i in 0..1000 {
    builder.append("item");
}
let result = builder.to_string();
```

#### Avoid Unnecessary Copies

```prim
// Bad
fn process(s: string) -> string {
    let temp1 = s.to_uppercase();
    let temp2 = temp1.trim();
    return temp2.replace(" ", "_");
}

// Good
fn process(s: string) -> string {
    return s.to_uppercase().trim().replace(" ", "_");
}
```

---

## Memory Management

### Avoid Memory Leaks

```prim
// Bad - Global cache never cleared
let cache = {};

fn get_data(key: string) -> any {
    if not cache.has(key) {
        cache[key] = fetch_data(key);
    }
    return cache[key];
}

// Good - Cache with expiration
let cache = {};

fn get_data(key: string) -> any {
    if cache.has(key) {
        let entry = cache[key];
        if time.now() - entry.time < 3600 {
            return entry.data;
        }
    }
    let data = fetch_data(key);
    cache[key] = {"data": data, "time": time.now()};
    return data;
}
```

### Use Weak References

```prim
import weak;

fn cache_result(key: string, value: any) {
    weak.set(key, value);
}

fn get_cached(key: string) -> any? {
    return weak.get(key);
}
```

### Release Resources

```prim
// Bad - File not closed
fn read_file(path: string) -> string {
    return file.read(path);
}

// Good - File properly closed
fn read_file(path: string) -> string {
    let f = file.open(path);
    let content = f.read();
    f.close();
    return content;
}
```

---

## Concurrency

### Use Async for I/O

```prim
// Bad - Blocking
fn fetch_all(urls: list) -> list {
    let results = [];
    for url in urls {
        results.push(http.get(url));  // Blocks
    }
    return results;
}

// Good - Async
async fn fetch_all(urls: list) -> list {
    let tasks = [];
    for url in urls {
        tasks.push(http.get(url));
    }
    return await Promise.all(tasks);
}
```

### Limit Concurrency

```prim
async fn fetch_all_limited(urls: list, limit: int = 10) -> list {
    let results = [];
    let active = [];

    for url in urls {
        while active.length() >= limit {
            let completed = await Promise.race(active);
            results.push(completed);
            active.remove(completed);
        }
        active.push(http.get(url));
    }

    results.extend(await Promise.all(active));
    return results;
}
```

### Use Thread Pools

```prim
import threadpool;

fn parallel_process(items: list, func: Callable) -> list {
    let pool = threadpool.new(4);  // 4 threads
    return pool.map(items, func);
}
```

---

## Benchmarking

### Microbenchmarks

```prim
import benchmark;

fn benchmark_add() {
    let iterations = 1000000;
    let start = time.now();

    for i in 0..iterations {
        let result = 5 + 3;
    }

    let duration = time.now() - start;
    print("Add: " + (duration / iterations) + " ns/op");
}
```

### Comparative Benchmarks

```prim
fn compare_implementations() {
    let data = [1, 2, 3, 4, 5];

    let t1 = time.now();
    let r1 = implementation1(data);
    let d1 = time.now() - t1;

    let t2 = time.now();
    let r2 = implementation2(data);
    let d2 = time.now() - t2;

    print("Impl1: " + d1 + "s");
    print("Impl2: " + d2 + "s");
    print("Speedup: " + (d1 / d2));
}
```

### Memory Benchmarks

```prim
fn benchmark_memory() {
    let before = memory.get_usage();

    // ... allocate objects ...

    let after = memory.get_usage();
    print("Memory used: " + (after - before) + " MB");
}
```

---

## Common Performance Issues

### N+1 Query Problem

```prim
// Bad - N+1 queries
fn get_users_posts(users: list) -> dict {
    let result = {};
    for user in users {
        result[user.id] = db.query("SELECT * FROM posts WHERE user_id = " + user.id);
    }
    return result;
}

// Good - Single query
fn get_users_posts(users: list) -> dict {
    let ids = users.map(fn(u) -> int { u.id });
    let posts = db.query("SELECT * FROM posts WHERE user_id IN (" + ids.join(",") + ")");

    let result = {};
    for post in posts {
        if not result.has(post.user_id) {
            result[post.user_id] = [];
        }
        result[post.user_id].push(post);
    }
    return result;
}
```

### Excessive Allocations

```prim
// Bad - Creates many small lists
fn chunk_list(list: list, size: int) -> list {
    let result = [];
    for i in 0..list.length() step size {
        result.push(list.slice(i, i + size));
    }
    return result;
}

// Good - Pre-allocate
fn chunk_list(list: list, size: int) -> list {
    let chunks = (list.length() / size) + 1;
    let result = list.with_capacity(chunks);
    for i in 0..list.length() step size {
        result.push(list.slice(i, i + size));
    }
    return result;
}
```

### Unnecessary Computations

```prim
// Bad - Computes same value multiple times
fn process(items: list) -> list {
    let result = [];
    for item in items {
        let computed = expensive_computation(item);
        result.push(computed);
        result.push(computed);  // Computed twice
    }
    return result;
}

// Good - Cache computation
fn process(items: list) -> list {
    let result = [];
    for item in items {
        let computed = expensive_computation(item);
        result.push(computed);
        result.push(computed);  // Reuses cached value
    }
    return result;
}
```

---

## Performance Tools

### Profiler

```bash
prim profile --cpu app.prim
prim profile --memory app.prim
```

### Benchmark

```bash
prim benchmark app.prim
```

### Memory Analyzer

```bash
prim analyze-memory app.prim
```

---

## Summary

Performance optimization involves:

1. **Profiling**: Identify bottlenecks
2. **Algorithms**: Use efficient algorithms
3. **Data Structures**: Choose appropriate structures
4. **Memory**: Manage memory efficiently
5. **Concurrency**: Use async and parallelism
6. **Benchmarking**: Measure improvements

For more information, see the [Best Practices](./best_practices.md) and [Deployment Guide](./deployment_guide.md).
