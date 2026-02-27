"""
Prim Concurrency Primitives
Provides async/await syntax, channel types, actor model, and runtime scheduling.
"""

import asyncio
from typing import Dict, List, Optional, Any, Callable, Coroutine
from dataclasses import dataclass, field
from enum import Enum
import threading
import queue


class ConcurrencyMode(Enum):
    """Concurrency modes"""
    ASYNC_AWAIT = "async_await"
    CHANNELS = "channels"
    ACTORS = "actors"
    THREADS = "threads"


@dataclass
class Promise:
    """Promise/Future for async operations"""
    result: Any = None
    error: Optional[Exception] = None
    completed: bool = False
    callbacks: List[Callable] = field(default_factory=list)

    def then(self, callback: Callable) -> 'Promise':
        """Chain a callback"""
        if self.completed:
            callback(self.result if self.error is None else None)
        else:
            self.callbacks.append(callback)
        return self

    def resolve(self, result: Any):
        """Resolve the promise"""
        self.result = result
        self.completed = True
        for callback in self.callbacks:
            callback(result)

    def reject(self, error: Exception):
        """Reject the promise"""
        self.error = error
        self.completed = True


class AsyncContext:
    """Async context manager for async/await"""

    def __init__(self):
        self.event_loop = asyncio.new_event_loop()

    async def run_async(self, coro: Coroutine) -> Any:
        """Run async coroutine"""
        return await coro

    def run(self, coro: Coroutine) -> Any:
        """Run coroutine in event loop"""
        return self.event_loop.run_until_complete(coro)


def async_func(func):
    """Decorator for async functions"""
    async def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper


def await_expr(coro: Coroutine) -> Any:
    """Await expression"""
    # This would be used in the language's await syntax
    # For now, it's a placeholder
    return coro


class Channel:
    """Channel for communication between coroutines"""

    def __init__(self, max_size: int = 0):
        self.queue = queue.Queue(maxsize=max_size)
        self.closed = False

    async def send(self, value: Any):
        """Send a value through the channel"""
        if self.closed:
            raise RuntimeError("Channel is closed")
        await asyncio.get_event_loop().run_in_executor(
            None, self.queue.put, value
        )

    async def receive(self) -> Any:
        """Receive a value from the channel"""
        if self.closed and self.queue.empty():
            raise RuntimeError("Channel is closed")
        return await asyncio.get_event_loop().run_in_executor(
            None, self.queue.get
        )

    def close(self):
        """Close the channel"""
        self.closed = True

    def is_closed(self) -> bool:
        """Check if channel is closed"""
        return self.closed


class Actor:
    """Actor for message-based concurrency"""

    def __init__(self, name: str):
        self.name = name
        self.mailbox = queue.Queue()
        self.running = False
        self.thread: Optional[threading.Thread] = None
        self.handlers: Dict[str, Callable] = {}

    def on(self, message_type: str, handler: Callable):
        """Register a message handler"""
        self.handlers[message_type] = handler

    async def send(self, message_type: str, *args, **kwargs):
        """Send a message to the actor"""
        await asyncio.get_event_loop().run_in_executor(
            None, self.mailbox.put, (message_type, args, kwargs)
        )

    def receive(self) -> Optional[tuple]:
        """Receive a message from the mailbox"""
        try:
            return self.mailbox.get_nowait()
        except queue.Empty:
            return None

    def process_messages(self):
        """Process all messages in the mailbox"""
        while self.running:
            msg = self.receive()
            if msg is None:
                break

            message_type, args, kwargs = msg
            handler = self.handlers.get(message_type)

            if handler:
                try:
                    handler(*args, **kwargs)
                except Exception as e:
                    print(f"Error processing message: {e}")

    def start(self):
        """Start the actor"""
        self.running = True
        self.thread = threading.Thread(target=self.process_messages)
        self.thread.start()

    def stop(self):
        """Stop the actor"""
        self.running = False
        if self.thread:
            self.thread.join()


class ActorSystem:
    """System for managing actors"""

    def __init__(self):
        self.actors: Dict[str, Actor] = {}

    def create_actor(self, name: str) -> Actor:
        """Create a new actor"""
        actor = Actor(name)
        self.actors[name] = actor
        return actor

    def get_actor(self, name: str) -> Optional[Actor]:
        """Get an actor by name"""
        return self.actors.get(name)

    def stop_all(self):
        """Stop all actors"""
        for actor in self.actors.values():
            actor.stop()


class Scheduler:
    """Runtime scheduler for coroutines"""

    def __init__(self):
        self.event_loop = asyncio.new_event_loop()
        self.tasks: List[asyncio.Task] = []

    async def schedule(self, coro: Coroutine):
        """Schedule a coroutine"""
        task = asyncio.create_task(coro)
        self.tasks.append(task)
        return await task

    def run(self):
        """Run the scheduler"""
        asyncio.set_event_loop(self.event_loop)
        self.event_loop.run_forever()

    def stop(self):
        """Stop the scheduler"""
        for task in self.tasks:
            task.cancel()
        self.event_loop.stop()


class ConcurrencyPrimitives:
    """All concurrency primitives"""

    def __init__(self):
        self.async_context = AsyncContext()
        self.actor_system = ActorSystem()
        self.scheduler = Scheduler()

    def create_channel(self, max_size: int = 0) -> Channel:
        """Create a channel"""
        return Channel(max_size)

    def create_actor(self, name: str) -> Actor:
        """Create an actor"""
        return self.actor_system.create_actor(name)

    def async_function(self, func: Callable) -> Callable:
        """Create an async function"""
        return async_func(func)

    def run_async(self, coro: Coroutine) -> Any:
        """Run an async coroutine"""
        return self.async_context.run(coro)


def main():
    """Main entry point for testing"""
    primitives = ConcurrencyPrimitives()

    # Test async/await
    @primitives.async_function
    async def example_async():
        await asyncio.sleep(0.1)
        return "Hello from async!"

    print("Testing async/await...")
    result = primitives.async_context.run(example_async())
    print(f"Result: {result}")

    # Test channels
    print("\nTesting channels...")
    channel = primitives.create_channel()

    async def sender():
        await channel.send("Hello")
        await channel.send("World")

    async def receiver():
        msg1 = await channel.receive()
        msg2 = await channel.receive()
        return f"{msg1} {msg2}"

    result = primitives.async_context.run(sender())
    result = primitives.async_context.run(receiver())
    print(f"Channel result: {result}")

    # Test actors
    print("\nTesting actors...")
    actor = primitives.create_actor("test_actor")

    def handle_greet(name):
        print(f"Hello, {name}!")

    actor.on("greet", handle_greet)
    actor.start()

    async def send_message():
        await actor.send("greet", "World")

    primitives.async_context.run(send_message())
    actor.stop()

    print("\nConcurrency primitives initialized successfully")


if __name__ == "__main__":
    main()
