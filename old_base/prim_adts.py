"""
Prim Algebraic Data Types
Provides sum types (union types), product types (structs/tuples), discriminated unions,
pattern matching integration, and type-safe enum implementations.
"""

from typing import Dict, List, Optional, Any, Union, TypeVar, Generic
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod


T = TypeVar('T')
U = TypeVar('U')


class ADTType(Enum):
    """ADT type categories"""
    SUM = "sum"
    PRODUCT = "product"
    ENUM = "enum"


@dataclass
class Variant:
    """Variant of a sum type"""
    name: str
    fields: Dict[str, type] = field(default_factory=dict)


@dataclass
class SumType:
    """Sum type (union type) definition"""
    name: str
    variants: Dict[str, Variant] = field(default_factory=dict)
    type_params: List[str] = field(default_factory=list)

    def add_variant(self, name: str, fields: Optional[Dict[str, type]] = None):
        """Add a variant to the sum type"""
        self.variants[name] = Variant(name=name, fields=fields or {})

    def create_variant(self, variant_name: str, **kwargs) -> 'SumValue':
        """Create a value of a specific variant"""
        if variant_name not in self.variants:
            raise ValueError(f"Unknown variant: {variant_name}")

        variant = self.variants[variant_name]

        # Validate field types
        for field_name, field_value in kwargs.items():
            if field_name not in variant.fields:
                raise ValueError(f"Unknown field: {field_name}")

        return SumValue(
            type_name=self.name,
            variant_name=variant_name,
            value=kwargs
        )


@dataclass
class SumValue:
    """Value of a sum type"""
    type_name: str
    variant_name: str
    value: Dict[str, Any]

    def match(self, **cases) -> Any:
        """Pattern match on the sum value"""
        variant_name = self.variant_name

        if variant_name in cases:
            return cases[variant_name](self.value)

        if '_' in cases:
            return cases['_'](self.value)

        raise ValueError(f"No matching case for variant: {variant_name}")


@dataclass
class ProductType:
    """Product type (struct/tuple) definition"""
    name: str
    fields: Dict[str, type] = field(default_factory=dict)
    type_params: List[str] = field(default_factory=list)

    def add_field(self, name: str, field_type: type):
        """Add a field to the product type"""
        self.fields[name] = field_type

    def create(self, **kwargs) -> 'ProductValue':
        """Create a value of the product type"""
        # Validate field types
        for field_name, field_value in kwargs.items():
            if field_name not in self.fields:
                raise ValueError(f"Unknown field: {field_name}")

            expected_type = self.fields[field_name]
            if not isinstance(field_value, expected_type):
                raise TypeError(
                    f"Expected type {expected_type} for field {field_name}, got {type(field_value)}"
                )

        return ProductValue(
            type_name=self.name,
            value=kwargs
        )


@dataclass
class ProductValue:
    """Value of a product type"""
    type_name: str
    value: Dict[str, Any]

    def get(self, field_name: str) -> Any:
        """Get a field value"""
        if field_name not in self.value:
            raise AttributeError(f"Field not found: {field_name}")
        return self.value[field_name]

    def set(self, field_name: str, value: Any):
        """Set a field value"""
        if field_name not in self.value:
            raise AttributeError(f"Field not found: {field_name}")
        self.value[field_name] = value


class EnumType:
    """Type-safe enum implementation"""

    def __init__(self, name: str, values: List[str]):
        self.name = name
        self._values = {v: i for i, v in enumerate(values)}
        self._reverse_values = {i: v for i, v in enumerate(values)}

    def create(self, value: str) -> 'EnumValue':
        """Create an enum value"""
        if value not in self._values:
            raise ValueError(f"Invalid enum value: {value}")
        return EnumValue(type_name=self.name, value=value)

    def from_index(self, index: int) -> 'EnumValue':
        """Create enum value from index"""
        if index not in self._reverse_values:
            raise ValueError(f"Invalid enum index: {index}")
        return EnumValue(type_name=self.name, value=self._reverse_values[index])

    def values(self) -> List[str]:
        """Get all enum values"""
        return list(self._values.keys())


@dataclass
class EnumValue:
    """Value of an enum type"""
    type_name: str
    value: str

    def __eq__(self, other):
        if not isinstance(other, EnumValue):
            return False
        return self.type_name == other.type_name and self.value == other.value

    def __hash__(self):
        return hash((self.type_name, self.value))

    def __repr__(self):
        return f"{self.type_name}.{self.value}"


class ADTRegistry:
    """Registry for ADT definitions"""

    def __init__(self):
        self.sum_types: Dict[str, SumType] = {}
        self.product_types: Dict[str, ProductType] = {}
        self.enum_types: Dict[str, EnumType] = {}

    def define_sum_type(
        self,
        name: str,
        variants: List[tuple],
        type_params: Optional[List[str]] = None
    ) -> SumType:
        """Define a sum type"""
        sum_type = SumType(name=name, type_params=type_params or [])

        for variant_def in variants:
            if isinstance(variant_def, str):
                # Simple variant with no fields
                sum_type.add_variant(variant_def)
            elif isinstance(variant_def, tuple):
                # Variant with fields
                variant_name = variant_def[0]
                fields = variant_def[1] if len(variant_def) > 1 else {}
                sum_type.add_variant(variant_name, fields)

        self.sum_types[name] = sum_type
        return sum_type

    def define_product_type(
        self,
        name: str,
        fields: Dict[str, type],
        type_params: Optional[List[str]] = None
    ) -> ProductType:
        """Define a product type"""
        product_type = ProductType(name=name, fields=fields, type_params=type_params or [])

        self.product_types[name] = product_type
        return product_type

    def define_enum_type(self, name: str, values: List[str]) -> EnumType:
        """Define an enum type"""
        enum_type = EnumType(name=name, values=values)
        self.enum_types[name] = enum_type
        return enum_type

    def get_sum_type(self, name: str) -> Optional[SumType]:
        """Get a sum type by name"""
        return self.sum_types.get(name)

    def get_product_type(self, name: str) -> Optional[ProductType]:
        """Get a product type by name"""
        return self.product_types.get(name)

    def get_enum_type(self, name: str) -> Optional[EnumType]:
        """Get an enum type by name"""
        return self.enum_types.get(name)


# Convenience decorators and functions

def sum_type(name: str, variants: List[tuple]):
    """Decorator to define a sum type"""
    def decorator(cls):
        cls._adt_type = 'sum'
        cls._adt_name = name
        cls._adt_variants = variants
        return cls
    return decorator


def product_type(name: str, fields: Dict[str, type]):
    """Decorator to define a product type"""
    def decorator(cls):
        cls._adt_type = 'product'
        cls._adt_name = name
        cls._adt_fields = fields
        return cls
    return decorator


def enum_type(name: str, values: List[str]):
    """Decorator to define an enum type"""
    def decorator(cls):
        cls._adt_type = 'enum'
        cls._adt_name = name
        cls._adt_values = values
        return cls
    return decorator


class ADTBuilder:
    """Builder for creating ADTs"""

    def __init__(self):
        self.registry = ADTRegistry()

    def sum(self, name: str, *variants) -> SumType:
        """Define a sum type"""
        variant_list = []
        for v in variants:
            if isinstance(v, str):
                variant_list.append(v)
            elif isinstance(v, tuple):
                variant_list.append(v)

        return self.registry.define_sum_type(name, variant_list)

    def product(self, name: str, **fields) -> ProductType:
        """Define a product type"""
        return self.registry.define_product_type(name, fields)

    def enum(self, name: str, *values) -> EnumType:
        """Define an enum type"""
        return self.registry.define_enum_type(name, list(values))


# Example usage patterns
"""
# Define a sum type (Option/Maybe)
Option = adt.sum("Option",
    ("Some", {"value": object}),
    "None"
)

# Create values
some_value = Option.create_variant("Some", value=42)
none_value = Option.create_variant("None")

# Pattern match
result = some_value.match(
    Some=lambda v: v["value"] * 2,
    None=lambda: 0
)

# Define a product type (struct)
Point = adt.product("Point", x=int, y=int)

# Create value
point = Point.create(x=10, y=20)

# Access fields
x = point.get("x")

# Define an enum
Color = adt.enum("Color", "Red", "Green", "Blue")

# Create value
red = Color.create("Red")
"""


def main():
    """Main entry point for testing"""
    builder = ADTBuilder()

    # Test sum type
    Option = builder.sum("Option",
        ("Some", {"value": object}),
        "None"
    )

    some = Option.create_variant("Some", value=42)
    none = Option.create_variant("None")

    print("Sum type test:")
    print(f"Some: {some}")
    print(f"None: {none}")

    result = some.match(
        Some=lambda v: v["value"] * 2,
        none=lambda: 0
    )
    print(f"Match result: {result}")

    # Test product type
    Point = builder.product("Point", x=int, y=int)
    point = Point.create(x=10, y=20)

    print("\nProduct type test:")
    print(f"Point: {point}")
    print(f"X: {point.get('x')}, Y: {point.get('y')}")

    # Test enum
    Color = builder.enum("Color", "Red", "Green", "Blue")
    red = Color.create("Red")

    print("\nEnum test:")
    print(f"Color: {red}")
    print(f"Values: {Color.values()}")

    print("\nADT system initialized successfully")


if __name__ == "__main__":
    main()
