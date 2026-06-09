# Archived Prim Source Files

This directory contains the original `.prim` source files from the Prim language prototype, including self-hosted versions of the compiler components converted from Python via `convert_all.py`.

**Status:** Archived — read-only reference.

## Contents

- `prim_compiler.prim`, `prim_interpreter.prim` — Self-hosted compiler/interpreter
- `prim_slim_parser.prim`, `prim_block_parser.prim`, `prim_flow_parser.prim` — Parsers
- `prim_ast.prim` — AST definitions with builder, visitor, transformer, serialization
- `prim_vm.c`, `prim_vm.h` — C reference VM (partial, ~5/28 opcodes implemented)
- `prism_get.prim` — Package manager (auto-converted, still references Python APIs)
- ~160 additional .prim module files (auto-converted from Python)
