# Prim Programming Language - v1.0

**Prim: Write it your way.**

Prim is a revolutionary multi-syntax programming language that allows developers to choose their preferred syntax style while sharing the same runtime and ecosystem. With three distinct syntax modes, Prim accommodates different programming backgrounds and preferences while maintaining semantic consistency.

> **🚀 Now Available on GitHub!** This is the official v1.0 release of the Prim programming language.

## Table of Contents
- [Overview](#overview)
- [Syntax Modes](#syntax-modes)
- [Features](#features)
- [Quick Start](#quick-start)
- [File Structure](#file-structure)
- [Installation](#installation)
- [Usage](#usage)
- [Standard Library](#standard-library)
- [Package Management](#package-management)
- [Examples](#examples)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [License](#license)

## Quick Start

Get started with Prim in under 2 minutes:

```bash
# Clone the repository
git clone https://github.com/HBAABA119/prim-language
cd prim-language

# Run a simple example
python prim_compiler.py

# Try different syntax modes
python prim_compiler.py examples/slim_example.prim
python prim_compiler.py examples/block_example.prim
python prim_compiler.py examples/flow_example.prim
```

**Example Code:**
```prim
#mode slim
message = "Hello, Prim!"
print(message)
```

See [Examples](#examples) for more code samples in all three syntax modes.

## Overview

Prim embodies the principle: **one language, multiple syntax "modes."** You pick how you want to write it. All modes compile to the same runtime, ensuring semantic equivalence across syntax choices.

The language is designed for:
- **Flexibility**: Choose syntax that feels most natural to you
- **Compatibility**: Code written in different modes interoperate seamlessly
- **Productivity**: Leverage familiar syntax patterns from other languages
- **Consistency**: Maintain the same underlying semantics and behavior

## Syntax Modes

### Slim Mode (`#mode slim`)
Python-like, indentation-based syntax:
```prim
#mode slim
x = 42
y = 28
result = x + y
print("Result:", result)
```

### Block Mode (`#mode block`)
C/JavaScript-style with braces and semicolons:
```prim
#mode block
var x = 42;
var y = 28;
var result = x + y;
print("Result:", result);
```

### Flow Mode (`#mode flow`)
Functional/pipe-based syntax:
```prim
#mode flow
x := 42
y := 28
result := x + y
"Result:" |> print(#, result)
```

## Features

- **Three Syntax Modes**: Choose between slim (Python-like), block (C/JS-like), or flow (functional)
- **Standard Library**: Comprehensive built-in functions for collections, strings, math, and I/O
- **Modules & Imports**: Organize code into reusable modules
- **Static Type System**: Optional type annotations and checking
- **Async/Await**: First-class asynchronous programming support
- **Bytecode Compiler**: High-performance virtual machine execution
- **Package Management**: Built-in package manager (prism-get)
- **Self-Hosting**: The compiler is written in Prim itself

## File Structure

### Core Runtime
- `prim_interpreter.py`: Core interpreter with runtime environment
- `prim_compiler.py`: Main compiler that selects parser based on mode directive
- `prim_slim_parser.py`: Parser for slim (Python-like) syntax
- `prim_block_parser.py`: Parser for block (C/JS-like) syntax  
- `prim_flow_parser.py`: Parser for flow (functional) syntax

### Standard Library
- `prim_std_lib.py`: Main standard library module
- `prim_std_collections.py`: Collection utilities (map, filter, reduce, etc.)
- `prim_std_strings.py`: String operations (upper, lower, split, etc.)
- `prim_std_math.py`: Mathematical functions (sqrt, sin, cos, etc.)
- `prim_std_io.py`: I/O operations (print, file operations, etc.)

### Advanced Features
- `prim_modules.py`: Module system and file I/O operations
- `prim_type_checker.py`: Static type annotations and type checking system
- `prim_async.py`: Async/await support and promise/future system
- `prim_bytecode.py`: Bytecode compiler and virtual machine

### Tools & Examples
- `prism_get.py`: Package manager (prism-get)
- `prim_self_hosted.prim`: Prim compiler written in Prim (self-hosted)
- `prim_syntax_examples.prim`: Examples demonstrating all three syntax modes

## Installation

Prim requires Python 3.6 or higher. Clone the repository and install dependencies:

```bash
git clone <repository-url>
cd prim-language
pip install -r requirements.txt  # if any
```

## Usage

### Running Prim Code

To run a Prim program, use the compiler:

```bash
python prim_compiler.py
```

The compiler automatically detects the mode from the `#mode` directive in your source file.

### Creating a New Project

1. Create a new `.prim` file
2. Add a mode directive at the top: `#mode slim`, `#mode block`, or `#mode flow`
3. Write your code using the chosen syntax
4. Run with the Prim compiler

### Example Programs

See `prim_syntax_examples.prim` for comprehensive examples in all three syntax modes.

## Standard Library

Prim includes a rich standard library organized into modules:

### Collections
- `map(list, fn)`: Transform list elements
- `filter(list, fn)`: Filter list elements
- `reduce(list, fn, initial?)`: Reduce list to single value
- `len(container)`: Get length of container

### Strings
- `upper(str)`, `lower(str)`: Case conversion
- `split(str, delimiter?)`: Split string by delimiter
- `join(list, separator?)`: Join list elements
- `trim(str)`: Trim whitespace

### Math
- `abs(n)`, `floor(n)`, `ceil(n)`: Basic math functions
- `sqrt(n)`, `pow(base, exp)`: Advanced operations
- `min(...n)`, `max(...n)`: Aggregate functions
- `pi`, `e`: Mathematical constants

### I/O
- `print(...values)`: Output to console
- `read_file(path)`, `write_file(path, content)`: File operations
- `file_exists(path)`: Check file existence
- `json_parse(str)`, `json_stringify(obj)`: JSON operations

## Package Management

Prim includes its own package manager, `prism-get`:

```bash
# Install a package
python prism_get.py install package_name

# Search for packages
python prism_get.py search query

# List installed packages
python prism_get.py list

# Initialize a new project
python prism_get.py init project_name
```

## Examples

### Basic Arithmetic (Slim Mode)
```prim
#mode slim
x = 10
y = 20
result = x + y
print("Sum:", result)
```

### Functional Programming (Flow Mode)
```prim
#mode flow
numbers := [1, 2, 3, 4, 5]
squared := map(numbers, |x| -> x * x)
sum_of_squares := reduce(squared, |acc, val| -> acc + val, 0)
print("Sum of squares:", sum_of_squares)
```

### Control Flow (Block Mode)
```prim
#mode block
var x = 15;
if (x > 10) {
    print("x is greater than 10");
} else {
    print("x is 10 or less");
};
```

## Roadmap

Check out our comprehensive [PRIM_ROADMAP.md](PRIM_ROADMAP.md) for the complete development plan from v1.1 through v15.3, including:

- **v1.x Series**: Foundation enhancement and self-hosting migration
- **v2.x Series**: Production readiness and platform expansion
- **v3.x Series**: AI and data science capabilities
- **v4.x-v10.x**: Advanced computing paradigms
- **v11.x-v15.x**: Hyperdimensional and absolute computing

## Contributing

We welcome contributions to Prim! Here's how you can help:

### Ways to Contribute
- **Code**: Help implement new features from the roadmap
- **Documentation**: Improve examples and tutorials
- **Testing**: Report bugs and edge cases
- **Feedback**: Share your experience with multi-syntax programming
- **Community**: Help others learn Prim

### Getting Started
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Setup
```bash
# Install dependencies (if any)
pip install -r requirements.txt

# Run tests
python -m pytest tests/

# Check code style
python -m flake8 .
```

### Reporting Issues
- Use the GitHub issue tracker
- Include code samples that reproduce the issue
- Specify which syntax mode you're using
- Mention your Python version and OS

## License

Prim is released under the MIT License. See the [LICENSE](LICENSE) file for details.

---

**"Prim: Write it your way"** - Because great code comes in many forms, but runs on one powerful foundation.

*"Prim: Write it your way." - Because great code comes in many forms, but runs on one powerful foundation.*