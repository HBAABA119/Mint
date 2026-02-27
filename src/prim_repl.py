"""
Prim Interactive REPL
Provides a syntax-highlighted command-line interface with tab completion,
history navigation, and multi-mode syntax support.
"""

import sys
import os
import re
import readline
import atexit
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import json


class SyntaxMode(Enum):
    """Syntax modes for Prim"""
    SLIM = "slim"
    BLOCK = "block"
    FLOW = "flow"


@dataclass
class REPLSession:
    """REPL session data"""
    variables: Dict[str, Any]
    history: List[str]
    current_mode: SyntaxMode
    multiline_input: List[str]


class PrimREPL:
    """Interactive REPL for Prim language"""

    def __init__(self):
        self.session = REPLSession(
            variables={},
            history=[],
            current_mode=SyntaxMode.SLIM,
            multiline_input=[]
        )
        
        # Setup readline for history
        self.history_file = os.path.expanduser("~/.prim_history")
        self._setup_history()
        
        # Import compiler components
        self._import_compiler()
        
        # Syntax highlighting colors
        self.colors = {
            'keyword': '\033[1;34m',    # Blue
            'string': '\033[1;32m',     # Green
            'number': '\033[1;36m',     # Cyan
            'comment': '\033[0;37m',     # Gray
            'function': '\033[1;35m',    # Magenta
            'variable': '\033[1;33m',   # Yellow
            'operator': '\033[1;31m',    # Red
            'reset': '\033[0m'
        }
        
        # Keywords for highlighting
        self.keywords = {
            'slim': ['if', 'else', 'elif', 'for', 'while', 'def', 'return', 'import', 'from', 'class', 'try', 'except', 'finally', 'with', 'as'],
            'block': ['if', 'else', 'elif', 'for', 'while', 'function', 'return', 'import', 'from', 'class', 'try', 'catch', 'finally', 'with', 'as'],
            'flow': ['if', 'else', 'elif', 'for', 'while', 'fn', 'return', 'import', 'from', 'type', 'try', 'catch', 'finally', 'with', 'as']
        }
        
        # Built-in functions
        self.builtins = ['print', 'len', 'map', 'filter', 'reduce', 'range', 'str', 'int', 'float', 'list', 'dict', 'set']

    def _setup_history(self):
        """Setup readline history"""
        try:
            readline.read_history_file(self.history_file)
        except FileNotFoundError:
            pass
        
        atexit.register(self._save_history)

    def _save_history(self):
        """Save readline history"""
        readline.write_history_file(self.history_file)

    def _import_compiler(self):
        """Import compiler components"""
        try:
            from prim_compiler import PrimCompiler
            self.compiler = PrimCompiler()
        except ImportError:
            print("Warning: Could not import compiler. REPL will be in limited mode.")
            self.compiler = None

    def get_prompt(self) -> str:
        """Get the current prompt"""
        mode_symbol = {
            SyntaxMode.SLIM: ">>>",
            SyntaxMode.BLOCK: ">>>",
            SyntaxMode.FLOW: ">>>"
        }[self.session.current_mode]
        
        return f"\033[1;32m{mode_symbol}\033[0m "

    def get_continuation_prompt(self) -> str:
        """Get continuation prompt for multiline input"""
        return "\033[1;32m...\033[0m "

    def highlight_syntax(self, code: str) -> str:
        """Apply syntax highlighting to code"""
        mode = self.session.current_mode.value
        
        # Highlight keywords
        for keyword in self.keywords.get(mode, []):
            pattern = r'\b' + keyword + r'\b'
            code = re.sub(pattern, f"{self.colors['keyword']}{keyword}{self.colors['reset']}", code)
        
        # Highlight strings
        code = re.sub(r'"[^"]*"', lambda m: f"{self.colors['string']}{m.group(0)}{self.colors['reset']}", code)
        code = re.sub(r"'[^']*'", lambda m: f"{self.colors['string']}{m.group(0)}{self.colors['reset']}", code)
        
        # Highlight numbers
        code = re.sub(r'\b\d+\.?\d*\b', lambda m: f"{self.colors['number']}{m.group(0)}{self.colors['reset']}", code)
        
        # Highlight built-in functions
        for builtin in self.builtins:
            pattern = r'\b' + builtin + r'\b'
            code = re.sub(pattern, f"{self.colors['function']}{builtin}{self.colors['reset']}", code)
        
        # Highlight comments
        code = re.sub(r'#.*$', lambda m: f"{self.colors['comment']}{m.group(0)}{self.colors['reset']}", code)
        
        return code

    def detect_mode(self, code: str) -> Optional[SyntaxMode]:
        """Detect syntax mode from code"""
        # Check for mode directive
        mode_match = re.search(r'#mode\s+(\w+)', code)
        if mode_match:
            mode_str = mode_match.group(1).upper()
            try:
                return SyntaxMode(mode_str)
            except ValueError:
                pass
        
        # Auto-detect based on syntax
        if '{' in code and '}' in code and ';' in code:
            return SyntaxMode.BLOCK
        elif '|>' in code or ':=' in code:
            return SyntaxMode.FLOW
        else:
            return SyntaxMode.SLIM

    def complete(self, text: str, state: int) -> Optional[str]:
        """Tab completion callback"""
        if state == 0:
            # Get the current line
            try:
                line = readline.get_line_buffer()
            except:
                line = ""
            
            # Get the word being completed
            words = line.split()
            if not words:
                self.completion_matches = []
                return None
            
            last_word = words[-1]
            
            # Build completion list
            completions = []
            
            # Variables in session
            completions.extend([v for v in self.session.variables.keys() if v.startswith(last_word)])
            
            # Keywords
            completions.extend([k for k in self.keywords.get(self.session.current_mode.value, []) if k.startswith(last_word)])
            
            # Built-in functions
            completions.extend([b for b in self.builtins if b.startswith(last_word)])
            
            # File paths (for import)
            if 'import' in line or 'from' in line:
                try:
                    current_dir = os.getcwd()
                    files = os.listdir(current_dir)
                    completions.extend([f for f in files if f.startswith(last_word)])
                except:
                    pass
            
            self.completion_matches = sorted(list(set(completions)))
        
        try:
            return self.completion_matches[state]
        except (IndexError, AttributeError):
            return None

    def setup_completer(self):
        """Setup tab completion"""
        readline.set_completer(self.complete)
        readline.parse_and_bind('tab: complete')
        readline.parse_and_bind('set show-all-if-ambiguous on')

    def execute_code(self, code: str) -> Tuple[bool, Any]:
        """Execute Prim code and return result"""
        if not self.compiler:
            print("Error: Compiler not available")
            return False, None
        
        try:
            # Detect mode
            mode = self.detect_mode(code)
            if mode:
                self.session.current_mode = mode
            
            # Compile and execute
            # For now, just print the code
            print(f"Executing in {self.session.current_mode.value} mode:")
            print(code)
            
            # TODO: Actually compile and execute
            # result = self.compiler.compile_and_execute(code)
            # return True, result
            
            return True, None
            
        except Exception as e:
            print(f"Error: {e}")
            return False, None

    def show_help(self):
        """Show help information"""
        help_text = """
Prim REPL - Interactive Shell

Commands:
  .help          Show this help message
  .mode [slim|block|flow]  Set syntax mode
  .vars          Show all variables
  .clear         Clear all variables
  .history       Show command history
  .exit          Exit the REPL

Syntax Modes:
  slim    - Python-like, indentation-based
  block   - C/JavaScript-style with braces
  flow    - Functional/pipe-based

Examples:
  >>> x = 42
  >>> print(x)
  42
  
  >>> #mode block
  >>> var y = 10;
  >>> print(y);
  10
  
  >>> #mode flow
  >>> z := 20
  >>> "Result:" |> print(#, z)
  Result: 20
"""
        print(help_text)

    def show_variables(self):
        """Show all variables in the session"""
        if not self.session.variables:
            print("No variables defined.")
            return
        
        print("Variables:")
        for name, value in sorted(self.session.variables.items()):
            print(f"  {name} = {value}")

    def clear_variables(self):
        """Clear all variables"""
        self.session.variables.clear()
        print("All variables cleared.")

    def show_history(self):
        """Show command history"""
        if not self.session.history:
            print("No history.")
            return
        
        print("History:")
        for i, cmd in enumerate(self.session.history, 1):
            print(f"  {i}: {cmd}")

    def process_command(self, line: str) -> bool:
        """Process a REPL command"""
        # Handle special commands
        if line.startswith('.'):
            parts = line.split()
            cmd = parts[0]
            
            if cmd == '.help':
                self.show_help()
                return True
            elif cmd == '.mode':
                if len(parts) > 1:
                    try:
                        mode = SyntaxMode(parts[1].upper())
                        self.session.current_mode = mode
                        print(f"Mode set to {mode.value}")
                    except ValueError:
                        print(f"Invalid mode: {parts[1]}")
                else:
                    print(f"Current mode: {self.session.current_mode.value}")
                return True
            elif cmd == '.vars':
                self.show_variables()
                return True
            elif cmd == '.clear':
                self.clear_variables()
                return True
            elif cmd == '.history':
                self.show_history()
                return True
            elif cmd == '.exit':
                return False
            else:
                print(f"Unknown command: {cmd}")
                print("Type .help for available commands")
                return True
        
        # Handle multiline input
        if line.strip().endswith(':') or line.strip().endswith('{'):
            self.session.multiline_input.append(line)
            return True
        
        # Execute multiline input if present
        if self.session.multiline_input:
            self.session.multiline_input.append(line)
            code = '\n'.join(self.session.multiline_input)
            self.session.multiline_input = []
            
            # Execute
            success, result = self.execute_code(code)
            if success:
                self.session.history.append(code)
            return True
        
        # Execute single line
        success, result = self.execute_code(line)
        if success:
            self.session.history.append(line)
        
        return True

    def run(self):
        """Run the REPL"""
        print("""
╔════════════════════════════════════════════════════════════╗
║           Prim Language - Interactive REPL v1.1            ║
║                                                            ║
║  Type .help for commands | Tab for completion | Ctrl+D to exit ║
╚════════════════════════════════════════════════════════════╝
""")
        
        # Setup tab completion
        self.setup_completer()
        
        # Main loop
        while True:
            try:
                # Get prompt
                if self.session.multiline_input:
                    prompt = self.get_continuation_prompt()
                else:
                    prompt = self.get_prompt()
                
                # Read line
                try:
                    line = input(prompt).strip()
                except EOFError:
                    print("\nGoodbye!")
                    break
                
                # Skip empty lines
                if not line:
                    continue
                
                # Process command
                should_continue = self.process_command(line)
                if not should_continue:
                    break
                
            except KeyboardInterrupt:
                print("\nInterrupted. Type .exit to quit.")
                self.session.multiline_input = []
            except Exception as e:
                print(f"Error: {e}")
                self.session.multiline_input = []


def main():
    """Main entry point"""
    repl = PrimREPL()
    repl.run()


if __name__ == "__main__":
    main()
