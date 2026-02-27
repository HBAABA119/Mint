"""
Prim Language Async/Await Support (v0.4)

Implementation of async/await syntax and promise/future system for Prim.
"""

import asyncio
from typing import Any, Callable, Optional
from prim_interpreter import AstNode, NodeType, RuntimeValue, RuntimeEnvironment


class Promise:
    """Represents a promise/future in Prim."""
    
    def __init__(self, executor: Optional[Callable] = None):
        self.executor = executor
        self.result = None
        self.error = None
        self.is_resolved = False
        self.is_rejected = False
        self.on_resolve_callbacks = []
        self.on_reject_callbacks = []
        
        if executor:
            try:
                executor(self._resolve, self._reject)
            except Exception as e:
                self._reject(e)
    
    def _resolve(self, value):
        if self.is_resolved or self.is_rejected:
            return
        
        self.result = value
        self.is_resolved = True
        
        for callback in self.on_resolve_callbacks:
            callback(value)
    
    def _reject(self, error):
        if self.is_resolved or self.is_rejected:
            return
        
        self.error = error
        self.is_rejected = True
        
        for callback in self.on_reject_callbacks:
            callback(error)
    
    def then(self, on_resolve: Callable):
        if self.is_resolved:
            return on_resolve(self.result)
        elif self.is_rejected:
            # In a real implementation, we'd handle rejections properly
            return self
        else:
            self.on_resolve_callbacks.append(on_resolve)
            return self
    
    def catch(self, on_reject: Callable):
        if self.is_rejected:
            return on_reject(self.error)
        else:
            self.on_reject_callbacks.append(on_reject)
            return self


class AsyncRuntimeEnvironment(RuntimeEnvironment):
    """Extended environment with async capabilities."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.event_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.event_loop)
    
    def run_coroutine(self, coro):
        """Run a coroutine and return the result."""
        return self.event_loop.run_until_complete(coro)


class PrimAsyncInterpreter:
    """Enhanced interpreter with async/await support."""
    
    def __init__(self, base_interpreter):
        self.base_interpreter = base_interpreter
        self.async_env = AsyncRuntimeEnvironment(parent=base_interpreter.global_env)
        self._setup_async_builtins()
    
    def _setup_async_builtins(self):
        """Setup async-related built-in functions."""
        # Add async/await related functions to the environment
        self.async_env.define("async", RuntimeValue(self._builtin_async))
        self.async_env.define("await", RuntimeValue(self._builtin_await))
        self.async_env.define("promise", RuntimeValue(self.create_promise))
    
    def _builtin_async(self, *args):
        """Wrapper for async functions."""
        # In a real implementation, this would mark a function as async
        fn = args[0] if args else None
        if fn and callable(fn.value):
            # Mark the function as async
            def async_wrapper(*call_args):
                # In a real implementation, this would create a coroutine
                result = fn.value(*call_args)
                return RuntimeValue(Promise(lambda res, rej: res(result.value)))
            return RuntimeValue(async_wrapper)
        return RuntimeValue(None)
    
    def _builtin_await(self, promise_val):
        """Await a promise."""
        promise = promise_val.value
        if isinstance(promise, Promise):
            # In a real implementation, this would await the promise
            # For now, we'll simulate by returning the result directly
            if promise.is_resolved:
                return RuntimeValue(promise.result)
            elif promise.is_rejected:
                raise RuntimeError(f"Promise rejected: {promise.error}")
            else:
                # This is a simplification - in reality, await would suspend execution
                # until the promise resolves
                return RuntimeValue(promise.result if promise.result is not None else None)
        else:
            # If it's not a promise, just return the value
            return promise_val
    
    def create_promise(self, executor_fn):
        """Create a new promise."""
        def executor(resolve_cb, reject_cb):
            # Execute the promise executor function
            # Pass resolve and reject callbacks to the executor
            pass  # Simplified for now
        
        promise = Promise(executor)
        return RuntimeValue(promise)
    
    def evaluate_async(self, node: AstNode, env: RuntimeEnvironment):
        """Evaluate a node in an async context."""
        # This would handle async-specific AST nodes
        # For now, delegate to the base interpreter
        return self.base_interpreter.evaluate(node, env)


class AsyncAstNodeExtension:
    """Extensions to AST nodes to support async operations."""
    
    @staticmethod
    def create_async_function(parameters, body):
        """Create an async function AST node."""
        return AstNode(
            NodeType.LAMBDA,
            parameters=parameters,
            body=body,
            is_async=True  # Mark as async function
        )
    
    @staticmethod
    def create_await_expression(expression):
        """Create an await expression AST node."""
        return AstNode(
            NodeType.AWAIT_EXPRESSION,  # This would be a new node type
            expression=expression
        )


def extend_interpreter_with_async(interpreter):
    """Extend the base interpreter with async capabilities."""
    async_interpreter = PrimAsyncInterpreter(interpreter)
    
    # Add async-related built-ins to the global environment
    def builtin_async_fn(*args):
        # Creates an async version of a function
        if args:
            fn = args[0]
            # Mark function as async
            return fn  # Simplified
        return RuntimeValue(None)
    
    def builtin_await_val(promise_val):
        # Await a promise
        return async_interpreter._builtin_await(promise_val)
    
    interpreter.global_env.define("async", builtin_async_fn)
    interpreter.global_env.define("await", builtin_await_val)
    interpreter.global_env.define("Promise", async_interpreter.create_promise)


# Example usage and testing
if __name__ == "__main__":
    print("Prim Async/Await Support (v0.4) - Prototype")
    print("This implements async/await syntax and promise system for Prim.")
    
    # Example of how async/await might work (conceptual):
    print("\nConceptual examples:")
    print("# Async functions in different modes:")
    print("  #mode slim")
    print("  async fn fetch_data(url):")
    print("      response = await http_get(url)")
    print("      return response")
    print("")
    print("  #mode block")
    print("  async fn fetch_data(url) {")
    print("      var response = await http_get(url);")
    print("      return response;")
    print("  }")
    print("")
    print("  #mode flow")
    print("  fetch_data = async |url| -> await http_get(url)")
    print("")
    print("# Working with promises:")
    print("  #mode slim")
    print("  promise = Promise((resolve, reject) -> resolve('success'))")
    print("  result = await promise")
    print("  print(result)  # prints: success")