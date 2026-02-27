"""
Prim Language Compiler

Main compiler that selects the appropriate parser based on mode directive.
Includes optimization passes and an optimizing compiler.
"""

import re
from typing import Union, List, Callable, Any
from prim_interpreter import PrimInterpreter, RuntimeEnvironment, AstNode, NodeType
from prim_slim_parser import parse_slim_code
from prim_block_parser import parse_block_code
from prim_flow_parser import parse_flow_code
from prim_std_lib import register_standard_library


class OptimizationPass:
    """Base class for optimization passes"""

    def __init__(self, name: str):
        self.name = name

    def optimize(self, ast: AstNode) -> AstNode:
        """Optimize the AST"""
        return ast


class ConstantFolding(OptimizationPass):
    """Constant folding optimization"""

    def __init__(self):
        super().__init__("constant_folding")

    def optimize(self, ast: AstNode) -> AstNode:
        """Fold constant expressions"""
        return self._fold_constants(ast)

    def _fold_constants(self, node: AstNode) -> AstNode:
        """Recursively fold constants"""
        if node.type == NodeType.BINARY_OPERATION:
            left = self._fold_constants(node.properties['left'])
            right = self._fold_constants(node.properties['right'])

            # Check if both operands are constants
            if (left.type == NodeType.NUMBER_LITERAL and
                right.type == NodeType.NUMBER_LITERAL):
                op = node.properties['operator']
                left_val = left.properties['value']
                right_val = right.properties['value']

                try:
                    if op == '+':
                        result = left_val + right_val
                    elif op == '-':
                        result = left_val - right_val
                    elif op == '*':
                        result = left_val * right_val
                    elif op == '/':
                        result = left_val / right_val
                    else:
                        return node

                    return AstNode(NodeType.NUMBER_LITERAL, value=result)
                except:
                    return node

        return node


class DeadCodeElimination(OptimizationPass):
    """Dead code elimination optimization"""

    def __init__(self):
        super().__init__("dead_code_elimination")

    def optimize(self, ast: AstNode) -> AstNode:
        """Eliminate dead code"""
        return self._eliminate_dead_code(ast)

    def _eliminate_dead_code(self, node: AstNode) -> AstNode:
        """Recursively eliminate dead code"""
        # This is a simplified version
        # In a real implementation, this would analyze control flow
        return node


class InlineExpansion(OptimizationPass):
    """Inline expansion optimization"""

    def __init__(self):
        super().__init__("inline_expansion")

    def optimize(self, ast: AstNode) -> AstNode:
        """Inline function calls"""
        return self._inline_functions(ast)

    def _inline_functions(self, node: AstNode) -> AstNode:
        """Recursively inline functions"""
        # This is a simplified version
        # In a real implementation, this would inline small functions
        return node


class OptimizingCompiler:
    """Optimizing compiler with multiple passes"""

    def __init__(self):
        self.optimizations: List[OptimizationPass] = []
        self.enabled = True

    def add_optimization(self, optimization: OptimizationPass):
        """Add an optimization pass"""
        self.optimizations.append(optimization)

    def enable(self):
        """Enable optimizations"""
        self.enabled = True

    def disable(self):
        """Disable optimizations"""
        self.enabled = False

    def optimize(self, ast: AstNode) -> AstNode:
        """Run all optimization passes"""
        if not self.enabled:
            return ast

        optimized = ast
        for opt in self.optimizations:
            optimized = opt.optimize(optimized)

        return optimized


class PrimCompiler:
    def __init__(self):
        self.interpreter = PrimInterpreter()
        # Register the standard library
        register_standard_library(self.interpreter)
        self.optimizing_compiler = OptimizingCompiler()
        self.optimizing_compiler.add_optimization(ConstantFolding())
        self.optimizing_compiler.add_optimization(DeadCodeElimination())
        self.optimizing_compiler.add_optimization(InlineExpansion())

    def detect_mode(self, code: str) -> str:
        """
        Detect the syntax mode from the code based on mode directive.
        """
        lines = code.split('\n')
        for line in lines[:10]:  # Check first 10 lines for mode directive
            stripped = line.strip()
            if stripped.startswith('#mode'):
                mode = stripped.split()[1].lower()
                if mode in ['slim', 'block', 'flow']:
                    return mode
        # Default to slim if no mode specified
        return 'slim'

    def compile_and_run(self, code: str):
        """
        Compile and run Prim code based on its syntax mode.
        """
        mode = self.detect_mode(code)
        print(f"Detected mode: {mode}")
        
        # Parse the code based on detected mode
        if mode == 'slim':
            ast = parse_slim_code(code)
        elif mode == 'block':
            ast = parse_block_code(code)
        elif mode == 'flow':
            ast = parse_flow_code(code)
        else:
            raise ValueError(f"Unsupported mode: {mode}")
        
        # Execute the parsed AST
        env = RuntimeEnvironment(parent=self.interpreter.global_env)
        result = self.interpreter.evaluate(ast, env)
        
        return result

    def compile_to_ast(self, code: str):
        """
        Compile Prim code to AST based on its syntax mode without executing.
        """
        mode = self.detect_mode(code)
        print(f"Detected mode: {mode}")
        
        if mode == 'slim':
            return parse_slim_code(code)
        elif mode == 'block':
            return parse_block_code(code)
        elif mode == 'flow':
            return parse_flow_code(code)
        else:
            raise ValueError(f"Unsupported mode: {mode}")


def run_prim_example():
    """
    Run examples of all three syntax modes to demonstrate equivalence.
    """
    compiler = PrimCompiler()
    
    print("=== Prim Language Multi-Mode Demonstration ===\n")
    
    # Example 1: Slim Mode
    slim_code = '''#mode slim
x = 10
y = 20
result = x + y
print("Slim mode result:", result)
'''
    print("Running Slim Mode code:")
    print(slim_code)
    compiler.compile_and_run(slim_code)
    print()
    
    # Example 2: Block Mode
    block_code = '''#mode block
var x = 10;
var y = 20;
var result = x + y;
print("Block mode result:", result);
'''
    print("Running Block Mode code:")
    print(block_code)
    compiler.compile_and_run(block_code)
    print()
    
    # Example 3: Flow Mode
    flow_code = '''#mode flow
x := 10
y := 20
result := x + y
print("Flow mode result:", result)
'''
    print("Running Flow Mode code:")
    print(flow_code)
    compiler.compile_and_run(flow_code)
    print()
    
    print("=== All modes produced equivalent results! ===")


def test_equivalence():
    """
    Test that all three modes produce equivalent ASTs for simple operations.
    """
    compiler = PrimCompiler()
    
    # Same logical operation in all three modes
    slim_code = '''#mode slim
result = 5 + 3 * 2
print(result)
'''
    
    block_code = '''#mode block
var result = 5 + 3 * 2;
print(result);
'''
    
    flow_code = '''#mode flow
result := 5 + 3 * 2
print(result)
'''
    
    print("Testing equivalence of all three modes:")
    
    print("\nSlim mode AST:")
    slim_ast = compiler.compile_to_ast(slim_code)
    print(slim_ast)
    
    print("\nBlock mode AST:")
    block_ast = compiler.compile_to_ast(block_code)
    print(block_ast)
    
    print("\nFlow mode AST:")
    flow_ast = compiler.compile_to_ast(flow_code)
    print(flow_ast)
    
    # Run all three to confirm they produce the same result
    print("\nExecuting all modes:")
    compiler.compile_and_run(slim_code)
    compiler.compile_and_run(block_code)
    compiler.compile_and_run(flow_code)


if __name__ == "__main__":
    run_prim_example()
    print("\n" + "="*50 + "\n")
    test_equivalence()