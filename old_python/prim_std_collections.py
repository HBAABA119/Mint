"""
Prim Standard Library - Collections Module

Provides essential data structure operations for Prim.
"""

from typing import Any, Callable, List, Dict, Optional
from prim_interpreter import RuntimeValue


def std_list_map(interpreter, lst_val, fn_val):
    """Map function for lists."""
    lst = lst_val.value
    fn = fn_val.value
    
    if not callable(fn):
        raise TypeError("Second argument to map must be a function")
    
    result = []
    for item in lst:
        item_runtime = RuntimeValue(item)
        mapped_item = fn(interpreter.global_env, item_runtime)
        result.append(mapped_item.value if hasattr(mapped_item, 'value') else mapped_item)
    
    return RuntimeValue(result)


def std_list_filter(interpreter, lst_val, fn_val):
    """Filter function for lists."""
    lst = lst_val.value
    fn = fn_val.value
    
    if not callable(fn):
        raise TypeError("Second argument to filter must be a function")
    
    result = []
    for item in lst:
        item_runtime = RuntimeValue(item)
        keep = fn(interpreter.global_env, item_runtime)
        if keep.value if hasattr(keep, 'value') else keep:
            result.append(item)
    
    return RuntimeValue(result)


def std_list_reduce(interpreter, lst_val, fn_val, initial_val=None):
    """Reduce function for lists."""
    lst = lst_val.value
    fn = fn_val.value
    
    if not callable(fn):
        raise TypeError("Second argument to reduce must be a function")
    
    if not lst and initial_val is None:
        raise ValueError("Cannot reduce empty list without initial value")
    
    if initial_val is None:
        accumulator = lst[0]
        start_idx = 1
    else:
        accumulator = initial_val.value if hasattr(initial_val, 'value') else initial_val
        start_idx = 0
    
    for i in range(start_idx, len(lst)):
        accumulator_runtime = RuntimeValue(accumulator)
        item_runtime = RuntimeValue(lst[i])
        accumulator = fn(interpreter.global_env, accumulator_runtime, item_runtime)
        accumulator = accumulator.value if hasattr(accumulator, 'value') else accumulator
    
    return RuntimeValue(accumulator)


def std_list_length(interpreter, lst_val):
    """Get length of a list."""
    lst = lst_val.value
    return RuntimeValue(len(lst))


def std_list_push(interpreter, lst_val, item_val):
    """Add an item to the end of a list."""
    lst = lst_val.value
    item = item_val.value if hasattr(item_val, 'value') else item_val
    lst.append(item)
    return RuntimeValue(lst)


def std_dict_get(interpreter, dict_val, key_val):
    """Get a value from a dictionary."""
    dict_obj = dict_val.value
    key = key_val.value if hasattr(key_val, 'value') else key_val
    
    if key in dict_obj:
        return RuntimeValue(dict_obj[key])
    else:
        return RuntimeValue(None)


def std_dict_set(interpreter, dict_val, key_val, value_val):
    """Set a value in a dictionary."""
    dict_obj = dict_val.value
    key = key_val.value if hasattr(key_val, 'value') else key_val
    value = value_val.value if hasattr(value_val, 'value') else value_val
    
    dict_obj[key] = value
    return RuntimeValue(dict_obj)


def std_dict_keys(interpreter, dict_val):
    """Get all keys from a dictionary."""
    dict_obj = dict_val.value
    return RuntimeValue(list(dict_obj.keys()))


def std_dict_values(interpreter, dict_val):
    """Get all values from a dictionary."""
    dict_obj = dict_val.value
    return RuntimeValue(list(dict_obj.values()))


def register_collections_functions(interpreter):
    """Register collection utility functions with the interpreter."""
    interpreter.global_env.define("map", std_list_map)
    interpreter.global_env.define("filter", std_list_filter)
    interpreter.global_env.define("reduce", std_list_reduce)
    interpreter.global_env.define("len", std_list_length)
    interpreter.global_env.define("push", std_list_push)
    interpreter.global_env.define("dict_get", std_dict_get)
    interpreter.global_env.define("dict_set", std_dict_set)
    interpreter.global_env.define("dict_keys", std_dict_keys)
    interpreter.global_env.define("dict_values", std_dict_values)