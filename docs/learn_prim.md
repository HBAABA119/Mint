# Learn Prim - A Complete Learning Guide

## Table of Contents

1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [Basic Concepts](#basic-concepts)
4. [Intermediate Features](#intermediate-features)
5. [Advanced Topics](#advanced-topics)
6. [Best Practices](#best-practices)
7. [Projects](#projects)
8. [Resources](#resources)

---

## Introduction

Welcome to Prim! This guide will take you from complete beginner to proficient Prim programmer. Prim is designed to be easy to learn while being powerful enough for production use.

### Why Prim?

- **Easy to Learn**: Clean syntax, minimal boilerplate
- **Type Safe**: Optional static typing catches errors early
- **Fast**: JIT compilation and native code generation
- **Modern**: Async/await, pattern matching, classes
- **Pragmatic**: Real-world solutions for real problems

### Prerequisites

- Basic programming knowledge (variables, functions, loops)
- Familiarity with any programming language helps
- Text editor or IDE
- Prim compiler/interpreter

---

## Getting Started

### Installation

```bash
# Install Prim
pip install prim-lang

# Or download from GitHub
git clone https://github.com/prim-lang/prim.git
cd prim
python setup.py install
```

### Your First Program

Create a file `hello.prim`:

```prim
fn main() {
    print("Hello, World!");
}
```

Run it:

```bash
prim run hello.prim
```

Output:
```
Hello, World!
```

### Understanding the Code

- `fn main()`: Defines a function named `main`
- `{ ... }`: Function body (block of code)
- `print(...)`: Function call to print text
- `"Hello, World!"`: String literal

---

## Basic Concepts

### Variables and Types

Variables store values. Prim has several built-in types:

```prim
// Integers (whole numbers)
let age: int = 25;
let count = 100;  // Type inferred

// Floats (decimal numbers)
let price: float = 19.99;
let pi = 3.14159;

// Strings (text)
let name: string = "Alice";
let greeting = "Hello, " + name;

// Booleans (true/false)
let is_active: bool = true;
let is_valid = false;

// Null (no value)
let nothing: null = null;
```

**Mutable vs Immutable:**

```prim
let mutable = 10;      // Can be reassigned
const immutable = 20;   // Cannot be reassigned

mutable = 15;          // OK
immutable = 25;        // Error!
```

### Basic Operations

```prim
// Arithmetic
let sum = 10 + 5;      // 15
let diff = 10 - 5;     // 5
let product = 10 * 5;   // 50
let quotient = 10 / 5;  // 2
let remainder = 10 % 5;  // 0
let power = 2 ** 10;    // 1024

// Comparison
let equal = 10 == 10;      // true
let not_equal = 10 != 5;   // true
let less = 5 < 10;         // true
let greater = 10 > 5;      // true

// Logical
let and_result = true && false;  // false
let or_result = true || false;   // true
let not_result = !true;           // false
```

### Control Flow

#### If Statements

```prim
fn check_age(age: int) {
    if age < 18 {
        print("Minor");
    } else if age >= 18 && age < 65 {
        print("Adult");
    } else {
        print("Senior");
    }
}
```

#### While Loops

```prim
fn count_down(n: int) {
    while n > 0 {
        print(n);
        n = n - 1;
    }
    print("Done!");
}
```

#### For Loops

```prim
fn print_numbers() {
    for i in 1..10 {
        print(i);
    }
}

fn iterate_list(items: list) {
    for item in items {
        print(item);
    }
}
```

### Functions

Functions are reusable blocks of code:

```prim
// Function definition
fn greet(name: string) {
    print("Hello, " + name);
}

// Function with return type
fn add(a: int, b: int) -> int {
    return a + b;
}

// Arrow function (shorter syntax)
let multiply = (a: int, b: int) -> int => a * b;

// Calling functions
greet("Alice");
let result = add(5, 3);  // 8
```

**Parameters and Return Types:**

```prim
fn calculate_area(width: int, height: int) -> int {
    return width * height;
}

fn get_name() -> string {
    return "Prim";
}

fn no_return() {
    print("This function returns nothing");
}
```

### Collections

#### Lists

```prim
// Create list
let numbers = [1, 2, 3, 4, 5];

// Access elements
let first = numbers[0];  // 1

// Add elements
numbers.push(6);

// Remove elements
numbers.pop();

// List methods
numbers.length();      // Get length
numbers.reverse();     // Reverse list
numbers.sort();        // Sort list
```

#### Dictionaries

```prim
// Create dictionary
let person = {
    "name": "Alice",
    "age": 30,
    "city": "NYC"
};

// Access values
let name = person["name"];

// Set values
person["age"] = 31;

// Check if key exists
if "name" in person {
    print("Name exists");
}
```

---

## Intermediate Features

### Pattern Matching

Pattern matching is a powerful way to handle different cases:

```prim
fn describe_number(n: int) {
    match n {
        0 => print("Zero"),
        1 => print("One"),
        2 => print("Two"),
        x if x < 0 => print("Negative"),
        x if x > 10 => print("Large"),
        _ => print("Other")
    }
}
```

### Classes and Objects

Classes define blueprints for objects:

```prim
class Person {
    let name: string;
    let age: int;

    // Constructor
    fn new(name: string, age: int) -> Person {
        return Person { name, age };
    }

    // Method
    fn greet(self) {
        print("Hello, I'm " + self.name);
    }

    fn get_age(self) -> int {
        return self.age;
    }
}

// Create instance
let person = Person.new("Alice", 30);
person.greet();
```

### Inheritance

Classes can extend other classes:

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

let dog = Dog.new("Buddy", "Golden Retriever");
dog.speak();  // Woof!
```

### Error Handling

Handle errors gracefully:

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
        print("Cleanup complete");
    }
}
```

### Modules and Imports

Organize code into modules:

```prim
// math.prim
export fn add(a: int, b: int) -> int {
    return a + b;
}

export fn multiply(a: int, b: int) -> int {
    return a * b;
}

// main.prim
import { add, multiply } from math;

let result = add(5, 3);
```

---

## Advanced Topics

### Async/Await

Handle asynchronous operations:

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

### Type System

Advanced type features:

```prim
// Union types
type Result = int | string;

// Optional types
type MaybeInt = int | null;

// Generic types
type Pair<T> = { first: T, second: T };

// Type inference
fn identity<T>(value: T) -> T {
    return value;
}
```

### Functional Programming

Higher-order functions:

```prim
// Map
let doubled = [1, 2, 3].map(fn(x) -> int { x * 2 });

// Filter
let evens = [1, 2, 3, 4, 5].filter(fn(x) -> bool { x % 2 == 0 });

// Reduce
let sum = [1, 2, 3].reduce(fn(a, b) -> int { a + b }, 0);
```

---

## Best Practices

### Naming Conventions

- **Variables**: `snake_case` - `my_variable`
- **Functions**: `snake_case` - `my_function`
- **Classes**: `PascalCase` - `MyClass`
- **Constants**: `SCREAMING_SNAKE_CASE` - `MY_CONSTANT`

### Code Style

```prim
// Good
fn calculate_total(price: float, tax_rate: float) -> float {
    return price * (1 + tax_rate);
}

// Avoid
fn calc(p, t) { return p * (1 + t); }
```

### Error Handling

Always handle potential errors:

```prim
fn safe_operation() -> Result {
    try {
        return Ok(do_something());
    } catch (error) {
        return Error(error);
    }
}
```

### Documentation

Document your code:

```prim
/// Adds two numbers together.
/// @param a First number
/// @param b Second number
/// @return Sum of a and b
fn add(a: int, b: int) -> int {
    return a + b;
}
```

---

## Projects

### Project 1: Calculator

Create a simple calculator:

```prim
fn main() {
    print("Calculator");
    print("Enter first number:");
    let a = input().to_int();
    print("Enter operation (+, -, *, /):");
    let op = input();
    print("Enter second number:");
    let b = input().to_int();

    let result = match op {
        "+" => a + b,
        "-" => a - b,
        "*" => a * b,
        "/" => a / b,
        _ => throw "Invalid operation"
    };

    print("Result: " + result);
}
```

### Project 2: Todo List

```prim
fn main() {
    let todos = [];

    while true {
        print("\n1. Add todo");
        print("2. List todos");
        print("3. Exit");
        print("Choice:");
        let choice = input().to_int();

        match choice {
            1 => {
                print("Enter todo:");
                let todo = input();
                todos.push(todo);
                print("Added!");
            },
            2 => {
                for i in 0..todos.length() {
                    print((i + 1) + ". " + todos[i]);
                }
            },
            3 => break,
            _ => print("Invalid choice")
        }
    }
}
```

### Project 3: Guess the Number

```prim
import math;

fn main() {
    let secret = math.random() * 100;
    let guesses = 0;

    while true {
        print("Guess a number (0-100):");
        let guess = input().to_int();
        guesses = guesses + 1;

        if guess == secret {
            print("Correct! You guessed it in " + guesses + " tries!");
            break;
        } else if guess < secret {
            print("Too low!");
        } else {
            print("Too high!");
        }
    }
}
```

---

## Resources

### Official Documentation

- [Language Specification](./language_specification.md)
- [Grammar Reference](./grammar.md)
- [API Documentation](./api.md)

### Community

- GitHub: https://github.com/prim-lang/prim
- Discord: https://discord.gg/prim
- Forum: https://forum.prim-lang.org

### Tutorials

- [Getting Started Guide](./tutorials/getting_started.md)
- [Advanced Patterns](./tutorials/advanced_patterns.md)
- [Best Practices](./tutorials/best_practices.md)

### Examples

- [Example Programs](../examples/)
- [Code Snippets](../snippets/)
- [Templates](../templates/)

---

## Next Steps

Now that you've learned the basics:

1. **Practice**: Build small projects
2. **Explore**: Try advanced features
3. **Contribute**: Help improve Prim
4. **Share**: Show off your projects

Happy coding with Prim! 🚀
