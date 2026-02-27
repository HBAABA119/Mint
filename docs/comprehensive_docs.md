# Prim Language - Comprehensive Documentation

## Table of Contents

1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [Language Fundamentals](#language-fundamentals)
4. [Advanced Features](#advanced-features)
5. [Standard Library](#standard-library)
6. [Best Practices](#best-practices)
7. [Examples](#examples)

---

## Introduction

Prim is a modern, high-level programming language designed for simplicity, safety, and performance. It combines the elegance of Python with the performance of compiled languages, featuring:

- **Type Safety**: Optional static typing with type inference
- **Performance**: JIT compilation and native code generation
- **Concurrency**: Built-in async/await and parallel processing
- **Safety**: Memory safety with automatic garbage collection
- **Expressiveness**: Clean syntax with powerful abstractions

### Design Philosophy

Prim follows these core principles:

1. **Simplicity First**: Easy to learn, easy to write, easy to read
2. **Safety by Default**: Type-safe, memory-safe, thread-safe
3. **Performance Matters**: Fast compilation, fast execution, low overhead
4. **Pragmatic**: Real-world solutions for real-world problems
5. **Extensible**: Easy to extend with modules and libraries

---

## Getting Started

### Installation

```bash
# Clone the repository
git clone https://github.com/prim-lang/prim.git

# Build from source
cd prim
python setup.py install

# Or install via pip
pip install prim-lang
```

### Hello World

```prim
fn main() {
    print("Hello, World!");
}
```

### Running Programs

```bash
# Run a Prim file
prim run hello.prim

# Compile to native code
prim build --native hello.prim -o hello

# Run with JIT
prim run --jit hello.prim
```

---

## Language Fundamentals

### Variables

Variables are declared with `let` (mutable) or `const` (immutable):

```prim
let name = "Prim";
const version = "1.0.0";

name = "New Name";  // OK
version = "2.0.0";  // Error: cannot reassign const
```

### Types

Prim has primitive and composite types:

```prim
// Primitive types
let integer: int = 42;
let floating: float = 3.14;
let text: string = "hello";
let flag: bool = true;
let nothing: null = null;

// Composite types
let numbers: list[int] = [1, 2, 3, 4, 5];
let mapping: dict[string, int] = {"one": 1, "two": 2};

// Function types
let adder: fn(int, int) -> int = fn(a, b) { a + b };
```

### Functions

Functions are first-class citizens:

```prim
// Function definition
fn add(a: int, b: int) -> int {
    return a + b;
}

// Arrow function
let multiply = (a: int, b: int) -> int => a * b;

// Higher-order function
fn apply(f: fn(int) -> int, value: int) -> int {
    return f(value);
}

// Closures
fn make_counter() -> fn() -> int {
    let count = 0;
    return fn() -> int {
        count = count + 1;
        return count;
    };
}
```

### Control Flow

```prim
// If-else
if condition {
    // do something
} else if other_condition {
    // do something else
} else {
    // default case
}

// While loop
while condition {
    // loop body
}

// For loop
for i in 0..10 {
    print(i);
}

// Break and continue
for i in 0..100 {
    if i == 5 {
        break;
    }
    if i % 2 == 0 {
        continue;
    }
    print(i);
}
```

### Pattern Matching

```prim
match value {
    1 => print("One"),
    2 => print("Two"),
    _ => print("Other")
}
```

---

## Advanced Features

### Classes and Objects

```prim
class Person {
    let name: string;
    let age: int;

    fn new(name: string, age: int) -> Person {
        return Person { name, age };
    }

    fn greet(self) {
        print("Hello, I'm " + self.name);
    }

    fn get_age(self) -> int {
        return self.age;
    }
}

let person = Person.new("Alice", 30);
person.greet();
```

### Inheritance

```prim
class Animal {
    let name: string;

    fn new(name: string) -> Animal {
        return Animal { name };
    }

    fn speak(self) {
        print("Animal sound");
    }
}

class Dog extends Animal {
    let breed: string;

    fn new(name: string, breed: string) -> Dog {
        return Dog { name, breed };
    }

    fn speak(self) {
        print("Woof!");
    }
}
```

### Async/Await

```prim
async fn fetch_data(url: string) -> string {
    let response = await http.get(url);
    return response.data;
}

async fn main() {
    let data = await fetch_data("https://api.example.com");
    print(data);
}
```

### Error Handling

```prim
fn divide(a: int, b: int) -> int {
    if b == 0 {
        throw "Division by zero";
    }
    return a / b;
}

fn safe_divide(a: int, b: int) -> int {
    try {
        return divide(a, b);
    } catch (error: string) {
        print("Error: " + error);
        return 0;
    } finally {
        print("Cleanup");
    }
}
```

### Modules and Imports

```prim
// Import specific items
import { add, subtract } from math;

// Import entire module
import math;

// Import with alias
import math as m;

// Export
export fn my_function() { ... }
export const MY_CONST = 42;
```

---

## Standard Library

### Collections

```prim
// Lists
let numbers = [1, 2, 3, 4, 5];
numbers.push(6);
numbers.pop();
numbers.map(fn(x) -> int { x * 2 });
numbers.filter(fn(x) -> bool { x > 3 });

// Dictionaries
let mapping = {"key": "value"};
mapping.get("key");
mapping.set("new_key", "new_value");

// Sets
let unique = set([1, 2, 2, 3, 3, 3]);
```

### I/O Operations

```prim
// File reading
let content = file.read("data.txt");

// File writing
file.write("output.txt", "Hello, World!");

// Console I/O
print("Enter your name:");
let name = input();
print("Hello, " + name);
```

### String Operations

```prim
let text = "Hello, World!";
text.length();           // 13
text.to_uppercase();     // "HELLO, WORLD!"
text.to_lowercase();     // "hello, world!"
text.contains("World");   // true
text.split(",");          // ["Hello", " World!"]
text.replace("World", "Prim");  // "Hello, Prim!"
```

### Math Operations

```prim
import math;

math.sqrt(16);      // 4.0
math.pow(2, 10);    // 1024.0
math.sin(math.pi);   // 0.0
math.random();      // Random number 0-1
```

---

## Best Practices

### Naming Conventions

- **Variables**: `snake_case` - `my_variable`
- **Functions**: `snake_case` - `my_function`
- **Classes**: `PascalCase` - `MyClass`
- **Constants**: `SCREAMING_SNAKE_CASE` - `MY_CONSTANT`
- **Modules**: `snake_case` - `my_module`

### Code Organization

```prim
// Imports
import std.io;
import std.math;

// Constants
const MAX_SIZE = 100;

// Types
type Result<T> = Ok(T) | Error(string);

// Functions
fn main() {
    // Main logic
}
```

### Error Handling

```prim
// Always handle potential errors
fn safe_operation() -> Result<string> {
    try {
        return Ok(do_something());
    } catch (error) {
        return Error(error);
    }
}

// Pattern match on results
match safe_operation() {
    Ok(value) => print(value),
    Error(error) => print("Error: " + error)
}
```

### Performance Tips

1. Use `const` for immutable values
2. Avoid unnecessary allocations
3. Use built-in functions over manual loops
4. Profile before optimizing
5. Use async/await for I/O operations

---

## Examples

### Fibonacci Sequence

```prim
fn fibonacci(n: int) -> int {
    if n <= 1 {
        return n;
    }
    return fibonacci(n - 1) + fibonacci(n - 2);
}

fn main() {
    for i in 0..10 {
        print(fibonacci(i));
    }
}
```

### Prime Numbers

```prim
fn is_prime(n: int) -> bool {
    if n < 2 {
        return false;
    }
    for i in 2..n {
        if n % i == 0 {
            return false;
        }
    }
    return true;
}

fn primes_up_to(n: int) -> list[int] {
    let result = [];
    for i in 2..n {
        if is_prime(i) {
            result.push(i);
        }
    }
    return result;
}
```

### HTTP Server

```prim
async fn handle_request(request: Request) -> Response {
    match request.path {
        "/" => Response.ok("Hello, World!"),
        "/api/data" => Response.json({"data": "value"}),
        _ => Response.not_found()
    }
}

async fn main() {
    let server = Server.new(handle_request);
    await server.listen("0.0.0.0:8080");
}
```

---

## Resources

- [Language Specification](./language_specification.md)
- [Grammar Reference](./grammar.md)
- [API Documentation](./api.md)
- [Tutorials](./tutorials/)
- [Examples](../examples/)
