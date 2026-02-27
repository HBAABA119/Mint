"""
Prim Standard Library - IO Module

Provides input/output operations for Prim.
"""

import os
import json
from prim_interpreter import RuntimeValue
from prim_modules import PrimFileIO


def std_io_print(interpreter, *values):
    """Print values to stdout."""
    output_values = []
    for val in values:
        output_values.append(val.value if hasattr(val, 'value') else val)
    print(*output_values)
    return RuntimeValue(None)


def std_io_input(interpreter, prompt_val=None):
    """Get input from stdin."""
    prompt = prompt_val.value if hasattr(prompt_val, 'value') else prompt_val
    if prompt:
        user_input = input(prompt)
    else:
        user_input = input()
    return RuntimeValue(user_input)


def std_io_read_file(interpreter, path_val):
    """Read content from a file."""
    path = path_val.value if hasattr(path_val, 'value') else path_val
    try:
        content = PrimFileIO.read_file(path)
        return RuntimeValue(content)
    except Exception as e:
        print(f"Error reading file {path}: {str(e)}")
        return RuntimeValue(None)


def std_io_write_file(interpreter, path_val, content_val):
    """Write content to a file."""
    path = path_val.value if hasattr(path_val, 'value') else path_val
    content = content_val.value if hasattr(content_val, 'value') else content_val
    try:
        PrimFileIO.write_file(path, content)
        return RuntimeValue(True)
    except Exception as e:
        print(f"Error writing file {path}: {str(e)}")
        return RuntimeValue(False)


def std_io_file_exists(interpreter, path_val):
    """Check if a file exists."""
    path = path_val.value if hasattr(path_val, 'value') else path_val
    return RuntimeValue(os.path.exists(path) and os.path.isfile(path))


def std_io_dir_exists(interpreter, path_val):
    """Check if a directory exists."""
    path = path_val.value if hasattr(path_val, 'value') else path_val
    return RuntimeValue(os.path.exists(path) and os.path.isdir(path))


def std_io_list_dir(interpreter, path_val):
    """List files in a directory."""
    path = path_val.value if hasattr(path_val, 'value') else path_val
    try:
        files = os.listdir(path)
        return RuntimeValue(files)
    except Exception as e:
        print(f"Error listing directory {path}: {str(e)}")
        return RuntimeValue([])


def std_io_create_dir(interpreter, path_val):
    """Create a directory."""
    path = path_val.value if hasattr(path_val, 'value') else path_val
    try:
        os.makedirs(path, exist_ok=True)
        return RuntimeValue(True)
    except Exception as e:
        print(f"Error creating directory {path}: {str(e)}")
        return RuntimeValue(False)


def std_io_delete_file(interpreter, path_val):
    """Delete a file."""
    path = path_val.value if hasattr(path_val, 'value') else path_val
    try:
        os.remove(path)
        return RuntimeValue(True)
    except Exception as e:
        print(f"Error deleting file {path}: {str(e)}")
        return RuntimeValue(False)


def std_io_json_parse(interpreter, json_str_val):
    """Parse JSON string."""
    json_str = json_str_val.value if hasattr(json_str_val, 'value') else json_str_val
    try:
        parsed = json.loads(json_str)
        return RuntimeValue(parsed)
    except Exception as e:
        print(f"Error parsing JSON: {str(e)}")
        return RuntimeValue(None)


def std_io_json_stringify(interpreter, obj_val):
    """Convert object to JSON string."""
    obj = obj_val.value if hasattr(obj_val, 'value') else obj_val
    try:
        json_str = json.dumps(obj)
        return RuntimeValue(json_str)
    except Exception as e:
        print(f"Error stringifying JSON: {str(e)}")
        return RuntimeValue(None)


def std_io_exit(interpreter, code_val=None):
    """Exit the program."""
    code = code_val.value if hasattr(code_val, 'value') else code_val
    if code is None:
        code = 0
    exit(int(code))


def register_io_functions(interpreter):
    """Register IO utility functions with the interpreter."""
    interpreter.global_env.define("print", std_io_print)
    interpreter.global_env.define("input", std_io_input)
    interpreter.global_env.define("read_file", std_io_read_file)
    interpreter.global_env.define("write_file", std_io_write_file)
    interpreter.global_env.define("file_exists", std_io_file_exists)
    interpreter.global_env.define("dir_exists", std_io_dir_exists)
    interpreter.global_env.define("list_dir", std_io_list_dir)
    interpreter.global_env.define("create_dir", std_io_create_dir)
    interpreter.global_env.define("delete_file", std_io_delete_file)
    interpreter.global_env.define("json_parse", std_io_json_parse)
    interpreter.global_env.define("json_stringify", std_io_json_stringify)
    interpreter.global_env.define("exit", std_io_exit)