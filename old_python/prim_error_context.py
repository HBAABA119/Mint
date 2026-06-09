"""
Prim Enhanced Error Reporting System
Provides context-aware error messages with precise line numbers,
intelligent suggestions, and multi-language support.
"""

import re
import sys
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum


class ErrorSeverity(Enum):
    """Error severity levels"""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"
    HINT = "hint"


class ErrorCategory(Enum):
    """Error categories for better classification"""
    SYNTAX = "syntax"
    TYPE = "type"
    RUNTIME = "runtime"
    IMPORT = "import"
    SEMANTIC = "semantic"
    DEPRECATED = "deprecated"


@dataclass
class ErrorSuggestion:
    """Suggestion for fixing an error"""
    message: str
    code_snippet: Optional[str] = None
    priority: int = 1  # 1 = highest, 3 = lowest


@dataclass
class ErrorContext:
    """Context information for an error"""
    file_path: str
    line_number: int
    column_number: Optional[int] = None
    code_line: Optional[str] = None
    surrounding_lines: Optional[List[str]] = None


@dataclass
class PrimError:
    """Complete error information"""
    message: str
    severity: ErrorSeverity
    category: ErrorCategory
    context: Optional[ErrorContext] = None
    suggestions: List[ErrorSuggestion] = None
    error_code: Optional[str] = None
    related_errors: List['PrimError'] = None

    def __post_init__(self):
        if self.suggestions is None:
            self.suggestions = []
        if self.related_errors is None:
            self.related_errors = []


class ErrorReporter:
    """Main error reporting system"""

    def __init__(self):
        self.errors: List[PrimError] = []
        self.warnings: List[PrimError] = []
        self.language: str = "en"
        self.error_database = self._initialize_error_database()
        self.suggestion_database = self._initialize_suggestion_database()

    def _initialize_error_database(self) -> Dict[str, Dict[str, str]]:
        """Initialize multi-language error messages"""
        return {
            "en": {
                "syntax_error": "Syntax error",
                "type_error": "Type error",
                "runtime_error": "Runtime error",
                "import_error": "Import error",
                "undefined_variable": "Variable '{0}' is not defined",
                "type_mismatch": "Type mismatch: expected {0}, got {1}",
                "missing_semicolon": "Missing semicolon at end of statement",
                "unclosed_bracket": "Unclosed bracket '{0}'",
                "invalid_syntax": "Invalid syntax",
                "unexpected_token": "Unexpected token '{0}'",
            },
            "es": {
                "syntax_error": "Error de sintaxis",
                "type_error": "Error de tipo",
                "runtime_error": "Error de tiempo de ejecución",
                "import_error": "Error de importación",
                "undefined_variable": "La variable '{0}' no está definida",
                "type_mismatch": "Discrepancia de tipos: se esperaba {0}, se obtuvo {1}",
                "missing_semicolon": "Falta punto y coma al final de la declaración",
                "unclosed_bracket": "Corchete sin cerrar '{0}'",
                "invalid_syntax": "Sintaxis inválida",
                "unexpected_token": "Token inesperado '{0}'",
            },
            "fr": {
                "syntax_error": "Erreur de syntaxe",
                "type_error": "Erreur de type",
                "runtime_error": "Erreur d'exécution",
                "import_error": "Erreur d'importation",
                "undefined_variable": "La variable '{0}' n'est pas définie",
                "type_mismatch": "Incompatibilité de types: attendu {0}, obtenu {1}",
                "missing_semicolon": "Point-virgule manquant à la fin de l'instruction",
                "unclosed_bracket": "Parenthèse fermante manquante '{0}'",
                "invalid_syntax": "Syntaxe invalide",
                "unexpected_token": "Jeton inattendu '{0}'",
            },
        }

    def _initialize_suggestion_database(self) -> Dict[str, List[str]]:
        """Initialize intelligent suggestions for common errors"""
        return {
            "undefined_variable": [
                "Check if the variable name is spelled correctly",
                "Ensure the variable is declared before use",
                "Consider using a different variable name",
            ],
            "type_mismatch": [
                "Check the types of both operands",
                "Consider using type conversion functions",
                "Review the expected type in the documentation",
            ],
            "missing_semicolon": [
                "Add a semicolon at the end of the statement",
                "Check if you're using the correct syntax mode",
            ],
            "unclosed_bracket": [
                "Add the closing bracket",
                "Check for nested brackets",
            ],
            "import_error": [
                "Verify the module name is correct",
                "Check if the module is installed",
                "Ensure the module is in the correct path",
            ],
        }

    def set_language(self, language: str):
        """Set the language for error messages"""
        if language in self.error_database:
            self.language = language

    def get_error_message(self, key: str, *args) -> str:
        """Get localized error message"""
        if self.language in self.error_database:
            messages = self.error_database[self.language]
            if key in messages:
                return messages[key].format(*args)
        # Fallback to English
        return self.error_database["en"].get(key, key).format(*args)

    def get_suggestions(self, error_type: str) -> List[ErrorSuggestion]:
        """Get intelligent suggestions for an error type"""
        suggestions = []
        if error_type in self.suggestion_database:
            for i, msg in enumerate(self.suggestion_database[error_type]):
                suggestions.append(ErrorSuggestion(msg, priority=i + 1))
        return suggestions

    def create_error_context(
        self,
        file_path: str,
        line_number: int,
        column_number: Optional[int] = None,
        code_lines: Optional[List[str]] = None
    ) -> ErrorContext:
        """Create error context with surrounding code"""
        code_line = None
        surrounding_lines = None

        if code_lines and 1 <= line_number <= len(code_lines):
            code_line = code_lines[line_number - 1]
            # Get 2 lines before and after
            start = max(0, line_number - 3)
            end = min(len(code_lines), line_number + 2)
            surrounding_lines = code_lines[start:end]

        return ErrorContext(
            file_path=file_path,
            line_number=line_number,
            column_number=column_number,
            code_line=code_line,
            surrounding_lines=surrounding_lines
        )

    def report_error(
        self,
        message: str,
        category: ErrorCategory = ErrorCategory.SYNTAX,
        severity: ErrorSeverity = ErrorSeverity.ERROR,
        file_path: Optional[str] = None,
        line_number: Optional[int] = None,
        column_number: Optional[int] = None,
        code_lines: Optional[List[str]] = None,
        error_code: Optional[str] = None,
        suggestions: Optional[List[ErrorSuggestion]] = None
    ) -> PrimError:
        """Report an error with full context"""
        context = None
        if file_path and line_number:
            context = self.create_error_context(
                file_path, line_number, column_number, code_lines
            )

        error = PrimError(
            message=message,
            severity=severity,
            category=category,
            context=context,
            suggestions=suggestions or [],
            error_code=error_code
        )

        if severity == ErrorSeverity.ERROR:
            self.errors.append(error)
        elif severity == ErrorSeverity.WARNING:
            self.warnings.append(error)

        return error

    def format_error(self, error: PrimError) -> str:
        """Format an error for display"""
        lines = []
        
        # Header
        severity_symbol = {
            ErrorSeverity.ERROR: "✖",
            ErrorSeverity.WARNING: "⚠",
            ErrorSeverity.INFO: "ℹ",
            ErrorSeverity.HINT: "→"
        }[error.severity]

        lines.append(f"{severity_symbol} {error.category.value.upper()}: {error.message}")

        # Location
        if error.context:
            loc = f"{error.context.file_path}:{error.context.line_number}"
            if error.context.column_number:
                loc += f":{error.context.column_number}"
            lines.append(f"  Location: {loc}")

            # Code snippet
            if error.context.code_line:
                lines.append("")
                lines.append("  " + error.context.code_line)
                if error.context.column_number:
                    lines.append("  " + " " * (error.context.column_number - 1) + "^")

            # Surrounding lines
            if error.context.surrounding_lines:
                lines.append("")
                start_line = error.context.line_number - 2
                for i, line in enumerate(error.context.surrounding_lines):
                    line_num = start_line + i + 1
                    marker = ">" if line_num == error.context.line_number else " "
                    lines.append(f"  {marker} {line_num}: {line}")

        # Error code
        if error.error_code:
            lines.append(f"  Error Code: {error.error_code}")

        # Suggestions
        if error.suggestions:
            lines.append("")
            lines.append("  Suggestions:")
            for suggestion in sorted(error.suggestions, key=lambda s: s.priority):
                lines.append(f"    • {suggestion.message}")
                if suggestion.code_snippet:
                    lines.append(f"      {suggestion.code_snippet}")

        return "\n".join(lines)

    def format_all_errors(self) -> str:
        """Format all errors and warnings"""
        output = []
        
        if self.errors:
            output.append("=" * 60)
            output.append("ERRORS")
            output.append("=" * 60)
            for error in self.errors:
                output.append(self.format_error(error))
                output.append("")

        if self.warnings:
            output.append("=" * 60)
            output.append("WARNINGS")
            output.append("=" * 60)
            for warning in self.warnings:
                output.append(self.format_error(warning))
                output.append("")

        return "\n".join(output)

    def clear_errors(self):
        """Clear all errors and warnings"""
        self.errors.clear()
        self.warnings.clear()

    def has_errors(self) -> bool:
        """Check if there are any errors"""
        return len(self.errors) > 0

    def has_warnings(self) -> bool:
        """Check if there are any warnings"""
        return len(self.warnings) > 0

    def get_error_count(self) -> int:
        """Get total error count"""
        return len(self.errors)

    def get_warning_count(self) -> int:
        """Get total warning count"""
        return len(self.warnings)


# Convenience functions for common error types

def report_syntax_error(
    reporter: ErrorReporter,
    message: str,
    file_path: str,
    line_number: int,
    column_number: Optional[int] = None,
    code_lines: Optional[List[str]] = None
) -> PrimError:
    """Report a syntax error"""
    return reporter.report_error(
        message=message,
        category=ErrorCategory.SYNTAX,
        severity=ErrorSeverity.ERROR,
        file_path=file_path,
        line_number=line_number,
        column_number=column_number,
        code_lines=code_lines,
        error_code="E001"
    )


def report_type_error(
    reporter: ErrorReporter,
    message: str,
    file_path: str,
    line_number: int,
    expected_type: str,
    actual_type: str,
    code_lines: Optional[List[str]] = None
) -> PrimError:
    """Report a type error with suggestions"""
    suggestions = [
        ErrorSuggestion(f"Convert the value to {expected_type}"),
        ErrorSuggestion(f"Check if the variable type is correct"),
        ErrorSuggestion(f"Review the type annotations")
    ]
    
    return reporter.report_error(
        message=message,
        category=ErrorCategory.TYPE,
        severity=ErrorSeverity.ERROR,
        file_path=file_path,
        line_number=line_number,
        code_lines=code_lines,
        suggestions=suggestions,
        error_code="E002"
    )


def report_runtime_error(
    reporter: ErrorReporter,
    message: str,
    file_path: str,
    line_number: int,
    code_lines: Optional[List[str]] = None
) -> PrimError:
    """Report a runtime error"""
    return reporter.report_error(
        message=message,
        category=ErrorCategory.RUNTIME,
        severity=ErrorSeverity.ERROR,
        file_path=file_path,
        line_number=line_number,
        code_lines=code_lines,
        error_code="E003"
    )


def report_undefined_variable(
    reporter: ErrorReporter,
    variable_name: str,
    file_path: str,
    line_number: int,
    code_lines: Optional[List[str]] = None
) -> PrimError:
    """Report an undefined variable error with intelligent suggestions"""
    suggestions = reporter.get_suggestions("undefined_variable")
    
    return reporter.report_error(
        message=reporter.get_error_message("undefined_variable", variable_name),
        category=ErrorCategory.SEMANTIC,
        severity=ErrorSeverity.ERROR,
        file_path=file_path,
        line_number=line_number,
        code_lines=code_lines,
        suggestions=suggestions,
        error_code="E004"
    )


def report_type_mismatch(
    reporter: ErrorReporter,
    expected: str,
    actual: str,
    file_path: str,
    line_number: int,
    code_lines: Optional[List[str]] = None
) -> PrimError:
    """Report a type mismatch error with suggestions"""
    suggestions = reporter.get_suggestions("type_mismatch")
    
    return reporter.report_error(
        message=reporter.get_error_message("type_mismatch", expected, actual),
        category=ErrorCategory.TYPE,
        severity=ErrorSeverity.ERROR,
        file_path=file_path,
        line_number=line_number,
        code_lines=code_lines,
        suggestions=suggestions,
        error_code="E005"
    )


# IDE highlighting hooks

class IDEErrorHighlighter:
    """Provides error highlighting for IDEs"""

    @staticmethod
    def get_lsp_diagnostics(reporter: ErrorReporter) -> List[Dict[str, Any]]:
        """Convert errors to LSP diagnostic format"""
        diagnostics = []
        
        all_errors = reporter.errors + reporter.warnings
        
        for error in all_errors:
            if not error.context:
                continue
                
            diagnostic = {
                "range": {
                    "start": {
                        "line": error.context.line_number - 1,
                        "character": error.context.column_number or 0
                    },
                    "end": {
                        "line": error.context.line_number - 1,
                        "character": error.context.column_number or 0
                    }
                },
                "severity": {
                    ErrorSeverity.ERROR: 1,
                    ErrorSeverity.WARNING: 2,
                    ErrorSeverity.INFO: 3,
                    ErrorSeverity.HINT: 4
                }[error.severity],
                "source": "prim",
                "message": error.message,
                "code": error.error_code
            }
            
            if error.suggestions:
                diagnostic["relatedInformation"] = [
                    {
                        "message": s.message,
                        "location": {
                            "uri": error.context.file_path,
                            "range": diagnostic["range"]
                        }
                    }
                    for s in error.suggestions
                ]
            
            diagnostics.append(diagnostic)
        
        return diagnostics


if __name__ == "__main__":
    # Example usage
    reporter = ErrorReporter()
    
    # Report various errors
    code_lines = [
        "x = 42",
        "y = x + z",  # Line 2: undefined variable z
        "print(y)"
    ]
    
    report_undefined_variable(reporter, "z", "example.prim", 2, code_lines)
    
    # Format and display errors
    print(reporter.format_all_errors())
    
    # Get LSP diagnostics
    highlighter = IDEErrorHighlighter()
    diagnostics = highlighter.get_lsp_diagnostics(reporter)
    print(f"\nLSP Diagnostics: {len(diagnostics)}")
