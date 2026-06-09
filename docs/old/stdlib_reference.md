# Prim Language Standard Library Reference

## Table of Contents

- [I/O Operations](#io-operations)
- [Collections](#collections)
- [Math Functions](#math-functions)
- [String Operations](#string-operations)
- [File System](#file-system)
- [HTTP Client](#http-client)
- [JSON](#json)
- [Date/Time](#datetime)
- [Concurrency](#concurrency)
- [Error Handling](#error-handling)

---

## I/O Operations

### print

Prints a value to standard output.

```prim
fn print(value: any) -> void
```

**Example:**
```prim
print("Hello, World!");
print(42);
```

### input

Reads a line from standard input.

```prim
fn input(prompt: string = "") -> string
```

**Example:**
```prim
let name = input("Enter your name: ");
print("Hello, " + name);
```

---

## Collections

### List

#### Creation

```prim
let empty = [];
let numbers = [1, 2, 3, 4, 5];
let strings = ["a", "b", "c"];
```

#### Methods

```prim
numbers.length()          // Get length
numbers.push(6)          // Add to end
numbers.pop()            // Remove from end
numbers.insert(0, 0)      // Insert at index
numbers.remove(0)         // Remove at index
numbers.reverse()         // Reverse in place
numbers.sort()            // Sort in place
numbers.map(f)            // Apply function to each element
numbers.filter(f)         // Filter elements
numbers.reduce(f, init)   // Reduce to single value
```

### Dictionary

#### Creation

```prim
let empty = {};
let mapping = {
    "one": 1,
    "two": 2,
    "three": 3
};
```

#### Methods

```prim
mapping.keys()          // Get all keys
mapping.values()        // Get all values
mapping.items()          // Get all key-value pairs
mapping.get(key, default)  // Get value or default
mapping.set(key, value)  // Set value
mapping.has(key)         // Check if key exists
mapping.remove(key)       // Remove key
```

### Set

#### Creation

```prim
let empty = set([]);
let numbers = set([1, 2, 2, 3]);  // {1, 2, 3}
```

#### Methods

```prim
numbers.add(4)           // Add element
numbers.remove(4)        // Remove element
numbers.has(4)           // Check if element exists
numbers.union(other)     // Union with another set
numbers.intersection(other)  // Intersection with another set
```

---

## Math Functions

### Basic Operations

```prim
import math;

math.abs(-5)             // 5
math.min(1, 2, 3)        // 1
math.max(1, 2, 3)        // 3
math.round(3.7)           // 4
math.floor(3.7)           // 3
math.ceil(3.2)            // 4
```

### Trigonometry

```prim
math.sin(0)               // 0.0
math.cos(0)               // 1.0
math.tan(0)               // 0.0
math.asin(0)              // 0.0
math.acos(1)              // 0.0
math.atan(0)              // 0.0
```

### Powers and Roots

```prim
math.pow(2, 10)           // 1024.0
math.sqrt(16)             // 4.0
math.cbrt(8)              // 2.0
math.exp(1)               // 2.718...
math.log(10)              // 2.302...
math.log10(10)            // 1.0
```

### Random

```prim
math.random()             // Random 0.0-1.0
math.random_int(10)        // Random 0-9
math.random_float(10.0)    // Random 0.0-10.0
```

### Constants

```prim
math.PI                   // 3.14159...
math.E                    // 2.718...
math.TAU                   // 6.283...
```

---

## String Operations

### Basic Methods

```prim
let s = "Hello, World!";

s.length()               // 13
s.to_uppercase()         // "HELLO, WORLD!"
s.to_lowercase()         // "hello, world!"
s.trim()                 // "Hello, World!"
s.contains("World")      // true
s.startswith("Hello")    // true
s.endswith("!")          // true
```

### Substrings

```prim
s.substring(0, 5)        // "Hello"
s.slice(7, 12)           // "World"
s.split(",")             // ["Hello", " World!"]
```

### Modification

```prim
s.replace("World", "Prim")  // "Hello, Prim!"
s.to_uppercase()            // "HELLO, WORLD!"
s.to_lowercase()            // "hello, world!"
s.repeat(3)                 // "Hello!Hello!Hello!"
```

### Formatting

```prim
let name = "Alice";
let age = 25;
let msg = "Name: {}, Age: {}".format(name, age);
// "Name: Alice, Age: 25"
```

---

## File System

### Basic Operations

```prim
import fs;

fs.exists("file.txt")          // Check if file exists
fs.is_file("file.txt")         // Check if path is a file
fs.is_dir("directory")         // Check if path is a directory
```

### Reading and Writing

```prim
fs.read("file.txt")            // Read file content
fs.write("file.txt", "data")   // Write to file
fs.append("file.txt", "data")  // Append to file
```

### Directory Operations

```prim
fs.mkdir("directory")          // Create directory
fs.rmdir("directory")          // Remove directory
fs.listdir(".")                // List directory contents
fs.mkdir_p("a/b/c")           // Create nested directories
```

### File Info

```prim
let info = fs.info("file.txt");
info.size                      // File size in bytes
info.modified                  // Modification time
info.created                   // Creation time
```

---

## HTTP Client

### Basic Request

```prim
import http;

async fn get_data(url: string) -> string {
    let response = await http.get(url);
    return response.data;
}
```

### POST Request

```prim
async fn post_data(url: string, data: dict) -> string {
    let response = await http.post(url, data);
    return response.data;
}
```

### Options

```prim
let options = {
    "headers": {"Content-Type": "application/json"},
    "timeout": 5000
};

let response = await http.get(url, options);
```

---

## JSON

### Parsing

```prim
import json;

let data = json.parse('{"name": "Alice", "age": 30}');
print(data["name"]);  // "Alice"
print(data["age"]);   // 30
```

### Stringifying

```prim
let data = {"name": "Alice", "age": 30};
let text = json.stringify(data);
// '{"name":"Alice","age":30}'
```

---

## Date/Time

### Current Time

```prim
import time;

let now = time.now();
let timestamp = time.timestamp();
```

### Formatting

```prim
let formatted = time.format(now, "%Y-%m-%d %H:%M:%S");
// "2024-02-27 14:30:00"
```

### Parsing

```prim
let parsed = time.parse("2024-02-27", "%Y-%m-%d");
```

---

## Concurrency

### Async Functions

```prim
async fn fetch_data(url: string) -> string {
    let response = await http.get(url);
    return response.data;
}
```

### Parallel Execution

```prim
async fn parallel_tasks() {
    let tasks = [
        fetch_data("url1"),
        fetch_data("url2"),
        fetch_data("url3")
    ];

    let results = await Promise.all(tasks);
    print(results);
}
```

### Race Conditions

```prim
async fn race(tasks: list) -> any {
    return await Promise.race(tasks);
}
```

---

## Error Handling

### Throwing Errors

```prim
fn divide(a: int, b: int) -> int {
    if b == 0 {
        throw "Division by zero";
    }
    return a / b;
}
```

### Catching Errors

```prim
fn safe_divide(a: int, b: int) -> int {
    try {
        return divide(a, b);
    } catch (error: string) {
        print("Error: " + error);
        return 0;
    }
}
```

### Result Type

```prim
type Result<T> = Ok(T) | Error(string);

fn safe_operation() -> Result<int> {
    try {
        return Ok(do_something());
    } catch (error) {
        return Error(error);
    }
}
```

---

## Additional Modules

### Base64

```prim
import base64;

let encoded = base64.encode("Hello");
// "SGVsbG8="

let decoded = base64.decode("SGVsbG8=");
// "Hello"
```

### Hash

```prim
import hash;

let md5 = hash.md5("data");
let sha256 = hash.sha256("data");
```

### UUID

```prim
import uuid;

let id = uuid.v4();  // Generate random UUID
```

---

## Complete API Index

For a complete index of all APIs, see the [API Reference](./api_reference.md).

For examples and usage patterns, see the [Examples](../examples/) directory.
