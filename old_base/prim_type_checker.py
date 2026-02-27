"""
Prim Language Type System (v0.3)

Implementation of static type annotations and type checking for Prim.
"""

from enum import Enum
from typing import Dict, List, Optional, Union, Any
from prim_interpreter import AstNode, NodeType


class PrimType(Enum):
    ANY = "any"
    NUMBER = "number"
    STRING = "string"
    BOOLEAN = "boolean"
    NULL = "null"
    LIST = "list"
    DICT = "dict"
    FUNCTION = "function"
    UNKNOWN = "unknown"


class TypeAnnotation:
    """Represents a type annotation in Prim."""
    
    def __init__(self, type_name: str, generic_args: Optional[List['TypeAnnotation']] = None):
        self.type_name = type_name
        self.generic_args = generic_args or []
    
    def __repr__(self):
        if self.generic_args:
            generics = ", ".join(str(arg) for arg in self.generic_args)
            return f"{self.type_name}<{generics}>"
        return self.type_name


class TypeInfo:
    """Information about a type including its annotation and inferred type."""
    
    def __init__(self, declared: Optional[TypeAnnotation] = None, inferred: Optional[PrimType] = None):
        self.declared = declared
        self.inferred = inferred or PrimType.UNKNOWN


class TypeEnvironment:
    """Tracks variable types in scope."""
    
    def __init__(self, parent=None):
        self.types: Dict[str, TypeInfo] = {}
        self.parent = parent
    
    def define(self, name: str, type_info: TypeInfo):
        self.types[name] = type_info
    
    def lookup(self, name: str) -> Optional[TypeInfo]:
        if name in self.types:
            return self.types[name]
        elif self.parent:
            return self.parent.lookup(name)
        return None
    
    def update(self, name: str, type_info: TypeInfo):
        if name in self.types:
            self.types[name] = type_info
        elif self.parent:
            self.parent.update(name, type_info)


class TypeChecker:
    """Performs static type checking on Prim AST."""
    
    def __init__(self):
        self.errors = []
        self.type_env = TypeEnvironment()
        
        # Set up built-in types
        self.builtin_types = {
            'number': PrimType.NUMBER,
            'string': PrimType.STRING,
            'boolean': PrimType.BOOLEAN,
            'bool': PrimType.BOOLEAN,  # alias
            'null': PrimType.NULL,
            'any': PrimType.ANY,
            'list': PrimType.LIST,
            'dict': PrimType.DICT,
            'function': PrimType.FUNCTION,
        }
    
    def check_program(self, ast: AstNode) -> List[str]:
        """Check the entire program for type errors."""
        self.errors = []
        
        if ast.type == NodeType.BLOCK_STATEMENT:
            for stmt in ast.properties['statements']:
                self.check_statement(stmt, self.type_env)
        
        return self.errors
    
    def check_statement(self, node: AstNode, env: TypeEnvironment):
        """Check a statement for type errors."""
        if node.type == NodeType.ASSIGNMENT:
            self.check_assignment(node, env)
        elif node.type == NodeType.VARIABLE_ACCESS:
            self.check_variable_access(node, env)
        elif node.type == NodeType.EXPRESSION_STATEMENT:
            self.check_expression(node.properties['expression'], env)
        elif node.type == NodeType.IF_STATEMENT:
            self.check_if_statement(node, env)
        elif node.type == NodeType.WHILE_LOOP:
            self.check_while_loop(node, env)
        elif node.type == NodeType.FUNCTION_CALL:
            self.check_function_call(node, env)
        elif node.type == NodeType.LAMBDA:
            self.check_lambda(node, env)
        # Add more statement types as needed
    
    def check_assignment(self, node: AstNode, env: TypeEnvironment):
        """Check an assignment statement for type errors."""
        var_name = node.properties['variable']
        value_expr = node.properties['value']
        
        # Check the type of the value being assigned
        value_type = self.check_expression(value_expr, env)
        
        # For now, just store the inferred type
        # In a full implementation, we'd also check against declared types
        env.define(var_name, TypeInfo(inferred=value_type))
    
    def check_variable_access(self, node: AstNode, env: TypeEnvironment) -> PrimType:
        """Check a variable access and return its type."""
        var_name = node.properties['name']
        type_info = env.lookup(var_name)
        
        if type_info is None:
            self.errors.append(f"Undefined variable: {var_name}")
            return PrimType.UNKNOWN
        
        return type_info.inferred or PrimType.UNKNOWN
    
    def check_if_statement(self, node: AstNode, env: TypeEnvironment):
        """Check an if statement for type errors."""
        condition_type = self.check_expression(node.properties['condition'], env)
        
        if condition_type != PrimType.BOOLEAN and condition_type != PrimType.ANY:
            self.errors.append(f"Condition in if statement must be boolean, got {condition_type}")
        
        # Check both branches
        if_env = TypeEnvironment(parent=env)
        self.check_statement(node.properties['consequent'], if_env)
        
        if 'alternate' in node.properties and node.properties['alternate']:
            else_env = TypeEnvironment(parent=env)
            self.check_statement(node.properties['alternate'], else_env)
    
    def check_while_loop(self, node: AstNode, env: TypeEnvironment):
        """Check a while loop for type errors."""
        condition_type = self.check_expression(node.properties['condition'], env)
        
        if condition_type != PrimType.BOOLEAN and condition_type != PrimType.ANY:
            self.errors.append(f"Condition in while loop must be boolean, got {condition_type}")
        
        # Check loop body
        body_env = TypeEnvironment(parent=env)
        self.check_statement(node.properties['body'], body_env)
    
    def check_binary_operation(self, node: AstNode, env: TypeEnvironment) -> PrimType:
        """Check a binary operation for type errors."""
        left_type = self.check_expression(node.properties['left'], env)
        right_type = self.check_expression(node.properties['right'], env)
        op = node.properties['operator']
        
        # Type checking rules for operators
        if op in ['+', '-', '*', '/', '%']:
            # Arithmetic operations
            if left_type not in [PrimType.NUMBER, PrimType.ANY]:
                self.errors.append(f"Left operand of arithmetic operation must be number, got {left_type}")
            if right_type not in [PrimType.NUMBER, PrimType.ANY]:
                self.errors.append(f"Right operand of arithmetic operation must be number, got {right_type}")
            return PrimType.NUMBER
        
        elif op in ['==', '!=']:
            # Equality operations work on any types but should be compatible
            return PrimType.BOOLEAN
        
        elif op in ['<', '>', '<=', '>=']:
            # Comparison operations
            if left_type not in [PrimType.NUMBER, PrimType.STRING, PrimType.ANY]:
                self.errors.append(f"Left operand of comparison must be number or string, got {left_type}")
            if right_type not in [PrimType.NUMBER, PrimType.STRING, PrimType.ANY]:
                self.errors.append(f"Right operand of comparison must be number or string, got {right_type}")
            return PrimType.BOOLEAN
        
        elif op in ['&&', '||']:
            # Logical operations
            if left_type != PrimType.BOOLEAN and left_type != PrimType.ANY:
                self.errors.append(f"Left operand of logical operation must be boolean, got {left_type}")
            if right_type != PrimType.BOOLEAN and right_type != PrimType.ANY:
                self.errors.append(f"Right operand of logical operation must be boolean, got {right_type}")
            return PrimType.BOOLEAN
        
        return PrimType.UNKNOWN
    
    def check_unary_operation(self, node: AstNode, env: TypeEnvironment) -> PrimType:
        """Check a unary operation for type errors."""
        operand_type = self.check_expression(node.properties['operand'], env)
        op = node.properties['operator']
        
        if op in ['-', '+']:
            if operand_type != PrimType.NUMBER and operand_type != PrimType.ANY:
                self.errors.append(f"Operand of unary {op} must be number, got {operand_type}")
            return PrimType.NUMBER
        elif op == '!':
            if operand_type != PrimType.BOOLEAN and operand_type != PrimType.ANY:
                self.errors.append(f"Operand of unary {op} must be boolean, got {operand_type}")
            return PrimType.BOOLEAN
        
        return PrimType.UNKNOWN
    
    def check_function_call(self, node: AstNode, env: TypeEnvironment) -> PrimType:
        """Check a function call for type errors."""
        callee = node.properties['callee']
        args = node.properties['arguments']
        
        # For now, just check that arguments are valid
        # In a full implementation, we'd check function signatures
        for arg in args:
            self.check_expression(arg, env)
        
        # Assume function calls return unknown type for now
        # In a full implementation, we'd look up the function signature
        return PrimType.UNKNOWN
    
    def check_lambda(self, node: AstNode, env: TypeEnvironment) -> PrimType:
        """Check a lambda function for type errors."""
        # Create a new environment for the function body
        lambda_env = TypeEnvironment(parent=env)
        
        # Add parameters to the lambda environment
        for param in node.properties['parameters']:
            # For now, parameters are untyped
            lambda_env.define(param, TypeInfo(inferred=PrimType.ANY))
        
        # Check the function body
        self.check_expression(node.properties['body'], lambda_env)
        
        return PrimType.FUNCTION
    
    def check_literal(self, node: AstNode) -> PrimType:
        """Check a literal value and return its type."""
        if node.type == NodeType.NUMBER_LITERAL:
            return PrimType.NUMBER
        elif node.type == NodeType.STRING_LITERAL:
            return PrimType.STRING
        elif node.type == NodeType.BOOLEAN_LITERAL:
            return PrimType.BOOLEAN
        elif node.type == NodeType.NULL_LITERAL:
            return PrimType.NULL
        elif node.type == NodeType.LIST_LITERAL:
            # For lists, we could infer the element type
            return PrimType.LIST
        elif node.type == NodeType.DICT_LITERAL:
            # For dicts, we could infer key/value types
            return PrimType.DICT
        
        return PrimType.UNKNOWN
    
    def check_expression(self, node: AstNode, env: TypeEnvironment) -> PrimType:
        """Check an expression for type errors and return its type."""
        if node.type in [NodeType.NUMBER_LITERAL, NodeType.STRING_LITERAL, 
                         NodeType.BOOLEAN_LITERAL, NodeType.NULL_LITERAL,
                         NodeType.LIST_LITERAL, NodeType.DICT_LITERAL]:
            return self.check_literal(node)
        elif node.type == NodeType.VARIABLE_ACCESS:
            return self.check_variable_access(node, env)
        elif node.type == NodeType.BINARY_OPERATION:
            return self.check_binary_operation(node, env)
        elif node.type == NodeType.UNARY_OPERATION:
            return self.check_unary_operation(node, env)
        elif node.type == NodeType.FUNCTION_CALL:
            return self.check_function_call(node, env)
        elif node.type == NodeType.LAMBDA:
            return self.check_lambda(node, env)
        
        return PrimType.UNKNOWN


def add_type_annotations_to_interpreter(interpreter):
    """Add type-related functionality to the interpreter."""
    # Add type checking built-ins
    def builtin_typeof(value):
        # Return the runtime type of a value
        val = value.value if hasattr(value, 'value') else value
        if val is None:
            return interpreter.global_env.lookup('string')('null')
        elif isinstance(val, bool):
            return interpreter.global_env.lookup('string')('boolean')
        elif isinstance(val, (int, float)):
            return interpreter.global_env.lookup('string')('number')
        elif isinstance(val, str):
            return interpreter.global_env.lookup('string')('string')
        elif isinstance(val, list):
            return interpreter.global_env.lookup('string')('list')
        elif isinstance(val, dict):
            return interpreter.global_env.lookup('string')('dict')
        else:
            return interpreter.global_env.lookup('string')('unknown')
    
    interpreter.global_env.define("typeof", builtin_typeof)


# Example usage and testing
if __name__ == "__main__":
    print("Prim Type System (v0.3) - Prototype")
    print("This implements static type annotations and type checking for Prim.")
    
    # Example of how type annotations might work (conceptual):
    print("\nConceptual examples:")
    print("# Type annotations in different modes:")
    print("  #mode slim")
    print("  x: number = 42")
    print("  name: string = \"hello\"")
    print("  items: list<number> = [1, 2, 3]")
    print("")
    print("  #mode block")
    print("  var x: number = 42;")
    print("  var name: string = \"hello\";")
    print("  var items: list<number> = [1, 2, 3];")
    print("")
    print("  #mode flow")
    print("  x: number := 42")
    print("  name: string := \"hello\"")
    print("  items: list<number> := [1, 2, 3]")