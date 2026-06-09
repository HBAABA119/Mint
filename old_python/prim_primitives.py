"""
Prim Essential Primitives
Provides native data structure implementations, string and collection types,
numeric type system, boolean and control flow primitives, and basic type conversion utilities.
"""

from typing import Dict, List, Optional, Any, Union, Callable, TypeVar, Generic
from dataclasses import dataclass, field
from enum import Enum
import math


class PrimType(Enum):
    """Prim type system"""
    NULL = "null"
    BOOLEAN = "boolean"
    INTEGER = "integer"
    FLOAT = "float"
    STRING = "string"
    LIST = "list"
    DICT = "dict"
    FUNCTION = "function"
    OBJECT = "object"


@dataclass
class PrimValue:
    """Prim value container"""
    type: PrimType
    value: Any
    metadata: Dict[str, Any] = field(default_factory=dict)

    def is_truthy(self) -> bool:
        """Check if value is truthy"""
        if self.type == PrimType.NULL:
            return False
        elif self.type == PrimType.BOOLEAN:
            return self.value
        elif self.type in [PrimType.INTEGER, PrimType.FLOAT]:
            return self.value != 0
        elif self.type == PrimType.STRING:
            return len(self.value) > 0
        elif self.type == PrimType.LIST:
            return len(self.value) > 0
        elif self.type == PrimType.DICT:
            return len(self.value) > 0
        return True

    def to_string(self) -> str:
        """Convert to string"""
        if self.type == PrimType.NULL:
            return "null"
        elif self.type == PrimType.BOOLEAN:
            return "true" if self.value else "false"
        elif self.type == PrimType.INTEGER:
            return str(self.value)
        elif self.type == PrimType.FLOAT:
            return str(self.value)
        elif self.type == PrimType.STRING:
            return self.value
        elif self.type == PrimType.LIST:
            return f"[{', '.join(str(v) for v in self.value)}]"
        elif self.type == PrimType.DICT:
            return f"{{{', '.join(f'{k}: {v}' for k, v in self.value.items())}}}"
        return str(self.value)


class StringOperations:
    """String operations"""

    @staticmethod
    def upper(s: str) -> str:
        """Convert to uppercase"""
        return s.upper()

    @staticmethod
    def lower(s: str) -> str:
        """Convert to lowercase"""
        return s.lower()

    @staticmethod
    def split(s: str, delimiter: str = " ") -> List[str]:
        """Split string"""
        return s.split(delimiter)

    @staticmethod
    def join(parts: List[str], separator: str = "") -> str:
        """Join parts"""
        return separator.join(parts)

    @staticmethod
    def trim(s: str) -> str:
        """Trim whitespace"""
        return s.strip()

    @staticmethod
    def length(s: str) -> int:
        """Get string length"""
        return len(s)

    @staticmethod
    def contains(s: str, substring: str) -> bool:
        """Check if string contains substring"""
        return substring in s

    @staticmethod
    def replace(s: str, old: str, new: str) -> str:
        """Replace substring"""
        return s.replace(old, new)

    @staticmethod
    def slice(s: str, start: int, end: Optional[int] = None) -> str:
        """Slice string"""
        if end is None:
            return s[start:]
        return s[start:end]


class CollectionOperations:
    """Collection operations"""

    @staticmethod
    def map(collection: List, func: Callable) -> List:
        """Map function over collection"""
        return [func(item) for item in collection]

    @staticmethod
    def filter(collection: List, func: Callable) -> List:
        """Filter collection"""
        return [item for item in collection if func(item)]

    @staticmethod
    def reduce(collection: List, func: Callable, initial: Optional[Any] = None) -> Any:
        """Reduce collection"""
        if initial is not None:
            result = initial
            for item in collection:
                result = func(result, item)
            return result
        elif collection:
            result = collection[0]
            for item in collection[1:]:
                result = func(result, item)
            return result
        return None

    @staticmethod
    def length(collection: List) -> int:
        """Get collection length"""
        return len(collection)

    @staticmethod
    def contains(collection: List, item: Any) -> bool:
        """Check if collection contains item"""
        return item in collection

    @staticmethod
    def append(collection: List, item: Any) -> List:
        """Append item to collection"""
        return collection + [item]

    @staticmethod
    def extend(collection: List, items: List) -> List:
        """Extend collection with items"""
        return collection + items

    @staticmethod
    def reverse(collection: List) -> List:
        """Reverse collection"""
        return collection[::-1]

    @staticmethod
    def sort(collection: List, key: Optional[Callable] = None) -> List:
        """Sort collection"""
        return sorted(collection, key=key)


class NumericOperations:
    """Numeric operations"""

    @staticmethod
    def add(a: Union[int, float], b: Union[int, float]) -> Union[int, float]:
        """Add two numbers"""
        return a + b

    @staticmethod
    def subtract(a: Union[int, float], b: Union[int, float]) -> Union[int, float]:
        """Subtract two numbers"""
        return a - b

    @staticmethod
    def multiply(a: Union[int, float], b: Union[int, float]) -> Union[int, float]:
        """Multiply two numbers"""
        return a * b

    @staticmethod
    def divide(a: Union[int, float], b: Union[int, float]) -> float:
        """Divide two numbers"""
        return a / b

    @staticmethod
    def floor(a: float) -> int:
        """Floor a number"""
        return math.floor(a)

    @staticmethod
    def ceil(a: float) -> int:
        """Ceil a number"""
        return math.ceil(a)

    @staticmethod
    def round_number(a: float, precision: int = 0) -> float:
        """Round a number"""
        return round(a, precision)

    @staticmethod
    def abs(a: Union[int, float]) -> Union[int, float]:
        """Absolute value"""
        return abs(a)

    @staticmethod
    def min(*values: Union[int, float]) -> Union[int, float]:
        """Minimum value"""
        return min(values)

    @staticmethod
    def max(*values: Union[int, float]) -> Union[int, float]:
        """Maximum value"""
        return max(values)

    @staticmethod
    def sum(values: List[Union[int, float]]) -> Union[int, float]:
        """Sum values"""
        return sum(values)


class BooleanOperations:
    """Boolean operations"""

    @staticmethod
    def and_op(a: bool, b: bool) -> bool:
        """Logical AND"""
        return a and b

    @staticmethod
    def or_op(a: bool, b: bool) -> bool:
        """Logical OR"""
        return a or b

    @staticmethod
    def not_op(a: bool) -> bool:
        """Logical NOT"""
        return not a

    @staticmethod
    def equal(a: Any, b: Any) -> bool:
        """Equality check"""
        return a == b

    @staticmethod
    def not_equal(a: Any, b: Any) -> bool:
        """Inequality check"""
        return a != b

    @staticmethod
    def less(a: Union[int, float], b: Union[int, float]) -> bool:
        """Less than"""
        return a < b

    @staticmethod
    def less_equal(a: Union[int, float], b: Union[int, float]) -> bool:
        """Less than or equal"""
        return a <= b

    @staticmethod
    def greater(a: Union[int, float], b: Union[int, float]) -> bool:
        """Greater than"""
        return a > b

    @staticmethod
    def greater_equal(a: Union[int, float], b: Union[int, float]) -> bool:
        """Greater than or equal"""
        return a >= b


class TypeConversion:
    """Type conversion utilities"""

    @staticmethod
    def to_string(value: Any) -> str:
        """Convert to string"""
        return str(value)

    @staticmethod
    def to_int(value: Any) -> int:
        """Convert to integer"""
        if isinstance(value, str):
            return int(value)
        return int(value)

    @staticmethod
    def to_float(value: Any) -> float:
        """Convert to float"""
        if isinstance(value, str):
            return float(value)
        return float(value)

    @staticmethod
    def to_bool(value: Any) -> bool:
        """Convert to boolean"""
        return bool(value)

    @staticmethod
    def to_list(value: Any) -> List:
        """Convert to list"""
        if isinstance(value, str):
            return list(value)
        return list(value)

    @staticmethod
    def to_dict(value: Any) -> Dict:
        """Convert to dict"""
        if isinstance(value, dict):
            return dict(value)
        return dict(value)

    @staticmethod
    def get_type(value: Any) -> PrimType:
        """Get type of value"""
        if value is None:
            return PrimType.NULL
        elif isinstance(value, bool):
            return PrimType.BOOLEAN
        elif isinstance(value, int):
            return PrimType.INTEGER
        elif isinstance(value, float):
            return PrimType.FLOAT
        elif isinstance(value, str):
            return PrimType.STRING
        elif isinstance(value, list):
            return PrimType.LIST
        elif isinstance(value, dict):
            return PrimType.DICT
        elif callable(value):
            return PrimType.FUNCTION
        return PrimType.OBJECT


class ControlFlow:
    """Control flow primitives"""

    @staticmethod
    def if_then_else(
        condition: bool,
        then_expr: Any,
        else_expr: Any
    ) -> Any:
        """If-then-else expression"""
        return then_expr if condition else else_expr

    @staticmethod
    def loop(
        iterable: Any,
        body: Callable,
        initial: Optional[Any] = None
    ) -> Any:
        """Loop over iterable"""
        result = initial
        for item in iterable:
            result = body(item, result)
        return result

    @staticmethod
    def while_loop(
        condition: Callable,
        body: Callable,
        initial: Optional[Any] = None
    ) -> Any:
        """While loop"""
        result = initial
        while condition():
            result = body(result)
        return result


class Primitives:
    """All Prim primitives"""

    def __init__(self):
        self.strings = StringOperations()
        self.collections = CollectionOperations()
        self.numeric = NumericOperations()
        self.booleans = BooleanOperations()
        self.conversion = TypeConversion()
        self.control = ControlFlow()

    def create_value(self, value: Any) -> PrimValue:
        """Create a Prim value"""
        prim_type = self.conversion.get_type(value)
        return PrimValue(type=prim_type, value=value)

    def is_type(self, value: Any, expected_type: PrimType) -> bool:
        """Check if value is of expected type"""
        actual_type = self.conversion.get_type(value)
        return actual_type == expected_type


# Standard library integration

def register_primitives(runtime):
    """Register primitives with runtime"""
    primitives = Primitives()

    # Register string operations
    runtime.register_function('str_upper', primitives.strings.upper)
    runtime.register_function('str_lower', primitives.strings.lower)
    runtime.register_function('str_split', primitives.strings.split)
    runtime.register_function('str_join', primitives.strings.join)
    runtime.register_function('str_trim', primitives.strings.trim)
    runtime.register_function('str_length', primitives.strings.length)

    # Register collection operations
    runtime.register_function('map', primitives.collections.map)
    runtime.register_function('filter', primitives.collections.filter)
    runtime.register_function('reduce', primitives.collections.reduce)
    runtime.register_function('len', primitives.collections.length)

    # Register numeric operations
    runtime.register_function('add', primitives.numeric.add)
    runtime.register_function('subtract', primitives.numeric.subtract)
    runtime.register_function('multiply', primitives.numeric.multiply)
    runtime.register_function('divide', primitives.numeric.divide)
    runtime.register_function('floor', primitives.numeric.floor)
    runtime.register_function('ceil', primitives.numeric.ceil)

    # Register boolean operations
    runtime.register_function('and', primitives.booleans.and_op)
    runtime.register_function('or', primitives.booleans.or_op)
    runtime.register_function('not', primitives.booleans.not_op)

    # Register type conversion
    runtime.register_function('str', primitives.conversion.to_string)
    runtime.register_function('int', primitives.conversion.to_int)
    runtime.register_function('float', primitives.conversion.to_float)
    runtime.register_function('bool', primitives.conversion.to_bool)


def main():
    """Main entry point for testing"""
    primitives = Primitives()

    # Test string operations
    s = "Hello World"
    print(f"Upper: {primitives.strings.upper(s)}")
    print(f"Lower: {primitives.strings.lower(s)}")
    print(f"Split: {primitives.strings.split(s)}")
    print(f"Length: {primitives.strings.length(s)}")

    # Test numeric operations
    a, b = 10, 5
    print(f"Add: {primitives.numeric.add(a, b)}")
    print(f"Subtract: {primitives.numeric.subtract(a, b)}")
    print(f"Multiply: {primitives.numeric.multiply(a, b)}")
    print(f"Divide: {primitives.numeric.divide(a, b)}")

    # Test boolean operations
    print(f"AND: {primitives.booleans.and_op(True, False)}")
    print(f"OR: {primitives.booleans.or_op(True, False)}")
    print(f"NOT: {primitives.booleans.not_op(True)}")

    # Test collection operations
    nums = [1, 2, 3, 4, 5]
    print(f"Map: {primitives.collections.map(nums, lambda x: x * 2)}")
    print(f"Filter: {primitives.collections.filter(nums, lambda x: x > 2)}")
    print(f"Reduce: {primitives.collections.reduce(nums, lambda a, b: a + b)}")

    # Test type conversion
    print(f"String to Int: {primitives.conversion.to_int('42')}")
    print(f"Int to String: {primitives.conversion.to_string(42)}")

    print("\nEssential Primitives initialized successfully")


if __name__ == "__main__":
    main()
