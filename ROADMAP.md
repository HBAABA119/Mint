# Mint Development Roadmap

## v0.1 — Rust Bootstrap Compiler

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

- [x] Brace mode lexer (`#mode brace` - C/JS style with `{}` and `;`)
- [x] Brace mode parser
- [x] Stream mode lexer (`#mode stream` - pipe-based, `|>` operator)
- [x] Stream mode parser
- [x] Cross-mode test suite (same program in all 3 modes → equivalent results)
- [x] Error messages with source locations
- [x] Better error recovery in parser

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

## v0.7 — Mint CLI Tooling

**Goal:** A world-class `mint` CLI — project scaffolding, build system, package management, dev tools, and IDE integration. Designed for a smooth developer experience from `mint new` to `mint publish`.

### Approach

| Option | Description | Timeline |
|--------|-------------|----------|
| **(A) Cargo wrapper** | `mint` is a thin Rust binary calling `mintc` under the hood | v0.7–v0.9 (fast to ship) |
| **(B) Self-hosted** | `mint` is written in Mint itself | v1.0+ (requires solid file I/O, subprocess spawning, arg parsing) |

**Plan:** Ship (A) first for immediate utility. The CLI architecture should be designed from day one so that (B) is a drop-in replacement — same interface, same exit codes, same JSON output schemas.

### Full Command Reference

#### Project Lifecycle
| Command | When | Complexity | Description |
|---------|------|------------|-------------|
| `mint new <project>` | v0.7 | Low | Scaffold a new project from template (`--lib`, `--bin`, `--web`, `--game`, `--bare`) |
| `mint init` | v0.7 | Low | Turn existing directory into a Mint project |
| `mint build` | v0.7 | Low | Compile project (already have via mintc) |
| `mint run` | v0.7 | Low | Build and run (already have via mintc) |
| `mint check` | v0.7 | Low | Type-check and lint without producing output |
| `mint clean` | v0.7 | Low | Remove build artifacts |
| `mint watch` | v0.8 | Medium | File watcher that re-runs `check` or `test` on change |

#### Testing
| Command | When | Complexity | Description |
|---------|------|------------|-------------|
| `mint test` | v0.7 | Medium | Discover and run `*.test.mint` files with assertion output |
| `mint test --watch` | v0.8 | Medium | Continuously run tests on file change |
| `mint test --coverage` | v1.0 | High | Code coverage reporting |
| `mint bench` | v0.9 | High | Microbenchmark harness with statistical reporting |

#### Package Management
| Command | When | Complexity | Description |
|---------|------|------------|-------------|
| `mint add <package>` | v0.9 | Medium | Add a package dependency |
| `mint add --dev <package>` | v0.9 | Medium | Add a dev dependency |
| `mint remove <package>` | v0.9 | Low | Remove a dependency |
| `mint update` | v0.9 | Medium | Update all dependencies to latest compatible |
| `mint update <package>` | v0.9 | Low | Update a specific package |
| `mint publish` | v1.0 | High | Publish package to registry |
| `mint login` / `mint logout` | v1.0 | Low | Registry authentication |
| `mint search <query>` | v1.0 | Medium | Search packages in registry |

#### Code Quality
| Command | When | Complexity | Description |
|---------|------|------------|-------------|
| `mint fmt` | v1.0 | High | Format code respecting per-mode style (light/brace/stream) |
| `mint fmt --check` | v1.0 | Low | CI mode — exit non-zero if files aren't formatted |
| `mint lint` | v1.0 | High | Static analysis with configurable rule sets |
| `mint lint --fix` | v1.0 | High | Auto-fix where possible |
| `mint analyze` | v1.5 | High | Deep code analysis (complexity, dependency graph, dead code) |

#### Documentation
| Command | When | Complexity | Description |
|---------|------|------------|-------------|
| `mint doc` | v1.0 | Medium | Generate HTML docs from doc comments |
| `mint doc --serve` | v1.0 | Low | Serve docs locally with live reload |
| `mint doc --check` | v1.0 | Low | Warn about missing or stale docs |

#### Developer Experience
| Command | When | Complexity | Description |
|---------|------|------------|-------------|
| `mint repl` | v0.8 | Medium | Interactive REPL with history, multi-line, tab completion |
| `mint lsp` | v1.5 | Very High | Language server protocol for IDE integration |
| `mint completions <shell>` | v0.8 | Low | Generate shell completions (bash, zsh, fish, powershell) |
| `mint config` | v0.8 | Low | View current configuration |
| `mint config set <key> <value>` | v0.8 | Low | Set a config value |
| `mint config init` | v0.8 | Low | Create default `mint.toml` in project |
| `mint info` | v0.7 | Low | Show compiler version, platform, installed tools |
| `mint doctor` | v0.8 | Low | Diagnose common environment issues |

#### Output & Integration
| Flag | Description |
|------|-------------|
| `--json` | Machine-readable JSON output (for editors, CI) |
| `--quiet` | Suppress non-essential output |
| `--verbose` / `-v` | Detailed logging |
| `--no-color` | Disable colored output |
| `--profile` | Print timing breakdown of each phase |

### CLI Architecture Notes

- **Exit codes:** 0 = success, 1 = user error (bad args), 2 = tool error (bug), 3 = test failure
- **JSON output schema:** Every command that produces output accepts `--json` with a documented schema
- **Progress spinner:** Long-running commands (`build`, `test`, `publish`) show a terminal spinner
- **Colors:** Respect `NO_COLOR`, `CLICOLOR`, `CLICOLOR_FORCE` conventions
- **Config hierarchy:** `mint.toml` (project) → `~/.config/mint/config.toml` (user) → env vars → defaults

- [ ] `mint new` / `mint init` — scaffolding with template presets
- [ ] `mint build` / `mint run` / `mint check` — wrap mintc as subcommands
- [ ] `mint clean` — build artifact removal
- [ ] `mint test` — test runner with discovery and assertions
- [ ] `mint completions` — shell completion generation
- [ ] `mint config` / `mint info` — configuration and diagnostics
- [ ] `mint watch` / `mint repl` — interactive dev loop
- [ ] `mint add` / `mint remove` / `mint update` — package management
- [ ] `mint fmt` / `mint lint` — formatting and linting
- [ ] `mint doc` — documentation generation
- [ ] `mint publish` / `mint search` — registry integration
- [ ] `mint lsp` / `mint analyze` — IDE and deep analysis
- [ ] CLI architecture: approach decision (wrapper vs self-hosted), exit codes, JSON output, config hierarchy

## v1.0 — Stable Release

**Goal:** Production-ready language with docs, tests, package manager.

- [ ] Comprehensive test suite (>90% coverage)
- [ ] Documentation site
- [ ] `mint doc` — API docs from comments
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
