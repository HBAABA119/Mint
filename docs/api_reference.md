# Prim Language API Reference

## Table of Contents

- [Core Language](#core-language)
- [Standard Library](#standard-library)
- [I/O Operations](#io-operations)
- [Collections](#collections)
- [Math Functions](#math-functions)
- [String Operations](#string-operations)
- [Concurrency](#concurrency)
- [Error Handling](#error-handling)
- [Modules](#modules)

---

## Core Language

### Types

#### Primitive Types

```prim
// Integer (64-bit signed)
let x: int = 42;

// Float (64-bit floating point)
let y: float = 3.14;

// String (Unicode)
let s: string = "Hello";

// Boolean
let b: bool = true;

// Null
let n: null = null;
```

#### Composite Types

```prim
// List
let numbers: list[int] = [1, 2, 3];

// Dictionary
let mapping: dict[string, int] = {"one": 1, "two": 2};

// Function
let fn_type: fn(int, int) -> int = fn(a, b) { a + b };

// Optional
let maybe: int? = null;

// Tuple
let pair: (int, string) = (42, "hello");
```

### Variables

#### Declaration

```prim
// Mutable variable
let name = "Alice";

// Immutable constant
const PI = 3.14159;

// With type annotation
let age: int = 25;
```

#### Assignment

```prim
let x = 10;
x = 20;  // OK

const y = 30;
y = 40;  // Error: cannot reassign const
```

### Functions

#### Definition

```prim
fn add(a: int, b: int) -> int {
    return a + b;
}
```

#### Arrow Functions

```prim
let multiply = (a: int, b: int) -> int => a * b;
```

#### Higher-Order Functions

```prim
fn apply(f: fn(int) -> int, value: int) -> int {
    return f(value);
}
```

#### Closures

```prim
fn make_counter() -> fn() -> int {
    let count = 0;
    return fn() -> int {
        count = count + 1;
        return count;
    };
}
```

### Control Flow

#### If Statement

```prim
if condition {
    // code
} else if other_condition {
    // code
} else {
    // code
}
```

#### While Loop

```prim
while condition {
    // code
}
```

#### For Loop

```prim
for i in 0..10 {
    print(i);
}

for item in list {
    print(item);
}
```

#### Match Statement

```prim
match value {
    1 => print("One"),
    2 => print("Two"),
    x if x > 2 => print("Greater"),
    _ => print("Other")
}
```

---

## Standard Library

### I/O Operations

#### print

```prim
fn print(value: any) -> void
```

Prints a value to standard output.

```prim
print("Hello, World!");
print(42);
print([1, 2, 3]);
```

#### input

```prim
fn input(prompt: string = "") -> string
```

Reads a line from standard input.

```prim
let name = input("Enter your name: ");
print("Hello, " + name);
```

#### file.read

```prim
fn file.read(path: string) -> string
```

Reads entire file content.

```prim
let content = file.read("data.txt");
print(content);
```

#### file.write

```prim
fn file.write(path: string, content: string) -> void
```

Writes content to a file.

```prim
file.write("output.txt", "Hello, World!");
```

#### file.append

```prim
fn file.append(path: string, content: string) -> void
```

Appends content to a file.

```prim
file.append("log.txt", "New entry\n");
```

---

## Collections

### List Operations

#### Creation

```prim
let empty = [];
let numbers = [1, 2, 3, 4, 5];
let strings = ["a", "b", "c"];
```

#### Access

```prim
let first = numbers[0];  // 1
let last = numbers[-1];  // 5
```

#### Modification

```prim
numbers.push(6);      // Add to end
numbers.pop();        // Remove from end
numbers.insert(0, 0); // Insert at index
numbers.remove(0);     // Remove at index
```

#### Iteration

```prim
for item in numbers {
    print(item);
}

for i in 0..numbers.length() {
    print(numbers[i]);
}
```

#### Methods

```prim
numbers.length();      // Get length
numbers.reverse();     // Reverse in place
numbers.sort();        // Sort in place
numbers.map(fn(x) -> int { x * 2 });
numbers.filter(fn(x) -> bool { x > 3 });
numbers.reduce(fn(a, b) -> int { a + b }, 0);
```

### Dictionary Operations

#### Creation

```prim
let empty = {};
let mapping = {
    "one": 1,
    "two": 2,
    "three": 3
};
```

#### Access

```prim
let value = mapping["one"];
let default = mapping.get("four", 0);
```

#### Modification

```prim
mapping["four"] = 4;
mapping.set("five", 5);
```

#### Methods

```prim
mapping.keys();      // Get all keys
mapping.values();    // Get all values
mapping.items();     // Get all key-value pairs
mapping.has("one");  // Check if key exists
mapping.remove("one"); // Remove key
```

---

## Math Functions

### Basic Operations

```prim
import math;

math.abs(-5);        // 5
math.min(1, 2, 3);   // 1
math.max(1, 2, 3);   // 3
math.round(3.7);      // 4
math.floor(3.7);      // 3
math.ceil(3.2);       // 4
```

### Trigonometry

```prim
math.sin(0);          // 0.0
math.cos(0);          // 1.0
math.tan(0);          // 0.0
math.asin(0);         // 0.0
math.acos(1);         // 0.0
math.atan(0);         // 0.0
```

### Powers and Roots

```prim
math.pow(2, 10);      // 1024.0
math.sqrt(16);        // 4.0
math.cbrt(8);         // 2.0
math.exp(1);          // 2.718...
math.log(10);         // 2.302...
```

### Random

```prim
math.random();        // Random 0.0-1.0
math.random_int(10);  // Random 0-9
```

---

## String Operations

### Basic Operations

```prim
let s = "Hello, World!";

s.length();           // 13
s.to_uppercase();     // "HELLO, WORLD!"
s.to_lowercase();     // "hello, world!"
s.trim();            // "Hello, World!"
s.contains("World");  // true
s.startswith("Hello"); // true
s.endswith("!");      // true
```

### Substrings

```prim
s.substring(0, 5);    // "Hello"
s.slice(7, 12);       // "World"
s.split(",");         // ["Hello", " World!"]
```

### Modification

```prim
s.replace("World", "Prim"); // "Hello, Prim!"
s.to_uppercase();          // "HELLO, WORLD!"
s.to_lowercase();          // "hello, world!"
```

### Formatting

```prim
let name = "Alice";
let age = 25;
let msg = "Name: {}, Age: {}".format(name, age);
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

### Async Main

```prim
async fn main() {
    let data = await fetch_data("https://api.example.com");
    print(data);
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

### Finally Block

```prim
fn with_cleanup() {
    try {
        // Do something
    } catch (error) {
        // Handle error
    } finally {
        // Always execute
        print("Cleanup");
    }
}
```

---

## Modules

### Exporting

```prim
// math.prim
export fn add(a: int, b: int) -> int {
    return a + b;
}

export const PI = 3.14159;
```

### Importing

```prim
// Import specific items
import { add, PI } from math;

// Import entire module
import math;

// Import with alias
import math as m;
```

### Module Structure

```
my_project/
├── main.prim
├── utils.prim
└── models/
    ├── user.prim
    └── product.prim
```

---

## Additional APIs

### HTTP Client

```prim
import http;

async fn get_data() -> string {
    let response = await http.get("https://api.example.com");
    return response.data;
}
```

### JSON

```prim
import json;

let data = json.parse('{"name": "Alice"}');
let text = json.stringify(data);
```

### File System

```prim
import fs;

fs.exists("file.txt");
fs.mkdir("directory");
fs.rmdir("directory");
fs.listdir(".");
```

### Date/Time

```prim
import time;

let now = time.now();
let timestamp = time.timestamp();
let formatted = time.format(now, "%Y-%m-%d");
```

---

## Complete API Index

For a complete index of all APIs, see the [API Index](./api_index.md).

For examples and usage patterns, see the [Examples](../examples/) directory.
