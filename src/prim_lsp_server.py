"""
Prim Language Server Protocol (LSP) Server
Provides real-time syntax checking, intelligent code completion,
go-to-definition, find-references, rename refactoring, and hover documentation.
"""

import sys
import json
import os
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import re


class LSPErrorCode(Enum):
    """LSP error codes"""
    ParseError = -32700
    InvalidRequest = -32600
    MethodNotFound = -32601
    InvalidParams = -32602
    InternalError = -32603
    ServerNotInitialized = -32002
    UnknownErrorCode = -32001


class DiagnosticSeverity(Enum):
    """Diagnostic severity levels"""
    Error = 1
    Warning = 2
    Information = 3
    Hint = 4


@dataclass
class Position:
    """Position in a document"""
    line: int
    character: int


@dataclass
class Range:
    """Range in a document"""
    start: Position
    end: Position


@dataclass
class Location:
    """Location in a document"""
    uri: str
    range: Range


@dataclass
class Diagnostic:
    """Diagnostic information"""
    range: Range
    severity: Optional[int]
    code: Optional[str]
    source: str
    message: str
    relatedInformation: Optional[List[Dict]]


@dataclass
class CompletionItem:
    """Completion item"""
    label: str
    kind: int
    detail: Optional[str]
    documentation: Optional[str]
    sortText: Optional[str]
    insertText: Optional[str]


@dataclass
class Hover:
    """Hover information"""
    contents: str
    range: Optional[Range]


@dataclass
class TextEdit:
    """Text edit"""
    range: Range
    newText: str


@dataclass
class WorkspaceEdit:
    """Workspace edit"""
    changes: Optional[Dict[str, List[TextEdit]]]
    documentChanges: Optional[List[Dict]]


class PrimLSPServer:
    """LSP Server for Prim language"""

    def __init__(self):
        self.documents: Dict[str, str] = {}
        self.document_symbols: Dict[str, List[Dict]] = {}
        self.completion_items: Dict[str, List[CompletionItem]] = {}
        self.initialized = False
        
        # Keywords and builtins for completion
        self.keywords = ['if', 'else', 'elif', 'for', 'while', 'def', 'return', 'import', 'from', 'class', 'try', 'except', 'finally', 'with', 'as']
        self.builtins = ['print', 'len', 'map', 'filter', 'reduce', 'range', 'str', 'int', 'float', 'list', 'dict', 'set', 'abs', 'min', 'max', 'sum', 'all', 'any']
        
        # Import error reporter
        try:
            from prim_error_context import ErrorReporter
            self.error_reporter = ErrorReporter()
        except ImportError:
            self.error_reporter = None

    def handle_request(self, request: Dict) -> Dict:
        """Handle incoming LSP request"""
        method = request.get('method')
        params = request.get('params', {})
        request_id = request.get('id')
        
        result = None
        error = None
        
        try:
            if method == 'initialize':
                result = self.handle_initialize(params)
            elif method == 'initialized':
                self.initialized = True
                result = {}
            elif method == 'shutdown':
                result = {}
            elif method == 'exit':
                sys.exit(0)
            elif method == 'textDocument/didOpen':
                self.handle_did_open(params)
            elif method == 'textDocument/didChange':
                self.handle_did_change(params)
            elif method == 'textDocument/didClose':
                self.handle_did_close(params)
            elif method == 'textDocument/didSave':
                self.handle_did_save(params)
            elif method == 'textDocument/completion':
                result = self.handle_completion(params)
            elif method == 'textDocument/hover':
                result = self.handle_hover(params)
            elif method == 'textDocument/definition':
                result = self.handle_definition(params)
            elif method == 'textDocument/references':
                result = self.handle_references(params)
            elif method == 'textDocument/rename':
                result = self.handle_rename(params)
            elif method == 'textDocument/codeAction':
                result = self.handle_code_action(params)
            elif method == 'textDocument/documentSymbol':
                result = self.handle_document_symbol(params)
            elif method == 'textDocument/diagnostics':
                result = self.handle_diagnostics(params)
            else:
                error = {
                    'code': LSPErrorCode.MethodNotFound.value,
                    'message': f'Method not found: {method}'
                }
        except Exception as e:
            error = {
                'code': LSPErrorCode.InternalError.value,
                'message': str(e)
            }
        
        response = {
            'jsonrpc': '2.0',
            'id': request_id
        }
        
        if error:
            response['error'] = error
        elif result is not None:
            response['result'] = result
        
        return response

    def handle_initialize(self, params: Dict) -> Dict:
        """Handle initialize request"""
        return {
            'capabilities': {
                'textDocumentSync': 2,  # Full sync
                'completionProvider': {
                    'resolveProvider': True,
                    'triggerCharacters': ['.', ':', '#']
                },
                'hoverProvider': True,
                'definitionProvider': True,
                'referencesProvider': True,
                'renameProvider': True,
                'codeActionProvider': True,
                'documentSymbolProvider': True,
                'diagnosticProvider': True
            },
            'serverInfo': {
                'name': 'prim-lsp',
                'version': '1.1.0'
            }
        }

    def handle_did_open(self, params: Dict):
        """Handle document open"""
        doc = params['textDocument']
        uri = doc['uri']
        text = doc['text']
        
        self.documents[uri] = text
        self._parse_document(uri, text)

    def handle_did_change(self, params: Dict):
        """Handle document change"""
        doc = params['textDocument']
        uri = doc['uri']
        changes = params['contentChanges']
        
        if uri in self.documents:
            for change in changes:
                if 'range' in change:
                    # Handle incremental change
                    self._apply_change(uri, change['range'], change['text'])
                else:
                    # Full document change
                    self.documents[uri] = change['text']
            
            self._parse_document(uri, self.documents[uri])

    def handle_did_close(self, params: Dict):
        """Handle document close"""
        doc = params['textDocument']
        uri = doc['uri']
        
        if uri in self.documents:
            del self.documents[uri]
        if uri in self.document_symbols:
            del self.document_symbols[uri]

    def handle_did_save(self, params: Dict):
        """Handle document save"""
        # Could trigger additional analysis here
        pass

    def handle_completion(self, params: Dict) -> Dict:
        """Handle completion request"""
        doc = params['textDocument']
        uri = doc['uri']
        position = params['position']
        
        if uri not in self.documents:
            return {'isIncomplete': False, 'items': []}
        
        text = self.documents[uri]
        line = text.split('\n')[position['line']]
        
        # Get word before cursor
        word_start = position['character'] - 1
        while word_start >= 0 and (line[word_start].isalnum() or line[word_start] in '_'):
            word_start -= 1
        word_start += 1
        
        prefix = line[word_start:position['character']]
        
        # Build completion items
        items = []
        
        # Keywords
        for keyword in self.keywords:
            if keyword.startswith(prefix):
                items.append(CompletionItem(
                    label=keyword,
                    kind=14,  # Keyword
                    detail='keyword',
                    documentation=f'{keyword} keyword',
                    sortText=keyword
                ))
        
        # Built-in functions
        for builtin in self.builtins:
            if builtin.startswith(prefix):
                items.append(CompletionItem(
                    label=builtin,
                    kind=3,  # Function
                    detail='builtin function',
                    documentation=f'{builtin}() built-in function',
                    sortText=builtin
                ))
        
        # Document symbols
        if uri in self.document_symbols:
            for symbol in self.document_symbols[uri]:
                name = symbol.get('name', '')
                if name.startswith(prefix):
                    kind = symbol.get('kind', 12)
                    items.append(CompletionItem(
                        label=name,
                        kind=kind,
                        detail=symbol.get('detail', ''),
                        documentation=symbol.get('documentation', ''),
                        sortText=name
                    ))
        
        return {
            'isIncomplete': False,
            'items': [asdict(item) for item in items]
        }

    def handle_hover(self, params: Dict) -> Optional[Dict]:
        """Handle hover request"""
        doc = params['textDocument']
        uri = doc['uri']
        position = params['position']
        
        if uri not in self.documents:
            return None
        
        text = self.documents[uri]
        line = text.split('\n')[position['line']]
        
        # Get word at position
        word_start = position['character'] - 1
        while word_start >= 0 and (line[word_start].isalnum() or line[word_start] in '_'):
            word_start -= 1
        word_start += 1
        
        word_end = position['character']
        while word_end < len(line) and (line[word_end].isalnum() or line[word_end] in '_'):
            word_end += 1
        
        word = line[word_start:word_end]
        
        # Get hover text
        hover_text = None
        
        if word in self.keywords:
            hover_text = f'**{word}** - Keyword'
        elif word in self.builtins:
            hover_text = f'**{word}** - Built-in function'
        elif uri in self.document_symbols:
            for symbol in self.document_symbols[uri]:
                if symbol.get('name') == word:
                    hover_text = symbol.get('documentation', '')
                    break
        
        if hover_text:
            return {
                'contents': hover_text,
                'range': {
                    'start': {'line': position['line'], 'character': word_start},
                    'end': {'line': position['line'], 'character': word_end}
                }
            }
        
        return None

    def handle_definition(self, params: Dict) -> Optional[List[Location]]:
        """Handle go-to-definition request"""
        doc = params['textDocument']
        uri = doc['uri']
        position = params['position']
        
        if uri not in self.documents:
            return None
        
        text = self.documents[uri]
        line = text.split('\n')[position['line']]
        
        # Get word at position
        word_start = position['character'] - 1
        while word_start >= 0 and (line[word_start].isalnum() or line[word_start] in '_'):
            word_start -= 1
        word_start += 1
        
        word_end = position['character']
        while word_end < len(line) and (line[word_end].isalnum() or line[word_end] in '_'):
            word_end += 1
        
        word = line[word_start:word_end]
        
        # Find definition
        if uri in self.document_symbols:
            for symbol in self.document_symbols[uri]:
                if symbol.get('name') == word:
                    location = symbol.get('location')
                    if location:
                        return [location]
        
        return None

    def handle_references(self, params: Dict) -> Optional[List[Location]]:
        """Handle find-references request"""
        doc = params['textDocument']
        uri = doc['uri']
        position = params['position']
        
        if uri not in self.documents:
            return None
        
        text = self.documents[uri]
        line = text.split('\n')[position['line']]
        
        # Get word at position
        word_start = position['character'] - 1
        while word_start >= 0 and (line[word_start].isalnum() or line[word_start] in '_'):
            word_start -= 1
        word_start += 1
        
        word_end = position['character']
        while word_end < len(line) and (line[word_end].isalnum() or line[word_end] in '_'):
            word_end += 1
        
        word = line[word_start:word_end]
        
        # Find all references
        references = []
        lines = text.split('\n')
        
        for line_num, line_text in enumerate(lines):
            if word in line_text:
                # Find all occurrences
                start = 0
                while True:
                    pos = line_text.find(word, start)
                    if pos == -1:
                        break
                    
                    references.append(Location(
                        uri=uri,
                        range=Range(
                            start=Position(line=line_num, character=pos),
                            end=Position(line=line_num, character=pos + len(word))
                        )
                    ))
                    start = pos + 1
        
        return references if references else None

    def handle_rename(self, params: Dict) -> Optional[WorkspaceEdit]:
        """Handle rename request"""
        doc = params['textDocument']
        uri = doc['uri']
        position = params['position']
        new_name = params['newName']
        
        if uri not in self.documents:
            return None
        
        text = self.documents[uri]
        line = text.split('\n')[position['line']]
        
        # Get word at position
        word_start = position['character'] - 1
        while word_start >= 0 and (line[word_start].isalnum() or line[word_start] in '_'):
            word_start -= 1
        word_start += 1
        
        word_end = position['character']
        while word_end < len(line) and (line[word_end].isalnum() or line[word_end] in '_'):
            word_end += 1
        
        old_name = line[word_start:word_end]
        
        # Find all occurrences and create edits
        edits = []
        lines = text.split('\n')
        
        for line_num, line_text in enumerate(lines):
            start = 0
            while True:
                pos = line_text.find(old_name, start)
                if pos == -1:
                    break
                
                # Check if it's a whole word
                if (pos == 0 or not line_text[pos - 1].isalnum()) and \
                   (pos + len(old_name) == len(line_text) or not line_text[pos + len(old_name)].isalnum()):
                    
                    edits.append(TextEdit(
                        range=Range(
                            start=Position(line=line_num, character=pos),
                            end=Position(line=line_num, character=pos + len(old_name))
                        ),
                        newText=new_name
                    ))
                
                start = pos + 1
        
        if edits:
            return WorkspaceEdit(
                changes={uri: [asdict(edit) for edit in edits]}
            )
        
        return None

    def handle_code_action(self, params: Dict) -> List[Dict]:
        """Handle code action request"""
        actions = []
        
        # Add quick fixes for common issues
        actions.append({
            'title': 'Add missing semicolon',
            'kind': 'quickfix',
            'edit': {}
        })
        
        actions.append({
            'title': 'Format document',
            'kind': 'source.formatDocument',
            'edit': {}
        })
        
        return actions

    def handle_document_symbol(self, params: Dict) -> List[Dict]:
        """Handle document symbol request"""
        doc = params['textDocument']
        uri = doc['uri']
        
        if uri not in self.document_symbols:
            return []
        
        return self.document_symbols[uri]

    def handle_diagnostics(self, params: Dict) -> List[Dict]:
        """Handle diagnostics request"""
        doc = params['textDocument']
        uri = doc['uri']
        
        if uri not in self.documents or not self.error_reporter:
            return []
        
        text = self.documents[uri]
        lines = text.split('\n')
        
        diagnostics = []
        
        # Check for common errors
        for line_num, line in enumerate(lines):
            # Check for undefined variables
            if re.search(r'\b[a-zA-Z_][a-zA-Z0-9_]*\s*=', line):
                # Variable assignment
                match = re.search(r'([a-zA-Z_][a-zA-Z0-9_]*)\s*=', line)
                if match:
                    var_name = match.group(1)
                    # Check if variable is used before definition
                    # This is simplified - actual implementation would be more sophisticated
                    pass
            
            # Check for syntax issues
            if line.count('{') != line.count('}'):
                diagnostics.append({
                    'range': {
                        'start': {'line': line_num, 'character': 0},
                        'end': {'line': line_num, 'character': len(line)}
                    },
                    'severity': DiagnosticSeverity.Error.value,
                    'source': 'prim',
                    'message': 'Unmatched braces'
                })
        
        return diagnostics

    def _apply_change(self, uri: str, range_dict: Dict, text: str):
        """Apply a text change to a document"""
        if uri not in self.documents:
            return
        
        document = self.documents[uri]
        lines = document.split('\n')
        
        start_line = range_dict['start']['line']
        start_char = range_dict['start']['character']
        end_line = range_dict['end']['line']
        end_char = range_dict['end']['character']
        
        # Get the text to replace
        if start_line == end_line:
            # Single line change
            line = lines[start_line]
            lines[start_line] = line[:start_char] + text + line[end_char:]
        else:
            # Multi-line change
            first_line = lines[start_line]
            last_line = lines[end_line]
            lines[start_line:end_line + 1] = [first_line[:start_char] + text + last_line[end_char:]]
        
        self.documents[uri] = '\n'.join(lines)

    def _parse_document(self, uri: str, text: str):
        """Parse document for symbols"""
        symbols = []
        lines = text.split('\n')
        
        # Simple parsing for function and variable definitions
        for line_num, line in enumerate(lines):
            # Function definitions
            match = re.match(r'\s*(?:def|fn|function)\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(', line)
            if match:
                name = match.group(1)
                symbols.append({
                    'name': name,
                    'kind': 12,  # Function
                    'detail': 'function',
                    'documentation': f'Function: {name}',
                    'location': {
                        'uri': uri,
                        'range': {
                            'start': {'line': line_num, 'character': 0},
                            'end': {'line': line_num, 'character': len(line)}
                        }
                    }
                })
            
            # Variable definitions
            match = re.match(r'\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*=', line)
            if match:
                name = match.group(1)
                symbols.append({
                    'name': name,
                    'kind': 13,  # Variable
                    'detail': 'variable',
                    'documentation': f'Variable: {name}',
                    'location': {
                        'uri': uri,
                        'range': {
                            'start': {'line': line_num, 'character': 0},
                            'end': {'line': line_num, 'character': len(line)}
                        }
                    }
                })
        
        self.document_symbols[uri] = symbols

    def run(self):
        """Run the LSP server"""
        try:
            for line in sys.stdin:
                try:
                    request = json.loads(line)
                    response = self.handle_request(request)
                    print(json.dumps(response), flush=True)
                except json.JSONDecodeError:
                    continue
        except KeyboardInterrupt:
            pass


def main():
    """Main entry point"""
    server = PrimLSPServer()
    server.run()


if __name__ == "__main__":
    main()
