"""
Prim Language Module System (v0.2)

Implementation of modules, imports, and file I/O for Prim.
"""

import os
import sys
from typing import Dict, Any, Optional
from prim_interpreter import PrimInterpreter, RuntimeEnvironment


class PrimModuleLoader:
    """Handles loading and caching of Prim modules."""
    
    def __init__(self, interpreter: PrimInterpreter):
        self.interpreter = interpreter
        self.module_cache: Dict[str, Any] = {}
        self.search_paths = [os.getcwd(), './modules', './std']
        
    def add_search_path(self, path: str):
        """Add a directory to the module search path."""
        if os.path.isdir(path) and path not in self.search_paths:
            self.search_paths.insert(0, path)
    
    def find_module(self, module_name: str) -> Optional[str]:
        """Find a module file by name in search paths."""
        # Convert dot notation to file path
        file_path = module_name.replace('.', os.sep) + '.prim'
        
        for search_path in self.search_paths:
            full_path = os.path.join(search_path, file_path)
            if os.path.isfile(full_path):
                return full_path
        
        return None
    
    def load_module(self, module_name: str, importer_env: RuntimeEnvironment) -> RuntimeEnvironment:
        """Load a module and return its environment."""
        if module_name in self.module_cache:
            return self.module_cache[module_name]
        
        module_file = self.find_module(module_name)
        if not module_file:
            raise ImportError(f"Module '{module_name}' not found")
        
        # Read and parse the module
        with open(module_file, 'r', encoding='utf-8') as f:
            source_code = f.read()
        
        # Create a new environment for the module
        module_env = RuntimeEnvironment(parent=importer_env)
        
        try:
            # Parse and execute the module code
            # In a full implementation, this would use the parser and compiler
            # For now, we'll use the interpreter directly
            from prim_interpreter import PrimInterpreter
            
            # Create a temporary interpreter for this module
            module_interpreter = PrimInterpreter()
            module_interpreter.global_env = module_env
            
            # Execute the module code
            module_interpreter.execute(source_code)
            
            # Cache the module environment
            self.module_cache[module_name] = module_env
            
            return module_env
            
        except Exception as e:
            raise ImportError(f"Failed to load module '{module_name}': {e}")


class PrimFileIO:
    """File I/O operations for Prim."""
    
    @staticmethod
    def read_file(file_path: str) -> str:
        """Read content from a file."""
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    @staticmethod
    def write_file(file_path: str, content: str):
        """Write content to a file."""
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    @staticmethod
    def read_lines(file_path: str) -> list:
        """Read file content as a list of lines."""
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.readlines()
    
    @staticmethod
    def file_exists(file_path: str) -> bool:
        """Check if a file exists."""
        return os.path.isfile(file_path)
    
    @staticmethod
    def list_directory(dir_path: str) -> list:
        """List files in a directory."""
        return os.listdir(dir_path)


def extend_interpreter_with_modules(interpreter: PrimInterpreter):
    """Extend the interpreter with module and file I/O functionality."""
    loader = PrimModuleLoader(interpreter)
    
    # Add module loading capability to interpreter
    def builtin_import(module_name):
        # Get the caller's environment to determine where to import
        # For this prototype, we'll use a simplified approach
        module_env = loader.load_module(module_name.value, interpreter.global_env)
        # Return the module's public interface
        # For now, return the whole environment as a proxy object
        return interpreter.global_env.lookup('null')  # Simplified for now
    
    def builtin_read_file(file_path):
        content = PrimFileIO.read_file(file_path.value)
        return interpreter.global_env.lookup('str')(content)
    
    def builtin_write_file(file_path, content):
        PrimFileIO.write_file(file_path.value, content.value)
        return interpreter.global_env.lookup('null')
    
    def builtin_file_exists(file_path):
        exists = PrimFileIO.file_exists(file_path.value)
        return interpreter.global_env.lookup('bool')(exists)
    
    # Register built-in functions
    interpreter.global_env.define("import", interpreter.global_env.lookup('null'))  # Will be implemented properly later
    interpreter.global_env.define("read_file", builtin_read_file)
    interpreter.global_env.define("write_file", builtin_write_file)
    interpreter.global_env.define("file_exists", builtin_file_exists)


# Example usage
if __name__ == "__main__":
    print("Prim Module System (v0.2) - Prototype")
    print("This module extends Prim with import/export and file I/O capabilities.")
    
    # Example of how modules might work (conceptual):
    print("\nConceptual examples:")
    print("# Importing a module:")
    print("  #mode slim")
    print("  import math")
    print("  result = math.sqrt(16)")
    print("")
    print("# File operations:")
    print("  #mode block")
    print("  var content = read_file('data.txt');")
    print("  write_file('output.txt', content);")
    print("")
    print("# Checking if file exists:")
    print("  #mode flow")
    print("  file_exists('config.prim') |> if (#) then (print('Config found')) else (print('Using defaults'))")