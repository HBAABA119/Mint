"""
Prim AST (Abstract Syntax Tree)
Defines the AST node types for the Prim language, AST construction utilities,
tree traversal and transformation, and AST serialization.
"""

from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import json


class NodeType(Enum):
    """AST node types"""
    PROGRAM = "program"
    MODULE = "module"
    IMPORT = "import"
    EXPORT = "export"
    FUNCTION = "function"
    FUNCTION_CALL = "function_call"
    VARIABLE = "variable"
    LITERAL = "literal"
    BINARY_OP = "binary_op"
    UNARY_OP = "unary_op"
    ASSIGNMENT = "assignment"
    BLOCK = "block"
    IF = "if"
    IF_ELSE = "if_else"
    FOR = "for"
    WHILE = "while"
    RETURN = "return"
    BREAK = "break"
    CONTINUE = "continue"
    LIST = "list"
    DICT = "dict"
    TUPLE = "tuple"
    LAMBDA = "lambda"
    MATCH = "match"
    PATTERN = "pattern"
    TYPE_ANNOTATION = "type_annotation"
    GENERIC_TYPE = "generic_type"
    MACRO_CALL = "macro_call"
    EFFECT = "effect"


@dataclass
class ASTNode:
    """Base AST node"""
    node_type: NodeType
    children: List['ASTNode'] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_child(self, node: 'ASTNode'):
        """Add a child node"""
        self.children.append(node)
        return self

    def to_dict(self) -> Dict[str, Any]:
        """Convert node to dictionary"""
        return {
            'type': self.node_type.value,
            'children': [child.to_dict() for child in self.children],
            'metadata': self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ASTNode':
        """Create node from dictionary"""
        node_type = NodeType(data['type'])
        children = [ASTNode.from_dict(child) for child in data.get('children', [])]
        return cls(node_type=node_type, children=children, metadata=data.get('metadata', {}))


@dataclass
class ProgramNode(ASTNode):
    """Program node"""
    modules: List['ModuleNode'] = field(default_factory=list)

    def __post_init__(self):
        self.node_type = NodeType.PROGRAM


@dataclass
class ModuleNode(ASTNode):
    """Module node"""
    name: str
    imports: List['ImportNode'] = field(default_factory=list)
    exports: List['ExportNode'] = field(default_factory=list)
    body: List[ASTNode] = field(default_factory=list)

    def __post_init__(self):
        self.node_type = NodeType.MODULE


@dataclass
class ImportNode(ASTNode):
    """Import node"""
    module_name: str
    alias: Optional[str] = None

    def __post_init__(self):
        self.node_type = NodeType.IMPORT


@dataclass
class ExportNode(ASTNode):
    """Export node"""
    name: str

    def __post_init__(self):
        self.node_type = NodeType.EXPORT


@dataclass
class FunctionNode(ASTNode):
    """Function node"""
    name: str
    parameters: List['ParameterNode'] = field(default_factory=list)
    return_type: Optional['TypeAnnotationNode'] = None
    body: Optional[ASTNode] = None
    effects: List['EffectNode'] = field(default_factory=list)

    def __post_init__(self):
        self.node_type = NodeType.FUNCTION


@dataclass
class ParameterNode(ASTNode):
    """Parameter node"""
    name: str
    type_annotation: Optional['TypeAnnotationNode'] = None
    default_value: Optional[ASTNode] = None

    def __post_init__(self):
        self.node_type = NodeType.VARIABLE


@dataclass
class FunctionCallNode(ASTNode):
    """Function call node"""
    function: ASTNode
    arguments: List[ASTNode] = field(default_factory=list)

    def __post_init__(self):
        self.node_type = NodeType.FUNCTION_CALL


@dataclass
class VariableNode(ASTNode):
    """Variable node"""
    name: str
    type_annotation: Optional['TypeAnnotationNode'] = None

    def __post_init__(self):
        self.node_type = NodeType.VARIABLE


@dataclass
class LiteralNode(ASTNode):
    """Literal node"""
    value: Any

    def __post_init__(self):
        self.node_type = NodeType.LITERAL


@dataclass
class BinaryOpNode(ASTNode):
    """Binary operation node"""
    operator: str
    left: ASTNode
    right: ASTNode

    def __post_init__(self):
        self.node_type = NodeType.BINARY_OP


@dataclass
class UnaryOpNode(ASTNode):
    """Unary operation node"""
    operator: str
    operand: ASTNode

    def __post_init__(self):
        self.node_type = NodeType.UNARY_OP


@dataclass
class AssignmentNode(ASTNode):
    """Assignment node"""
    target: ASTNode
    value: ASTNode

    def __post_init__(self):
        self.node_type = NodeType.ASSIGNMENT


@dataclass
class BlockNode(ASTNode):
    """Block node"""
    statements: List[ASTNode] = field(default_factory=list)

    def __post_init__(self):
        self.node_type = NodeType.BLOCK


@dataclass
class IfNode(ASTNode):
    """If node"""
    condition: ASTNode
    then_branch: ASTNode

    def __post_init__(self):
        self.node_type = NodeType.IF


@dataclass
class IfElseNode(ASTNode):
    """If-else node"""
    condition: ASTNode
    then_branch: ASTNode
    else_branch: ASTNode

    def __post_init__(self):
        self.node_type = NodeType.IF_ELSE


@dataclass
class ForNode(ASTNode):
    """For loop node"""
    variable: ASTNode
    iterable: ASTNode
    body: ASTNode

    def __post_init__(self):
        self.node_type = NodeType.FOR


@dataclass
class WhileNode(ASTNode):
    """While loop node"""
    condition: ASTNode
    body: ASTNode

    def __post_init__(self):
        self.node_type = NodeType.WHILE


@dataclass
class ReturnNode(ASTNode):
    """Return node"""
    value: Optional[ASTNode] = None

    def __post_init__(self):
        self.node_type = NodeType.RETURN


@dataclass
class ListNode(ASTNode):
    """List literal node"""
    elements: List[ASTNode] = field(default_factory=list)

    def __post_init__(self):
        self.node_type = NodeType.LIST


@dataclass
class DictNode(ASTNode):
    """Dictionary literal node"""
    pairs: List[tuple] = field(default_factory=list)

    def __post_init__(self):
        self.node_type = NodeType.DICT


@dataclass
class TypeAnnotationNode(ASTNode):
    """Type annotation node"""
    type_name: str
    type_params: List[str] = field(default_factory=list)

    def __post_init__(self):
        self.node_type = NodeType.TYPE_ANNOTATION


@dataclass
class EffectNode(ASTNode):
    """Effect annotation node"""
    effect_type: str

    def __post_init__(self):
        self.node_type = NodeType.EFFECT


class ASTBuilder:
    """Builder for constructing ASTs"""

    def __init__(self):
        self.current_node: Optional[ASTNode] = None
        self.node_stack: List[ASTNode] = []

    def start_node(self, node: ASTNode):
        """Start a new node"""
        if self.current_node:
            self.node_stack.append(self.current_node)
        self.current_node = node
        return self

    def end_node(self) -> ASTNode:
        """End the current node"""
        node = self.current_node
        if self.node_stack:
            self.current_node = self.node_stack.pop()
            self.current_node.add_child(node)
        else:
            self.current_node = None
        return node

    def add_child(self, node: ASTNode):
        """Add a child to current node"""
        if self.current_node:
            self.current_node.add_child(node)
        return self

    def get_ast(self) -> Optional[ASTNode]:
        """Get the constructed AST"""
        return self.current_node


class ASTVisitor:
    """AST visitor base class"""

    def visit(self, node: ASTNode) -> Any:
        """Visit a node"""
        method_name = f'visit_{node.node_type.value}'
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node: ASTNode):
        """Generic visitor"""
        for child in node.children:
            self.visit(child)


class ASTTransformer(ASTVisitor):
    """AST transformer base class"""

    def transform(self, node: ASTNode) -> ASTNode:
        """Transform a node"""
        result = self.visit(node)
        return result if result is not None else node

    def generic_visit(self, node: ASTNode) -> ASTNode:
        """Generic transformer"""
        for i, child in enumerate(node.children):
            node.children[i] = self.visit(child)
        return node


class ASTSerializer:
    """AST serialization utilities"""

    @staticmethod
    def serialize(node: ASTNode) -> str:
        """Serialize AST to JSON string"""
        return json.dumps(node.to_dict(), indent=2)

    @staticmethod
    def deserialize(json_str: str) -> ASTNode:
        """Deserialize AST from JSON string"""
        data = json.loads(json_str)
        return ASTNode.from_dict(data)


class ASTPrinter(ASTVisitor):
    """Pretty-print AST"""

    def __init__(self):
        self.indent = 0

    def print(self, text: str):
        """Print with indentation"""
        print("  " * self.indent + text)

    def generic_visit(self, node: ASTNode):
        """Generic visitor for printing"""
        self.print(f"{node.node_type.value}")
        self.indent += 1
        for child in node.children:
            self.visit(child)
        self.indent -= 1


def main():
    """Main entry point for testing"""
    # Build a simple AST
    builder = ASTBuilder()

    # Create a program
    program = ProgramNode()
    builder.start_node(program)

    # Create a module
    module = ModuleNode(name="main")
    builder.start_node(module)

    # Create a function
    func = FunctionNode(name="add")
    builder.start_node(func)

    # Add parameters
    param1 = ParameterNode(name="x")
    param2 = ParameterNode(name="y")
    builder.add_child(param1)
    builder.add_child(param2)

    # Create a return statement
    ret = ReturnNode(value=BinaryOpNode(
        operator="+",
        left=VariableNode(name="x"),
        right=VariableNode(name="y")
    ))
    builder.add_child(ret)

    # End function
    builder.end_node()

    # End module
    builder.end_node()

    # End program
    ast = builder.end_node()

    # Print the AST
    printer = ASTPrinter()
    printer.visit(ast)

    # Serialize and deserialize
    json_str = ASTSerializer.serialize(ast)
    print("\nSerialized AST:")
    print(json_str[:200] + "...")

    print("\nAST system initialized successfully")


if __name__ == "__main__":
    main()
