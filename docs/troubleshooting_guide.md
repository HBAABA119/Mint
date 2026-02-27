# Prim Language Troubleshooting Guide

## Table of Contents

- [Common Errors](#common-errors)
- [Performance Issues](#performance-issues)
- [Memory Issues](#memory-issues)
- [Build Issues](#build-issues)
- [Runtime Issues](#runtime-issues)

---

## Common Errors

### Type Errors

**Error**: Type mismatch

```prim
fn add(a: int, b: string) -> int {
    return a + b;  // Error: cannot add int and string
}
```

**Fix**: Convert types

```prim
fn add(a: int, b: string) -> int {
    return a + b.to_int();
}
```

### Null Pointer

**Error**: Null reference

```prim
fn get_user(id: int) -> User {
    let user = database.get_user(id);
    return user.name;  // Error: user might be null
}
```

**Fix**: Use optional types

```prim
fn get_user(id: int) -> User? {
    let user = database.get_user(id);
    return user;
}
```

### Import Errors

**Error**: Module not found

```prim
import nonexistent;  // Error: module not found
```

**Fix**: Check module path

```prim
import std.io;  // Correct path
```

---

## Performance Issues

### Slow Startup

**Issue**: Application takes long to start

**Diagnosis**:
```prim
import profiler;

fn main() {
    profiler.start();
    // ... application code ...
    profiler.stop();
    profiler.print_report();
}
```

**Fix**: Lazy load modules

### Memory Leaks

**Issue**: Memory usage grows over time

**Diagnosis**:
```prim
import memory;

fn check_memory() {
    let usage = memory.get_usage();
    print("Memory: " + usage);
}
```

**Fix**: Clear caches, use weak references

### Slow Queries

**Issue**: Database queries are slow

**Diagnosis**:
```prim
fn profile_query(query: string) {
    let start = time.now();
    db.query(query);
    let duration = time.now() - start;
    print("Query took: " + duration);
}
```

**Fix**: Add indexes, optimize queries

---

## Memory Issues

### Out of Memory

**Issue**: Application runs out of memory

**Fix**: Process data in chunks

```prim
fn process_large_file(path: string) {
    let file = fs.open(path);

    while not file.eof() {
        let chunk = file.read(4096);
        process(chunk);
    }

    file.close();
}
```

### Memory Fragmentation

**Issue**: High memory fragmentation

**Fix**: Pre-allocate containers

```prim
fn process_items(items: list) {
    let result = list.with_capacity(items.length());
    for item in items {
        result.push(transform(item));
    }
}
```

---

## Build Issues

### Compilation Errors

**Issue**: Code doesn't compile

**Fix**: Check syntax, types

```bash
prim build --check app.prim
```

### Link Errors

**Issue**: Can't find dependencies

**Fix**: Install dependencies

```bash
prim install dependency_name
```

### Native Build Failures

**Issue**: Native compilation fails

**Fix**: Check toolchain

```bash
prim build --native --verbose app.prim
```

---

## Runtime Issues

### Segmentation Faults

**Issue**: Application crashes

**Fix**: Add safety checks

```prim
fn safe_operation(data: any) {
    if data is null {
        throw "Data is null";
    }
    // ... process data ...
}
```

### Deadlocks

**Issue**: Application hangs

**Fix**: Avoid circular dependencies

```prim
fn safe_locks() {
    let lock1 = mutex.new();
    let lock2 = mutex.new();

    // Always acquire in same order
    lock1.acquire();
    lock2.acquire();
    // ...
    lock2.release();
    lock1.release();
}
```

### Race Conditions

**Issue**: Data corruption

**Fix**: Use synchronization

```prim
let counter = atomic.new(0);

fn increment() {
    counter.increment();
}
```

---

## Debugging

### Logging

```prim
import logging;

fn main() {
    logging.info("Application started");
    logging.debug("Debug info");
    logging.warning("Warning");
    logging.error("Error occurred");
}
```

### Breakpoints

```prim
fn debug_function() {
    debug.break();  // Breakpoint
    let value = 42;
    debug.log("Value: " + value);
}
```

### Stack Traces

```prim
fn print_stack_trace() {
    let trace = debug.stack_trace();
    for frame in trace {
        print(frame.file + ":" + frame.line);
    }
}
```

---

## Summary

Troubleshooting involves:

1. **Common Errors**: Type mismatches, null references
2. **Performance**: Profile and optimize
3. **Memory**: Manage allocations
4. **Build**: Check dependencies
5. **Runtime**: Debug and fix

For more information, see the [Best Practices](./best_practices.md).
