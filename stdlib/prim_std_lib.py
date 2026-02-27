"""
Prim Standard Library - Main Module

Combines all standard library modules into one importable unit.
"""

from prim_std_collections import register_collections_functions
from prim_std_strings import register_string_functions
from prim_std_math import register_math_functions
from prim_std_io import register_io_functions


def register_standard_library(interpreter):
    """
    Register all standard library functions with the interpreter.
    
    This function adds all standard library functions to the interpreter's
    global environment, making them available for use in Prim programs.
    """
    register_collections_functions(interpreter)
    register_string_functions(interpreter)
    register_math_functions(interpreter)
    register_io_functions(interpreter)
    
    print("Prim Standard Library v1.0 loaded successfully!")