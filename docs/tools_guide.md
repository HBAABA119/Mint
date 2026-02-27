# Prim Language Tools and Tooling

## Table of Contents

- [CLI Tools](#cli-tools)
- [IDE Plugins](#ide-plugins)
- [LSP Server](#lsp-server)
- [Formatters](#formatters)
- [Linters](#linters)

---

## CLI Tools

### prim

Main CLI tool for Prim development.

```bash
# Run code
prim run app.prim

# Build
prim build app.prim

# Test
prim test

# Format
prim format app.prim

# Lint
prim lint app.prim

# Profile
prim profile app.prim
```

### prim-run

Run Prim programs.

```bash
prim run app.prim
prim run --jit app.prim
prim run --debug app.prim
```

### prim-build

Build Prim programs.

```bash
prim build app.prim
prim build --native app.prim
prim build --wasm app.prim
prim build --release app.prim
```

### prim-test

Run tests.

```bash
prim test
prim test --coverage
prim test --watch
prim test test_file.prim
```

---

## IDE Plugins

### VS Code

Install from marketplace:

```
Prim Language Support
```

Features:
- Syntax highlighting
- Code completion
- Error highlighting
- Debugging support

### JetBrains

Install from plugin repository:

```
Prim Plugin
```

Features:
- Full IDE support
- Refactoring
- Debugging
- Testing

### Vim/Neovim

Install via plugin manager:

```vim
Plug 'prim-lang/prim.vim'
```

Features:
- Syntax highlighting
- Auto-completion
- LSP integration

---

## LSP Server

### Installation

```bash
npm install -g prim-language-server
```

### Configuration

```json
{
  "prim.server.path": "/path/to/prim-language-server",
  "prim.server.args": ["--stdio"]
}
```

### Features

- Auto-completion
- Go to definition
- Find references
- Hover information
- Diagnostics
- Code formatting

---

## Formatters

### prim-format

Format Prim code.

```bash
prim format app.prim
prim format --check app.prim
prim format --write app.prim
```

### Configuration

```json
{
  "indent_size": 4,
  "max_line_length": 100,
  "trailing_comma": true
}
```

---

## Linters

### prim-lint

Lint Prim code.

```bash
prim lint app.prim
prim lint --fix app.prim
prim lint --strict app.prim
```

### Rules

- Line length
- Naming conventions
- Type annotations
- Error handling
- Security issues

---

## Debugging Tools

### prim-debug

Debug Prim programs.

```bash
prim debug app.prim
prim debug --breakpoint main:10
prim debug --inspect variable
```

### Features

- Breakpoints
- Step through code
- Inspect variables
- View call stack
- Evaluate expressions

---

## Summary

Prim tooling includes:

1. **CLI**: Command-line tools
2. **IDE**: Editor plugins
3. **LSP**: Language server
4. **Formatters**: Code formatting
5. **Linters**: Code quality

For more information, see the [API Reference](./api_reference.md).
