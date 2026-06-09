# Prim Language Error Handling Guide

## Table of Contents

- [Throwing Errors](#throwing-errors)
- [Catching Errors](#catching-errors)
- [Error Types](#error-types)
- [Error Propagation](#error-propagation)
- [Best Practices](#best-practices)

---

## Throwing Errors

### Basic Throw

```prim
fn divide(a: int, b: int) -> int {
    if b == 0 {
        throw "Division by zero";
    }
    return a / b;
}
```

### Throwing Objects

```prim
class Error {
    let message: string;
    let code: int;

    fn new(message: string, code: int) -> Error {
        return Error { message, code };
    }
}

fn validate_input(input: string) {
    if input.length() == 0 {
        throw Error.new("Empty input", 400);
    }
}
```

### Custom Error Types

```prim
type ValidationError = Error(string, int);
type DatabaseError = Error(string, int);
type NetworkError = Error(string, int);
```

---

## Catching Errors

### Basic Catch

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

### Multiple Catch Blocks

```prim
fn handle_operation() {
    try {
        do_something();
    } catch (error: ValidationError) {
        print("Validation error: " + error.message);
    } catch (error: DatabaseError) {
        print("Database error: " + error.message);
    } catch (error: string) {
        print("Unknown error: " + error);
    }
}
```

### Finally Block

```prim
fn with_cleanup() {
    let resource = open_resource();

    try {
        use_resource(resource);
    } catch (error) {
        print("Error: " + error);
    } finally {
        resource.close();
    }
}
```

---

## Error Types

### Result Type

```prim
type Result<T> = Ok(T) | Error(string);

fn divide(a: int, b: int) -> Result<int> {
    if b == 0 {
        return Error("Division by zero");
    }
    return Ok(a / b);
}
```

### Option Type

```prim
type Option<T> = Some(T) | None;

fn find_user(id: int) -> Option<User> {
    let user = database.get_user(id);
    if user {
        return Some(user);
    }
    return None;
}
```

### Pattern Matching on Results

```prim
fn handle_result(result: Result<int>) {
    match result {
        Ok(value) => print("Success: " + value),
        Error(error) => print("Error: " + error)
    }
}
```

---

## Error Propagation

### Propagating Errors

```prim
fn process_data(data: string) -> Result<string> {
    let validated = validate_input(data);
    if validated is Error {
        return validated;
    }

    let processed = transform(validated);
    return Ok(processed);
}
```

### Error Chaining

```prim
fn chain_operations() -> Result<string> {
    let step1 = operation1();
    if step1 is Error {
        return step1;
    }

    let step2 = operation2(step1);
    if step2 is Error {
        return step2;
    }

    return Ok(step2);
}
```

### Error Wrapping

```prim
fn wrap_error(inner: Result<string>, context: string) -> Result<string> {
    match inner {
        Ok(value) => Ok(value),
        Error(message) => Error(context + ": " + message)
    }
}
```

---

## Best Practices

### Always Handle Errors

```prim
// Bad
fn divide(a: int, b: int) -> int {
    return a / b;  // Might throw
}

// Good
fn divide(a: int, b: int) -> Result<int> {
    if b == 0 {
        return Error("Division by zero");
    }
    return Ok(a / b);
}
```

### Provide Context

```prim
// Bad
throw "Error";

// Good
throw "Failed to connect to database: connection timeout";
```

### Use Result Types

```prim
// Good
fn parse_int(s: string) -> Result<int> {
    try {
        return Ok(s.to_int());
    } catch {
        return Error("Invalid integer");
    }
}
```

### Document Errors

```prim
/// Divides two numbers.
/// @throws Error if b is zero
fn divide(a: int, b: int) -> Result<int> {
    if b == 0 {
        return Error("Division by zero");
    }
    return Ok(a / b);
}
```

---

## Summary

Error handling in Prim involves:

1. **Throwing**: Raise errors with context
2. **Catching**: Handle errors appropriately
3. **Types**: Use Result and Option types
4. **Propagation**: Chain errors properly
5. **Best Practices**: Always handle errors

For more information, see the [Best Practices](./best_practices.md).
