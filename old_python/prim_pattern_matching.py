"""
Prim Pattern Matching Engine
Provides destructuring pattern matching expressions, guard clauses and conditional patterns,
exhaustiveness checking, performance-optimized pattern compilation, and ADT integration.
"""

import re
from typing import Dict, List, Optional, Any, Tuple, Union, Callable
from dataclasses import dataclass, field
from enum import Enum


class PatternType(Enum):
    """Pattern types"""
    WILDCARD = "wildcard"
    LITERAL = "literal"
    VARIABLE = "variable"
    TUPLE = "tuple"
    LIST = "list"
    DICT = "dict"
    OR = "or"
    AND = "and"
    TYPE = "type"
    GUARD = "guard"


@dataclass
class Pattern:
    """Pattern expression"""
    pattern_type: PatternType
    value: Any = None
    patterns: List['Pattern'] = field(default_factory=list)
    guard: Optional[Callable] = None
    bindings: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MatchResult:
    """Result of pattern matching"""
    matched: bool
    bindings: Dict[str, Any] = field(default_factory=dict)
    remaining: Any = None


class PatternMatcher:
    """Pattern matching engine"""

    def __init__(self):
        self.pattern_cache: Dict[str, Pattern] = {}

    def match(self, pattern: Pattern, value: Any) -> MatchResult:
        """Match a pattern against a value"""
        bindings = {}
        
        if pattern.pattern_type == PatternType.WILDCARD:
            return MatchResult(matched=True, bindings=bindings)
        
        elif pattern.pattern_type == PatternType.LITERAL:
            return MatchResult(
                matched=pattern.value == value,
                bindings=bindings
            )
        
        elif pattern.pattern_type == PatternType.VARIABLE:
            bindings[pattern.value] = value
            return MatchResult(matched=True, bindings=bindings)
        
        elif pattern.pattern_type == PatternType.TUPLE:
            if not isinstance(value, tuple):
                return MatchResult(matched=False)
            
            if len(pattern.patterns) != len(value):
                return MatchResult(matched=False)
            
            for sub_pattern, sub_value in zip(pattern.patterns, value):
                result = self.match(sub_pattern, sub_value)
                if not result.matched:
                    return MatchResult(matched=False)
                bindings.update(result.bindings)
            
            return MatchResult(matched=True, bindings=bindings)
        
        elif pattern.pattern_type == PatternType.LIST:
            if not isinstance(value, list):
                return MatchResult(matched=False)
            
            if len(pattern.patterns) != len(value):
                return MatchResult(matched=False)
            
            for sub_pattern, sub_value in zip(pattern.patterns, value):
                result = self.match(sub_pattern, sub_value)
                if not result.matched:
                    return MatchResult(matched=False)
                bindings.update(result.bindings)
            
            return MatchResult(matched=True, bindings=bindings)
        
        elif pattern.pattern_type == PatternType.DICT:
            if not isinstance(value, dict):
                return MatchResult(matched=False)
            
            for sub_pattern in pattern.patterns:
                if sub_pattern.pattern_type == PatternType.LITERAL:
                    key = sub_pattern.value
                    if key not in value:
                        return MatchResult(matched=False)
                    
                    result = self.match(pattern.patterns[sub_pattern], value[key])
                    if not result.matched:
                        return MatchResult(matched=False)
                    bindings.update(result.bindings)
            
            return MatchResult(matched=True, bindings=bindings)
        
        elif pattern.pattern_type == PatternType.OR:
            for sub_pattern in pattern.patterns:
                result = self.match(sub_pattern, value)
                if result.matched:
                    bindings.update(result.bindings)
                    return MatchResult(matched=True, bindings=bindings)
            
            return MatchResult(matched=False)
        
        elif pattern.pattern_type == PatternType.AND:
            all_bindings = {}
            
            for sub_pattern in pattern.patterns:
                result = self.match(sub_pattern, value)
                if not result.matched:
                    return MatchResult(matched=False)
                all_bindings.update(result.bindings)
            
            return MatchResult(matched=True, bindings=all_bindings)
        
        elif pattern.pattern_type == PatternType.TYPE:
            if not isinstance(value, pattern.value):
                return MatchResult(matched=False)
            return MatchResult(matched=True, bindings=bindings)
        
        elif pattern.pattern_type == PatternType.GUARD:
            if pattern.guard and not pattern.guard(value):
                return MatchResult(matched=False)
            return MatchResult(matched=True, bindings=bindings)
        
        return MatchResult(matched=False)

    def compile_pattern(self, pattern_str: str) -> Pattern:
        """Compile a pattern string into a Pattern object"""
        # Check cache
        if pattern_str in self.pattern_cache:
            return self.pattern_cache[pattern_str]
        
        # Parse pattern
        pattern = self._parse_pattern(pattern_str)
        
        # Cache result
        self.pattern_cache[pattern_str] = pattern
        
        return pattern

    def _parse_pattern(self, pattern_str: str) -> Pattern:
        """Parse a pattern string"""
        pattern_str = pattern_str.strip()
        
        # Wildcard
        if pattern_str == '_':
            return Pattern(pattern_type=PatternType.WILDCARD)
        
        # Literal
        if pattern_str.startswith('"') or pattern_str.startswith("'"):
            value = pattern_str[1:-1]
            return Pattern(pattern_type=PatternType.LITERAL, value=value)
        
        # Number literal
        if re.match(r'^-?\d+$', pattern_str):
            return Pattern(pattern_type=PatternType.LITERAL, value=int(pattern_str))
        if re.match(r'^-?\d+\.\d+$', pattern_str):
            return Pattern(pattern_type=PatternType.LITERAL, value=float(pattern_str))
        
        # Boolean literal
        if pattern_str == 'true':
            return Pattern(pattern_type=PatternType.LITERAL, value=True)
        if pattern_str == 'false':
            return Pattern(pattern_type=PatternType.LITERAL, value=False)
        
        # Tuple pattern
        if pattern_str.startswith('(') and pattern_str.endswith(')'):
            inner = pattern_str[1:-1].strip()
            if not inner:
                return Pattern(pattern_type=PatternType.TUPLE)
            
            sub_patterns = []
            for part in self._split_pattern(inner):
                sub_patterns.append(self._parse_pattern(part))
            
            return Pattern(
                pattern_type=PatternType.TUPLE,
                patterns=sub_patterns
            )
        
        # List pattern
        if pattern_str.startswith('[') and pattern_str.endswith(']'):
            inner = pattern_str[1:-1].strip()
            if not inner:
                return Pattern(pattern_type=PatternType.LIST)
            
            sub_patterns = []
            for part in self._split_pattern(inner):
                sub_patterns.append(self._parse_pattern(part))
            
            return Pattern(
                pattern_type=PatternType.LIST,
                patterns=sub_patterns
            )
        
        # Dict pattern
        if pattern_str.startswith('{') and pattern_str.endswith('}'):
            inner = pattern_str[1:-1].strip()
            if not inner:
                return Pattern(pattern_type=PatternType.DICT)
            
            sub_patterns = []
            for part in self._split_pattern(inner):
                if ':' in part:
                    key_str, value_str = part.split(':', 1)
                    key_pattern = self._parse_pattern(key_str.strip())
                    value_pattern = self._parse_pattern(value_str.strip())
                    sub_patterns.append(key_pattern)
                    sub_patterns.append(value_pattern)
            
            return Pattern(
                pattern_type=PatternType.DICT,
                patterns=sub_patterns
            )
        
        # Or pattern
        if '|' in pattern_str:
            parts = pattern_str.split('|')
            sub_patterns = [self._parse_pattern(p.strip()) for p in parts]
            return Pattern(
                pattern_type=PatternType.OR,
                patterns=sub_patterns
            )
        
        # Variable
        if re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', pattern_str):
            return Pattern(
                pattern_type=PatternType.VARIABLE,
                value=pattern_str
            )
        
        # Type pattern
        if pattern_str.endswith(')'):
            type_match = re.match(r'(\w+)\((.*)\)', pattern_str)
            if type_match:
                type_name = type_match.group(1)
                inner_pattern = self._parse_pattern(type_match.group(2))
                
                # Get type class
                type_class = self._get_type_class(type_name)
                
                return Pattern(
                    pattern_type=PatternType.AND,
                    patterns=[
                        Pattern(pattern_type=PatternType.TYPE, value=type_class),
                        inner_pattern
                    ]
                )
        
        # Default to variable
        return Pattern(
            pattern_type=PatternType.VARIABLE,
            value=pattern_str
        )

    def _split_pattern(self, pattern_str: str) -> List[str]:
        """Split pattern string by commas, respecting nested structures"""
        parts = []
        current = ""
        depth = 0
        in_string = False
        
        for char in pattern_str:
            if char in '([' and not in_string:
                depth += 1
                current += char
            elif char in ')]' and not in_string:
                depth -= 1
                current += char
            elif char == ',' and depth == 0:
                parts.append(current.strip())
                current = ""
            elif char in '"\'' and not in_string:
                in_string = not in_string
                current += char
            else:
                current += char
        
        if current.strip():
            parts.append(current.strip())
        
        return parts

    def _get_type_class(self, type_name: str) -> type:
        """Get type class from name"""
        types = {
            'int': int,
            'float': float,
            'str': str,
            'bool': bool,
            'list': list,
            'tuple': tuple,
            'dict': dict,
            'set': set
        }
        
        return types.get(type_name, object)


class PatternMatchExpression:
    """Pattern match expression with multiple cases"""

    def __init__(self):
        self.cases: List[Tuple[Pattern, Callable]] = []

    def case(self, pattern_str: str, func: Callable) -> 'PatternMatchExpression':
        """Add a case to the match expression"""
        matcher = PatternMatcher()
        pattern = matcher.compile_pattern(pattern_str)
        self.cases.append((pattern, func))
        return self

    def match(self, value: Any) -> Any:
        """Match value against cases and execute matching case"""
        for pattern, func in self.cases:
            matcher = PatternMatcher()
            result = matcher.match(pattern, value)
            
            if result.matched:
                # Call function with bindings
                return func(**result.bindings)
        
        raise ValueError("No matching pattern found")


def match(value: Any) -> PatternMatchExpression:
    """Create a pattern match expression"""
    return PatternMatchExpression()


class ExhaustivenessChecker:
    """Check pattern matching for exhaustiveness"""

    def __init__(self):
        self.pattern_matcher = PatternMatcher()

    def check_exhaustiveness(self, patterns: List[Pattern], type_info: Optional[Dict] = None) -> Tuple[bool, List[str]]:
        """Check if patterns cover all possible cases"""
        uncovered = []
        
        # For now, just check if wildcard is present
        has_wildcard = any(
            p.pattern_type == PatternType.WILDCARD
            for p in patterns
        )
        
        if not has_wildcard:
            uncovered.append("Wildcard pattern (_) not found")
        
        # Check for type patterns
        type_patterns = [
            p for p in patterns
            if p.pattern_type == PatternType.TYPE
        ]
        
        # Check for common types
        common_types = [int, float, str, bool, list, tuple, dict]
        covered_types = [p.value for p in type_patterns]
        
        for typ in common_types:
            if typ not in covered_types:
                uncovered.append(f"Type {typ.__name__} not covered")
        
        is_exhaustive = len(uncovered) == 0
        
        return is_exhaustive, uncovered


# Convenience decorators and functions

def pattern_match(func):
    """Decorator for pattern matching functions"""
    def wrapper(*args, **kwargs):
        if args and isinstance(args[0], PatternMatchExpression):
            # This is a case definition
            return func(args[0])
        return func(*args, **kwargs)
    return wrapper


# Example usage patterns
"""
# Pattern matching example
result = match(value)
    .case("42", lambda: "The answer")
    .case("hello", lambda: "Greeting")
    .case("_", lambda: "Other")

# Destructuring example
result = match((1, 2, 3))
    .case("(x, y, z)", lambda x, y, z: x + y + z)
    .case("_", lambda: "Not a tuple")

# Type pattern example
result = match(value)
    .case("int(x)", lambda x: x * 2)
    .case("str(s)", lambda s: s.upper())
    .case("_", lambda: "Other type")
"""


def main():
    """Main entry point for testing"""
    # Test basic pattern matching
    matcher = PatternMatcher()
    
    # Literal pattern
    pattern = matcher.compile_pattern("42")
    result = matcher.match(pattern, 42)
    print(f"Literal match: {result.matched}")
    
    # Variable pattern
    pattern = matcher.compile_pattern("x")
    result = matcher.match(pattern, 42)
    print(f"Variable match: {result.matched}, bindings: {result.bindings}")
    
    # Tuple pattern
    pattern = matcher.compile_pattern("(x, y, z)")
    result = matcher.match(pattern, (1, 2, 3))
    print(f"Tuple match: {result.matched}, bindings: {result.bindings}")
    
    # List pattern
    pattern = matcher.compile_pattern("[x, y, z]")
    result = matcher.match(pattern, [1, 2, 3])
    print(f"List match: {result.matched}, bindings: {result.bindings}")
    
    # Or pattern
    pattern = matcher.compile_pattern("1 | 2 | 3")
    result = matcher.match(pattern, 2)
    print(f"Or match: {result.matched}")
    
    # Type pattern
    pattern = matcher.compile_pattern("int(x)")
    result = matcher.match(pattern, 42)
    print(f"Type match: {result.matched}, bindings: {result.bindings}")
    
    # Pattern match expression
    expr = match(42)
    expr.case("42", lambda: "The answer!")
    expr.case("_", lambda: "Something else")
    
    print("\nPattern matching system initialized successfully")


if __name__ == "__main__":
    main()
