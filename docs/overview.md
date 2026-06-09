# Mint Architecture Overview

Mint is a multi-syntax programming language with a Rust-based compiler toolchain. This document describes the current architecture (v0.1).

## Compiler Pipeline

```
Source (.mint) → Lexer → Tokens → Parser → AST → Interpreter → Result
                      ↓                                ↓
                  Error                           Runtime Value
```

### 1. mint-core — Shared Types

Foundation crate defining:
- **TokenKind**: All token types (keywords, operators, literals, indentation)
- **Token**: Token with kind, lexeme, and source location
- **Node**: AST node types (program, statements, expressions, literals)
- **BinaryOp/UnaryOp**: Operation types
- **RuntimeValue**: Runtime values (Number, String, Bool, Null, List, Dict, Function, NativeFn)
- **Environment**: Scoped variable store with lexical parent chaining
- **Mode**: Syntax mode enum (Light, Brace, Stream)

### 2. mint-lexer — Tokenizer

Character-by-character tokenizer. Currently implements:
- **light**: Indentation-based tokenizer (Python-like: INDENT/DEDENT tokens, NEWLINE-separated statements, `#` comments)

### 3. mint-parser — Recursive-Descent Parser

Precedence-climbing expression parser. Currently implements:
- **light**: Parses light mode tokens into AST
- Error recovery via synchronize()
- Block parsing with INDENT/DEDENT

### 4. mint-vm — Tree-Walk Interpreter

Evaluates AST nodes recursively:
- Literals, identifiers, assignments
- Binary/unary operations with type checking
- Function definitions and calls (native and user-defined)
- Closures via captured environments
- If/else, while loops, for loops
- Return via EvalError::Return propagation
- Block scoping via child environments

### 5. mint-stdlib — Built-in Functions

Rust functions registered as NativeFn in the global environment:
- `print`, `len`, `str`, `num`, `bool`, `int`, `push`, `pop`, `input`, `type_of`

### 6. mintc — CLI

Command-line interface with commands:
- `run` — Full pipeline execution
- `check` — Parse-only validation
- `tokens` — Token stream dump

## Crate Dependency Graph

```
mintc
  ├── mint-parser
  │     ├── mint-lexer
  │     │     └── mint-core
  │     └── mint-core
  └── mint-vm
        ├── mint-stdlib
        │     └── mint-core
        └── mint-core
```

## Future Architecture

```
                    ┌─────────────────────┐
                    │    mintc (CLI)       │
                    └────────┬────────────┘
                             │
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
        mint-parser     mint-bytecode   mint-compiler
              │              │              │
              ▼              ▼              │
        mint-lexer      mint-vm (VM)        │
              │              │              │
              └──────┬───────┘              │
                     ▼                      ▼
               mint-core              stdlib/*.mint
                                          │
                                     mint-compiler.mint
                                     (self-hosted compiler)
```
