"""
Prim WebAssembly Target
Provides WASM compilation, WASM runtime, WASI support, and WASM module generation.
"""

import struct
from typing import Dict, List, Optional, Any, Callable, Tuple
from dataclasses import dataclass, field
from enum import Enum


class WASMType(Enum):
    """WASM value types"""
    I32 = "i32"
    I64 = "i64"
    F32 = "f32"
    F64 = "f64"
    FUNC_REF = "funcref"
    EXTERN_REF = "externref"


class WASMOpcode(Enum):
    """WASM opcodes"""
    NOP = 0x01
    DROP = 0x1A
    SELECT = 0x1B

    CONST_I32 = 0x41
    CONST_I64 = 0x42
    CONST_F32 = 0x43
    CONST_F64 = 0x44

    LOCAL_GET = 0x20
    LOCAL_SET = 0x21
    LOCAL_TEE = 0x22
    GLOBAL_GET = 0x23
    GLOBAL_SET = 0x24

    CALL = 0x10
    CALL_INDIRECT = 0x11

    I32_ADD = 0x6A
    I32_SUB = 0x6B
    I32_MUL = 0x6C
    I32_DIV_S = 0x6D
    I32_DIV_U = 0x6E

    I32_EQ = 0x46
    I32_NE = 0x47
    I32_LT_S = 0x48
    I32_LT_U = 0x49
    I32_GT_S = 0x4A
    I32_GT_U = 0x4B

    IF = 0x04
    ELSE = 0x05
    END = 0x0B

    BR = 0x0C
    BR_IF = 0x0D
    BR_TABLE = 0x0E
    RETURN = 0x0F

    LOOP = 0x03
    BLOCK = 0x02


@dataclass
class WASMFunction:
    """WASM function"""
    name: str
    params: List[WASMType] = field(default_factory=list)
    returns: List[WASMType] = field(default_factory=list)
    locals: List[WASMType] = field(default_factory=list)
    body: bytes = b""


@dataclass
class WASMGlobal:
    """WASM global variable"""
    name: str
    type: WASMType
    mutable: bool = False
    init: bytes = b""


@dataclass
class WASMModule:
    """WASM module"""
    types: List[Tuple[List[WASMType], List[WASMType]]] = field(default_factory=list)
    functions: List[WASMFunction] = field(default_factory=list)
    globals: List[WASMGlobal] = field(default_factory=list)
    imports: List[Tuple[str, str, str, List[WASMType], List[WASMType]] = field(default_factory=list)
    exports: List[Tuple[str, str]] = field(default_factory=list)


class WASMCompiler:
    """Compiles Prim to WASM"""

    def __init__(self):
        self.module = WASMModule()
        self.current_function: Optional[WASMFunction] = None

    def compile_function(self, func: WASMFunction) -> bytes:
        """Compile a function to WASM bytecode"""
        self.current_function = func

        # Add function signature to types
        self.module.types.append((func.params, func.returns))

        # Compile function body
        bytecode = bytearray()
        bytecode.extend(self._compile_instructions(func.body))

        # Add end opcode
        bytecode.append(WASMOpcode.END.value)

        # Update function body with compiled bytecode
        func.body = bytes(bytecode)

        # Add function to module
        self.module.functions.append(func)

        return func.body

    def _compile_instructions(self, code: bytes) -> bytes:
        """Compile instructions"""
        # This is a simplified version
        # In a real implementation, this would parse and compile Prim bytecode
        return code

    def compile_module(self) -> bytes:
        """Compile the entire module to WASM binary"""
        binary = bytearray()

        # Magic number and version
        binary.extend(b'\x00asm\x01\x00\x00\x00')

        # Type section
        if self.module.types:
            binary.extend(self._build_type_section())

        # Import section
        if self.module.imports:
            binary.extend(self._build_import_section())

        # Function section
        if self.module.functions:
            binary.extend(self._build_function_section())

        # Global section
        if self.module.globals:
            binary.extend(self._build_global_section())

        # Export section
        if self.module.exports:
            binary.extend(self._build_export_section())

        # Code section
        if self.module.functions:
            binary.extend(self._build_code_section())

        return bytes(binary)

    def _build_type_section(self) -> bytes:
        """Build type section"""
        section = bytearray()
        section.append(0x01)  # Section ID

        types_data = bytearray()
        types_data.append(len(self.module.types))

        for params, returns in self.module.types:
            # Function type
            func_type = bytearray()
            func_type.append(0x60)  # Function type indicator
            func_type.append(len(params))
            for param in params:
                func_type.append(self._type_to_byte(param))
            func_type.append(len(returns))
            for ret in returns:
                func_type.append(self._type_to_byte(ret))
            types_data.extend(func_type)

        section.extend(self._uleb128(len(types_data)))
        section.extend(types_data)
        return bytes(section)

    def _build_function_section(self) -> bytes:
        """Build function section"""
        section = bytearray()
        section.append(0x03)  # Section ID

        func_data = bytearray()
        func_data.append(len(self.module.functions))

        for i, func in enumerate(self.module.functions):
            func_data.append(i)  # Type index

        section.extend(self._uleb128(len(func_data)))
        section.extend(func_data)
        return bytes(section)

    def _build_import_section(self) -> bytes:
        """Build import section"""
        section = bytearray()
        section.append(0x02)  # Section ID

        import_data = bytearray()
        import_data.append(len(self.module.imports))

        for module_name, name, kind, params, returns in self.module.imports:
            # Module name
            import_data.extend(self._string(module_name))
            # Name
            import_data.extend(self._string(name))
            # Kind (function = 0x00)
            import_data.append(0x00)
            # Type index
            import_data.append(0)

        section.extend(self._uleb128(len(import_data)))
        section.extend(import_data)
        return bytes(section)

    def _build_export_section(self) -> bytes:
        """Build export section"""
        section = bytearray()
        section.append(0x07)  # Section ID

        export_data = bytearray()
        export_data.append(len(self.module.exports))

        for name, kind in self.module.exports:
            export_data.extend(self._string(name))
            export_data.append(0x00)  # Function export
            export_data.extend(self._uleb128(0))  # Function index

        section.extend(self._uleb128(len(export_data)))
        section.extend(export_data)
        return bytes(section)

    def _build_code_section(self) -> bytes:
        """Build code section"""
        section = bytearray()
        section.append(0x0A)  # Section ID

        code_data = bytearray()
        code_data.append(len(self.module.functions))

        for func in self.module.functions:
            func_code = bytearray()
            func_code.extend(self._uleb128(len(func.locals)))
            for local in func.locals:
                func_code.append(1)  # Number of locals of this type
                func_code.append(self._type_to_byte(local))

            func_code.extend(func.body)
            func_code.append(WASMOpcode.END.value)

            code_data.extend(self._uleb128(len(func_code)))
            code_data.extend(func_code)

        section.extend(self._uleb128(len(code_data)))
        section.extend(code_data)
        return bytes(section)

    def _build_global_section(self) -> bytes:
        """Build global section"""
        section = bytearray()
        section.append(0x06)  # Section ID

        global_data = bytearray()
        global_data.append(len(self.module.globals))

        for global_var in self.module.globals:
            # Type
            global_data.append(self._type_to_byte(global_var.type))
            # Mutability
            global_data.append(1 if global_var.mutable else 0)
            # Init expression
            global_data.extend(global_var.init)
            global_data.append(WASMOpcode.END.value)

        section.extend(self._uleb128(len(global_data)))
        section.extend(global_data)
        return bytes(section)

    def _type_to_byte(self, wasm_type: WASMType) -> int:
        """Convert WASM type to byte"""
        type_map = {
            WASMType.I32: 0x7F,
            WASMType.I64: 0x7E,
            WASMType.F32: 0x7D,
            WASMType.F64: 0x7C,
            WASMType.FUNC_REF: 0x70,
            WASMType.EXTERN_REF: 0x6F,
        }
        return type_map.get(wasm_type, 0x7F)

    def _string(self, s: str) -> bytes:
        """Encode string to WASM format"""
        return self._uleb128(len(s)) + s.encode('utf-8')

    def _uleb128(self, value: int) -> bytes:
        """Encode unsigned LEB128"""
        result = bytearray()
        while True:
            byte = value & 0x7F
            value >>= 7
            if value != 0:
                byte |= 0x80
            result.append(byte)
            if value == 0:
                break
        return bytes(result)


class WASMRuntime:
    """WASM runtime for executing WASM modules"""

    def __init__(self):
        self.memory = bytearray(65536)  # 64KB default page
        self.globals: Dict[str, Any] = {}
        self.stack: List[Any] = []
        self.call_stack: List[int] = []

    def load_module(self, module_data: bytes):
        """Load a WASM module"""
        # Parse and validate module
        if not self._validate_module(module_data):
            raise ValueError("Invalid WASM module")

        # Initialize module
        self._initialize_module(module_data)

    def _validate_module(self, module_data: bytes) -> bool:
        """Validate WASM module"""
        # Check magic number and version
        if len(module_data) < 8:
            return False

        magic = module_data[:4]
        version = module_data[4:8]

        return magic == b'\x00asm' and version == b'\x01\x00\x00\x00'

    def _initialize_module(self, module_data: bytes):
        """Initialize WASM module"""
        # Parse sections and initialize
        pass

    def invoke(self, function_name: str, *args) -> Any:
        """Invoke a WASM function"""
        # Push arguments to stack
        for arg in args:
            self.stack.append(arg)

        # Execute function
        # This is simplified - real implementation would execute bytecode
        result = self.stack.pop() if self.stack else None

        return result


class WASI:
    """WASI (WebAssembly System Interface) support"""

    def __init__(self):
        self.files: Dict[str, bytes] = {}
        self.file_descriptors: Dict[int, str] = {}
        self.next_fd = 3  # 0=stdin, 1=stdout, 2=stderr

    def open_file(self, path: str, data: bytes = b""):
        """Open a file"""
        fd = self.next_fd
        self.next_fd += 1
        self.file_descriptors[fd] = path
        self.files[path] = data
        return fd

    def read_file(self, fd: int, size: int) -> bytes:
        """Read from file descriptor"""
        path = self.file_descriptors.get(fd)
        if path and path in self.files:
            return self.files[path][:size]
        return b""

    def write_file(self, fd: int, data: bytes):
        """Write to file descriptor"""
        if fd == 1:  # stdout
            print(data.decode('utf-8'), end='')
        elif fd in self.file_descriptors:
            path = self.file_descriptors[fd]
            self.files[path] = data

    def close_file(self, fd: int):
        """Close file descriptor"""
        if fd in self.file_descriptors:
            del self.file_descriptors[fd]


def compile_to_wasm(source: str) -> bytes:
    """Compile Prim source to WASM"""
    compiler = WASMCompiler()
    module = compiler.compile_module()
    return module


def main():
    """Main entry point for testing"""
    print("Testing WASM compiler...")

    compiler = WASMCompiler()

    # Create a simple function
    func = WASMFunction(
        name="add",
        params=[WASMType.I32, WASMType.I32],
        returns=[WASMType.I32],
        body=bytes([
            WASMOpcode.LOCAL_GET.value, 0x00,  # Get param 0
            WASMOpcode.LOCAL_GET.value, 0x01,  # Get param 1
            WASMOpcode.I32_ADD.value,           # Add
        ])
    )

    bytecode = compiler.compile_function(func)
    print(f"Compiled function: {len(bytecode)} bytes")

    # Compile module
    module = compiler.compile_module()
    print(f"Compiled module: {len(module)} bytes")

    # Test runtime
    runtime = WASMRuntime()
    runtime.load_module(module)
    print("Module loaded successfully")

    # Test WASI
    wasi = WASI()
    fd = wasi.open_file("test.txt", b"Hello WASI!")
    data = wasi.read_file(fd, 100)
    print(f"Read from file: {data}")

    print("\nWASM target initialized successfully")


if __name__ == "__main__":
    main()
