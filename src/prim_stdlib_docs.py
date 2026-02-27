"""
Prim Standard Library Documentation Generator
Provides API documentation, examples, and reference documentation
for all standard library modules.
"""

import inspect
import os
from typing import List, Dict, Any, Optional, Type, Callable
from dataclasses import dataclass, field
from enum import Enum


class DocType(Enum):
    """Documentation types"""
    MODULE = "module"
    CLASS = "class"
    FUNCTION = "function"
    METHOD = "method"
    VARIABLE = "variable"


@dataclass
class Parameter:
    """Function parameter documentation"""
    name: str
    type: str
    description: str
    default: Optional[str] = None


@dataclass
class Example:
    """Code example"""
    code: str
    description: str
    output: Optional[str] = None


@dataclass
class Documentation:
    """Documentation entry"""
    name: str
    type: DocType
    description: str
    parameters: List[Parameter] = field(default_factory=list)
    returns: Optional[str] = None
    raises: List[str] = field(default_factory=list)
    examples: List[Example] = field(default_factory=list)
    see_also: List[str] = field(default_factory=list)
    deprecated: bool = False
    version_added: str = "1.0.0"


class DocumentationGenerator:
    """Documentation generator"""

    def __init__(self, output_dir: str = "docs"):
        self.output_dir = output_dir
        self.docs: Dict[str, Documentation] = {}

        os.makedirs(output_dir, exist_ok=True)

    def generate_from_module(self, module: Any) -> Documentation:
        """Generate documentation from module"""
        module_name = module.__name__
        docstring = inspect.getdoc(module) or ""

        doc = Documentation(
            name=module_name,
            type=DocType.MODULE,
            description=docstring
        )

        # Document classes
        for name, obj in inspect.getmembers(module, inspect.isclass):
            if obj.__module__ == module_name:
                class_doc = self._generate_class_doc(obj)
                self.docs[f"{module_name}.{name}"] = class_doc

        # Document functions
        for name, obj in inspect.getmembers(module, inspect.isfunction):
            if obj.__module__ == module_name:
                func_doc = self._generate_function_doc(obj)
                self.docs[f"{module_name}.{name}"] = func_doc

        return doc

    def _generate_class_doc(self, cls: Type) -> Documentation:
        """Generate class documentation"""
        docstring = inspect.getdoc(cls) or ""

        doc = Documentation(
            name=cls.__name__,
            type=DocType.CLASS,
            description=docstring
        )

        # Document methods
        for name, obj in inspect.getmembers(cls, inspect.isfunction):
            if not name.startswith('_'):
                method_doc = self._generate_function_doc(obj, is_method=True)
                self.docs[f"{cls.__name__}.{name}"] = method_doc

        return doc

    def _generate_function_doc(self, func: Callable, is_method: bool = False) -> Documentation:
        """Generate function documentation"""
        docstring = inspect.getdoc(func) or ""
        signature = inspect.signature(func)

        doc = Documentation(
            name=func.__name__,
            type=DocType.METHOD if is_method else DocType.FUNCTION,
            description=docstring
        )

        # Parse parameters
        for param_name, param in signature.parameters.items():
            param_type = str(param.annotation) if param.annotation else "Any"
            param_default = str(param.default) if param.default != inspect.Parameter.empty else None

            doc.parameters.append(Parameter(
                name=param_name,
                type=param_type,
                description="",
                default=param_default
            ))

        # Parse return type
        if signature.return_annotation and signature.return_annotation != inspect.Signature.empty:
            doc.returns = str(signature.return_annotation)

        return doc

    def add_example(self, doc_name: str, example: Example):
        """Add example to documentation"""
        if doc_name in self.docs:
            self.docs[doc_name].examples.append(example)

    def mark_deprecated(self, doc_name: str, version: str = "1.0.0"):
        """Mark documentation as deprecated"""
        if doc_name in self.docs:
            self.docs[doc_name].deprecated = True
            self.docs[doc_name].version_added = version

    def generate_markdown(self, doc: Documentation) -> str:
        """Generate markdown documentation"""
        lines = []

        # Title
        lines.append(f"# {doc.name}")
        lines.append("")

        # Type badge
        lines.append(f"**Type:** `{doc.type.value}`")
        lines.append("")

        # Description
        lines.append("## Description")
        lines.append(doc.description)
        lines.append("")

        # Deprecation warning
        if doc.deprecated:
            lines.append("⚠️ **This is deprecated and will be removed in a future version.**")
            lines.append("")

        # Parameters
        if doc.parameters:
            lines.append("## Parameters")
            for param in doc.parameters:
                default_str = f" = {param.default}" if param.default else ""
                lines.append(f"- **{param.name}** ({param.type}){default_str}: {param.description}")
            lines.append("")

        # Returns
        if doc.returns:
            lines.append("## Returns")
            lines.append(f"Type: `{doc.returns}`")
            lines.append("")

        # Raises
        if doc.raises:
            lines.append("## Raises")
            for exc in doc.raises:
                lines.append(f"- `{exc}`")
            lines.append("")

        # Examples
        if doc.examples:
            lines.append("## Examples")
            for example in doc.examples:
                if example.description:
                    lines.append(f"### {example.description}")
                lines.append("```prim")
                lines.append(example.code)
                lines.append("```")
                if example.output:
                    lines.append("**Output:**")
                    lines.append("```")
                    lines.append(example.output)
                    lines.append("```")
                lines.append("")

        # See also
        if doc.see_also:
            lines.append("## See Also")
            for ref in doc.see_also:
                lines.append(f"- [{ref}]({ref.replace('.', '/')}.md)")
            lines.append("")

        return "\n".join(lines)

    def generate_all(self):
        """Generate all documentation"""
        for doc_name, doc in self.docs.items():
            markdown = self.generate_markdown(doc)

            # Create file path
            parts = doc_name.split('.')
            file_path = os.path.join(self.output_dir, *parts[:-1]) + ".md"

            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            with open(file_path, 'w') as f:
                f.write(markdown)

        print(f"Generated {len(self.docs)} documentation files")


class SecurityAuditor:
    """Security auditor for standard library"""

    def __init__(self):
        self.issues: List[Dict[str, Any]] = []

    def audit_module(self, module: Any) -> List[Dict[str, Any]]:
        """Audit module for security issues"""
        self.issues = []

        # Check for dangerous imports
        self._check_dangerous_imports(module)

        # Check for unsafe functions
        self._check_unsafe_functions(module)

        # Check for input validation
        self._check_input_validation(module)

        return self.issues

    def _check_dangerous_imports(self, module: Any):
        """Check for dangerous imports"""
        dangerous = ['eval', 'exec', 'pickle', 'subprocess']

        for name, obj in inspect.getmembers(module):
            if inspect.isfunction(obj) or inspect.isclass(obj):
                source = inspect.getsource(obj) if hasattr(obj, '__module__') else ""
                for danger in dangerous:
                    if danger in source:
                        self.issues.append({
                            'severity': 'high',
                            'type': 'dangerous_import',
                            'message': f'Use of dangerous {danger}',
                            'location': f"{module.__name__}.{name}"
                        })

    def _check_unsafe_functions(self, module: Any):
        """Check for unsafe functions"""
        for name, obj in inspect.getmembers(module, inspect.isfunction):
            if name in ['eval', 'exec', 'compile']:
                self.issues.append({
                    'severity': 'high',
                    'type': 'unsafe_function',
                    'message': f'Unsafe function {name}',
                    'location': f"{module.__name__}.{name}"
                })

    def _check_input_validation(self, module: Any):
        """Check for input validation"""
        for name, obj in inspect.getmembers(module, inspect.isfunction):
            sig = inspect.signature(obj)
            if len(sig.parameters) == 0:
                continue

            # Check if function validates inputs
            source = inspect.getsource(obj) if hasattr(obj, '__module__') else ""
            if 'validate' not in source.lower() and 'check' not in source.lower():
                self.issues.append({
                    'severity': 'medium',
                    'type': 'missing_validation',
                    'message': f'Function {name} may lack input validation',
                    'location': f"{module.__name__}.{name}"
                })


def main():
    """Main entry point"""
    print("Testing Standard Library Documentation...")

    # Test documentation generator
    gen = DocumentationGenerator()
    gen.generate_all()

    # Test security auditor
    auditor = SecurityAuditor()
    issues = auditor.audit_module(gen)
    print(f"Found {len(issues)} security issues")

    print("Standard Library Documentation initialized successfully")


if __name__ == "__main__":
    main()
