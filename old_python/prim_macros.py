"""
Prim Macros System
Provides compile-time code generation, hygienic macro system, syntax extension capabilities,
macro debugging and introspection, and template-based metaprogramming.
"""

import re
import inspect
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, field
from enum import Enum


class MacroType(Enum):
    """Macro types"""
    FUNCTION = "function"
    SYMBOLIC = "symbolic"
    TEMPLATE = "template"
    HYGIENIC = "hygienic"


@dataclass
class MacroDefinition:
    """Macro definition"""
    name: str
    macro_type: MacroType
    pattern: str
    template: str
    func: Optional[Callable] = None
    docstring: str = ""
    hygiene_level: int = 0


@dataclass
class MacroExpansion:
    """Result of macro expansion"""
    code: str
    bindings: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


class MacroEnvironment:
    """Environment for macro execution"""

    def __init__(self):
        self.macros: Dict[str, MacroDefinition] = {}
        self.symbols: Dict[str, Any] = {}
        self.debug_mode = False

    def define_macro(self, macro: MacroDefinition):
        """Define a macro in the environment"""
        self.macros[macro.name] = macro

    def get_macro(self, name: str) -> Optional[MacroDefinition]:
        """Get a macro by name"""
        return self.macros.get(name)

    def has_macro(self, name: str) -> bool:
        """Check if macro exists"""
        return name in self.macros

    def set_symbol(self, name: str, value: Any):
        """Set a symbol value"""
        self.symbols[name] = value

    def get_symbol(self, name: str) -> Optional[Any]:
        """Get a symbol value"""
        return self.symbols.get(name)


class MacroExpander:
    """Macro expansion engine"""

    def __init__(self, env: MacroEnvironment):
        self.env = env
        self.expansion_count = 0
        self.max_expansions = 1000

    def expand(self, code: str) -> str:
        """Expand all macros in code"""
        self.expansion_count = 0
        return self._expand_recursive(code)

    def _expand_recursive(self, code: str) -> str:
        """Recursively expand macros"""
        if self.expansion_count >= self.max_expansions:
            raise RecursionError("Maximum macro expansion depth exceeded")

        # Find macro invocations
        macro_pattern = r'@(\w+)\s*\(([^)]*)\)'
        matches = list(re.finditer(macro_pattern, code))

        if not matches:
            return code

        # Process matches in reverse order to maintain positions
        for match in reversed(matches):
            macro_name = match.group(1)
            args_str = match.group(2)

            # Get macro definition
            macro = self.env.get_macro(macro_name)
            if not macro:
                continue

            # Parse arguments
            args = self._parse_arguments(args_str)

            # Expand macro
            expansion = self._expand_macro(macro, args)

            # Replace macro invocation with expansion
            start, end = match.span()
            code = code[:start] + expansion.code + code[end:]

            self.expansion_count += 1

        # Recursively expand again to handle nested macros
        if re.search(macro_pattern, code):
            return self._expand_recursive(code)

        return code

    def _expand_macro(self, macro: MacroDefinition, args: List[str]) -> MacroExpansion:
        """Expand a single macro"""
        if macro.macro_type == MacroType.FUNCTION:
            return self._expand_function_macro(macro, args)
        elif macro.macro_type == MacroType.SYMBOLIC:
            return self._expand_symbolic_macro(macro, args)
        elif macro.macro_type == MacroType.TEMPLATE:
            return self._expand_template_macro(macro, args)
        elif macro.macro_type == MacroType.HYGIENIC:
            return self._expand_hygienic_macro(macro, args)

        return MacroExpansion(code="")

    def _expand_function_macro(self, macro: MacroDefinition, args: List[str]) -> MacroExpansion:
        """Expand a function macro"""
        if macro.func is None:
            return MacroExpansion(code="")

        try:
            # Call macro function with arguments
            result = macro.func(*args)
            return MacroExpansion(code=str(result))
        except Exception as e:
            if self.env.debug_mode:
                print(f"Error expanding macro {macro.name}: {e}")
            return MacroExpansion(code="")

    def _expand_symbolic_macro(self, macro: MacroDefinition, args: List[str]) -> MacroExpansion:
        """Expand a symbolic macro"""
        # Simple pattern matching and replacement
        pattern = macro.pattern
        template = macro.template

        # Create bindings from pattern
        bindings = self._match_pattern(pattern, args)
        if not bindings:
            return MacroExpansion(code="")

        # Apply template
        code = template
        for key, value in bindings.items():
            code = code.replace(f"${{{key}}}", str(value))

        return MacroExpansion(code=code, bindings=bindings)

    def _expand_template_macro(self, macro: MacroDefinition, args: List[str]) -> MacroExpansion:
        """Expand a template macro"""
        template = macro.template

        # Replace positional placeholders
        for i, arg in enumerate(args):
            template = template.replace(f"${{{i}}}", arg)

        # Replace named placeholders
        for i, arg in enumerate(args):
            template = template.replace("${{arg" + str(i) + "}}", arg)

        return MacroExpansion(code=template)

    def _expand_hygienic_macro(self, macro: MacroDefinition, args: List[str]) -> MacroExpansion:
        """Expand a hygienic macro with variable hygiene"""
        # Generate unique identifiers for bound variables
        bindings = {}
        template = macro.template

        # Find all variable placeholders
        var_pattern = r'\$\{(\w+)\}'
        vars = re.findall(var_pattern, template)

        # Generate unique identifiers
        for var in vars:
            unique_id = f"_{var}_{id(macro.name)}_{len(bindings)}"
            bindings[var] = unique_id
            template = template.replace(f"${{{var}}}", unique_id)

        # Replace with arguments
        for i, arg in enumerate(args):
            template = template.replace(f"${{{i}}}", arg)

        return MacroExpansion(code=template, bindings=bindings)

    def _parse_arguments(self, args_str: str) -> List[str]:
        """Parse macro arguments"""
        if not args_str.strip():
            return []

        args = []
        current = ""
        depth = 0
        in_string = False

        for char in args_str:
            if char in '([' and not in_string:
                depth += 1
                current += char
            elif char in ')]' and not in_string:
                depth -= 1
                current += char
            elif char == ',' and depth == 0:
                args.append(current.strip())
                current = ""
            elif char in '"\'' and not in_string:
                in_string = not in_string
                current += char
            else:
                current += char

        if current.strip():
            args.append(current.strip())

        return args

    def _match_pattern(self, pattern: str, args: List[str]) -> Optional[Dict[str, str]]:
        """Match pattern against arguments and return bindings"""
        # Simple pattern matching
        pattern_parts = pattern.split()
        bindings = {}

        if len(pattern_parts) != len(args):
            return None

        for i, part in enumerate(pattern_parts):
            if part.startswith('$'):
                var_name = part[1:]
                bindings[var_name] = args[i]
            elif part != args[i]:
                return None

        return bindings


class MacroSystem:
    """Main macro system"""

    def __init__(self):
        self.env = MacroEnvironment()
        self.expander = MacroExpander(self.env)
        self._register_builtin_macros()

    def _register_builtin_macros(self):
        """Register built-in macros"""
        # Define macro
        @self.macro("define")
        def define_macro(name: str, value: str):
            self.env.set_symbol(name, value)
            return f"{name} = {value}"

        # If macro
        @self.macro("if")
        def if_macro(condition: str, then_expr: str, else_expr: str = ""):
            if else_expr:
                return f"if {condition} {{ {then_expr} }} else {{ {else_expr} }}"
            return f"if {condition} {{ {then_expr} }}"

        # Let macro
        @self.macro("let")
        def let_macro(bindings: str, body: str):
            return f"{{ {bindings}; {body} }}"

        # Loop macro
        @self.macro("for")
        def for_macro(var: str, iterable: str, body: str):
            return f"for {var} in {iterable} {{ {body} }}"

        # Debug macro
        @self.macro("debug")
        def debug_macro(expr: str):
            return f"print('DEBUG: {expr} =', {expr}); {expr}"

        # Assert macro
        @self.macro("assert")
        def assert_macro(condition: str, message: str = ""):
            if message:
                return f"assert {condition}, '{message}'"
            return f"assert {condition}"

        # Time macro
        @self.macro("time")
        def time_macro(expr: str):
            return f"""
import time
start = time.time()
result = {expr}
print('Time:', time.time() - start)
result
"""

    def macro(self, name: str):
        """Decorator to define a macro"""
        def decorator(func):
            macro = MacroDefinition(
                name=name,
                macro_type=MacroType.FUNCTION,
                pattern="",
                template="",
                func=func,
                docstring=func.__doc__ or ""
            )
            self.env.define_macro(macro)
            return func
        return decorator

    def define_template_macro(
        self,
        name: str,
        pattern: str,
        template: str,
        docstring: str = ""
    ):
        """Define a template macro"""
        macro = MacroDefinition(
            name=name,
            macro_type=MacroType.TEMPLATE,
            pattern=pattern,
            template=template,
            docstring=docstring
        )
        self.env.define_macro(macro)

    def define_hygienic_macro(
        self,
        name: str,
        template: str,
        docstring: str = ""
    ):
        """Define a hygienic macro"""
        macro = MacroDefinition(
            name=name,
            macro_type=MacroType.HYGIENIC,
            pattern="",
            template=template,
            docstring=docstring
        )
        self.env.define_macro(macro)

    def expand_code(self, code: str) -> str:
        """Expand all macros in code"""
        return self.expander.expand(code)

    def expand_file(self, file_path: str, output_path: Optional[str] = None) -> str:
        """Expand macros in a file"""
        with open(file_path, 'r') as f:
            code = f.read()

        expanded = self.expand_code(code)

        if output_path:
            with open(output_path, 'w') as f:
                f.write(expanded)

        return expanded

    def list_macros(self) -> List[str]:
        """List all defined macros"""
        return list(self.env.macros.keys())

    def get_macro_info(self, name: str) -> Optional[Dict]:
        """Get information about a macro"""
        macro = self.env.get_macro(name)
        if not macro:
            return None

        return {
            'name': macro.name,
            'type': macro.macro_type.value,
            'docstring': macro.docstring,
            'pattern': macro.pattern,
            'template': macro.template
        }

    def enable_debug(self):
        """Enable debug mode"""
        self.env.debug_mode = True

    def disable_debug(self):
        """Disable debug mode"""
        self.env.debug_mode = False


class MacroCLI:
    """Command-line interface for macro system"""

    def __init__(self):
        self.system = MacroSystem()

    def run(self, args: List[str]):
        """Run CLI command"""
        if not args:
            self.show_help()
            return

        command = args[0]
        command_args = args[1:]

        if command == 'expand':
            self.cmd_expand(command_args)
        elif command == 'list':
            self.cmd_list(command_args)
        elif command == 'info':
            self.cmd_info(command_args)
        elif command == 'debug':
            self.cmd_debug(command_args)
        else:
            print(f"Unknown command: {command}")
            self.show_help()

    def cmd_expand(self, args: List[str]):
        """Expand macros in a file"""
        if not args:
            print("Usage: expand <input_file> [output_file]")
            return

        input_file = args[0]
        output_file = args[1] if len(args) > 1 else None

        try:
            expanded = self.system.expand_file(input_file, output_file)

            if output_file:
                print(f"Expanded code written to {output_file}")
            else:
                print(expanded)
        except Exception as e:
            print(f"Error: {e}")

    def cmd_list(self, args: List[str]):
        """List all macros"""
        macros = self.system.list_macros()

        if not macros:
            print("No macros defined")
            return

        print("Defined macros:")
        for name in sorted(macros):
            info = self.system.get_macro_info(name)
            print(f"  {name} ({info['type']})")
            if info['docstring']:
                print(f"    {info['docstring']}")

    def cmd_info(self, args: List[str]):
        """Show macro information"""
        if not args:
            print("Usage: info <macro_name>")
            return

        name = args[0]
        info = self.system.get_macro_info(name)

        if not info:
            print(f"Macro '{name}' not found")
            return

        print(f"Macro: {name}")
        print(f"Type: {info['type']}")
        print(f"Docstring: {info['docstring']}")
        if info['pattern']:
            print(f"Pattern: {info['pattern']}")
        if info['template']:
            print(f"Template: {info['template']}")

    def cmd_debug(self, args: List[str]):
        """Toggle debug mode"""
        if args and args[0] == 'on':
            self.system.enable_debug()
            print("Debug mode enabled")
        elif args and args[0] == 'off':
            self.system.disable_debug()
            print("Debug mode disabled")
        else:
            print("Usage: debug <on|off>")

    def show_help(self):
        """Show help"""
        print("""
Prim Macro System Commands:
  expand <input> [output]    Expand macros in a file
  list                       List all defined macros
  info <name>                Show macro information
  debug <on|off>             Toggle debug mode

Example:
  python prim_macros.py expand example.prim output.prim
  python prim_macros.py list
  python prim_macros.py info define
""")


def main():
    """Main entry point"""
    import sys

    cli = MacroCLI()
    cli.run(sys.argv[1:])


if __name__ == "__main__":
    main()
