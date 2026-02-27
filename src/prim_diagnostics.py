"""
Prim Error Handling & Diagnostics
Provides comprehensive error messages, stack traces, warnings,
linting, and static analysis for Prim Language.
"""

import sys
import traceback
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import inspect


class ErrorSeverity(Enum):
    """Error severity"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class ErrorCategory(Enum):
    """Error categories"""
    SYNTAX = "syntax"
    RUNTIME = "runtime"
    TYPE = "type"
    VALUE = "value"
    IMPORT = "import"
    NAME = "name"
    ATTRIBUTE = "attribute"
    KEY = "key"
    INDEX = "index"
    MEMORY = "memory"
    IO = "io"
    SYSTEM = "system"


@dataclass
class ErrorLocation:
    """Error location"""
    file: str
    line: int
    column: int
    function: str


@dataclass
class PrimError:
    """Prim error"""
    message: str
    category: ErrorCategory
    severity: ErrorSeverity
    location: Optional[ErrorLocation]
    traceback: Optional[str]
    suggestions: List[str]
    code_snippet: Optional[str]

    def __str__(self) -> str:
        """Format error message"""
        output = []

        # Severity and category
        output.append(f"[{self.severity.value.upper()}] {self.category.value.upper()}")

        # Location
        if self.location:
            loc = self.location
            output.append(f"  at {loc.file}:{loc.line}:{loc.column}")
            if loc.function:
                output.append(f"  in {loc.function}()")

        # Message
        output.append(f"\n{self.message}")

        # Code snippet
        if self.code_snippet:
            output.append(f"\n  Code:\n{self.code_snippet}")

        # Suggestions
        if self.suggestions:
            output.append("\n  Suggestions:")
            for suggestion in self.suggestions:
                output.append(f"    - {suggestion}")

        # Traceback
        if self.traceback:
            output.append(f"\n  Traceback:\n{self.traceback}")

        return "\n".join(output)


class ErrorReporter:
    """Error reporter"""

    def __init__(self):
        self.errors: List[PrimError] = []
        self.warnings: List[PrimError] = []

    def report_error(
        self,
        message: str,
        category: ErrorCategory,
        location: Optional[ErrorLocation] = None,
        suggestions: Optional[List[str]] = None
    ) -> PrimError:
        """Report error"""
        error = PrimError(
            message=message,
            category=category,
            severity=ErrorSeverity.ERROR,
            location=location,
            traceback=traceback.format_exc(),
            suggestions=suggestions or [],
            code_snippet=self._get_code_snippet(location) if location else None
        )
        self.errors.append(error)
        return error

    def report_warning(
        self,
        message: str,
        category: ErrorCategory,
        location: Optional[ErrorLocation] = None,
        suggestions: Optional[List[str]] = None
    ) -> PrimError:
        """Report warning"""
        warning = PrimError(
            message=message,
            category=category,
            severity=ErrorSeverity.WARNING,
            location=location,
            traceback=None,
            suggestions=suggestions or [],
            code_snippet=self._get_code_snippet(location) if location else None
        )
        self.warnings.append(warning)
        return warning

    def _get_code_snippet(self, location: ErrorLocation) -> Optional[str]:
        """Get code snippet at location"""
        try:
            with open(location.file, 'r') as f:
                lines = f.readlines()

            start = max(0, location.line - 3)
            end = min(len(lines), location.line + 2)

            snippet_lines = []
            for i in range(start, end):
                line_num = i + 1
                marker = ">>>" if line_num == location.line else "   "
                snippet_lines.append(f"{marker} {line_num:4d}: {lines[i].rstrip()}")

            return "\n".join(snippet_lines)

        except Exception:
            return None

    def print_errors(self):
        """Print all errors"""
        for error in self.errors:
            print(error)
            print("-" * 60)

    def print_warnings(self):
        """Print all warnings"""
        for warning in self.warnings:
            print(warning)
            print("-" * 60)

    def has_errors(self) -> bool:
        """Check if errors exist"""
        return len(self.errors) > 0

    def clear(self):
        """Clear errors and warnings"""
        self.errors.clear()
        self.warnings.clear()


class Linter:
    """Code linter"""

    def __init__(self):
        self.issues: List[PrimError] = []

    def lint(self, code: str, filename: str = "<string>") -> List[PrimError]:
        """Lint code"""
        self.issues = []
        lines = code.split('\n')

        for line_num, line in enumerate(lines, 1):
            self._check_line(line, line_num, filename)

        return self.issues

    def _check_line(self, line: str, line_num: int, filename: str):
        """Check single line"""
        # Check for long lines
        if len(line) > 100:
            self.issues.append(PrimError(
                message=f"Line too long ({len(line)} > 100 characters)",
                category=ErrorCategory.SYNTAX,
                severity=ErrorSeverity.WARNING,
                location=ErrorLocation(file=filename, line=line_num, column=0, function=""),
                suggestions=["Consider breaking this line into multiple lines",
                           "Use line continuation or string concatenation"],
                code_snippet=line
            ))

        # Check for trailing whitespace
        if line.endswith(' ') and not line.endswith('  '):
            self.issues.append(PrimError(
                message="Trailing whitespace",
                category=ErrorCategory.SYNTAX,
                severity=ErrorSeverity.WARNING,
                location=ErrorLocation(file=filename, line=line_num, column=len(line), function=""),
                suggestions=["Remove trailing whitespace"],
                code_snippet=line
            ))

        # Check for print statements (should use logging)
        if 'print(' in line:
            self.issues.append(PrimError(
                message="Use logging instead of print",
                category=ErrorCategory.RUNTIME,
                severity=ErrorSeverity.WARNING,
                location=ErrorLocation(file=filename, line=line_num, column=line.index('print'), function=""),
                suggestions=["Use logging module for production code"],
                code_snippet=line
            ))


class StaticAnalyzer:
    """Static code analyzer"""

    def __init__(self):
        self.issues: List[PrimError] = []

    def analyze(self, code: str, filename: str = "<string>") -> List[PrimError]:
        """Analyze code statically"""
        self.issues = []

        # Check for common issues
        self._check_unreachable_code(code, filename)
        self._check_unused_imports(code, filename)
        self._check_shadowing(code, filename)

        return self.issues

    def _check_unreachable_code(self, code: str, filename: str):
        """Check for unreachable code"""
        lines = code.split('\n')
        in_unreachable = False

        for line_num, line in enumerate(lines, 1):
            if 'return' in line or 'break' in line or 'continue' in line:
                in_unreachable = True
            elif in_unreachable and line.strip() and not line.strip().startswith('#'):
                self.issues.append(PrimError(
                    message="Unreachable code detected",
                    category=ErrorCategory.RUNTIME,
                    severity=ErrorSeverity.WARNING,
                    location=ErrorLocation(file=filename, line=line_num, column=0, function=""),
                    suggestions=["Remove unreachable code"],
                    code_snippet=line
                ))
                in_unreachable = False

    def _check_unused_imports(self, code: str, filename: str):
        """Check for unused imports"""
        imports = []
        lines = code.split('\n')

        for line_num, line in enumerate(lines, 1):
            if line.strip().startswith('import ') or line.strip().startswith('from '):
                imports.append((line_num, line))

        # Simple check - in production would be more sophisticated
        for line_num, line in imports:
            module = line.split()[1] if 'import ' in line else line.split()[1]
            if module not in code:
                self.issues.append(PrimError(
                    message=f"Unused import: {module}",
                    category=ErrorCategory.IMPORT,
                    severity=ErrorSeverity.WARNING,
                    location=ErrorLocation(file=filename, line=line_num, column=0, function=""),
                    suggestions=["Remove unused imports"],
                    code_snippet=line
                ))

    def _check_shadowing(self, code: str, filename: str):
        """Check for variable shadowing"""
        # Simplified check - production would use AST
        lines = code.split('\n')
        variables = {}

        for line_num, line in enumerate(lines, 1):
            if '=' in line and not line.strip().startswith('#'):
                parts = line.split('=')
                var_name = parts[0].strip().split()[0]

                if var_name in variables:
                    self.issues.append(PrimError(
                        message=f"Variable '{var_name}' shadows previous declaration",
                        category=ErrorCategory.NAME,
                        severity=ErrorSeverity.WARNING,
                        location=ErrorLocation(file=filename, line=line_num, column=0, function=""),
                        suggestions=["Use different variable names"],
                        code_snippet=line
                    ))

                variables[var_name] = line_num


# Global error reporter
_reporter = ErrorReporter()
_linter = Linter()
_analyzer = StaticAnalyzer()


def get_error_reporter() -> ErrorReporter:
    """Get global error reporter"""
    return _reporter


def get_linter() -> Linter:
    """Get global linter"""
    return _linter


def get_analyzer() -> StaticAnalyzer:
    """Get global static analyzer"""
    return _analyzer


def main():
    """Main entry point"""
    print("Testing Error Handling & Diagnostics...")

    # Test error reporting
    reporter = get_error_reporter()
    error = reporter.report_error(
        message="Test error message",
        category=ErrorCategory.RUNTIME,
        location=ErrorLocation(file="test.prim", line=10, column=5, function="main"),
        suggestions=["Fix the error"]
    )
    print(error)

    # Test linting
    linter = get_linter()
    code = "print('hello')\n" + "x" * 120
    issues = linter.lint(code, "test.prim")
    print(f"\nFound {len(issues)} linting issues")

    # Test static analysis
    analyzer = get_analyzer()
    issues = analyzer.analyze(code, "test.prim")
    print(f"Found {len(issues)} static analysis issues")

    print("Error Handling & Diagnostics initialized successfully")


if __name__ == "__main__":
    main()
