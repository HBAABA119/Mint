"""
Prim Ecosystem Development
Provides IDE integration, LSP server, debugging support,
community tools, and documentation site generation.
"""

import json
import os
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum


class LSPMethod(Enum):
    """LSP methods"""
    INITIALIZE = "initialize"
    SHUTDOWN = "shutdown"
    TEXT_DOCUMENT_DID_OPEN = "textDocument/didOpen"
    TEXT_DOCUMENT_DID_CHANGE = "textDocument/didChange"
    TEXT_DOCUMENT_COMPLETION = "textDocument/completion"
    TEXT_DOCUMENT_HOVER = "textDocument/hover"
    TEXT_DOCUMENT_DEFINITION = "textDocument/definition"
    TEXT_DOCUMENT_REFERENCES = "textDocument/references"
    TEXT_DOCUMENT_DIAGNOSTIC = "textDocument/diagnostic"


@dataclass
class LSPMessage:
    """LSP message"""
    jsonrpc: str
    id: Optional[int]
    method: Optional[LSPMethod]
    params: Optional[Dict[str, Any]]
    result: Optional[Any]
    error: Optional[Dict[str, Any]]


@dataclass
class CompletionItem:
    """Completion item"""
    label: str
    kind: int
    detail: str
    documentation: str
    insert_text: str


class LSPServer:
    """Language Server Protocol server"""

    def __init__(self):
        self.documents: Dict[str, str] = {}
        self.diagnostics: Dict[str, List[Dict[str, Any]]] = {}

    def handle_message(self, message: str) -> str:
        """Handle LSP message"""
        try:
            msg = json.loads(message)
            lsp_msg = LSPMessage(
                jsonrpc=msg.get("jsonrpc", "2.0"),
                id=msg.get("id"),
                method=LSPMethod(msg["method"]) if "method" in msg else None,
                params=msg.get("params"),
                result=msg.get("result"),
                error=msg.get("error")
            )

            if lsp_msg.method == LSPMethod.INITIALIZE:
                return self._handle_initialize(lsp_msg)
            elif lsp_msg.method == LSPMethod.TEXT_DOCUMENT_DID_OPEN:
                return self._handle_did_open(lsp_msg)
            elif lsp_msg.method == LSPMethod.TEXT_DOCUMENT_DID_CHANGE:
                return self._handle_did_change(lsp_msg)
            elif lsp_msg.method == LSPMethod.TEXT_DOCUMENT_COMPLETION:
                return self._handle_completion(lsp_msg)
            elif lsp_msg.method == LSPMethod.TEXT_DOCUMENT_HOVER:
                return self._handle_hover(lsp_msg)
            elif lsp_msg.method == LSPMethod.TEXT_DOCUMENT_DIAGNOSTIC:
                return self._handle_diagnostic(lsp_msg)

        except Exception as e:
            return json.dumps({
                "jsonrpc": "2.0",
                "error": {
                    "code": -32603,
                    "message": str(e)
                }
            })

    def _handle_initialize(self, msg: LSPMessage) -> str:
        """Handle initialize request"""
        return json.dumps({
            "jsonrpc": "2.0",
            "id": msg.id,
            "result": {
                "capabilities": {
                    "textDocumentSync": 1,
                    "completionProvider": {
                        "resolveProvider": False
                    },
                    "hoverProvider": True,
                    "definitionProvider": True,
                    "referencesProvider": True,
                    "diagnosticProvider": True
                },
                "serverInfo": {
                    "name": "prim-language-server",
                    "version": "1.0.0"
                }
            }
        })

    def _handle_did_open(self, msg: LSPMessage) -> str:
        """Handle document open"""
        uri = msg.params["textDocument"]["uri"]
        text = msg.params["textDocument"]["text"]
        self.documents[uri] = text

        return json.dumps({
            "jsonrpc": "2.0",
            "result": None
        })

    def _handle_did_change(self, msg: LSPMessage) -> str:
        """Handle document change"""
        uri = msg.params["textDocument"]["uri"]
        changes = msg.params["contentChanges"]

        for change in changes:
            self.documents[uri] = change["text"]

        return json.dumps({
            "jsonrpc": "2.0",
            "result": None
        })

    def _handle_completion(self, msg: LSPMessage) -> str:
        """Handle completion request"""
        uri = msg.params["textDocument"]["uri"]
        position = msg.params["position"]

        # Generate completion items
        completions = [
            CompletionItem(
                label="fn",
                kind=3,
                detail="function",
                documentation="Define a function",
                insert_text="fn "
            ),
            CompletionItem(
                label="let",
                kind=12,
                detail="keyword",
                documentation="Declare a variable",
                insert_text="let "
            ),
            CompletionItem(
                label="const",
                kind=12,
                detail="keyword",
                documentation="Declare a constant",
                insert_text="const "
            ),
            CompletionItem(
                label="if",
                kind=12,
                detail="keyword",
                documentation="Conditional statement",
                insert_text="if "
            ),
            CompletionItem(
                label="while",
                kind=12,
                detail="keyword",
                documentation="While loop",
                insert_text="while "
            )
        ]

        return json.dumps({
            "jsonrpc": "2.0",
            "id": msg.id,
            "result": {
                "isIncomplete": False,
                "items": [
                    {
                        "label": item.label,
                        "kind": item.kind,
                        "detail": item.detail,
                        "documentation": item.documentation,
                        "insertText": item.insert_text
                    }
                    for item in completions
                ]
            }
        })

    def _handle_hover(self, msg: LSPMessage) -> str:
        """Handle hover request"""
        uri = msg.params["textDocument"]["uri"]
        position = msg.params["position"]

        # Simulated hover - in production would analyze code
        return json.dumps({
            "jsonrpc": "2.0",
            "id": msg.id,
            "result": {
                "contents": [
                    {
                        "kind": "markdown",
                        "value": "Hover information"
                    }
                ]
            }
        })

    def _handle_diagnostic(self, msg: LSPMessage) -> str:
        """Handle diagnostic request"""
        uri = msg.params["textDocument"]["uri"]

        # Simulated diagnostics - in production would analyze code
        diagnostics = [
            {
                "range": {
                    "start": {"line": 0, "character": 0},
                    "end": {"line": 0, "character": 10}
                },
                "severity": 1,
                "source": "prim",
                "message": "Example diagnostic"
            }
        ]

        return json.dumps({
            "jsonrpc": "2.0",
            "id": msg.id,
            "result": diagnostics
        })


class Debugger:
    """Prim language debugger"""

    def __init__(self):
        self.breakpoints: Dict[str, List[int]] = {}
        self.current_line: Optional[int] = None
        self.current_file: Optional[str] = None
        self.variables: Dict[str, Any] = {}
        self.call_stack: List[Dict[str, Any]] = []

    def set_breakpoint(self, file: str, line: int):
        """Set breakpoint"""
        if file not in self.breakpoints:
            self.breakpoints[file] = []
        self.breakpoints[file].append(line)

    def clear_breakpoint(self, file: str, line: int):
        """Clear breakpoint"""
        if file in self.breakpoints and line in self.breakpoints[file]:
            self.breakpoints[file].remove(line)

    def step_over(self):
        """Step over"""
        self.current_line += 1

    def step_into(self):
        """Step into"""
        self.current_line += 1

    def step_out(self):
        """Step out"""
        if self.call_stack:
            frame = self.call_stack.pop()
            self.current_line = frame.get("line", 0)
            self.current_file = frame.get("file", "")

    def continue_execution(self):
        """Continue execution"""
        return "running"

    def get_variables(self) -> Dict[str, Any]:
        """Get current variables"""
        return self.variables

    def get_call_stack(self) -> List[Dict[str, Any]]:
        """Get call stack"""
        return self.call_stack


class Formatter:
    """Prim code formatter"""

    def format(self, code: str) -> str:
        """Format code"""
        lines = code.split('\n')
        formatted = []

        indent_level = 0
        for line in lines:
            stripped = line.strip()

            # Decrease indent for closing braces
            if stripped.startswith('}') or stripped.startswith(']') or stripped.startswith(')'):
                indent_level = max(0, indent_level - 1)

            # Add indentation
            if stripped:
                formatted.append('    ' * indent_level + stripped)
            else:
                formatted.append('')

            # Increase indent for opening braces
            if stripped.endswith('{') or stripped.endswith('[') or stripped.endswith('('):
                indent_level += 1

        return '\n'.join(formatted)


class DocumentationGenerator:
    """Documentation site generator"""

    def __init__(self, output_dir: str = "docs_site"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def generate_site(self, modules: List[str]):
        """Generate documentation site"""
        # Generate index
        self._generate_index()

        # Generate module documentation
        for module in modules:
            self._generate_module_doc(module)

        # Generate API reference
        self._generate_api_reference()

        # Generate guides
        self._generate_guides()

        print(f"Documentation site generated in {self.output_dir}")

    def _generate_index(self):
        """Generate index page"""
        index = """# Prim Language Documentation

Welcome to the Prim Language documentation.

## Getting Started

- [Installation](installation.md)
- [Quick Start](quickstart.md)
- [Language Reference](reference.md)

## API Reference

- [Standard Library](api/stdlib.md)
- [Modules](api/modules.md)

## Guides

- [Tutorial](guides/tutorial.md)
- [Best Practices](guides/best_practices.md)
- [Examples](guides/examples.md)
"""

        with open(os.path.join(self.output_dir, "index.md"), 'w') as f:
            f.write(index)

    def _generate_module_doc(self, module: str):
        """Generate module documentation"""
        doc = f"""# {module}

Documentation for {module} module.

## Functions

### example_function

Example function description.

#### Parameters

- `param1`: Description
- `param2`: Description

#### Returns

Return value description.

#### Examples

```
{module}.example_function(arg1, arg2)
```
"""

        with open(os.path.join(self.output_dir, "api", f"{module}.md"), 'w') as f:
            f.write(doc)

    def _generate_api_reference(self):
        """Generate API reference"""
        api = """# API Reference

Complete API reference for Prim Language.

## Standard Library

- [Collections](collections.md)
- [I/O](io.md)
- [Math](math.md)
- [Strings](strings.md)
"""

        with open(os.path.join(self.output_dir, "api", "index.md"), 'w') as f:
            f.write(api)

    def _generate_guides(self):
        """Generate guides"""
        guides = """# Guides

## Tutorial

Learn Prim step by step.

## Best Practices

Recommended patterns and conventions.

## Examples

Real-world code examples.
"""

        with open(os.path.join(self.output_dir, "guides", "index.md"), 'w') as f:
            f.write(guides)


def main():
    """Main entry point"""
    print("Testing Ecosystem Development...")

    # Test LSP server
    lsp = LSPServer()
    msg = json.dumps({
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {}
    })
    response = lsp.handle_message(msg)
    print(f"LSP response: {len(response)} characters")

    # Test debugger
    debugger = Debugger()
    debugger.set_breakpoint("test.prim", 10)
    print(f"Breakpoints: {len(debugger.breakpoints)}")

    # Test formatter
    formatter = Formatter()
    code = "fn test() {\n    print('hello');\n}"
    formatted = formatter.format(code)
    print(f"Formatted: {len(formatted)} characters")

    # Test documentation generator
    doc_gen = DocumentationGenerator()
    doc_gen.generate_site(["stdlib"])

    print("Ecosystem Development initialized successfully")


if __name__ == "__main__":
    main()
