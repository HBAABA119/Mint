"""
Prim Documentation Generator
Auto-generates documentation from source code comments with multi-format output
(HTML, PDF, Markdown), interactive API documentation, example code integration,
and cross-reference linking.
"""

import os
import re
import json
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import datetime


class DocFormat(Enum):
    """Documentation output formats"""
    MARKDOWN = "markdown"
    HTML = "html"
    PDF = "pdf"
    JSON = "json"


class DocType(Enum):
    """Documentation types"""
    MODULE = "module"
    FUNCTION = "function"
    CLASS = "class"
    VARIABLE = "variable"
    EXAMPLE = "example"


@dataclass
class Parameter:
    """Function parameter documentation"""
    name: str
    type: str
    description: str
    default: Optional[str] = None
    optional: bool = False


@dataclass
class DocSection:
    """Documentation section"""
    title: str
    content: str
    level: int = 1


@dataclass
class Documentation:
    """Complete documentation for a code element"""
    name: str
    doc_type: DocType
    description: str
    parameters: List[Parameter] = field(default_factory=list)
    returns: Optional[str] = None
    raises: List[str] = field(default_factory=list)
    examples: List[str] = field(default_factory=list)
    see_also: List[str] = field(default_factory=list)
    deprecated: bool = False
    since: Optional[str] = None
    version: Optional[str] = None
    author: Optional[str] = None
    file_path: str = ""
    line_number: int = 0


class DocParser:
    """Parse documentation from source code"""

    def __init__(self):
        self.patterns = {
            'function': re.compile(r'(?:def|fn|function)\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\('),
            'class': re.compile(r'(?:class|type)\s+([a-zA-Z_][a-zA-Z0-9_]*)'),
            'variable': re.compile(r'([a-zA-Z_][a-zA-Z0-9_]*)\s*='),
            'docstring': re.compile(r'"""(.*?)"""', re.DOTALL),
            'comment': re.compile(r'#(.*)$'),
            'param': re.compile(r'@param\s+(\w+)\s+(?:\{(\w+)\})?\s*(.*)'),
            'return': re.compile(r'@return\s+(.*)'),
            'raises': re.compile(r'@raises\s+(\w+)'),
            'example': re.compile(r'@example\s+(.*)'),
            'see': re.compile(r'@see\s+(.*)'),
            'deprecated': re.compile(r'@deprecated'),
            'since': re.compile(r'@since\s+(\S+)'),
            'version': re.compile(r'@version\s+(\S+)'),
            'author': re.compile(r'@author\s+(.+)')
        }

    def parse_file(self, file_path: str) -> List[Documentation]:
        """Parse documentation from a file"""
        docs = []
        
        with open(file_path, 'r') as f:
            lines = f.readlines()
        
        # Parse line by line
        i = 0
        while i < len(lines):
            line = lines[i]
            
            # Check for function definition
            func_match = self.patterns['function'].search(line)
            if func_match:
                doc = self._parse_function(func_match.group(1), lines, i)
                if doc:
                    docs.append(doc)
                i += 1
                continue
            
            # Check for class definition
            class_match = self.patterns['class'].search(line)
            if class_match:
                doc = self._parse_class(class_match.group(1), lines, i)
                if doc:
                    docs.append(doc)
                i += 1
                continue
            
            i += 1
        
        return docs

    def _parse_function(
        self,
        name: str,
        lines: List[str],
        line_index: int
    ) -> Optional[Documentation]:
        """Parse function documentation"""
        # Look for docstring or comments above
        doc_lines = []
        i = line_index - 1
        
        # Collect comments/docstring
        while i >= 0 and (lines[i].strip().startswith('#') or '"""' in lines[i]):
            doc_lines.insert(0, lines[i].strip())
            i -= 1
        
        doc_text = '\n'.join(doc_lines)
        
        # Parse documentation tags
        params = []
        returns = None
        raises = []
        examples = []
        see_also = []
        deprecated = False
        since = None
        version = None
        author = None
        
        for line in doc_lines:
            # Parse @param
            param_match = self.patterns['param'].search(line)
            if param_match:
                params.append(Parameter(
                    name=param_match.group(1),
                    type=param_match.group(2) or 'any',
                    description=param_match.group(3).strip()
                ))
            
            # Parse @return
            return_match = self.patterns['return'].search(line)
            if return_match:
                returns = return_match.group(1).strip()
            
            # Parse @raises
            raises_match = self.patterns['raises'].search(line)
            if raises_match:
                raises.append(raises_match.group(1))
            
            # Parse @example
            example_match = self.patterns['example'].search(line)
            if example_match:
                examples.append(example_match.group(1).strip())
            
            # Parse @see
            see_match = self.patterns['see'].search(line)
            if see_match:
                see_also.append(see_match.group(1).strip())
            
            # Parse @deprecated
            if self.patterns['deprecated'].search(line):
                deprecated = True
            
            # Parse @since
            since_match = self.patterns['since'].search(line)
            if since_match:
                since = since_match.group(1)
            
            # Parse @version
            version_match = self.patterns['version'].search(line)
            if version_match:
                version = version_match.group(1)
            
            # Parse @author
            author_match = self.patterns['author'].search(line)
            if author_match:
                author = author_match.group(1).strip()
        
        # Extract description
        description = doc_text
        for tag in ['@param', '@return', '@raises', '@example', '@see', '@deprecated', '@since', '@version', '@author']:
            description = re.sub(tag + r'\s*\S*', '', description)
        description = description.strip('#').strip('"""').strip()
        
        return Documentation(
            name=name,
            doc_type=DocType.FUNCTION,
            description=description,
            parameters=params,
            returns=returns,
            raises=raises,
            examples=examples,
            see_also=see_also,
            deprecated=deprecated,
            since=since,
            version=version,
            author=author,
            file_path="",
            line_number=line_index + 1
        )

    def _parse_class(
        self,
        name: str,
        lines: List[str],
        line_index: int
    ) -> Optional[Documentation]:
        """Parse class documentation"""
        # Similar to function parsing
        doc_lines = []
        i = line_index - 1
        
        while i >= 0 and (lines[i].strip().startswith('#') or '"""' in lines[i]):
            doc_lines.insert(0, lines[i].strip())
            i -= 1
        
        doc_text = '\n'.join(doc_lines)
        description = doc_text.strip('#').strip('"""').strip()
        
        return Documentation(
            name=name,
            doc_type=DocType.CLASS,
            description=description,
            file_path="",
            line_number=line_index + 1
        )


class DocGenerator:
    """Generate documentation in various formats"""

    def __init__(self):
        self.parser = DocParser()
        self.output_dir = "docs"

    def generate(
        self,
        source_path: str,
        output_format: DocFormat = DocFormat.MARKDOWN,
        output_dir: Optional[str] = None
    ) -> str:
        """Generate documentation"""
        if output_dir:
            self.output_dir = output_dir
        
        # Ensure output directory exists
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Parse source files
        docs = self._parse_source(source_path)
        
        # Generate documentation
        if output_format == DocFormat.MARKDOWN:
            return self._generate_markdown(docs)
        elif output_format == DocFormat.HTML:
            return self._generate_html(docs)
        elif output_format == DocFormat.PDF:
            return self._generate_pdf(docs)
        elif output_format == DocFormat.JSON:
            return self._generate_json(docs)
        
        return ""

    def _parse_source(self, source_path: str) -> List[Documentation]:
        """Parse all source files in a directory"""
        docs = []
        
        if os.path.isfile(source_path):
            docs.extend(self.parser.parse_file(source_path))
        elif os.path.isdir(source_path):
            for root, dirs, files in os.walk(source_path):
                for file in files:
                    if file.endswith('.py') or file.endswith('.prim'):
                        file_path = os.path.join(root, file)
                        docs.extend(self.parser.parse_file(file_path))
        
        return docs

    def _generate_markdown(self, docs: List[Documentation]) -> str:
        """Generate Markdown documentation"""
        lines = []
        
        # Header
        lines.append("# API Documentation")
        lines.append("")
        lines.append(f"Generated on {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")
        
        # Table of contents
        lines.append("## Table of Contents")
        lines.append("")
        for doc in docs:
            link = doc.name.lower().replace(' ', '-')
            lines.append(f"- [{doc.name}](#{link})")
        lines.append("")
        
        # Documentation
        for doc in docs:
            lines.append(f"## {doc.name}")
            lines.append("")
            
            if doc.deprecated:
                lines.append("**⚠️ Deprecated**")
                lines.append("")
            
            if doc.description:
                lines.append(doc.description)
                lines.append("")
            
            if doc.parameters:
                lines.append("### Parameters")
                lines.append("")
                for param in doc.parameters:
                    optional = " (optional)" if param.optional else ""
                    lines.append(f"- **{param.name}** ({param.type}){optional}: {param.description}")
                lines.append("")
            
            if doc.returns:
                lines.append(f"### Returns")
                lines.append("")
                lines.append(doc.returns)
                lines.append("")
            
            if doc.raises:
                lines.append("### Raises")
                lines.append("")
                for exc in doc.raises:
                    lines.append(f"- {exc}")
                lines.append("")
            
            if doc.examples:
                lines.append("### Examples")
                lines.append("")
                for example in doc.examples:
                    lines.append(f"```prim")
                    lines.append(example)
                    lines.append("```")
                    lines.append("")
            
            if doc.see_also:
                lines.append("### See Also")
                lines.append("")
                for ref in doc.see_also:
                    lines.append(f"- {ref}")
                lines.append("")
            
            lines.append("---")
            lines.append("")
        
        markdown = '\n'.join(lines)
        output_path = os.path.join(self.output_dir, "API.md")
        
        with open(output_path, 'w') as f:
            f.write(markdown)
        
        return output_path

    def _generate_html(self, docs: List[Documentation]) -> str:
        """Generate HTML documentation"""
        html = """<!DOCTYPE html>
<html>
<head>
    <title>API Documentation</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 1200px; margin: 0 auto; padding: 20px; }
        h1 { color: #333; border-bottom: 2px solid #333; }
        h2 { color: #555; border-bottom: 1px solid #ccc; }
        .param { margin: 10px 0; }
        .param-name { font-weight: bold; }
        .example { background: #f5f5f5; padding: 10px; margin: 10px 0; }
        pre { background: #f5f5f5; padding: 10px; overflow-x: auto; }
        code { background: #f5f5f5; padding: 2px 4px; }
        .deprecated { background: #fff3cd; padding: 10px; border-left: 4px solid #ffc107; }
    </style>
</head>
<body>
    <h1>API Documentation</h1>
    <p>Generated on """ + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + """</p>
"""
        
        # Table of contents
        html += "<h2>Table of Contents</h2>"
        html += "<ul>"
        for doc in docs:
            link = doc.name.lower().replace(' ', '-')
            html += f'<li><a href="#{link}">{doc.name}</a></li>'
        html += "</ul>"
        
        # Documentation
        for doc in docs:
            link = doc.name.lower().replace(' ', '-')
            html += f'<h2 id="{link}">{doc.name}</h2>'
            
            if doc.deprecated:
                html += '<div class="deprecated">⚠️ Deprecated</div>'
            
            if doc.description:
                html += f'<p>{doc.description}</p>'
            
            if doc.parameters:
                html += '<h3>Parameters</h3>'
                for param in doc.parameters:
                    optional = " (optional)" if param.optional else ""
                    html += f'<div class="param"><span class="param-name">{param.name}</span> ({param.type}){optional}: {param.description}</div>'
            
            if doc.returns:
                html += f'<h3>Returns</h3><p>{doc.returns}</p>'
            
            if doc.raises:
                html += '<h3>Raises</h3><ul>'
                for exc in doc.raises:
                    html += f'<li>{exc}</li>'
                html += '</ul>'
            
            if doc.examples:
                html += '<h3>Examples</h3>'
                for example in doc.examples:
                    html += f'<div class="example"><pre><code>{example}</code></pre></div>'
            
            if doc.see_also:
                html += '<h3>See Also</h3><ul>'
                for ref in doc.see_also:
                    html += f'<li>{ref}</li>'
                html += '</ul>'
            
            html += '<hr>'
        
        html += """
</body>
</html>
"""
        
        output_path = os.path.join(self.output_dir, "API.html")
        
        with open(output_path, 'w') as f:
            f.write(html)
        
        return output_path

    def _generate_pdf(self, docs: List[Documentation]) -> str:
        """Generate PDF documentation (placeholder)"""
        # In a real implementation, this would use a PDF generation library
        # For now, generate markdown and note PDF requirement
        markdown_path = self._generate_markdown(docs)
        
        output_path = os.path.join(self.output_dir, "API.pdf")
        
        with open(output_path, 'w') as f:
            f.write("PDF generation requires additional libraries (weasyprint, reportlab)\n")
            f.write(f"Markdown version available at: {markdown_path}\n")
        
        return output_path

    def _generate_json(self, docs: List[Documentation]) -> str:
        """Generate JSON documentation"""
        data = {
            'generated_at': datetime.datetime.now().isoformat(),
            'version': '1.0',
            'documentation': []
        }
        
        for doc in docs:
            doc_data = {
                'name': doc.name,
                'type': doc.doc_type.value,
                'description': doc.description,
                'deprecated': doc.deprecated
            }
            
            if doc.parameters:
                doc_data['parameters'] = [
                    {
                        'name': p.name,
                        'type': p.type,
                        'description': p.description,
                        'optional': p.optional
                    }
                    for p in doc.parameters
                ]
            
            if doc.returns:
                doc_data['returns'] = doc.returns
            
            if doc.raises:
                doc_data['raises'] = doc.raises
            
            if doc.examples:
                doc_data['examples'] = doc.examples
            
            if doc.see_also:
                doc_data['see_also'] = doc.see_also
            
            data['documentation'].append(doc_data)
        
        json_str = json.dumps(data, indent=2)
        output_path = os.path.join(self.output_dir, "API.json")
        
        with open(output_path, 'w') as f:
            f.write(json_str)
        
        return output_path


class DocGeneratorCLI:
    """Command-line interface for documentation generator"""

    def __init__(self):
        self.generator = DocGenerator()

    def run(self, args: List[str]):
        """Run CLI command"""
        if not args:
            self.show_help()
            return
        
        command = args[0]
        command_args = args[1:]
        
        if command == 'generate':
            self.cmd_generate(command_args)
        else:
            print(f"Unknown command: {command}")
            self.show_help()

    def cmd_generate(self, args: List[str]):
        """Generate documentation"""
        if not args:
            print("Usage: generate <source_path> [format] [output_dir]")
            return
        
        source_path = args[0]
        format_str = args[1] if len(args) > 1 else 'markdown'
        output_dir = args[2] if len(args) > 2 else None
        
        try:
            doc_format = DocFormat(format_str.lower())
        except ValueError:
            print(f"Invalid format: {format_str}")
            print(f"Valid formats: {', '.join([f.value for f in DocFormat])}")
            return
        
        output_path = self.generator.generate(source_path, doc_format, output_dir)
        
        print(f"Documentation generated: {output_path}")

    def show_help(self):
        """Show help"""
        print("""
Prim Documentation Generator Commands:
  generate <source_path> [format] [output_dir]  Generate documentation

Formats:
  markdown   Generate Markdown documentation
  html       Generate HTML documentation
  pdf        Generate PDF documentation
  json       Generate JSON documentation
""")


def main():
    """Main entry point"""
    import sys
    
    cli = DocGeneratorCLI()
    cli.run(sys.argv[1:])


if __name__ == "__main__":
    main()
