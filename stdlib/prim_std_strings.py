"""
Prim Standard Library - String Module

Provides essential string operations for Prim.
"""

import re
from prim_interpreter import RuntimeValue


def std_string_length(interpreter, str_val):
    """Get the length of a string."""
    s = str_val.value if hasattr(str_val, 'value') else str_val
    return RuntimeValue(len(s))


def std_string_upper(interpreter, str_val):
    """Convert string to uppercase."""
    s = str_val.value if hasattr(str_val, 'value') else str_val
    return RuntimeValue(s.upper())


def std_string_lower(interpreter, str_val):
    """Convert string to lowercase."""
    s = str_val.value if hasattr(str_val, 'value') else str_val
    return RuntimeValue(s.lower())


def std_string_split(interpreter, str_val, delimiter_val=None):
    """Split a string by delimiter."""
    s = str_val.value if hasattr(str_val, 'value') else str_val
    delimiter = delimiter_val.value if hasattr(delimiter_val, 'value') else delimiter_val
    
    if delimiter is None:
        # Split on whitespace by default
        parts = s.split()
    else:
        parts = s.split(delimiter)
    
    return RuntimeValue(parts)


def std_string_join(interpreter, lst_val, separator_val=None):
    """Join a list of strings with a separator."""
    lst = lst_val.value if hasattr(lst_val, 'value') else lst_val
    separator = separator_val.value if hasattr(separator_val, 'value') else separator_val
    
    if separator is None:
        separator = ""
    
    # Convert all items to strings
    str_lst = [str(item) for item in lst]
    result = separator.join(str_lst)
    
    return RuntimeValue(result)


def std_string_trim(interpreter, str_val):
    """Trim whitespace from both ends of a string."""
    s = str_val.value if hasattr(str_val, 'value') else str_val
    return RuntimeValue(s.strip())


def std_string_starts_with(interpreter, str_val, prefix_val):
    """Check if string starts with a prefix."""
    s = str_val.value if hasattr(str_val, 'value') else str_val
    prefix = prefix_val.value if hasattr(prefix_val, 'value') else prefix_val
    return RuntimeValue(s.startswith(prefix))


def std_string_ends_with(interpreter, str_val, suffix_val):
    """Check if string ends with a suffix."""
    s = str_val.value if hasattr(str_val, 'value') else str_val
    suffix = suffix_val.value if hasattr(suffix_val, 'value') else suffix_val
    return RuntimeValue(s.endswith(suffix))


def std_string_contains(interpreter, str_val, substr_val):
    """Check if string contains a substring."""
    s = str_val.value if hasattr(str_val, 'value') else str_val
    substr = substr_val.value if hasattr(substr_val, 'value') else substr_val
    return RuntimeValue(substr in s)


def std_string_replace(interpreter, str_val, old_val, new_val):
    """Replace occurrences of a substring with another."""
    s = str_val.value if hasattr(str_val, 'value') else str_val
    old = old_val.value if hasattr(old_val, 'value') else old_val
    new = new_val.value if hasattr(new_val, 'value') else new_val
    return RuntimeValue(s.replace(old, new))


def std_string_pad_start(interpreter, str_val, length_val, pad_val=None):
    """Pad string at the start to reach specified length."""
    s = str_val.value if hasattr(str_val, 'value') else str_val
    length = int(length_val.value if hasattr(length_val, 'value') else length_val)
    pad_char = pad_val.value if hasattr(pad_val, 'value') else pad_val
    
    if pad_char is None:
        pad_char = " "
    
    return RuntimeValue(s.rjust(length, pad_char))


def std_string_pad_end(interpreter, str_val, length_val, pad_val=None):
    """Pad string at the end to reach specified length."""
    s = str_val.value if hasattr(str_val, 'value') else str_val
    length = int(length_val.value if hasattr(length_val, 'value') else length_val)
    pad_char = pad_val.value if hasattr(pad_val, 'value') else pad_val
    
    if pad_char is None:
        pad_char = " "
    
    return RuntimeValue(s.ljust(length, pad_char))


def std_string_slice(interpreter, str_val, start_val, end_val=None):
    """Extract a substring from start to end index."""
    s = str_val.value if hasattr(str_val, 'value') else str_val
    start = int(start_val.value if hasattr(start_val, 'value') else start_val)
    end = int(end_val.value if hasattr(end_val, 'value') else end_val) if end_val is not None else None
    
    if end is None:
        return RuntimeValue(s[start:])
    else:
        return RuntimeValue(s[start:end])


def register_string_functions(interpreter):
    """Register string utility functions with the interpreter."""
    interpreter.global_env.define("strlen", std_string_length)
    interpreter.global_env.define("upper", std_string_upper)
    interpreter.global_env.define("lower", std_string_lower)
    interpreter.global_env.define("split", std_string_split)
    interpreter.global_env.define("join", std_string_join)
    interpreter.global_env.define("trim", std_string_trim)
    interpreter.global_env.define("starts_with", std_string_starts_with)
    interpreter.global_env.define("ends_with", std_string_ends_with)
    interpreter.global_env.define("contains", std_string_contains)
    interpreter.global_env.define("replace", std_string_replace)
    interpreter.global_env.define("pad_start", std_string_pad_start)
    interpreter.global_env.define("pad_end", std_string_pad_end)
    interpreter.global_env.define("slice", std_string_slice)