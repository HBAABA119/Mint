# Mint v0.2

**Mint** is a systems-oriented programming language being rewritten from the ground up in Rust. It supports three syntax modes — **light**, **brace**, and **stream** — that all compile to the same AST and produce identical output for equivalent programs.

## Status

Mint is in **active development**. This is a complete rewrite of the original Prim language prototype (which was written in Python). All three syntax modes are now implemented and pass cross-mode equivalence tests.

### What works
- All three syntax modes (light, brace, stream)
- Lexers, parsers, and tree-walk interpreter for all modes
- Variables, arithmetic, if/else, while/for loops, functions, lambdas, lists
- Pipe operator (`|>`) in stream mode
- Lambda expressions (`|x| -> x * 2`) in stream mode
- `var`/`let` declarations in brace and stream modes
- `:=` walrus operator in stream mode
- Built-in stdlib: `print`, `len`, `str`, `num`, `bool`, `int`, `push`, `pop`, `input`, `type_of`

### What's coming
- Better error messages with source locations
- Comprehensive pure-Mint standard library
- Self-hosting (Mint compiler written in Mint)
- Bytecode compiler and VM
- FFI for system-level programming

## Quick Start

```bash
# Build the compiler
cargo build

# Run a Mint file
cargo run -- run hello.mint

# Or use the binary directly
cargo build --release
./target/release/mintc run hello.mint
```

### Hello World

```mint
#mode light

print("Hello, Mint!")
```

### More examples

```mint
#mode light

fn greet(name):
    print("Hello,", name)

greet("world")

# Fibonacci
fn fib(n):
    if n <= 1:
        return n
    return fib(n - 1) + fib(n - 2)

print("fib(10) =", fib(10))
```

## Syntax Modes

| Directive | Style | Like |
|-----------|-------|------|
| `#mode light` | Indentation-based | Python |
| `#mode brace` | Braces + semicolons | C/JS |
| `#mode stream` | Pipes + arrows, `:=`, `\|>`, `\|x\| -> expr` | Elixir/F# |

## Project Structure

```
mintc/          - CLI binary (mintc run, check, tokens)
mint-core/     - Shared types (AST, tokens, runtime values, environment)
mint-lexer/    - Tokenizers for all syntax modes
mint-parser/   - Parsers for all syntax modes
mint-vm/       - Tree-walk interpreter (later: bytecode VM)
mint-stdlib/   - Built-in standard library functions
stdlib/         - Pure-Mint standard library modules
tests/          - Mint test programs
old_python/    - Archived Python prototype (Prim)
old_src/       - Archived original .prim source files
```

## CLI Usage

```
mintc run <file.mint>     Run a Mint program
mintc check <file.mint>   Check for errors
mintc tokens <file.mint>  Show token stream
mintc help                Show help
```

## Why the rewrite?

The original Prim was a 5-day prototype built with Python and Cursor to explore multi-syntax language design. Mint is the serious rewrite: Rust for performance and safety, cleaner architecture, and a clear path toward self-hosting, system programming, game development, UI toolkits, and web hosting.

## License

MIT
