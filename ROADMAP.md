# Mint Development Roadmap

## v0.1 — Rust Bootstrap Compiler (Current)

**Goal:** `mintc run` works for light mode programs.

- [x] Project structure and Cargo workspace
- [x] mint-core: AST, tokens, runtime values, environment
- [x] mint-lexer: light mode tokenizer
- [x] mint-parser: light mode recursive-descent parser
- [x] mint-vm: tree-walk interpreter
- [x] mint-stdlib: built-in functions (print, len, str, num, etc.)
- [x] mintc CLI: run, check, tokens commands
- [x] Basic test programs working

## v0.2 — Brace and Stream Modes

**Goal:** All three syntax modes compile to the same AST and pass a cross-mode test suite.

- [ ] Brace mode lexer (`#mode brace` - C/JS style with `{}` and `;`)
- [ ] Brace mode parser
- [ ] Stream mode lexer (`#mode stream` - pipe-based, `|>` operator)
- [ ] Stream mode parser
- [ ] Cross-mode test suite (same program in all 3 modes → equivalent results)
- [ ] Error messages with source locations
- [ ] Better error recovery in parser

## v0.3 — Standard Library

**Goal:** Comprehensive stdlib written in pure Mint (stdlib/*.mint) with Rust FFI backing.

- [ ] Collections: map, filter, reduce, sort, find
- [ ] Strings: split, join, upper, lower, trim, replace
- [ ] Math: abs, sqrt, pow, sin, cos, pi, e (implemented in pure Mint)
- [ ] I/O: read_file, write_file, file_exists
- [ ] JSON: parse, stringify
- [ ] Iterators and lazy evaluation
- [ ] Result/Option types for error handling

## v0.4 — Self-Hosting

**Goal:** The Mint compiler can compile itself.

- [ ] Write `stdlib/compiler.mint` — Mint compiler in Mint
- [ ] Lexer in Mint
- [ ] Parser in Mint
- [ ] Code generation / interpreter in Mint
- [ ] Bootstrap: compile compiler.mint with Rust mintc
- [ ] Self-hosting: compiler.mint can compile itself
- [ ] Bootstrap compiler becomes optional

## v0.5 — Bytecode VM

**Goal:** `mintc build` produces bytecode; stack VM executes it.

- [ ] Bytecode instruction set design
- [ ] Bytecode compiler (AST → bytecode)
- [ ] Stack-based VM in Rust
- [ ] Replace tree-walk interpreter with bytecode VM
- [ ] Performance benchmarks vs v0.1-v0.4

## v0.6 — Performance and Benchmarks

**Goal:** Measured performance with benchmark suite.

- [ ] Benchmark harness in benchmarks/
- [ ] Parse speed benchmarks
- [ ] Execution speed benchmarks
- [ ] Memory usage benchmarks
- [ ] Comparison vs C, Rust, Python, Lua
- [ ] Profiling-guided optimizations
- [ ] JIT compilation exploration

## v1.0 — Stable Release

**Goal:** Production-ready language with docs, tests, package manager.

- [ ] Comprehensive test suite (>90% coverage)
- [ ] Documentation site
- [ ] Error messages with suggestions
- [ ] Package manager (mint-get)
- [ ] Language server protocol (LSP) support
- [ ] Formatter and linter
- [ ] v1.0 release

## v2.0+ — Systems Programming and Domain Expansion

**Goal:** Mint can be used for real systems development, game engines, UI, and web.

### System Programming
- [ ] C FFI (call C libraries from Mint)
- [ ] Unsafe blocks for raw memory access
- [ ] Inline assembly
- [ ] OS API bindings (POSIX, Win32)
- [ ] No-std / no-alloc mode for embedded

### Game Development
- [ ] SDL2/GLFW bindings
- [ ] OpenGL/Vulkan compute shader integration
- [ ] ECS (Entity Component System) pattern
- [ ] Audio library bindings

### UI Development
- [ ] Windowing toolkit bindings
- [ ] Immediate mode GUI library
- [ ] Reactive UI framework

### Web
- [ ] HTTP server
- [ ] WebSocket support
- [ ] Router and middleware
- [ ] Template engine
- [ ] WASM compilation target

### App Building
- [ ] Cross-platform build tooling
- [ ] Resource bundler
- [ ] Package format and distribution
