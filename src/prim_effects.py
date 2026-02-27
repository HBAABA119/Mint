"""
Prim Effect System
Provides explicit side effect tracking, pure function verification, effect polymorphism,
resource management effects, and async/await effect integration.
"""

from typing import Dict, List, Optional, Any, Callable, TypeVar, Union
from dataclasses import dataclass, field
from enum import Enum
from functools import wraps
import inspect


class EffectType(Enum):
    """Effect types"""
    PURE = "pure"
    IO = "io"
    STATE = "state"
    EXCEPTION = "exception"
    NONDET = "nondeterministic"
    ASYNC = "async"
    MUTABLE = "mutable"
    RESOURCE = "resource"


@dataclass
class Effect:
    """Effect annotation"""
    effect_type: EffectType
    description: str = ""
    dependencies: List['Effect'] = field(default_factory=list)


@dataclass
class EffectSignature:
    """Effect signature for a function"""
    name: str
    effects: List[Effect] = field(default_factory=list)
    pure: bool = True


class EffectTracker:
    """Track effects in code"""

    def __init__(self):
        self.function_effects: Dict[str, EffectSignature] = {}
        self.current_effects: List[Effect] = []

    def register_function(
        self,
        name: str,
        effects: List[Effect]
    ):
        """Register a function with its effects"""
        is_pure = all(e.effect_type == EffectType.PURE for e in effects)
        signature = EffectSignature(
            name=name,
            effects=effects,
            pure=is_pure
        )
        self.function_effects[name] = signature

    def get_function_effects(self, name: str) -> Optional[EffectSignature]:
        """Get effects for a function"""
        return self.function_effects.get(name)

    def is_pure(self, name: str) -> bool:
        """Check if a function is pure"""
        signature = self.function_effects.get(name)
        return signature.pure if signature else False

    def get_effect_types(self, name: str) -> List[EffectType]:
        """Get effect types for a function"""
        signature = self.function_effects.get(name)
        return [e.effect_type for e in signature.effects] if signature else []


class EffectChecker:
    """Check effects in code"""

    def __init__(self, tracker: EffectTracker):
        self.tracker = tracker

    def check_function_purity(self, func: Callable) -> bool:
        """Check if a function is pure"""
        # Get source code
        source = inspect.getsource(func)

        # Check for impure operations
        impure_patterns = [
            r'\bprint\s*\(',
            r'\bopen\s*\(',
            r'\binput\s*\(',
            r'\bimport\s+',
            r'\b__import__\s*\(',
            r'\beval\s*\(',
            r'\bexec\s*\(',
            r'\bexit\s*\(',
            r'\bquit\s*\(',
            r'\bglobals\s*\(\)',
            r'\blocals\s*\(\)',
            r'\bsetattr\s*\(',
            r'\bdelattr\s*\(',
        ]

        for pattern in impure_patterns:
            if re.search(pattern, source):
                return False

        # Check for mutable default arguments
        sig = inspect.signature(func)
        for param in sig.parameters.values():
            if param.default is not inspect.Parameter.empty:
                if isinstance(param.default, (list, dict, set)):
                    return False

        return True

    def infer_effects(self, func: Callable) -> List[Effect]:
        """Infer effects from function body"""
        effects = []
        source = inspect.getsource(func)

        # I/O effects
        if re.search(r'\b(print|input|open)\s*\(', source):
            effects.append(Effect(EffectType.IO, "I/O operation"))

        # State effects
        if re.search(r'\b(global|nonlocal)\s+', source):
            effects.append(Effect(EffectType.STATE, "State mutation"))

        # Exception effects
        if re.search(r'\b(raise|try|except|finally)\s+', source):
            effects.append(Effect(EffectType.EXCEPTION, "Exception handling"))

        # Async effects
        if re.search(r'\b(async|await)\s+', source):
            effects.append(Effect(EffectType.ASYNC, "Async operation"))

        # Mutable effects
        if re.search(r'\b(setattr|delattr|del\s+\w+)\s+', source):
            effects.append(Effect(EffectType.MUTABLE, "Mutation"))

        # Resource effects
        if re.search(r'\b(open|close)\s*\(', source):
            effects.append(Effect(EffectType.RESOURCE, "Resource management"))

        if not effects:
            effects.append(Effect(EffectType.PURE, "Pure function"))

        return effects


class EffectSystem:
    """Main effect system"""

    def __init__(self):
        self.tracker = EffectTracker()
        self.checker = EffectChecker(self.tracker)
        self.pure_functions: List[str] = []

    def register_function(
        self,
        func: Callable,
        effects: Optional[List[Effect]] = None
    ):
        """Register a function with its effects"""
        name = func.__name__

        if effects is None:
            effects = self.checker.infer_effects(func)

        self.tracker.register_function(name, effects)

        if self.tracker.is_pure(name):
            self.pure_functions.append(name)

    def verify_pure(self, func: Callable) -> bool:
        """Verify that a function is pure"""
        return self.checker.check_function_purity(func)

    def get_function_signature(self, name: str) -> Optional[EffectSignature]:
        """Get effect signature for a function"""
        return self.tracker.get_function_effects(name)

    def list_pure_functions(self) -> List[str]:
        """List all pure functions"""
        return self.pure_functions.copy()

    def list_impure_functions(self) -> List[str]:
        """List all impure functions"""
        return [
            name for name, sig in self.tracker.function_effects.items()
            if not sig.pure
        ]


# Decorators

def pure(func):
    """Decorator to mark a function as pure"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    wrapper._effect_pure = True
    return wrapper


def io(func):
    """Decorator to mark a function as having I/O effects"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    wrapper._effect_io = True
    return wrapper


def state(func):
    """Decorator to mark a function as having state effects"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    wrapper._effect_state = True
    return wrapper


def effect(*effect_types):
    """Decorator to specify effects"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        wrapper._effects = list(effect_types)
        return wrapper
    return decorator


class Resource:
    """Resource with effect tracking"""

    def __init__(self, name: str, acquire_func: Callable, release_func: Callable):
        self.name = name
        self.acquire_func = acquire_func
        self.release_func = release_func
        self.acquired = False

    def acquire(self) -> Any:
        """Acquire the resource"""
        if self.acquired:
            raise RuntimeError(f"Resource {self.name} already acquired")

        result = self.acquire_func()
        self.acquired = True
        return result

    def release(self):
        """Release the resource"""
        if not self.acquired:
            raise RuntimeError(f"Resource {self.name} not acquired")

        self.release_func()
        self.acquired = False

    def __enter__(self):
        return self.acquire()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()
        return False


class ResourceManager:
    """Manage resources with effect tracking"""

    def __init__(self):
        self.resources: Dict[str, Resource] = {}

    def register_resource(
        self,
        name: str,
        acquire_func: Callable,
        release_func: Callable
    ):
        """Register a resource"""
        self.resources[name] = Resource(name, acquire_func, release_func)

    def get_resource(self, name: str) -> Optional[Resource]:
        """Get a resource"""
        return self.resources.get(name)

    def with_resource(self, name: str, func: Callable) -> Any:
        """Execute a function with a resource"""
        resource = self.get_resource(name)
        if not resource:
            raise ValueError(f"Resource not found: {name}")

        with resource:
            return func()


class EffectPolymorphism:
    """Effect polymorphism support"""

    def __init__(self):
        self.effect_handlers: Dict[EffectType, Callable] = {}

    def register_handler(
        self,
        effect_type: EffectType,
        handler: Callable
    ):
        """Register an effect handler"""
        self.effect_handlers[effect_type] = handler

    def handle_effect(
        self,
        effect: Effect,
        *args,
        **kwargs
    ) -> Any:
        """Handle an effect"""
        handler = self.effect_handlers.get(effect.effect_type)
        if not handler:
            raise ValueError(f"No handler for effect: {effect.effect_type}")

        return handler(effect, *args, **kwargs)


class AsyncEffectIntegration:
    """Integration with async/await"""

    def __init__(self):
        self.async_effects: Dict[str, List[Effect]] = {}

    def register_async_function(
        self,
        name: str,
        effects: List[Effect]
    ):
        """Register an async function with effects"""
        self.async_effects[name] = effects

    def get_async_effects(self, name: str) -> List[Effect]:
        """Get effects for an async function"""
        return self.async_effects.get(name, [])


def main():
    """Main entry point for testing"""
    system = EffectSystem()

    # Test pure function
    @pure
    def add(x: int, y: int) -> int:
        return x + y

    system.register_function(add)
    print(f"add is pure: {system.tracker.is_pure('add')}")

    # Test I/O function
    @io
    def greet(name: str) -> str:
        print(f"Hello, {name}!")
        return f"Hello, {name}!"

    system.register_function(greet)
    print(f"greet is pure: {system.tracker.is_pure('greet')}")

    # Test resource management
    def acquire_file():
        print("Acquiring file...")
        return open("test.txt", "w")

    def release_file(f):
        print("Releasing file...")
        f.close()

    manager = ResourceManager()
    manager.register_resource("file", acquire_file, release_file)

    print("\nEffect system initialized successfully")
    print(f"Pure functions: {system.list_pure_functions()}")
    print(f"Impure functions: {system.list_impure_functions()}")


if __name__ == "__main__":
    main()
