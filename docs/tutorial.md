# Prim Language Tutorial - Getting Started

## Welcome to Prim!

This tutorial will guide you from complete beginner to proficient Prim programmer. Prim is designed to be easy to learn while being powerful enough for production use.

## Lesson 1: Your First Program

### Hello World

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

**Output:**
```
Hello, World!
```

### Understanding the Code

- `fn main()`: Defines the main function (entry point)
- `{ ... }`: Function body (block of code)
- `print(...)`: Function to output text
- `"Hello, World!"`: String literal

## Lesson 2: Variables and Types

### Variables

Variables store values:

```prim
fn main() {
    let name = "Prim";
    let version = "1.0.0";
    let year = 2024;

    print("Language: " + name);
    print("Version: " + version);
    print("Year: " + year);
}
```

### Types

Prim has several built-in types:

```prim
fn types() {
    // Integer
    let integer: int = 42;

    // Float
    let floating: float = 3.14;

    // String
    let text: string = "Hello";

    // Boolean
    let flag: bool = true;

    // Null
    let nothing: null = null;

    print(integer);
    print(floating);
    print(text);
    print(flag);
    print(nothing);
}
```

### Mutable vs Immutable

```prim
fn mutability() {
    let mutable = 10;      // Can be reassigned
    const immutable = 20;   // Cannot be reassigned

    mutable = 15;          // OK
    // immutable = 25;      // Error!
}
```

## Lesson 3: Basic Operations

### Arithmetic

```prim
fn arithmetic() {
    let a = 10;
    let b = 5;

    print(a + b);   // 15 (addition)
    print(a - b);   // 5 (subtraction)
    print(a * b);   // 50 (multiplication)
    print(a / b);   // 2 (division)
    print(a % b);   // 0 (modulo)
    print(a ** b);  // 100000 (power)
}
```

### Comparison

```prim
fn comparison() {
    let a = 10;
    let b = 5;

    print(a == b);  // false (equal)
    print(a != b);  // true (not equal)
    print(a < b);   // false (less than)
    print(a > b);   // true (greater than)
    print(a <= b);  // false (less or equal)
    print(a >= b);  // true (greater or equal)
}
```

### Logical

```prim
fn logical() {
    let a = true;
    let b = false;

    print(a && b);  // false (AND)
    print(a || b);  // true (OR)
    print(!a);      // false (NOT)
}
```

## Lesson 4: Functions

### Defining Functions

```prim
fn greet(name: string) {
    print("Hello, " + name);
}

fn main() {
    greet("Alice");
    greet("Bob");
}
```

### Functions with Return Values

```prim
fn add(a: int, b: int) -> int {
    return a + b;
}

fn main() {
    let result = add(5, 3);
    print(result);  // 8
}
```

### Arrow Functions

```prim
fn main() {
    let multiply = (a: int, b: int) -> int => a * b;
    print(multiply(5, 3));  // 15
}
```

### Multiple Parameters

```prim
fn calculate_total(price: float, tax_rate: float) -> float {
    return price * (1 + tax_rate);
}

fn main() {
    let total = calculate_total(100.0, 0.08);
    print("Total: " + total);  // Total: 108.0
}
```

## Lesson 5: Control Flow

### If Statements

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

### While Loops

```prim
fn count_down(n: int) {
    while n > 0 {
        print(n);
        n = n - 1;
    }
    print("Done!");
}

fn main() {
    count_down(5);
}
```

### For Loops

```prim
fn print_numbers() {
    for i in 1..10 {
        print(i);
    }
}

fn print_list(items: list) {
    for item in items {
        print(item);
    }
}
```

### Break and Continue

```prim
fn demo_break_continue() {
    for i in 1..20 {
        if i == 5 {
            break;  // Exit loop
        }
        if i % 2 == 0 {
            continue;  // Skip this iteration
        }
        print(i);
    }
}
```

## Lesson 6: Collections

### Lists

```prim
fn lists() {
    // Create list
    let numbers = [1, 2, 3, 4, 5];

    // Access elements
    print(numbers[0]);  // 1
    print(numbers[-1]); // 5

    // Add elements
    numbers.push(6);

    // Remove elements
    numbers.pop();

    // Get length
    print(numbers.length());  // 5

    // Iterate
    for n in numbers {
        print(n);
    }
}
```

### Dictionaries

```prim
fn dictionaries() {
    // Create dictionary
    let person = {
        "name": "Alice",
        "age": 30,
        "city": "NYC"
    };

    // Access values
    print(person["name"]);  // Alice

    // Set values
    person["age"] = 31;

    // Check if key exists
    if "name" in person {
        print("Name exists");
    }
}
```

### List Methods

```prim
fn list_methods() {
    let numbers = [3, 1, 4, 1, 5, 9];

    // Sort
    numbers.sort();
    print(numbers);  // [1, 1, 3, 4, 5, 9]

    // Reverse
    numbers.reverse();
    print(numbers);  // [9, 5, 4, 3, 1, 1]

    // Map
    let doubled = numbers.map(fn(x) -> int { x * 2 });
    print(doubled);

    // Filter
    let evens = numbers.filter(fn(x) -> bool { x % 2 == 0 });
    print(evens);

    // Reduce
    let sum = numbers.reduce(fn(a, b) -> int { a + b }, 0);
    print(sum);
}
```

## Lesson 7: Pattern Matching

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

fn main() {
    describe_number(0);   // Zero
    describe_number(5);  // Other
    describe_number(15); // Large
}
```

## Lesson 8: Classes and Objects

### Defining Classes

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
```

### Using Classes

```prim
fn main() {
    let person = Person.new("Alice", 30);
    person.greet();
    print("Age: " + person.get_age());
}
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
    fn new(name: string) -> Dog {
        return Dog { name };
    }

    fn speak(self) {
        print("Woof!");
    }
}

fn main() {
    let dog = Dog.new("Buddy");
    dog.speak();  // Woof!
}
```

## Lesson 9: Error Handling

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

fn main() {
    let result = safe_divide(10, 0);
    print(result);  // Error: Division by zero, 0
}
```

### Finally Block

```prim
fn with_cleanup() {
    try {
        // Do something that might fail
    } catch (error) {
        // Handle error
    } finally {
        // Always execute
        print("Cleanup complete");
    }
}
```

## Lesson 10: Async/Await

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

### Parallel Tasks

```prim
async fn parallel() {
    let results = await Promise.all([
        fetch_data("url1"),
        fetch_data("url2"),
        fetch_data("url3")
    ]);
    print(results);
}
```

## Lesson 11: Working with Files

### Reading Files

```prim
fn read_file() {
    let content = file.read("data.txt");
    print(content);
}
```

### Writing Files

```prim
fn write_file() {
    file.write("output.txt", "Hello, World!");
}
```

### File Operations

```prim
fn file_operations() {
    // Check if file exists
    if file.exists("data.txt") {
        print("File exists");
    }

    // Get file info
    let info = file.info("data.txt");
    print("Size: " + info.size);
}
```

## Lesson 12: Modules and Imports

### Creating Modules

```prim
// math.prim
export fn add(a: int, b: int) -> int {
    return a + b;
}

export fn multiply(a: int, b: int) -> int {
    return a * b;
}
```

### Importing Modules

```prim
// main.prim
import { add, multiply } from math;

fn main() {
    print(add(5, 3));      // 8
    print(multiply(5, 3)); // 15
}
```

## Lesson 13: Complete Example

### Todo List Application

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

## Next Steps

Congratulations! You've completed the Prim tutorial. Next steps:

1. **Practice**: Build small projects
2. **Explore**: Try advanced features
3. **Read**: Check the [API Reference](./api_reference.md)
4. **Examples**: See more [examples](../examples/)

Happy coding with Prim! 🚀
