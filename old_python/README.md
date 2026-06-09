# Archived Python Prototype

This directory contains the original **Prim** language prototype written in Python. It was built in 5 days as a proof of concept for the multi-syntax language idea.

**Status:** Archived — read-only reference. All active development is now in Rust (see ../mintc, ../mint-core, etc.).

## Contents

- `prim_compiler.py` — Main compiler (orchestrates parsing + evaluation)
- `prim_interpreter.py` — Tree-walk interpreter and runtime
- `prim_slim_parser.py` — Slim mode (now "light") parser
- `prim_block_parser.py` — Block mode (now "brace") parser
- `prim_flow_parser.py` — Flow mode (now "stream") parser
- `prim_bytecode.py` — Bytecode compiler and VM (standalone, v0.5)
- `prim_type_checker.py` — Static type checker (standalone, v0.3)
- `prim_modules.py` — Module system (partially broken)
- `prim_std_*.py` — Standard library implementations
- `prism_get.py` — Package manager
- ~160 additional module files (quantum, blockchain, web, etc.)

## Known Issues

- `parse_block()` only parses 1 statement (breaks all indentation blocks)
- Module system calls nonexistent `execute()` method
- No `for`-loop evaluation in interpreter
- Bytecode VM and type checker not integrated into compile pipeline
- No actual tests — only test infrastructure
- Stdlib I/O functions are stubs
