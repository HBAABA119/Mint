"""
Prim Standard Library - Math Module

Provides essential mathematical operations for Prim.
"""

import math
from prim_interpreter import RuntimeValue


def std_math_abs(interpreter, num_val):
    """Absolute value."""
    num = num_val.value if hasattr(num_val, 'value') else num_val
    return RuntimeValue(abs(num))


def std_math_floor(interpreter, num_val):
    """Floor function."""
    num = num_val.value if hasattr(num_val, 'value') else num_val
    return RuntimeValue(math.floor(num))


def std_math_ceil(interpreter, num_val):
    """Ceiling function."""
    num = num_val.value if hasattr(num_val, 'value') else num_val
    return RuntimeValue(math.ceil(num))


def std_math_round(interpreter, num_val, digits_val=None):
    """Round function."""
    num = num_val.value if hasattr(num_val, 'value') else num_val
    digits = digits_val.value if hasattr(digits_val, 'value') else digits_val
    
    if digits is None:
        return RuntimeValue(round(num))
    else:
        return RuntimeValue(round(num, digits))


def std_math_sqrt(interpreter, num_val):
    """Square root."""
    num = num_val.value if hasattr(num_val, 'value') else num_val
    return RuntimeValue(math.sqrt(num))


def std_math_pow(interpreter, base_val, exp_val):
    """Power function."""
    base = base_val.value if hasattr(base_val, 'value') else base_val
    exp = exp_val.value if hasattr(exp_val, 'value') else exp_val
    return RuntimeValue(pow(base, exp))


def std_math_min(interpreter, *args):
    """Minimum of multiple values."""
    values = [arg.value if hasattr(arg, 'value') else arg for arg in args]
    return RuntimeValue(min(values))


def std_math_max(interpreter, *args):
    """Maximum of multiple values."""
    values = [arg.value if hasattr(arg, 'value') else arg for arg in args]
    return RuntimeValue(max(values))


def std_math_sin(interpreter, num_val):
    """Sine function."""
    num = num_val.value if hasattr(num_val, 'value') else num_val
    return RuntimeValue(math.sin(num))


def std_math_cos(interpreter, num_val):
    """Cosine function."""
    num = num_val.value if hasattr(num_val, 'value') else num_val
    return RuntimeValue(math.cos(num))


def std_math_tan(interpreter, num_val):
    """Tangent function."""
    num = num_val.value if hasattr(num_val, 'value') else num_val
    return RuntimeValue(math.tan(num))


def std_math_log(interpreter, num_val, base_val=None):
    """Logarithm function."""
    num = num_val.value if hasattr(num_val, 'value') else num_val
    base = base_val.value if hasattr(base_val, 'value') else base_val
    
    if base is None:
        return RuntimeValue(math.log(num))  # Natural log
    else:
        return RuntimeValue(math.log(num, base))


def std_math_exp(interpreter, num_val):
    """Exponential function."""
    num = num_val.value if hasattr(num_val, 'value') else num_val
    return RuntimeValue(math.exp(num))


def std_math_pi(interpreter):
    """Return the value of pi."""
    return RuntimeValue(math.pi)


def std_math_e(interpreter):
    """Return the value of e."""
    return RuntimeValue(math.e)


def std_math_random(interpreter):
    """Generate a random number between 0 and 1."""
    import random
    return RuntimeValue(random.random())


def register_math_functions(interpreter):
    """Register math utility functions with the interpreter."""
    interpreter.global_env.define("abs", std_math_abs)
    interpreter.global_env.define("floor", std_math_floor)
    interpreter.global_env.define("ceil", std_math_ceil)
    interpreter.global_env.define("round", std_math_round)
    interpreter.global_env.define("sqrt", std_math_sqrt)
    interpreter.global_env.define("pow", std_math_pow)
    interpreter.global_env.define("min", std_math_min)
    interpreter.global_env.define("max", std_math_max)
    interpreter.global_env.define("sin", std_math_sin)
    interpreter.global_env.define("cos", std_math_cos)
    interpreter.global_env.define("tan", std_math_tan)
    interpreter.global_env.define("log", std_math_log)
    interpreter.global_env.define("exp", std_math_exp)
    interpreter.global_env.define("pi", RuntimeValue(math.pi))
    interpreter.global_env.define("e", RuntimeValue(math.e))
    interpreter.global_env.define("random", std_math_random)