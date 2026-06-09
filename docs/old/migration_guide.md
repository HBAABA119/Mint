# Prim Language Migration Guide

## Table of Contents

- [From Python](#from-python)
- [From JavaScript](#from-javascript)
- [From Java](#from-java)
- [From C++](#from-c++)
- [From Rust](#from-rust)

---

## From Python

### Similarities

- Clean, readable syntax
- Dynamic typing (optional static in Prim)
- High-level abstractions
- Rich standard library

### Key Differences

```python
# Python
def add(a, b):
    return a + b
```

```prim
// Prim
fn add(a: int, b: int) -> int {
    return a + b;
}
```

### Migration Steps

1. Add type annotations
2. Replace Python libraries with Prim equivalents
3. Use async/await for I/O
4. Update error handling

### Common Patterns

```python
# Python
def process(items):
    return [x * 2 for x in items]
```

```prim
// Prim
fn process(items: list[int]) -> list[int] {
    return items.map(fn(x) -> int { x * 2 });
}
```

---

## From JavaScript

### Similarities

- Modern syntax
- Arrow functions
- Async/await
- First-class functions

### Key Differences

```javascript
// JavaScript
const add = (a, b) => a + b;
```

```prim
// Prim
let add = (a: int, b: int) -> int => a + b;
```

### Migration Steps

1. Add type annotations
2. Replace JS libraries with Prim equivalents
3. Use classes instead of prototypes
4. Update error handling

### Common Patterns

```javascript
// JavaScript
fetch(url)
  .then(response => response.json())
  .then(data => console.log(data));
```

```prim
// Prim
async fn fetch_data(url: string) {
    let response = await http.get(url);
    let data = response.json();
    print(data);
}
```

---

## From Java

### Similarities

- Optional static typing
- Classes and objects
- Exception handling
- Strong type system

### Key Differences

```java
// Java
public int add(int a, int b) {
    return a + b;
}
```

```prim
// Prim
fn add(a: int, b: int) -> int {
    return a + b;
}
```

### Migration Steps

1. Simplify syntax
2. Remove boilerplate
3. Use modern features
4. Optimize hot paths

### Common Patterns

```java
// Java
List<Integer> numbers = Arrays.asList(1, 2, 3);
for (int n : numbers) {
    System.out.println(n);
}
```

```prim
// Prim
let numbers = [1, 2, 3];
for n in numbers {
    print(n);
}
```

---

## From C++

### Similarities

- Performance focus
- Type safety
- Manual optimization possible

### Key Differences

```cpp
// C++
int add(int a, int b) {
    return a + b;
}
```

```prim
// Prim
fn add(a: int, b: int) -> int {
    return a + b;
}
```

### Migration Steps

1. Simplify syntax
2. Use memory safety
3. Leverage GC
4. Use modern features

### Common Patterns

```cpp
// C++
std::vector<int> numbers = {1, 2, 3};
for (int n : numbers) {
    std::cout << n << std::endl;
}
```

```prim
// Prim
let numbers = [1, 2, 3];
for n in numbers {
    print(n);
}
```

---

## From Rust

### Similarities

- Type safety
- Modern features
- Pattern matching

### Key Differences

```rust
// Rust
fn add(a: i32, b: i32) -> i32 {
    a + b
}
```

```prim
// Prim
fn add(a: int, b: int) -> int {
    return a + b;
}
```

### Migration Steps

1. Simplify syntax
2. Use GC instead of ownership
3. Easier learning curve
4. Faster development

### Common Patterns

```rust
// Rust
fn main() {
    let numbers = vec![1, 2, 3];
    for n in numbers {
        println!("{}", n);
    }
}
```

```prim
// Prim
fn main() {
    let numbers = [1, 2, 3];
    for n in numbers {
        print(n);
    }
}
```

---

## Summary

Migration from other languages involves:

1. **Python**: Add types, use async/await
2. **JavaScript**: Add types, update patterns
3. **Java**: Simplify syntax, modernize
4. **C++**: Use GC, simplify
5. **Rust**: Easier syntax, use GC

For more information, see the [Tutorial](./tutorial.md).
