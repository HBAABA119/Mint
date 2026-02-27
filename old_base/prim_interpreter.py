"""
Prim Language Prototype Interpreter

This is a basic prototype to demonstrate the multi-syntax concept of Prim.
Currently implements the core interpreter with support for basic operations.
"""

from enum import Enum
from typing import Any, Dict, List, Union, Optional, Callable
import re


class NodeType(Enum):
    NUMBER_LITERAL = "NumberLiteral"
    STRING_LITERAL = "StringLiteral"
    BOOLEAN_LITERAL = "BooleanLiteral"
    NULL_LITERAL = "NullLiteral"
    LIST_LITERAL = "ListLiteral"
    DICT_LITERAL = "DictLiteral"
    VARIABLE_ACCESS = "VariableAccess"
    ASSIGNMENT = "Assignment"
    BINARY_OPERATION = "BinaryOperation"
    UNARY_OPERATION = "UnaryOperation"
    FUNCTION_CALL = "FunctionCall"
    LAMBDA = "Lambda"
    EXPRESSION_STATEMENT = "ExpressionStatement"
    IF_STATEMENT = "IfStatement"
    WHILE_LOOP = "WhileLoop"
    FOR_LOOP = "ForLoop"
    RETURN_STATEMENT = "ReturnStatement"
    BLOCK_STATEMENT = "BlockStatement"


class AstNode:
    def __init__(self, node_type: NodeType, **kwargs):
        self.type = node_type
        self.properties = kwargs

    def __repr__(self):
        return f"AstNode({self.type.value}, {self.properties})"


class RuntimeValue:
    def __init__(self, value: Any):
        self.value = value

    def __repr__(self):
        return repr(self.value)


class RuntimeEnvironment:
    def __init__(self, parent=None):
        self.variables = {}
        self.parent = parent

    def define(self, name: str, value: RuntimeValue):
        self.variables[name] = value

    def assign(self, name: str, value: RuntimeValue):
        if name in self.variables:
            self.variables[name] = value
        elif self.parent:
            self.parent.assign(name, value)
        else:
            raise NameError(f"Undefined variable: {name}")

    def lookup(self, name: str) -> RuntimeValue:
        if name in self.variables:
            return self.variables[name]
        elif self.parent:
            return self.parent.lookup(name)
        else:
            raise NameError(f"Undefined variable: {name}")


class PrimInterpreter:
    def __init__(self):
        self.global_env = RuntimeEnvironment()
        self._setup_builtins()

    def _setup_builtins(self):
        """Setup built-in functions."""
        self.global_env.define("print", RuntimeValue(self._builtin_print))
        self.global_env.define("len", RuntimeValue(self._builtin_len))
        self.global_env.define("str", RuntimeValue(self._builtin_str))
        self.global_env.define("num", RuntimeValue(self._builtin_num))
        self.global_env.define("bool", RuntimeValue(self._builtin_bool))

    def _builtin_print(self, *values):
        output_values = []
        for val in values:
            if isinstance(val, RuntimeValue):
                output_values.append(val.value)
            else:
                # For direct values (when called from standard library functions)
                output_values.append(val)
        print(*output_values)
        return RuntimeValue(None)

    def _builtin_len(self, container):
        if isinstance(container.value, (list, str)):
            return RuntimeValue(len(container.value))
        elif isinstance(container.value, dict):
            return RuntimeValue(len(container.value))
        else:
            raise TypeError(f"len() argument must be a list, string, or dict, got {type(container.value)}")

    def _builtin_str(self, value):
        return RuntimeValue(str(value.value if isinstance(value, RuntimeValue) else value))

    def _builtin_num(self, value):
        val = value.value if isinstance(value, RuntimeValue) else value
        try:
            return RuntimeValue(float(val))
        except ValueError:
            raise TypeError(f"Cannot convert {val} to number")

    def _builtin_bool(self, value):
        val = value.value if isinstance(value, RuntimeValue) else value
        return RuntimeValue(bool(val))

    def evaluate(self, node: AstNode, env: RuntimeEnvironment):
        if node.type == NodeType.NUMBER_LITERAL:
            return RuntimeValue(node.properties['value'])
        elif node.type == NodeType.STRING_LITERAL:
            return RuntimeValue(node.properties['value'])
        elif node.type == NodeType.BOOLEAN_LITERAL:
            return RuntimeValue(node.properties['value'])
        elif node.type == NodeType.NULL_LITERAL:
            return RuntimeValue(None)
        elif node.type == NodeType.LIST_LITERAL:
            elements = [self.evaluate(elem, env) for elem in node.properties['elements']]
            return RuntimeValue([elem.value for elem in elements])
        elif node.type == NodeType.DICT_LITERAL:
            pairs = node.properties['pairs']
            result_dict = {}
            for pair in pairs:
                key_node, value_node = pair['key'], pair['value']
                key_val = self.evaluate(key_node, env).value
                value_val = self.evaluate(value_node, env).value
                result_dict[key_val] = value_val
            return RuntimeValue(result_dict)
        elif node.type == NodeType.VARIABLE_ACCESS:
            var_name = node.properties['name']
            return env.lookup(var_name)
        elif node.type == NodeType.ASSIGNMENT:
            var_name = node.properties['variable']
            value = self.evaluate(node.properties['value'], env)
            # Check if it's a mutable assignment
            if node.properties.get('mutable', False):
                env.define(var_name, value)
            else:
                env.define(var_name, value)
            return value
        elif node.type == NodeType.BINARY_OPERATION:
            left_val = self.evaluate(node.properties['left'], env).value
            right_val = self.evaluate(node.properties['right'], env).value
            op = node.properties['operator']

            if op == '+':
                return RuntimeValue(left_val + right_val)
            elif op == '-':
                return RuntimeValue(left_val - right_val)
            elif op == '*':
                return RuntimeValue(left_val * right_val)
            elif op == '/':
                return RuntimeValue(left_val / right_val)
            elif op == '%':
                return RuntimeValue(left_val % right_val)
            elif op == '==':
                return RuntimeValue(left_val == right_val)
            elif op == '!=':
                return RuntimeValue(left_val != right_val)
            elif op == '<':
                return RuntimeValue(left_val < right_val)
            elif op == '>':
                return RuntimeValue(left_val > right_val)
            elif op == '<=':
                return RuntimeValue(left_val <= right_val)
            elif op == '>=':
                return RuntimeValue(left_val >= right_val)
            elif op == '&&':
                return RuntimeValue(bool(left_val and right_val))
            elif op == '||':
                return RuntimeValue(bool(left_val or right_val))
            else:
                raise ValueError(f"Unknown binary operator: {op}")
        elif node.type == NodeType.UNARY_OPERATION:
            operand_val = self.evaluate(node.properties['operand'], env).value
            op = node.properties['operator']

            if op == '!':
                return RuntimeValue(not operand_val)
            elif op == '-':
                return RuntimeValue(-operand_val)
            elif op == '+':
                return RuntimeValue(+operand_val)
            else:
                raise ValueError(f"Unknown unary operator: {op}")
        elif node.type == NodeType.FUNCTION_CALL:
            fn_node = node.properties['callee']
            fn_val = self.evaluate(fn_node, env)
                            
            # fn_val might be a RuntimeValue containing the function or the function directly
            if isinstance(fn_val, RuntimeValue):
                # fn_val is a RuntimeValue containing the actual function
                actual_fn = fn_val.value
            else:
                # fn_val is the function directly
                actual_fn = fn_val
                            
            if callable(actual_fn):
                args = []
                for arg_node in node.properties['arguments']:
                    arg_val = self.evaluate(arg_node, env)
                    args.append(arg_val)
                            
                # Determine if this is a standard library function (takes interpreter as first arg)
                # For this, we'll use a different approach since we can't easily check the signature at runtime
                # Standard library functions have a specific pattern: they accept interpreter as first parameter
                # We'll try calling with interpreter first, and if it fails, call without
                try:
                    import inspect
                    sig = inspect.signature(actual_fn)
                    # If the function accepts 'interpreter' as first parameter, it's a standard library function
                    params = list(sig.parameters.keys())
                    if len(params) > 0 and params[0] in ['interpreter', 'self']:
                        # Standard library function - pass interpreter as first argument
                        return RuntimeValue(actual_fn(self, *args))
                    else:
                        # Regular function - call directly with args
                        return RuntimeValue(actual_fn(*args))
                except (ValueError, TypeError):
                    # If we can't inspect the signature, assume it's a regular function
                    result = actual_fn(*args)
                    if isinstance(result, RuntimeValue):
                        return result
                    else:
                        return RuntimeValue(result)
            else:
                raise TypeError(f"{actual_fn} is not callable")
        elif node.type == NodeType.LAMBDA:
            params = node.properties['parameters']
            body = node.properties['body']

            def lambda_func(*args):
                # Create new environment for lambda execution
                lambda_env = RuntimeEnvironment(env)
                for param, arg in zip(params, args):
                    lambda_env.define(param, arg)
                return self.evaluate(body, lambda_env)

            return RuntimeValue(lambda_func)
        elif node.type == NodeType.EXPRESSION_STATEMENT:
            return self.evaluate(node.properties['expression'], env)
        elif node.type == NodeType.IF_STATEMENT:
            condition_val = self.evaluate(node.properties['condition'], env)
            if condition_val.value:
                return self.evaluate(node.properties['consequent'], env)
            elif 'alternate' in node.properties and node.properties['alternate']:
                return self.evaluate(node.properties['alternate'], env)
            else:
                return RuntimeValue(None)
        elif node.type == NodeType.WHILE_LOOP:
            condition = node.properties['condition']
            body = node.properties['body']

            while True:
                cond_val = self.evaluate(condition, env)
                if not cond_val.value:
                    break
                self.evaluate(body, env)
            return RuntimeValue(None)
        elif node.type == NodeType.BLOCK_STATEMENT:
            block_env = RuntimeEnvironment(env)
            result = RuntimeValue(None)
            for stmt in node.properties['statements']:
                result = self.evaluate(stmt, block_env)
            return result
        else:
            raise ValueError(f"Unknown node type: {node.type}")


# Basic parser for demonstration purposes
class SimpleParser:
    def __init__(self):
        self.pos = 0
        self.source = ""
        self.tokens = []
        self.current_token_idx = 0

    def tokenize(self, source: str):
        """Simple tokenizer for demonstration."""
        self.source = source
        # Simple tokenization - in a real implementation this would be more robust
        tokens = []
        
        # Token patterns
        patterns = [
            (r'\d+(\.\d+)?', 'NUMBER'),
            (r'"([^"\\]|\\.)*"', 'STRING'),
            (r"'([^'\\]|\\.)*'", 'STRING'),
            (r'[a-zA-Z_][a-zA-Z0-9_]*', 'IDENTIFIER'),
            (r'[+\-*/%=!<>&|]', 'OPERATOR'),
            (r'[{}()\[\];,]', 'PUNCTUATION'),
            (r'\s+', 'WHITESPACE'),
        ]
        
        pos = 0
        while pos < len(source):
            matched = False
            for pattern, token_type in patterns:
                regex = re.compile(pattern)
                match = regex.match(source, pos)
                if match:
                    value = match.group(0)
                    if token_type != 'WHITESPACE':  # Skip whitespace tokens
                        tokens.append((token_type, value))
                    pos = match.end()
                    matched = True
                    break
            
            if not matched:
                raise ValueError(f"Unexpected character at position {pos}: {source[pos]}")
        
        self.tokens = tokens
        self.current_token_idx = 0
        return tokens

    def peek(self):
        if self.current_token_idx >= len(self.tokens):
            return None
        return self.tokens[self.current_token_idx]

    def consume(self):
        if self.current_token_idx >= len(self.tokens):
            return None
        token = self.tokens[self.current_token_idx]
        self.current_token_idx += 1
        return token

    def match(self, expected_type):
        token = self.peek()
        if token and token[0] == expected_type:
            return self.consume()
        return None

    def parse_expression(self):
        # Simple expression parser for demonstration
        # In a real implementation this would handle precedence and associativity
        token = self.peek()
        if not token:
            return None

        token_type, value = token

        if token_type == 'NUMBER':
            self.consume()
            return AstNode(NodeType.NUMBER_LITERAL, value=float(value))
        elif token_type == 'STRING':
            self.consume()
            # Remove quotes from string
            unquoted = value[1:-1]  # Remove first and last character (quotes)
            return AstNode(NodeType.STRING_LITERAL, value=unquoted)
        elif token_type == 'IDENTIFIER':
            if value == 'true':
                self.consume()
                return AstNode(NodeType.BOOLEAN_LITERAL, value=True)
            elif value == 'false':
                self.consume()
                return AstNode(NodeType.BOOLEAN_LITERAL, value=False)
            elif value == 'null':
                self.consume()
                return AstNode(NodeType.NULL_LITERAL, value=None)
            else:
                self.consume()
                return AstNode(NodeType.VARIABLE_ACCESS, name=value)
        else:
            raise ValueError(f"Unexpected token: {token}")


def demo_prim_concept():
    """Demonstrate the Prim language concept with a simple example."""
    print("=== Prim Language Prototype Demo ===\n")
    
    # Create interpreter
    interpreter = PrimInterpreter()
    env = interpreter.global_env
    
    # Create a simple AST representing: x = 10; y = 20; print(x + y)
    ast_nodes = [
        AstNode(NodeType.ASSIGNMENT, 
                variable="x", 
                value=AstNode(NodeType.NUMBER_LITERAL, value=10),
                mutable=True),
        AstNode(NodeType.ASSIGNMENT,
                variable="y",
                value=AstNode(NodeType.NUMBER_LITERAL, value=20),
                mutable=True),
        AstNode(NodeType.FUNCTION_CALL,
                callee=AstNode(NodeType.VARIABLE_ACCESS, name="print"),
                arguments=[
                    AstNode(NodeType.BINARY_OPERATION,
                            operator="+",
                            left=AstNode(NodeType.VARIABLE_ACCESS, name="x"),
                            right=AstNode(NodeType.VARIABLE_ACCESS, name="y"))
                ])
    ]
    
    # Execute the AST
    for node in ast_nodes:
        result = interpreter.evaluate(node, env)
    
    print("\n=== End Demo ===")


if __name__ == "__main__":
    demo_prim_concept()