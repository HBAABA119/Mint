"""
Prim Language Slim Mode Parser

This parser handles the indentation-based syntax similar to Python.
"""

import re
from typing import List, Optional
from prim_interpreter import AstNode, NodeType


class Token:
    def __init__(self, type_: str, value: str, line: int, column: int):
        self.type = type_
        self.value = value
        self.line = line
        self.column = column

    def __repr__(self):
        return f"Token({self.type}, {self.value}, {self.line}:{self.column})"


class SlimLexer:
    def __init__(self, text: str):
        self.text = text
        self.pos = 0
        self.line = 1
        self.column = 1
        self.tokens = []

    def tokenize(self) -> List[Token]:
        while self.pos < len(self.text):
            char = self.text[self.pos]

            # Skip whitespace except newlines and track indentation
            if char.isspace() and char != '\n':
                self._skip_whitespace()
                continue

            # Handle newlines and indentation
            if char == '\n':
                self._handle_newline()
                continue

            # Identify token type
            if char.isalpha() or char == '_':
                self._read_identifier()
            elif char.isdigit():
                self._read_number()
            elif char in ('"', "'"):
                self._read_string(char)
            elif char in '+-*/%=!<>&|':
                self._read_operator()
            elif char in '{}()[],;':
                self._read_punctuation()
            elif char == '#':
                self._read_comment()
            else:
                raise SyntaxError(f"Unexpected character '{char}' at {self.line}:{self.column}")

        return self.tokens

    def _skip_whitespace(self):
        while self.pos < len(self.text) and self.text[self.pos].isspace() and self.text[self.pos] != '\n':
            self.pos += 1
            self.column += 1

    def _handle_newline(self):
        self.tokens.append(Token('NEWLINE', '\n', self.line, self.column))
        self.pos += 1
        self.line += 1
        self.column = 1

    def _read_identifier(self):
        start_pos = self.pos
        start_col = self.column

        while self.pos < len(self.text) and (self.text[self.pos].isalnum() or self.text[self.pos] == '_'):
            self.pos += 1
            self.column += 1

        identifier = self.text[start_pos:self.pos]
        
        # Check if it's a keyword
        if identifier in ['fn', 'if', 'else', 'elif', 'while', 'for', 'return', 'true', 'false', 'null']:
            token_type = identifier.upper()
        else:
            token_type = 'IDENTIFIER'
            
        self.tokens.append(Token(token_type, identifier, self.line, start_col))

    def _read_number(self):
        start_pos = self.pos
        start_col = self.column

        while self.pos < len(self.text) and (self.text[self.pos].isdigit() or self.text[self.pos] == '.'):
            self.pos += 1
            self.column += 1

        number_str = self.text[start_pos:self.pos]
        self.tokens.append(Token('NUMBER', number_str, self.line, start_col))

    def _read_string(self, quote_char: str):
        start_pos = self.pos
        start_col = self.column
        self.pos += 1  # Skip opening quote
        self.column += 1

        value = ""
        while self.pos < len(self.text) and self.text[self.pos] != quote_char:
            if self.text[self.pos] == '\n':
                raise SyntaxError(f"Unterminated string at {self.line}:{self.column}")
            if self.text[self.pos] == '\\':
                # Handle escape sequences
                self.pos += 1
                self.column += 1
                if self.pos >= len(self.text):
                    raise SyntaxError(f"Unterminated string at {self.line}:{self.column}")
                escaped_char = self.text[self.pos]
                if escaped_char == 'n':
                    value += '\n'
                elif escaped_char == 't':
                    value += '\t'
                elif escaped_char in ['\\', '"', "'"]:
                    value += escaped_char
                else:
                    value += '\\' + escaped_char
            else:
                value += self.text[self.pos]
            self.pos += 1
            self.column += 1

        if self.pos >= len(self.text) or self.text[self.pos] != quote_char:
            raise SyntaxError(f"Unterminated string at {self.line}:{self.column}")

        self.pos += 1  # Skip closing quote
        self.column += 1
        self.tokens.append(Token('STRING', value, self.line, start_col))

    def _read_operator(self):
        start_col = self.column
        op = self.text[self.pos]
        self.pos += 1
        self.column += 1

        # Check for two-character operators
        if self.pos < len(self.text):
            two_char_op = op + self.text[self.pos]
            if two_char_op in ['==', '!=', '<=', '>=', '&&', '||', '->', '|>']:
                op = two_char_op
                self.pos += 1
                self.column += 1

        self.tokens.append(Token('OPERATOR', op, self.line, start_col))

    def _read_punctuation(self):
        char = self.text[self.pos]
        self.tokens.append(Token('PUNCTUATION', char, self.line, self.column))
        self.pos += 1
        self.column += 1

    def _read_comment(self):
        # Skip until end of line
        while self.pos < len(self.text) and self.text[self.pos] != '\n':
            self.pos += 1
            self.column += 1


class SlimParser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0
        self.current_token = self.tokens[0] if tokens else None

    def _advance(self):
        self.pos += 1
        if self.pos < len(self.tokens):
            self.current_token = self.tokens[self.pos]
        else:
            self.current_token = None

    def _match(self, expected_type: str, expected_value: Optional[str] = None):
        if not self.current_token:
            return False
        if self.current_token.type != expected_type:
            return False
        if expected_value is not None and self.current_token.value != expected_value:
            return False
        return True

    def _consume(self, expected_type: str, expected_value: Optional[str] = None):
        if not self._match(expected_type, expected_value):
            raise SyntaxError(
                f"Expected {expected_type}{'=' + expected_value if expected_value else ''}, "
                f"got {self.current_token.type}='{self.current_token.value}' at {self.current_token.line}:{self.current_token.column}"
            )
        token = self.current_token
        self._advance()
        return token

    def parse_program(self):
        statements = []
        while self.current_token and self.current_token.type != 'EOF':
            if self.current_token.type == 'NEWLINE':
                self._advance()
                continue
            stmt = self.parse_statement()
            if stmt:
                statements.append(stmt)
        return AstNode(NodeType.BLOCK_STATEMENT, statements=statements)

    def parse_statement(self):
        if self._match('IDENTIFIER') and self.pos + 1 < len(self.tokens) and self.tokens[self.pos + 1].value == '=':
            return self.parse_assignment()
        elif self._match('FN'):
            return self.parse_function_definition()
        elif self._match('IF'):
            return self.parse_if_statement()
        elif self._match('WHILE'):
            return self.parse_while_loop()
        elif self._match('RETURN'):
            return self.parse_return_statement()
        else:
            # Assume it's an expression statement
            expr = self.parse_expression()
            if expr:
                return AstNode(NodeType.EXPRESSION_STATEMENT, expression=expr)
        return None

    def parse_assignment(self):
        # Parse: identifier = expression
        var_name = self._consume('IDENTIFIER').value
        self._consume('OPERATOR', '=')
        value_expr = self.parse_expression()
        return AstNode(NodeType.ASSIGNMENT, variable=var_name, value=value_expr, mutable=True)

    def parse_function_definition(self):
        self._consume('FN')
        name = self._consume('IDENTIFIER').value
        self._consume('PUNCTUATION', '(')
        
        params = []
        if not self._match('PUNCTUATION', ')'):
            params.append(self._consume('IDENTIFIER').value)
            while self._match('PUNCTUATION', ','):
                self._advance()
                params.append(self._consume('IDENTIFIER').value)
        
        self._consume('PUNCTUATION', ')')
        self._consume('PUNCTUATION', ':')
        
        # In slim mode, function body is indented
        body = self.parse_block()
        return AstNode(NodeType.LAMBDA, name=name, parameters=params, body=body)

    def parse_if_statement(self):
        self._consume('IF')
        condition = self.parse_expression()
        self._consume('PUNCTUATION', ':')
        
        consequent = self.parse_block()
        alternate = None
        
        if self._match('IDENTIFIER', 'else'):
            self._advance()
            self._consume('PUNCTUATION', ':')
            alternate = self.parse_block()
        
        return AstNode(NodeType.IF_STATEMENT, condition=condition, consequent=consequent, alternate=alternate)

    def parse_while_loop(self):
        self._consume('WHILE')
        condition = self.parse_expression()
        self._consume('PUNCTUATION', ':')
        
        body = self.parse_block()
        return AstNode(NodeType.WHILE_LOOP, condition=condition, body=body)

    def parse_return_statement(self):
        self._consume('RETURN')
        value = self.parse_expression() if self.current_token and not self._match('NEWLINE') else None
        return AstNode(NodeType.RETURN_STATEMENT, value=value)

    def parse_block(self):
        # In slim mode, blocks are defined by indentation
        statements = []
        while self.current_token and not self._match('EOF'):
            if self.current_token.type == 'NEWLINE':
                self._advance()
                continue
            # For simplicity in this prototype, we'll assume the block continues until
            # we encounter a token at the same indentation level or EOF
            stmt = self.parse_statement()
            if stmt:
                statements.append(stmt)
            # Simplified: just parse one statement for now
            break
        return AstNode(NodeType.BLOCK_STATEMENT, statements=statements)

    def parse_expression(self):
        return self.parse_logical_or()

    def parse_logical_or(self):
        left = self.parse_logical_and()
        while self._match('OPERATOR', '||'):
            self._advance()
            right = self.parse_logical_and()
            left = AstNode(NodeType.BINARY_OPERATION, operator='||', left=left, right=right)
        return left

    def parse_logical_and(self):
        left = self.parse_equality()
        while self._match('OPERATOR', '&&'):
            self._advance()
            right = self.parse_equality()
            left = AstNode(NodeType.BINARY_OPERATION, operator='&&', left=left, right=right)
        return left

    def parse_equality(self):
        left = self.parse_comparison()
        while self._match('OPERATOR') and self.current_token.value in ['==', '!=']:
            op = self._consume('OPERATOR').value
            right = self.parse_comparison()
            left = AstNode(NodeType.BINARY_OPERATION, operator=op, left=left, right=right)
        return left

    def parse_comparison(self):
        left = self.parse_addition()
        while self._match('OPERATOR') and self.current_token.value in ['<', '>', '<=', '>=']:
            op = self._consume('OPERATOR').value
            right = self.parse_addition()
            left = AstNode(NodeType.BINARY_OPERATION, operator=op, left=left, right=right)
        return left

    def parse_addition(self):
        left = self.parse_multiplication()
        while self._match('OPERATOR') and self.current_token.value in ['+', '-']:
            op = self._consume('OPERATOR').value
            right = self.parse_multiplication()
            left = AstNode(NodeType.BINARY_OPERATION, operator=op, left=left, right=right)
        return left

    def parse_multiplication(self):
        left = self.parse_unary()
        while self._match('OPERATOR') and self.current_token.value in ['*', '/', '%']:
            op = self._consume('OPERATOR').value
            right = self.parse_unary()
            left = AstNode(NodeType.BINARY_OPERATION, operator=op, left=left, right=right)
        return left

    def parse_unary(self):
        if self._match('OPERATOR') and self.current_token.value in ['!', '-', '+']:
            op = self._consume('OPERATOR').value
            operand = self.parse_unary()
            return AstNode(NodeType.UNARY_OPERATION, operator=op, operand=operand)
        return self.parse_primary()

    def parse_primary(self):
        if self._match('NUMBER'):
            value = float(self._consume('NUMBER').value)
            return AstNode(NodeType.NUMBER_LITERAL, value=value)
        elif self._match('STRING'):
            value = self._consume('STRING').value
            return AstNode(NodeType.STRING_LITERAL, value=value)
        elif self._match('IDENTIFIER', 'true'):
            self._consume('IDENTIFIER', 'true')
            return AstNode(NodeType.BOOLEAN_LITERAL, value=True)
        elif self._match('IDENTIFIER', 'false'):
            self._consume('IDENTIFIER', 'false')
            return AstNode(NodeType.BOOLEAN_LITERAL, value=False)
        elif self._match('IDENTIFIER', 'null'):
            self._consume('IDENTIFIER', 'null')
            return AstNode(NodeType.NULL_LITERAL, value=None)
        elif self._match('IDENTIFIER'):
            name = self._consume('IDENTIFIER').value
            # Check if it's a function call
            if self._match('PUNCTUATION', '('):
                self._consume('PUNCTUATION', '(')
                args = []
                if not self._match('PUNCTUATION', ')'):
                    args.append(self.parse_expression())
                    while self._match('PUNCTUATION', ','):
                        self._advance()  # consume comma
                        args.append(self.parse_expression())
                self._consume('PUNCTUATION', ')')
                callee = AstNode(NodeType.VARIABLE_ACCESS, name=name)
                return AstNode(NodeType.FUNCTION_CALL, callee=callee, arguments=args)
            return AstNode(NodeType.VARIABLE_ACCESS, name=name)
        elif self._match('PUNCTUATION', '('):
            self._consume('PUNCTUATION', '(')
            expr = self.parse_expression()
            self._consume('PUNCTUATION', ')')
            return expr
        else:
            raise SyntaxError(f"Unexpected token: {self.current_token}")


def parse_slim_code(code: str):
    """Parse slim mode code and return AST."""
    lexer = SlimLexer(code)
    tokens = lexer.tokenize()
    # Add EOF token
    if tokens:
        last_token = tokens[-1]
        tokens.append(Token('EOF', '', last_token.line, last_token.column))
    else:
        tokens.append(Token('EOF', '', 1, 1))
    
    parser = SlimParser(tokens)
    return parser.parse_program()


# Test the parser with a simple example
if __name__ == "__main__":
    test_code = '''
x = 42
y = 58
result = x + y
print(result)
'''
    
    try:
        ast = parse_slim_code(test_code)
        print("Parsed AST:")
        print(ast)
        print("\nStatements:")
        for i, stmt in enumerate(ast.properties['statements']):
            print(f"{i}: {stmt}")
    except Exception as e:
        print(f"Error parsing code: {e}")
        import traceback
        traceback.print_exc()