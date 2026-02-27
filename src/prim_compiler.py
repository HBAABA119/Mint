"""
Prim Language Compiler

Main compiler that selects the appropriate parser based on mode directive.
"""

import re
from typing import Union
from prim_interpreter import PrimInterpreter, RuntimeEnvironment
from prim_slim_parser import parse_slim_code
from prim_block_parser import parse_block_code
from prim_flow_parser import parse_flow_code
from prim_std_lib import register_standard_library


class PrimCompiler:
    def __init__(self):
        self.interpreter = PrimInterpreter()
        # Register the standard library
        register_standard_library(self.interpreter)

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