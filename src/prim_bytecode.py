"""
Prim Language Bytecode Compiler and VM (v0.5)

Implementation of bytecode compiler and virtual machine for Prim.
"""

from enum import Enum
from typing import List, Dict, Any, Union
from prim_interpreter import AstNode, NodeType, RuntimeValue, RuntimeEnvironment


class Opcode(Enum):
    """Bytecode operation codes."""
    # Constants
    LOAD_CONST = 0
    LOAD_NAME = 1
    STORE_NAME = 2
    
    # Operations
    BINARY_ADD = 3
    BINARY_SUB = 4
    BINARY_MUL = 5
    BINARY_DIV = 6
    BINARY_MOD = 7
    
    BINARY_EQ = 8
    BINARY_NE = 9
    BINARY_LT = 10
    BINARY_GT = 11
    BINARY_LE = 12
    BINARY_GE = 13
    
    BINARY_AND = 14
    BINARY_OR = 15
    
    # Unary operations
    UNARY_NEG = 16
    UNARY_NOT = 17
    
    # Control flow
    JUMP_ABSOLUTE = 18
    JUMP_IF_FALSE_OR_POP = 19
    POP_JUMP_IF_TRUE = 20
    POP_JUMP_IF_FALSE = 21
    
    # Function calls
    CALL_FUNCTION = 22
    RETURN_VALUE = 23
    
    # Stack operations
    POP_TOP = 24
    ROT_TWO = 25
    ROT_THREE = 26
    DUP_TOP = 27
    DUP_TOP_TWO = 28


class Instruction:
    """A single bytecode instruction."""
    
    def __init__(self, opcode: Opcode, arg: Union[int, str, float, None] = None, lineno: int = 0):
        self.opcode = opcode
        self.arg = arg
        self.lineno = lineno
    
    def __repr__(self):
        if self.arg is not None:
            return f"{self.opcode.name}({self.arg})"
        return self.opcode.name


class Bytecode:
    """Collection of bytecode instructions."""
    
    def __init__(self):
        self.code: List[Instruction] = []
        self.consts: List[Any] = []
        self.names: List[str] = []
        self.varnames: List[str] = []
    
    def add_instruction(self, opcode: Opcode, arg=None, lineno=0):
        """Add an instruction to the bytecode."""
        self.code.append(Instruction(opcode, arg, lineno))
    
    def add_const(self, const: Any) -> int:
        """Add a constant to the constants pool and return its index."""
        if const not in self.consts:
            self.consts.append(const)
        return self.consts.index(const)
    
    def add_name(self, name: str) -> int:
        """Add a name to the names table and return its index."""
        if name not in self.names:
            self.names.append(name)
        return self.names.index(name)
    
    def add_varname(self, name: str) -> int:
        """Add a variable name to the varnames table and return its index."""
        if name not in self.varnames:
            self.varnames.append(name)
        return self.varnames.index(name)


class BytecodeCompiler:
    """Compiles AST to bytecode."""
    
    def __init__(self):
        self.bytecode = Bytecode()
        self.environment_stack = []
    
    def compile(self, ast: AstNode) -> Bytecode:
        """Compile an AST to bytecode."""
        self.bytecode = Bytecode()
        
        if ast.type == NodeType.BLOCK_STATEMENT:
            for stmt in ast.properties['statements']:
                self.compile_statement(stmt)
        else:
            self.compile_statement(ast)
        
        # Add return statement at the end
        self.bytecode.add_instruction(Opcode.LOAD_CONST, self.bytecode.add_const(None))
        self.bytecode.add_instruction(Opcode.RETURN_VALUE)
        
        return self.bytecode
    
    def compile_statement(self, node: AstNode):
        """Compile a statement."""
        if node.type == NodeType.ASSIGNMENT:
            self.compile_assignment(node)
        elif node.type == NodeType.EXPRESSION_STATEMENT:
            self.compile_expression(node.properties['expression'])
            # Pop the result since it's a statement
            self.bytecode.add_instruction(Opcode.POP_TOP)
        elif node.type == NodeType.IF_STATEMENT:
            self.compile_if_statement(node)
        elif node.type == NodeType.WHILE_LOOP:
            self.compile_while_loop(node)
        elif node.type == NodeType.RETURN_STATEMENT:
            self.compile_return_statement(node)
        # Add more statement types as needed
    
    def compile_assignment(self, node: AstNode):
        """Compile an assignment statement."""
        # Compile the value
        self.compile_expression(node.properties['value'])
        
        # Store it in the variable
        var_name = node.properties['variable']
        name_idx = self.bytecode.add_name(var_name)
        self.bytecode.add_instruction(Opcode.STORE_NAME, name_idx)
    
    def compile_if_statement(self, node: AstNode):
        """Compile an if statement."""
        # Compile the condition
        self.compile_expression(node.properties['condition'])
        
        # Jump to else block if condition is false
        jump_else_pos = len(self.bytecode.code)
        self.bytecode.add_instruction(Opcode.POP_JUMP_IF_FALSE, 0)  # Placeholder
        
        # Compile the if block
        self.compile_statement(node.properties['consequent'])
        
        # Jump to end after if block
        jump_end_pos = len(self.bytecode.code)
        self.bytecode.add_instruction(Opcode.JUMP_ABSOLUTE, 0)  # Placeholder
        
        # Update the jump to else position
        self.bytecode.code[jump_else_pos] = Instruction(
            Opcode.POP_JUMP_IF_FALSE, len(self.bytecode.code)
        )
        
        # Compile the else block if present
        if 'alternate' in node.properties and node.properties['alternate']:
            self.compile_statement(node.properties['alternate'])
        
        # Update the jump to end position
        self.bytecode.code[jump_end_pos] = Instruction(
            Opcode.JUMP_ABSOLUTE, len(self.bytecode.code)
        )
    
    def compile_while_loop(self, node: AstNode):
        """Compile a while loop."""
        loop_start = len(self.bytecode.code)
        
        # Compile the condition
        self.compile_expression(node.properties['condition'])
        
        # Jump to after loop if condition is false
        jump_out_pos = len(self.bytecode.code)
        self.bytecode.add_instruction(Opcode.POP_JUMP_IF_FALSE, 0)  # Placeholder
        
        # Compile the loop body
        self.compile_statement(node.properties['body'])
        
        # Jump back to the condition
        self.bytecode.add_instruction(Opcode.JUMP_ABSOLUTE, loop_start)
        
        # Update the jump out position
        self.bytecode.code[jump_out_pos] = Instruction(
            Opcode.POP_JUMP_IF_FALSE, len(self.bytecode.code)
        )
    
    def compile_return_statement(self, node: AstNode):
        """Compile a return statement."""
        if 'value' in node.properties and node.properties['value']:
            self.compile_expression(node.properties['value'])
        else:
            self.bytecode.add_instruction(Opcode.LOAD_CONST, 
                                         self.bytecode.add_const(None))
        self.bytecode.add_instruction(Opcode.RETURN_VALUE)
    
    def compile_expression(self, node: AstNode):
        """Compile an expression."""
        if node.type == NodeType.NUMBER_LITERAL:
            const_idx = self.bytecode.add_const(node.properties['value'])
            self.bytecode.add_instruction(Opcode.LOAD_CONST, const_idx)
        elif node.type == NodeType.STRING_LITERAL:
            const_idx = self.bytecode.add_const(node.properties['value'])
            self.bytecode.add_instruction(Opcode.LOAD_CONST, const_idx)
        elif node.type == NodeType.BOOLEAN_LITERAL:
            const_idx = self.bytecode.add_const(node.properties['value'])
            self.bytecode.add_instruction(Opcode.LOAD_CONST, const_idx)
        elif node.type == NodeType.NULL_LITERAL:
            const_idx = self.bytecode.add_const(node.properties['value'])
            self.bytecode.add_instruction(Opcode.LOAD_CONST, const_idx)
        elif node.type == NodeType.VARIABLE_ACCESS:
            name_idx = self.bytecode.add_name(node.properties['name'])
            self.bytecode.add_instruction(Opcode.LOAD_NAME, name_idx)
        elif node.type == NodeType.BINARY_OPERATION:
            self.compile_binary_operation(node)
        elif node.type == NodeType.UNARY_OPERATION:
            self.compile_unary_operation(node)
        elif node.type == NodeType.FUNCTION_CALL:
            self.compile_function_call(node)
        # Add more expression types as needed
    
    def compile_binary_operation(self, node: AstNode):
        """Compile a binary operation."""
        op = node.properties['operator']
        
        # Compile left and right operands
        self.compile_expression(node.properties['left'])
        self.compile_expression(node.properties['right'])
        
        # Perform the operation based on the operator
        if op == '+':
            self.bytecode.add_instruction(Opcode.BINARY_ADD)
        elif op == '-':
            self.bytecode.add_instruction(Opcode.BINARY_SUB)
        elif op == '*':
            self.bytecode.add_instruction(Opcode.BINARY_MUL)
        elif op == '/':
            self.bytecode.add_instruction(Opcode.BINARY_DIV)
        elif op == '%':
            self.bytecode.add_instruction(Opcode.BINARY_MOD)
        elif op == '==':
            self.bytecode.add_instruction(Opcode.BINARY_EQ)
        elif op == '!=':
            self.bytecode.add_instruction(Opcode.BINARY_NE)
        elif op == '<':
            self.bytecode.add_instruction(Opcode.BINARY_LT)
        elif op == '>':
            self.bytecode.add_instruction(Opcode.BINARY_GT)
        elif op == '<=':
            self.bytecode.add_instruction(Opcode.BINARY_LE)
        elif op == '>=':
            self.bytecode.add_instruction(Opcode.BINARY_GE)
        elif op == '&&':
            self.bytecode.add_instruction(Opcode.BINARY_AND)
        elif op == '||':
            self.bytecode.add_instruction(Opcode.BINARY_OR)
    
    def compile_unary_operation(self, node: AstNode):
        """Compile a unary operation."""
        op = node.properties['operator']
        
        # Compile the operand
        self.compile_expression(node.properties['operand'])
        
        # Perform the operation based on the operator
        if op == '-':
            self.bytecode.add_instruction(Opcode.UNARY_NEG)
        elif op == '!':
            self.bytecode.add_instruction(Opcode.UNARY_NOT)
    
    def compile_function_call(self, node: AstNode):
        """Compile a function call."""
        # Compile the function
        self.compile_expression(node.properties['callee'])
        
        # Compile arguments
        arg_count = 0
        for arg in node.properties['arguments']:
            self.compile_expression(arg)
            arg_count += 1
        
        # Call the function
        self.bytecode.add_instruction(Opcode.CALL_FUNCTION, arg_count)


class VirtualMachine:
    """Prim virtual machine to execute bytecode."""
    
    def __init__(self):
        self.stack: List[Any] = []
        self.frames: List['Frame'] = []
        self.return_value = None
    
    def execute(self, bytecode: Bytecode, global_env=None):
        """Execute bytecode."""
        frame = Frame(bytecode, global_env or {})
        self.frames.append(frame)
        
        while frame.pc < len(frame.code.code):
            instruction = frame.code.code[frame.pc]
            self.execute_instruction(instruction, frame)
            frame.pc += 1
            
            if self.return_value is not None:
                break
        
        self.frames.pop()
        return self.return_value
    
    def execute_instruction(self, instruction: Instruction, frame: 'Frame'):
        """Execute a single instruction."""
        if instruction.opcode == Opcode.LOAD_CONST:
            const = frame.code.consts[instruction.arg]
            frame.push(const)
        elif instruction.opcode == Opcode.LOAD_NAME:
            name = frame.code.names[instruction.arg]
            if name in frame.local_vars:
                frame.push(frame.local_vars[name])
            elif name in frame.global_vars:
                frame.push(frame.global_vars[name])
            else:
                raise NameError(f"Name '{name}' is not defined")
        elif instruction.opcode == Opcode.STORE_NAME:
            name = frame.code.names[instruction.arg]
            value = frame.pop()
            frame.local_vars[name] = value
        elif instruction.opcode == Opcode.BINARY_ADD:
            right = frame.pop()
            left = frame.pop()
            frame.push(left + right)
        elif instruction.opcode == Opcode.BINARY_SUB:
            right = frame.pop()
            left = frame.pop()
            frame.push(left - right)
        elif instruction.opcode == Opcode.BINARY_MUL:
            right = frame.pop()
            left = frame.pop()
            frame.push(left * right)
        elif instruction.opcode == Opcode.BINARY_DIV:
            right = frame.pop()
            left = frame.pop()
            frame.push(left / right)
        elif instruction.opcode == Opcode.BINARY_MOD:
            right = frame.pop()
            left = frame.pop()
            frame.push(left % right)
        elif instruction.opcode == Opcode.BINARY_EQ:
            right = frame.pop()
            left = frame.pop()
            frame.push(left == right)
        elif instruction.opcode == Opcode.BINARY_NE:
            right = frame.pop()
            left = frame.pop()
            frame.push(left != right)
        elif instruction.opcode == Opcode.BINARY_LT:
            right = frame.pop()
            left = frame.pop()
            frame.push(left < right)
        elif instruction.opcode == Opcode.BINARY_GT:
            right = frame.pop()
            left = frame.pop()
            frame.push(left > right)
        elif instruction.opcode == Opcode.BINARY_LE:
            right = frame.pop()
            left = frame.pop()
            frame.push(left <= right)
        elif instruction.opcode == Opcode.BINARY_GE:
            right = frame.pop()
            left = frame.pop()
            frame.push(left >= right)
        elif instruction.opcode == Opcode.UNARY_NEG:
            value = frame.pop()
            frame.push(-value)
        elif instruction.opcode == Opcode.UNARY_NOT:
            value = frame.pop()
            frame.push(not value)
        elif instruction.opcode == Opcode.POP_JUMP_IF_FALSE:
            value = frame.pop()
            if not value:
                frame.pc = instruction.arg - 1  # -1 because pc will be incremented
        elif instruction.opcode == Opcode.JUMP_ABSOLUTE:
            frame.pc = instruction.arg - 1  # -1 because pc will be incremented
        elif instruction.opcode == Opcode.POP_TOP:
            frame.pop()
        elif instruction.opcode == Opcode.RETURN_VALUE:
            self.return_value = frame.pop()
        elif instruction.opcode == Opcode.CALL_FUNCTION:
            arg_count = instruction.arg
            args = []
            for _ in range(arg_count):
                args.append(frame.pop())
            args.reverse()  # Reverse to get correct order
            
            func = frame.pop()
            
            if callable(func):
                result = func(*args)
                frame.push(result)
            else:
                raise TypeError(f"{func} is not callable")
        else:
            raise NotImplementedError(f"Opcode {instruction.opcode} not implemented")


class Frame:
    """Execution frame for the virtual machine."""
    
    def __init__(self, code: Bytecode, global_vars: Dict[str, Any]):
        self.code = code
        self.global_vars = global_vars
        self.local_vars: Dict[str, Any] = {}
        self.stack: List[Any] = []
        self.pc = 0  # Program counter
    
    def push(self, value):
        """Push a value onto the stack."""
        self.stack.append(value)
    
    def pop(self):
        """Pop a value from the stack."""
        if not self.stack:
            raise IndexError("pop from empty stack")
        return self.stack.pop()


def compile_and_run_vm(ast, global_env=None):
    """Compile AST to bytecode and run in VM."""
    compiler = BytecodeCompiler()
    bytecode = compiler.compile(ast)
    
    vm = VirtualMachine()
    result = vm.execute(bytecode, global_env)
    
    return result


# Example usage and testing
if __name__ == "__main__":
    print("Prim Bytecode Compiler and VM (v0.5) - Prototype")
    print("This implements bytecode compilation and virtual machine execution for Prim.")
    
    # Example of how bytecode compilation might work (conceptual):
    print("\nConceptual examples:")
    print("# Compiling and running code through the VM:")
    print("# AST -> Bytecode -> VM Execution")
    print("")
    print("# The bytecode compiler transforms AST nodes into a sequence of")
    print("# low-level operations that the VM can execute efficiently.")
    print("")
    print("# Sample bytecode for 'x = 5 + 3':")
    print("# LOAD_CONST 5    # Push 5 onto stack")
    print("# LOAD_CONST 3    # Push 3 onto stack") 
    print("# BINARY_ADD      # Add top two values")
    print("# STORE_NAME x    # Store result in variable x")
    print("# RETURN_VALUE    # Return from function")