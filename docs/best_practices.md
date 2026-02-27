# Prim Language Best Practices

## Overview

This guide covers best practices for writing clean, efficient, and maintainable Prim code.

## Code Style

### Naming Conventions

#### Variables and Functions

Use `snake_case` for variables and functions:

```prim
// Good
let user_name = "Alice";
fn calculate_total(price, tax) { ... }

// Bad
let UserName = "Alice";
fn CalculateTotal(price, tax) { ... }
```

#### Classes

Use `PascalCase` for classes:

```prim
// Good
class UserController { ... }
class DatabaseConnection { ... }

// Bad
class userController { ... }
class database_connection { ... }
```

#### Constants

Use `SCREAMING_SNAKE_CASE` for constants:

```prim
// Good
const MAX_SIZE = 1000;
const API_KEY = "xyz123";

// Bad
const max_size = 1000;
const api_key = "xyz123";
```

### Indentation and Spacing

Use 4 spaces for indentation:

```prim
fn example() {
    if condition {
        do_something();
    } else {
        do_else();
    }
}
```

### Line Length

Keep lines under 100 characters:

```prim
// Good
fn calculate_total(price: float, tax_rate: float) -> float {
    return price * (1 + tax_rate);
}

// Bad
fn calculate_total(price: float, tax_rate: float) -> float { return price * (1 + tax_rate); }
```

## Code Organization

### File Structure

Organize code logically:

```
project/
├── main.prim
├── models/
│   ├── user.prim
│   └── product.prim
├── utils/
│   ├── helpers.prim
│   └── validators.prim
└── config.prim
```

### Module Structure

```prim
// Imports
import std.io;
import std.math;

// Constants
const MAX_SIZE = 1000;

// Types
type Result<T> = Ok(T) | Error(string);

// Functions
fn main() { ... }
```

## Type Safety

### Use Type Annotations

Add type annotations to function signatures:

```prim
// Good
fn add(a: int, b: int) -> int {
    return a + b;
}

// Bad
fn add(a, b) {
    return a + b;
}
```

### Use Const for Immutability

Use `const` for values that shouldn't change:

```prim
// Good
const PI = 3.14159;
const MAX_SIZE = 1000;

// Bad
let pi = 3.14159;
let max_size = 1000;
```

### Use Optional Types

Use optional types for values that might be null:

```prim
// Good
fn find_user(id: int) -> User? {
    if has_user(id) {
        return get_user(id);
    }
    return null;
}

// Bad
fn find_user(id: int) -> User {
    return get_user(id);  // Might return null
}
```

## Error Handling

### Always Handle Errors

Never ignore potential errors:

```prim
// Good
fn safe_divide(a: int, b: int) -> Result<int> {
    if b == 0 {
        return Error("Division by zero");
    }
    return Ok(a / b);
}

// Bad
fn divide(a: int, b: int) -> int {
    return a / b;  // Might divide by zero
}
```

### Use Pattern Matching for Results

```prim
// Good
match result {
    Ok(value) => print(value),
    Error(error) => print("Error: " + error)
}

// Bad
if result.is_ok() {
    print(result.unwrap());
}
```

### Provide Helpful Error Messages

```prim
// Good
throw "Failed to connect to database: " + error_message;

// Bad
throw "Error";
```

## Performance

### Avoid Unnecessary Allocations

```prim
// Good
fn process_string(s: string) -> string {
    return s.to_uppercase();
}

// Bad
fn process_string(s: string) -> string {
    let temp1 = s.to_uppercase();
    let temp2 = temp1.trim();
    let temp3 = temp2.replace(" ", "_");
    return temp3;
}
```

### Use Built-in Functions

```prim
// Good
let sum = numbers.reduce(fn(a, b) -> int { a + b }, 0);

// Bad
let sum = 0;
for n in numbers {
    sum = sum + n;
}
```

### Profile Before Optimizing

```prim
// Profile first, then optimize hot paths
fn main() {
    let start = time.now();
    // ... code ...
    let duration = time.now() - start;
    print("Duration: " + duration);
}
```

## Security

### Validate Input

```prim
// Good
fn process_input(input: string) -> Result<string> {
    if input.length() == 0 {
        return Error("Empty input");
    }
    return Ok(input.trim());
}

// Bad
fn process_input(input: string) -> string {
    return input;
}
```

### Use Safe Defaults

```prim
// Good
fn get_config(key: string) -> string {
    return config.get(key, "default_value");
}

// Bad
fn get_config(key: string) -> string {
    return config[key];  // Might not exist
}
```

### Sanitize Output

```prim
// Good
fn sanitize_html(input: string) -> string {
    return input.replace("<", "&lt;").replace(">", "&gt;");
}

// Bad
fn display_html(input: string) -> string {
    return input;  // XSS vulnerability
}
```

## Testing

### Write Tests

```prim
@test
fn test_add() {
    assert_equal(add(2, 3), 5);
    assert_equal(add(-1, 1), 0);
}
```

### Test Edge Cases

```prim
@test
fn test_divide() {
    assert_equal(divide(10, 2), 5);
    assert_raises(divide(10, 0));
}
```

### Keep Tests Simple

```prim
// Good
@test
fn test_addition() {
    assert_equal(add(2, 3), 5);
}

// Bad
@test
fn test_complex_flow() {
    let result = complex_function();
    assert_true(result.is_some());
    // ... more complex assertions
}
```

## Documentation

### Document Public APIs

```prim
/// Adds two numbers together.
/// @param a First number
/// @param b Second number
/// @return Sum of a and b
fn add(a: int, b: int) -> int {
    return a + b;
}
```

### Add Examples

```prim
/// Calculate the total price including tax.
///
/// # Examples
/// ```
/// calculate_total(100.0, 0.08)  // Returns 108.0
/// ```
fn calculate_total(price: float, tax_rate: float) -> float {
    return price * (1 + tax_rate);
}
```

### Keep Docs Updated

Update documentation when code changes.

## Concurrency

### Use Async for I/O

```prim
// Good
async fn fetch_data(url: string) -> string {
    let response = await http.get(url);
    return response.data;
}

// Bad
fn fetch_data(url: string) -> string {
    let response = http.get(url);  // Blocks
    return response.data;
}
```

### Handle Race Conditions

```prim
// Good
let lock = Lock.new();

fn update_counter() {
    lock.acquire();
    counter = counter + 1;
    lock.release();
}

// Bad
fn update_counter() {
    counter = counter + 1;  // Race condition
}
```

### Use Proper Error Handling in Async

```prim
// Good
async fn safe_fetch(url: string) -> Result<string> {
    try {
        let data = await http.get(url);
        return Ok(data);
    } catch (error) {
        return Error(error);
    }
}

// Bad
async fn fetch(url: string) -> string {
    return await http.get(url);  // Might throw
}
```

## Memory Management

### Avoid Memory Leaks

```prim
// Good
fn process_data(data: list) {
    let result = transform(data);
    // Use result, then let it be garbage collected
}

// Bad
fn process_data(data: list) {
    let cache = {};  // Global cache never cleared
    cache["data"] = data;
}
```

### Use Appropriate Data Structures

```prim
// Good - Use set for unique values
let unique = set([1, 2, 2, 3]);

// Bad - Use list and check manually
let unique = [];
for n in numbers {
    if not (n in unique) {
        unique.push(n);
    }
}
```

## Code Reviews

### Review Your Own Code

Before committing, review your code:
- Does it work correctly?
- Is it readable?
- Is it efficient?
- Is it secure?
- Is it documented?

### Get Peer Reviews

Have others review your code for:
- Logic errors
- Style issues
- Performance problems
- Security vulnerabilities

## Common Pitfalls

### Avoid Global State

```prim
// Bad
let global_counter = 0;

fn increment() {
    global_counter = global_counter + 1;
}

// Good
class Counter {
    let count: int;

    fn new() -> Counter {
        return Counter { count: 0 };
    }

    fn increment(self) {
        self.count = self.count + 1;
    }
}
```

### Avoid Magic Numbers

```prim
// Bad
if user.age > 65 {
    print("Senior");
}

// Good
const SENIOR_AGE = 65;

if user.age > SENIOR_AGE {
    print("Senior");
}
```

### Avoid Deep Nesting

```prim
// Bad
if condition1 {
    if condition2 {
        if condition3 {
            do_something();
        }
    }
}

// Good
if condition1 && condition2 && condition3 {
    do_something();
}
```

## Tools and Automation

### Use Linters

Configure linters to enforce style:

```prim
// .primrc
{
    "indent_size": 4,
    "max_line_length": 100,
    "require_type_annotations": true
}
```

### Use Formatters

Auto-format code:

```bash
prim format --check .
prim format --write .
```

### Use Pre-commit Hooks

```bash
# .git/hooks/pre-commit
#!/bin/bash
prim format --check .
prim test
```

## Summary

Following these best practices will help you write:
- Clean, readable code
- Efficient, performant code
- Secure, reliable code
- Maintainable, scalable code

For more information, see the [API Reference](./api_reference.md) and [Tutorial](./tutorial.md).
