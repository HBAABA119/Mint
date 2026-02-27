"""
Prim Linting Tools
Provides static code analysis for quality issues, best practice enforcement,
performance anti-pattern detection, security vulnerability scanning, and custom rule development.
"""

import os
import re
from typing import Dict, List, Optional, Any, Tuple, Callable
from dataclasses import dataclass, field
from enum import Enum


class LintSeverity(Enum):
    """Lint message severity"""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"
    HINT = "hint"


class LintCategory(Enum):
    """Lint message categories"""
    STYLE = "style"
    QUALITY = "quality"
    PERFORMANCE = "performance"
    SECURITY = "security"
    BEST_PRACTICE = "best_practice"


@dataclass
class LintMessage:
    """Lint message"""
    file_path: str
    line_number: int
    column_number: int
    severity: LintSeverity
    category: LintCategory
    message: str
    rule_id: str
    suggestion: Optional[str] = None


@dataclass
class LintRule:
    """Lint rule definition"""
    id: str
    name: str
    description: str
    category: LintCategory
    severity: LintSeverity
    check: Callable[[str, int, List[str]], Optional[LintMessage]]


class PrimLinter:
    """Main linter for Prim language"""

    def __init__(self):
        self.rules: List[LintRule] = []
        self.messages: List[LintMessage] = []
        self._register_default_rules()

    def _register_default_rules(self):
        """Register default lint rules"""
        # Style rules
        self.register_rule(LintRule(
            id="E001",
            name="LineTooLong",
            description="Line exceeds maximum length",
            category=LintCategory.STYLE,
            severity=LintSeverity.WARNING,
            check=self._check_line_too_long
        ))

        self.register_rule(LintRule(
            id="E002",
            name="TrailingWhitespace",
            description="Trailing whitespace",
            category=LintCategory.STYLE,
            severity=LintSeverity.WARNING,
            check=self._check_trailing_whitespace
        ))

        # Quality rules
        self.register_rule(LintRule(
            id="Q001",
            name="UnusedVariable",
            description="Variable defined but never used",
            category=LintCategory.QUALITY,
            severity=LintSeverity.WARNING,
            check=self._check_unused_variable
        ))

        self.register_rule(LintRule(
            id="Q002",
            name="UndefinedVariable",
            description="Use of undefined variable",
            category=LintCategory.QUALITY,
            severity=LintSeverity.ERROR,
            check=self._check_undefined_variable
        ))

        # Performance rules
        self.register_rule(LintRule(
            id="P001",
            name="InefficientLoop",
            description="Inefficient loop construction",
            category=LintCategory.PERFORMANCE,
            severity=LintSeverity.INFO,
            check=self._check_inefficient_loop
        ))

        self.register_rule(LintRule(
            id="P002",
            name="StringConcatenationInLoop",
            description="String concatenation in loop",
            category=LintCategory.PERFORMANCE,
            severity=LintSeverity.WARNING,
            check=self._check_string_concatenation
        ))

        # Security rules
        self.register_rule(LintRule(
            id="S001",
            name="HardcodedPassword",
            description="Possible hardcoded password",
            category=LintCategory.SECURITY,
            severity=LintSeverity.WARNING,
            check=self._check_hardcoded_password
        ))

        self.register_rule(LintRule(
            id="S002",
            name="SQLInjection",
            description="Possible SQL injection vulnerability",
            category=LintCategory.SECURITY,
            severity=LintSeverity.ERROR,
            check=self._check_sql_injection
        ))

        # Best practice rules
        self.register_rule(LintRule(
            id="B001",
            name="MissingDocstring",
            description="Function missing docstring",
            category=LintCategory.BEST_PRACTICE,
            severity=LintSeverity.INFO,
            check=self._check_missing_docstring
        ))

        self.register_rule(LintRule(
            id="B002",
            name="TooManyArguments",
            description="Function has too many arguments",
            category=LintCategory.BEST_PRACTICE,
            severity=LintSeverity.WARNING,
            check=self._check_too_many_arguments
        ))

    def register_rule(self, rule: LintRule):
        """Register a lint rule"""
        self.rules.append(rule)

    def lint_file(self, file_path: str) -> List[LintMessage]:
        """Lint a single file"""
        with open(file_path, 'r') as f:
            code = f.read()

        return self.lint_code(code, file_path)

    def lint_code(self, code: str, file_path: str = "<string>") -> List[LintMessage]:
        """Lint code"""
        self.messages = []
        lines = code.split('\n')

        # Track variables for quality checks
        variables = set()
        used_variables = set()

        for line_num, line in enumerate(lines, 1):
            # Track variable definitions
            var_match = re.match(r'([a-zA-Z_][a-zA-Z0-9_]*)\s*=', line)
            if var_match:
                variables.add(var_match.group(1))

            # Track variable usage
            for var in variables:
                if re.search(r'\b' + var + r'\b', line):
                    used_variables.add(var)

            # Apply all rules
            for rule in self.rules:
                message = rule.check(line, line_num, lines)
                if message:
                    self.messages.append(message)

        # Check unused variables
        for var in variables - used_variables:
            self.messages.append(LintMessage(
                file_path=file_path,
                line_number=0,
                column_number=0,
                severity=LintSeverity.WARNING,
                category=LintCategory.QUALITY,
                message=f"Unused variable: {var}",
                rule_id="Q001"
            ))

        return self.messages

    def _check_line_too_long(
        self,
        line: str,
        line_num: int,
        lines: List[str]
    ) -> Optional[LintMessage]:
        """Check if line is too long"""
        max_length = 88
        if len(line) > max_length:
            return LintMessage(
                file_path="",
                line_number=line_num,
                column_number=max_length,
                severity=LintSeverity.WARNING,
                category=LintCategory.STYLE,
                message=f"Line too long ({len(line)} > {max_length} characters)",
                rule_id="E001"
            )
        return None

    def _check_trailing_whitespace(
        self,
        line: str,
        line_num: int,
        lines: List[str]
    ) -> Optional[LintMessage]:
        """Check for trailing whitespace"""
        if line != line.rstrip():
            return LintMessage(
                file_path="",
                line_number=line_num,
                column_number=len(line.rstrip()),
                severity=LintSeverity.WARNING,
                category=LintCategory.STYLE,
                message="Trailing whitespace",
                rule_id="E002"
            )
        return None

    def _check_unused_variable(
        self,
        line: str,
        line_num: int,
        lines: List[str]
    ) -> Optional[LintMessage]:
        """Check for unused variables (handled in lint_code)"""
        return None

    def _check_undefined_variable(
        self,
        line: str,
        line_num: int,
        lines: List[str]
    ) -> Optional[LintMessage]:
        """Check for undefined variable usage"""
        # Find potential variable references
        matches = re.finditer(r'\b([a-zA-Z_][a-zA-Z0-9_]*)\b', line)
        
        # Get all defined variables from previous lines
        defined_vars = set()
        for i in range(line_num - 1):
            var_match = re.match(r'([a-zA-Z_][a-zA-Z0-9_]*)\s*=', lines[i])
            if var_match:
                defined_vars.add(var_match.group(1))

        for match in matches:
            var_name = match.group(1)
            # Skip keywords
            if var_name in ['if', 'else', 'elif', 'for', 'while', 'def', 'return', 'import', 'from', 'class', 'try', 'except', 'finally', 'with', 'as']:
                continue
            # Check if variable is defined
            if var_name not in defined_vars and var_name not in ['print', 'len', 'str', 'int', 'list']:
                return LintMessage(
                    file_path="",
                    line_number=line_num,
                    column_number=match.start() + 1,
                    severity=LintSeverity.ERROR,
                    category=LintCategory.QUALITY,
                    message=f"Undefined variable: {var_name}",
                    rule_id="Q002"
                )
        
        return None

    def _check_inefficient_loop(
        self,
        line: str,
        line_num: int,
        lines: List[str]
    ) -> Optional[LintMessage]:
        """Check for inefficient loop patterns"""
        # Check for range(len()) pattern
        if 'range(len(' in line:
            return LintMessage(
                file_path="",
                line_number=line_num,
                column_number=line.find('range') + 1,
                severity=LintSeverity.INFO,
                category=LintCategory.PERFORMANCE,
                message="Consider using enumerate() instead of range(len())",
                rule_id="P001",
                suggestion="Use: for i, item in enumerate(items):"
            )
        return None

    def _check_string_concatenation(
        self,
        line: str,
        line_num: int,
        lines: List[str]
    ) -> Optional[LintMessage]:
        """Check for string concatenation in loop"""
        # Look for loop with string concatenation
        if 'for' in line and '+=' in line and '"' in line:
            return LintMessage(
                file_path="",
                line_number=line_num,
                column_number=line.find('+=') + 1,
                severity=LintSeverity.WARNING,
                category=LintCategory.PERFORMANCE,
                message="String concatenation in loop is inefficient",
                rule_id="P002",
                suggestion="Use list comprehension and join()"
            )
        return None

    def _check_hardcoded_password(
        self,
        line: str,
        line_num: int,
        lines: List[str]
    ) -> Optional[LintMessage]:
        """Check for hardcoded passwords"""
        # Look for variable names that suggest passwords
        password_patterns = [
            r'password\s*=\s*["\']',
            r'passwd\s*=\s*["\']',
            r'secret\s*=\s*["\']',
            r'api_key\s*=\s*["\']',
        ]

        for pattern in password_patterns:
            if re.search(pattern, line, re.IGNORECASE):
                return LintMessage(
                    file_path="",
                    line_number=line_num,
                    column_number=re.search(pattern, line, re.IGNORECASE).start() + 1,
                    severity=LintSeverity.WARNING,
                    category=LintCategory.SECURITY,
                    message="Possible hardcoded password or secret",
                    rule_id="S001",
                    suggestion="Use environment variables or configuration files"
                )
        
        return None

    def _check_sql_injection(
        self,
        line: str,
        line_num: int,
        lines: List[str]
    ) -> Optional[LintMessage]:
        """Check for SQL injection vulnerabilities"""
        # Look for string concatenation in SQL queries
        if ('SELECT' in line.upper() or 'INSERT' in line.upper() or 'UPDATE' in line.upper()) and '+' in line:
            return LintMessage(
                file_path="",
                line_number=line_num,
                column_number=line.find('+') + 1,
                severity=LintSeverity.ERROR,
                category=LintCategory.SECURITY,
                message="Possible SQL injection vulnerability",
                rule_id="S002",
                suggestion="Use parameterized queries"
            )
        return None

    def _check_missing_docstring(
        self,
        line: str,
        line_num: int,
        lines: List[str]
    ) -> Optional[LintMessage]:
        """Check for missing function docstrings"""
        # Check for function definition
        func_match = re.match(r'(?:def|fn|function)\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(', line)
        if func_match:
            # Check next line for docstring
            if line_num < len(lines):
                next_line = lines[line_num].strip()
                if not next_line.startswith('"""') and not next_line.startswith("#"):
                    return LintMessage(
                        file_path="",
                        line_number=line_num,
                        column_number=0,
                        severity=LintSeverity.INFO,
                        category=LintCategory.BEST_PRACTICE,
                        message=f"Function '{func_match.group(1)}' missing docstring",
                        rule_id="B001"
                    )
        return None

    def _check_too_many_arguments(
        self,
        line: str,
        line_num: int,
        lines: List[str]
    ) -> Optional[LintMessage]:
        """Check for functions with too many arguments"""
        func_match = re.match(r'(?:def|fn|function)\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(([^)]*)\)', line)
        if func_match:
            args = func_match.group(2).strip()
            if args:
                arg_count = len([a.strip() for a in args.split(',') if a.strip()])
                if arg_count > 5:
                    return LintMessage(
                        file_path="",
                        line_number=line_num,
                        column_number=0,
                        severity=LintSeverity.WARNING,
                        category=LintCategory.BEST_PRACTICE,
                        message=f"Function has {arg_count} arguments (consider using a data class or dictionary)",
                        rule_id="B002"
                    )
        return None

    def format_messages(self, messages: List[LintMessage]) -> str:
        """Format lint messages for display"""
        lines = []
        
        # Group by file
        by_file = {}
        for msg in messages:
            if msg.file_path not in by_file:
                by_file[msg.file_path] = []
            by_file[msg.file_path].append(msg)
        
        for file_path, file_messages in by_file.items():
            lines.append(f"{file_path}:")
            
            for msg in sorted(file_messages, key=lambda m: (m.line_number, m.column_number)):
                severity_symbol = {
                    LintSeverity.ERROR: "✖",
                    LintSeverity.WARNING: "⚠",
                    LintSeverity.INFO: "ℹ",
                    LintSeverity.HINT: "→"
                }[msg.severity]
                
                lines.append(f"  {severity_symbol} {msg.line_number}:{msg.column_number} {msg.rule_id} {msg.category.value}: {msg.message}")
                
                if msg.suggestion:
                    lines.append(f"    Suggestion: {msg.suggestion}")
            
            lines.append("")
        
        return "\n".join(lines)

    def get_statistics(self, messages: List[LintMessage]) -> Dict[str, int]:
        """Get lint statistics"""
        stats = {
            'total': len(messages),
            'errors': 0,
            'warnings': 0,
            'info': 0,
            'hints': 0
        }
        
        for msg in messages:
            if msg.severity == LintSeverity.ERROR:
                stats['errors'] += 1
            elif msg.severity == LintSeverity.WARNING:
                stats['warnings'] += 1
            elif msg.severity == LintSeverity.INFO:
                stats['info'] += 1
            elif msg.severity == LintSeverity.HINT:
                stats['hints'] += 1
        
        return stats


class LinterCLI:
    """Command-line interface for linter"""

    def __init__(self):
        self.linter = PrimLinter()

    def run(self, args: List[str]):
        """Run CLI command"""
        if not args:
            self.show_help()
            return
        
        command = args[0]
        command_args = args[1:]
        
        if command == 'lint':
            self.cmd_lint(command_args)
        elif command == 'check':
            self.cmd_check(command_args)
        else:
            print(f"Unknown command: {command}")
            self.show_help()

    def cmd_lint(self, args: List[str]):
        """Lint files"""
        if not args:
            print("Usage: lint <file_or_directory>")
            return
        
        path = args[0]
        
        if os.path.isfile(path):
            messages = self.linter.lint_file(path)
            print(self.linter.format_messages(messages))
            stats = self.linter.get_statistics(messages)
            print(f"\nStatistics: {stats['total']} total ({stats['errors']} errors, {stats['warnings']} warnings)")
        elif os.path.isdir(path):
            all_messages = []
            for root, dirs, files in os.walk(path):
                for file in files:
                    if file.endswith('.prim'):
                        file_path = os.path.join(root, file)
                        messages = self.linter.lint_file(file_path)
                        all_messages.extend(messages)
            
            print(self.linter.format_messages(all_messages))
            stats = self.linter.get_statistics(all_messages)
            print(f"\nStatistics: {stats['total']} total ({stats['errors']} errors, {stats['warnings']} warnings)")

    def cmd_check(self, args: List[str]):
        """Check if files pass linting"""
        if not args:
            print("Usage: check <file_or_directory>")
            return
        
        path = args[0]
        
        if os.path.isfile(path):
            messages = self.linter.lint_file(path)
            stats = self.linter.get_statistics(messages)
            
            if stats['errors'] > 0:
                print(f"FAIL: {stats['errors']} error(s) found")
                return 1
            elif stats['warnings'] > 0:
                print(f"WARN: {stats['warnings']} warning(s) found")
                return 0
            else:
                print("PASS: No issues found")
                return 0
        else:
            print("Directory linting not supported in check mode")
            return 1

    def show_help(self):
        """Show help"""
        print("""
Prim Linter Commands:
  lint <file_or_directory>  Lint files and show all issues
  check <file_or_directory>  Check if files pass linting (exit code)

Example:
  python prim_linter.py lint example.prim
  python prim_linter.py lint src/
  python prim_linter.py check example.prim
""")


def main():
    """Main entry point"""
    import sys
    
    cli = LinterCLI()
    sys.exit(cli.run(sys.argv[1:]) or 0)


if __name__ == "__main__":
    main()
