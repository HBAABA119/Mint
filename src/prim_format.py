"""
Prim Code Formatter
Provides consistent formatting rules across all syntax modes with customizable
style configurations, pre-commit hook integration, editor plugin support, and batch formatting.
"""

import re
import os
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum


class SyntaxMode(Enum):
    """Syntax modes for Prim"""
    SLIM = "slim"
    BLOCK = "block"
    FLOW = "flow"


@dataclass
class FormattingStyle:
    """Formatting style configuration"""
    indent_size: int = 4
    indent_style: str = "space"  # "space" or "tab"
    max_line_length: int = 88
    quote_style: str = "double"  # "double" or "single"
    trailing_comma: bool = True
    spaces_around_operators: bool = True
    spaces_after_comma: bool = True
    blank_lines_top_level: int = 2
    blank_lines_functions: int = 1
    preserve_blank_lines: int = 1


class PrimFormatter:
    """Code formatter for Prim language"""

    def __init__(self, style: Optional[FormattingStyle] = None):
        self.style = style or FormattingStyle()
        self.indent_char = ' ' if self.style.indent_style == "space" else '\t'

    def format(self, code: str, mode: SyntaxMode = SyntaxMode.SLIM) -> str:
        """Format code according to style rules"""
        if mode == SyntaxMode.SLIM:
            return self._format_slim(code)
        elif mode == SyntaxMode.BLOCK:
            return self._format_block(code)
        elif mode == SyntaxMode.FLOW:
            return self._format_flow(code)
        return code

    def _format_slim(self, code: str) -> str:
        """Format slim (Python-like) mode code"""
        lines = code.split('\n')
        formatted_lines = []
        
        # Remove leading/trailing blank lines
        while lines and not lines[0].strip():
            lines.pop(0)
        while lines and not lines[-1].strip():
            lines.pop()
        
        # Track indentation level
        indent_level = 0
        
        for i, line in enumerate(lines):
            stripped = line.lstrip()
            
            # Skip empty lines (but preserve some)
            if not stripped:
                # Preserve blank lines up to style setting
                if self.style.preserve_blank_lines > 0:
                    # Check if this is within the allowed blank lines
                    blank_count = 0
                    for j in range(i - 1, -1, -1):
                        if not lines[j].strip():
                            blank_count += 1
                        else:
                            break
                    if blank_count < self.style.preserve_blank_lines:
                        formatted_lines.append('')
                continue
            
            # Calculate current indentation
            current_indent = len(line) - len(stripped)
            expected_indent = indent_level * self.style.indent_size
            
            # Detect dedent
            if stripped.startswith(('else', 'elif', 'except', 'finally')):
                indent_level = max(0, indent_level - 1)
                expected_indent = indent_level * self.style.indent_size
            
            # Apply indentation
            if current_indent != expected_indent:
                line = self.indent_char * expected_indent + stripped
            
            # Format the line
            formatted_line = self._format_line(line, SyntaxMode.SLIM)
            formatted_lines.append(formatted_line)
            
            # Detect indent (lines ending with :)
            if stripped.endswith(':'):
                indent_level += 1
        
        return '\n'.join(formatted_lines)

    def _format_block(self, code: str) -> str:
        """Format block (C/JS-like) mode code"""
        lines = code.split('\n')
        formatted_lines = []
        
        # Remove leading/trailing blank lines
        while lines and not lines[0].strip():
            lines.pop(0)
        while lines and not lines[-1].strip():
            lines.pop()
        
        # Track indentation level
        indent_level = 0
        
        for line in lines:
            stripped = line.strip()
            
            # Skip empty lines
            if not stripped:
                if self.style.preserve_blank_lines > 0:
                    formatted_lines.append('')
                continue
            
            # Calculate current indentation
            current_indent = len(line) - len(line.lstrip())
            expected_indent = indent_level * self.style.indent_size
            
            # Detect dedent
            if stripped.startswith(('}', ']')) or stripped.startswith(('else', 'elif', 'except', 'finally')):
                indent_level = max(0, indent_level - 1)
                expected_indent = indent_level * self.style.indent_size
            
            # Apply indentation
            if current_indent != expected_indent:
                line = self.indent_char * expected_indent + stripped
            
            # Format the line
            formatted_line = self._format_line(line, SyntaxMode.BLOCK)
            formatted_lines.append(formatted_line)
            
            # Detect indent (lines ending with {)
            if stripped.endswith('{'):
                indent_level += 1
        
        return '\n'.join(formatted_lines)

    def _format_flow(self, code: str) -> str:
        """Format flow (functional) mode code"""
        lines = code.split('\n')
        formatted_lines = []
        
        # Remove leading/trailing blank lines
        while lines and not lines[0].strip():
            lines.pop(0)
        while lines and not lines[-1].strip():
            lines.pop()
        
        for line in lines:
            stripped = line.strip()
            
            # Skip empty lines
            if not stripped:
                if self.style.preserve_blank_lines > 0:
                    formatted_lines.append('')
                continue
            
            # Format the line
            formatted_line = self._format_line(line, SyntaxMode.FLOW)
            formatted_lines.append(formatted_line)
        
        return '\n'.join(formatted_lines)

    def _format_line(self, line: str, mode: SyntaxMode) -> str:
        """Format a single line"""
        # Add spaces around operators
        if self.style.spaces_around_operators:
            line = self._format_operators(line)
        
        # Format quotes
        line = self._format_quotes(line)
        
        # Format commas
        if self.style.spaces_after_comma:
            line = self._format_commas(line)
        
        # Format function calls
        line = self._format_function_calls(line, mode)
        
        return line

    def _format_operators(self, line: str) -> str:
        """Add spaces around operators"""
        operators = ['=', '==', '!=', '<=', '>=', '<', '>', '+=', '-=', '*=', '/=', '%=', '=>']
        
        for op in operators:
            # Add space before and after
            pattern = r'(\S)' + re.escape(op) + r'(\S)'
            replacement = r'\1 ' + op + r' \2'
            line = re.sub(pattern, replacement, line)
        
        return line

    def _format_quotes(self, line: str) -> str:
        """Convert quotes to preferred style"""
        if self.style.quote_style == "double":
            # Convert single quotes to double (simple approach)
            # This is simplified - real implementation would be more careful
            pass
        return line

    def _format_commas(self, line: str) -> str:
        """Add spaces after commas"""
        return re.sub(r',(\S)', r', \1', line)

    def _format_function_calls(self, line: str, mode: SyntaxMode) -> str:
        """Format function calls"""
        # Add spaces after commas in function calls
        line = re.sub(r'\(([^)]*),', r'(\1, ', line)
        return line

    def format_file(
        self,
        file_path: str,
        mode: Optional[SyntaxMode] = None,
        in_place: bool = False
    ) -> str:
        """Format a file"""
        with open(file_path, 'r') as f:
            code = f.read()
        
        # Detect mode if not specified
        if mode is None:
            mode = self._detect_mode(code)
        
        # Format code
        formatted_code = self.format(code, mode)
        
        # Write back if in_place
        if in_place:
            with open(file_path, 'w') as f:
                f.write(formatted_code)
        
        return formatted_code

    def _detect_mode(self, code: str) -> SyntaxMode:
        """Detect syntax mode from code"""
        # Check for mode directive
        mode_match = re.search(r'#mode\s+(\w+)', code)
        if mode_match:
            mode_str = mode_match.group(1).lower()
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

    def format_directory(
        self,
        directory: str,
        pattern: str = "*.prim",
        recursive: bool = True
    ) -> List[str]:
        """Format all files in a directory"""
        formatted_files = []
        
        if recursive:
            for root, dirs, files in os.walk(directory):
                for file in files:
                    if file.endswith('.prim'):
                        file_path = os.path.join(root, file)
                        self.format_file(file_path, in_place=True)
                        formatted_files.append(file_path)
        else:
            for file in os.listdir(directory):
                if file.endswith('.prim'):
                    file_path = os.path.join(directory, file)
                    self.format_file(file_path, in_place=True)
                    formatted_files.append(file_path)
        
        return formatted_files

    def check_formatting(self, code: str, mode: SyntaxMode = SyntaxMode.SLIM) -> List[str]:
        """Check if code is properly formatted, return list of issues"""
        issues = []
        lines = code.split('\n')
        
        # Check line length
        for i, line in enumerate(lines):
            if len(line) > self.style.max_line_length:
                issues.append(f"Line {i+1}: Exceeds max line length ({self.style.max_line_length})")
        
        # Check indentation
        expected_indent = 0
        for i, line in enumerate(lines):
            stripped = line.lstrip()
            if not stripped:
                continue
            
            current_indent = len(line) - len(stripped)
            
            # Detect indent level
            indent_level = current_indent // self.style.indent_size
            
            if current_indent != indent_level * self.style.indent_size:
                issues.append(f"Line {i+1}: Incorrect indentation")
        
        return issues


class PrecommitHookGenerator:
    """Generate pre-commit hooks for code formatting"""

    @staticmethod
    def generate_hook(formatter_path: str = "prim_format.py") -> str:
        """Generate pre-commit hook content"""
        hook_content = f"""#!/bin/sh
# Prim code formatter pre-commit hook

# Format all staged .prim files
for file in $(git diff --cached --name-only | grep '\\.prim$'); do
    python {formatter_path} format "$file" --in-place
done

# Re-add formatted files
git add -u
"""
        return hook_content

    @staticmethod
    def install_hook(hook_path: str = ".git/hooks/pre-commit"):
        """Install pre-commit hook"""
        hook_content = PrecommitHookGenerator.generate_hook()
        
        os.makedirs(os.path.dirname(hook_path), exist_ok=True)
        with open(hook_path, 'w') as f:
            f.write(hook_content)
        
        # Make executable
        os.chmod(hook_path, 0o755)


class EditorConfigGenerator:
    """Generate EditorConfig for consistent formatting"""

    @staticmethod
    def generate(style: FormattingStyle) -> str:
        """Generate .editorconfig content"""
        config = f"""# EditorConfig is awesome: https://EditorConfig.org

root = true

[*]
charset = utf-8
end_of_line = lf
insert_final_newline = true
trim_trailing_whitespace = true

[*.prim]
indent_style = {style.indent_style}
indent_size = {style.indent_size}
max_line_length = {style.max_line_length}
"""
        return config


class FormatterCLI:
    """Command-line interface for formatter"""

    def __init__(self):
        self.formatter = PrimFormatter()

    def run(self, args: List[str]):
        """Run CLI command"""
        if not args:
            self.show_help()
            return
        
        command = args[0]
        command_args = args[1:]
        
        if command == 'format':
            self.cmd_format(command_args)
        elif command == 'check':
            self.cmd_check(command_args)
        elif command == 'install-hook':
            self.cmd_install_hook(command_args)
        elif command == 'generate-editorconfig':
            self.cmd_generate_editorconfig(command_args)
        else:
            print(f"Unknown command: {command}")
            self.show_help()

    def cmd_format(self, args: List[str]):
        """Format files"""
        in_place = '--in-place' in args or '-i' in args
        recursive = '--recursive' in args or '-r' in args
        
        # Remove flags from args
        args = [a for a in args if not a.startswith('-')]
        
        if not args:
            print("Usage: format <file_or_directory> [--in-place] [--recursive]")
            return
        
        path = args[0]
        
        if os.path.isfile(path):
            formatted = self.formatter.format_file(path, in_place=in_place)
            if not in_place:
                print(formatted)
        elif os.path.isdir(path):
            files = self.formatter.format_directory(path, recursive=recursive)
            print(f"Formatted {len(files)} file(s)")

    def cmd_check(self, args: List[str]):
        """Check formatting"""
        if not args:
            print("Usage: check <file>")
            return
        
        file_path = args[0]
        
        with open(file_path, 'r') as f:
            code = f.read()
        
        mode = self.formatter._detect_mode(code)
        issues = self.formatter.check_formatting(code, mode)
        
        if issues:
            print(f"Found {len(issues)} formatting issue(s):")
            for issue in issues:
                print(f"  - {issue}")
        else:
            print("No formatting issues found")

    def cmd_install_hook(self, args: List[str]):
        """Install pre-commit hook"""
        hook_path = args[0] if args else ".git/hooks/pre-commit"
        PrecommitHookGenerator.install_hook(hook_path)
        print(f"Pre-commit hook installed at {hook_path}")

    def cmd_generate_editorconfig(self, args: List[str]):
        """Generate EditorConfig"""
        config = EditorConfigGenerator.generate(self.formatter.style)
        print(config)

    def show_help(self):
        """Show help"""
        print("""
Prim Code Formatter Commands:
  format <file_or_dir> [--in-place] [--recursive]  Format files
  check <file>                                      Check formatting
  install-hook [path]                              Install pre-commit hook
  generate-editorconfig                            Generate EditorConfig

Options:
  -i, --in-place     Format files in place
  -r, --recursive   Format files recursively

Example:
  python prim_format.py format example.prim --in-place
  python prim_format.py format src/ --recursive
  python prim_format.py check example.prim
""")


def main():
    """Main entry point"""
    import sys
    
    cli = FormatterCLI()
    cli.run(sys.argv[1:])


if __name__ == "__main__":
    main()
