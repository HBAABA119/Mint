"""
Prim Foreign Function Interface (FFI)
Provides C interop, dynamic library loading, foreign type mapping, and callback support.
"""

import ctypes
import os
from typing import Dict, List, Optional, Any, Callable, Union, TypeVar
from dataclasses import dataclass, field
from enum import Enum


class ForeignType(Enum):
    """Foreign types"""
    VOID = "void"
    INT = "int"
    INT8 = "int8"
    INT16 = "int16"
    INT32 = "int32"
    INT64 = "int64"
    UINT = "uint"
    UINT8 = "uint8"
    UINT16 = "uint16"
    UINT32 = "uint32"
    UINT64 = "uint64"
    FLOAT = "float"
    DOUBLE = "double"
    BOOL = "bool"
    CHAR = "char"
    POINTER = "pointer"
    STRING = "string"
    FUNCTION = "function"


@dataclass
class ForeignFunction:
    """Foreign function definition"""
    name: str
    return_type: ForeignType
    arg_types: List[ForeignType]
    library: Optional['ForeignLibrary'] = None
    func_ptr: Optional[Any] = None


@dataclass
class ForeignLibrary:
    """Foreign library"""
    name: str
    path: str
    handle: Optional[Any] = None
    functions: Dict[str, ForeignFunction] = field(default_factory=dict)

    def load(self):
        """Load the library"""
        try:
            self.handle = ctypes.CDLL(self.path)
            return True
        except Exception as e:
            print(f"Failed to load library {self.path}: {e}")
            return False

    def unload(self):
        """Unload the library"""
        if self.handle:
            # ctypes doesn't have a direct unload method
            # The library will be unloaded when the handle is garbage collected
            self.handle = None

    def get_function(self, name: str, return_type: ForeignType, arg_types: List[ForeignType]) -> Optional[ForeignFunction]:
        """Get a function from the library"""
        if not self.handle:
            return None

        try:
            # Map foreign types to ctypes types
            ctypes_return_type = self._map_type(return_type)
            ctypes_arg_types = [self._map_type(t) for t in arg_types]

            # Get function pointer
            func_ptr = self.handle[name]
            func_ptr.argtypes = ctypes_arg_types
            func_ptr.restype = ctypes_return_type

            # Create foreign function
            foreign_func = ForeignFunction(
                name=name,
                return_type=return_type,
                arg_types=arg_types,
                library=self,
                func_ptr=func_ptr
            )

            self.functions[name] = foreign_func
            return foreign_func

        except Exception as e:
            print(f"Failed to get function {name}: {e}")
            return None

    def _map_type(self, foreign_type: ForeignType) -> Any:
        """Map foreign type to ctypes type"""
        type_map = {
            ForeignType.VOID: None,
            ForeignType.INT: ctypes.c_int,
            ForeignType.INT8: ctypes.c_int8,
            ForeignType.INT16: ctypes.c_int16,
            ForeignType.INT32: ctypes.c_int32,
            ForeignType.INT64: ctypes.c_int64,
            ForeignType.UINT: ctypes.c_uint,
            ForeignType.UINT8: ctypes.c_uint8,
            ForeignType.UINT16: ctypes.c_uint16,
            ForeignType.UINT32: ctypes.c_uint32,
            ForeignType.UINT64: ctypes.c_uint64,
            ForeignType.FLOAT: ctypes.c_float,
            ForeignType.DOUBLE: ctypes.c_double,
            ForeignType.BOOL: ctypes.c_bool,
            ForeignType.CHAR: ctypes.c_char,
            ForeignType.POINTER: ctypes.c_void_p,
            ForeignType.STRING: ctypes.c_char_p,
            ForeignType.FUNCTION: ctypes.CFUNCTYPE,
        }
        return type_map.get(foreign_type, ctypes.c_void_p)


class ForeignFunctionInterface:
    """Foreign Function Interface"""

    def __init__(self):
        self.libraries: Dict[str, ForeignLibrary] = {}
        self.type_conversions: Dict[ForeignType, Callable] = {}

    def load_library(self, name: str, path: str) -> Optional[ForeignLibrary]:
        """Load a foreign library"""
        library = ForeignLibrary(name=name, path=path)
        if library.load():
            self.libraries[name] = library
            return library
        return None

    def get_library(self, name: str) -> Optional[ForeignLibrary]:
        """Get a loaded library"""
        return self.libraries.get(name)

    def call_function(self, func: ForeignFunction, *args) -> Any:
        """Call a foreign function"""
        if not func.func_ptr:
            raise RuntimeError(f"Function {func.name} not loaded")

        # Convert arguments
        converted_args = []
        for i, arg in enumerate(args):
            arg_type = func.arg_types[i] if i < len(func.arg_types) else ForeignType.VOID
            converted_args.append(self._convert_to_foreign(arg, arg_type))

        # Call function
        result = func.func_ptr(*converted_args)

        # Convert result
        return self._convert_from_foreign(result, func.return_type)

    def _convert_to_foreign(self, value: Any, foreign_type: ForeignType) -> Any:
        """Convert Python value to foreign type"""
        if foreign_type == ForeignType.STRING:
            if isinstance(value, str):
                return value.encode('utf-8')
            return value
        elif foreign_type == ForeignType.BOOL:
            return 1 if value else 0
        return value

    def _convert_from_foreign(self, value: Any, foreign_type: ForeignType) -> Any:
        """Convert foreign value to Python type"""
        if foreign_type == ForeignType.STRING:
            if isinstance(value, bytes):
                return value.decode('utf-8')
            return value
        elif foreign_type == ForeignType.BOOL:
            return bool(value)
        return value


class CallbackRegistry:
    """Registry for callbacks passed to foreign code"""

    def __init__(self):
        self.callbacks: Dict[str, Callable] = {}
        self.callback_wrappers: Dict[str, Any] = {}

    def register(self, name: str, callback: Callable, return_type: ForeignType, arg_types: List[ForeignType]):
        """Register a callback"""
        self.callbacks[name] = callback

        # Create ctypes callback wrapper
        ffi = ForeignFunctionInterface()
        ctypes_return_type = ffi._map_type(return_type)
        ctypes_arg_types = [ffi._map_type(t) for t in arg_types]

        callback_wrapper = ctypes.CFUNCTYPE(ctypes_return_type, *ctypes_arg_types)(callback)
        self.callback_wrappers[name] = callback_wrapper

        return callback_wrapper

    def get(self, name: str) -> Optional[Any]:
        """Get a callback wrapper"""
        return self.callback_wrappers.get(name)


class StructBuilder:
    """Builder for foreign structs"""

    def __init__(self):
        self.structs: Dict[str, type] = {}

    def define_struct(self, name: str, fields: Dict[str, ForeignType]) -> type:
        """Define a foreign struct"""
        field_types = {}
        for field_name, field_type in fields.items():
            ffi = ForeignFunctionInterface()
            field_types[field_name] = ffi._map_type(field_type)

        struct_class = type(name, (ctypes.Structure,), {'_fields_': list(field_types.items())})
        self.structs[name] = struct_class
        return struct_class

    def get_struct(self, name: str) -> Optional[type]:
        """Get a struct definition"""
        return self.structs.get(name)


class MemoryManager:
    """Memory manager for foreign allocations"""

    def __init__(self):
        self.allocations: Dict[int, int] = {}

    def alloc(self, size: int) -> int:
        """Allocate foreign memory"""
        ptr = ctypes.create_string_buffer(size)
        address = ctypes.addressof(ptr)
        self.allocations[address] = size
        return address

    def free(self, address: int):
        """Free foreign memory"""
        if address in self.allocations:
            del self.allocations[address]

    def read_string(self, address: int) -> str:
        """Read string from foreign memory"""
        try:
            ptr = ctypes.cast(address, ctypes.c_char_p)
            return ptr.value.decode('utf-8')
        except:
            return ""

    def write_string(self, address: int, string: str):
        """Write string to foreign memory"""
        try:
            ptr = ctypes.cast(address, ctypes.c_char_p)
            ptr.value = string.encode('utf-8')
        except:
            pass


def load_library(name: str, path: str) -> Optional[ForeignLibrary]:
    """Load a foreign library"""
    ffi = ForeignFunctionInterface()
    return ffi.load_library(name, path)


def call_foreign(func: ForeignFunction, *args) -> Any:
    """Call a foreign function"""
    ffi = ForeignFunctionInterface()
    return ffi.call_function(func, *args)


def main():
    """Main entry point for testing"""
    ffi = ForeignFunctionInterface()

    # Test loading a library (using system library for example)
    print("Testing FFI...")

    # Try loading libc on Unix or msvcrt on Windows
    if os.name == 'nt':
        lib_path = "msvcrt.dll"
    else:
        lib_path = "libc.so.6"

    # This will likely fail on most systems, but demonstrates the API
    lib = ffi.load_library("c_lib", lib_path)
    if lib:
        print(f"Loaded library: {lib.name}")

        # Try to get a function
        func = lib.get_function("printf", ForeignType.INT, [ForeignType.STRING])
        if func:
            print(f"Got function: {func.name}")

            # Call the function
            result = ffi.call_function(func, b"Hello from C!\n")
            print(f"Result: {result}")
    else:
        print("Could not load library (expected on most systems)")

    # Test struct builder
    builder = StructBuilder()
    point_struct = builder.define_struct("Point", {
        "x": ForeignType.INT,
        "y": ForeignType.INT
    })
    print(f"Created struct: {point_struct}")

    # Test memory manager
    memory = MemoryManager()
    addr = memory.alloc(100)
    print(f"Allocated memory at: {hex(addr)}")
    memory.write_string(addr, "Test string")
    value = memory.read_string(addr)
    print(f"Read string: {value}")
    memory.free(addr)

    print("\nFFI initialized successfully")


if __name__ == "__main__":
    main()
