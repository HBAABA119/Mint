"""
Prim Actor Model
Provides actor-based concurrency, message passing, actor lifecycle management,
supervision trees, and distributed actor support.
"""

import threading
import queue
import time
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, field
from enum import Enum


class ActorState(Enum):
    """Actor states"""
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    STOPPED = "stopped"
    FAILED = "failed"


class SupervisorStrategy(Enum):
    """Supervision strategies"""
    ONE_FOR_ONE = "one_for_one"
    ONE_FOR_ALL = "one_for_all"
    RESTART = "restart"
    ESCALATE = "escalate"


@dataclass
class Message:
    """Message passed between actors"""
    sender: Optional['Actor']
    type: str
    data: Any = None
    reply_to: Optional['Actor'] = None


class Actor:
    """Base actor class"""

    def __init__(self, name: str):
        self.name = name
        self.state = ActorState.STOPPED
        self.mailbox: queue.Queue = queue.Queue()
        self.thread: Optional[threading.Thread] = None
        self.handlers: Dict[str, Callable] = {}
        self.supervisor: Optional['Actor'] = None
        self.children: List['Actor'] = []

    def on_start(self):
        """Called when actor starts"""
        pass

    def on_stop(self):
        """Called when actor stops"""
        pass

    def on_message(self, message: Message):
        """Handle incoming message"""
        handler = self.handlers.get(message.type)
        if handler:
            handler(message)

    def on_error(self, error: Exception):
        """Handle errors"""
        print(f"Actor {self.name} error: {error}")

    def receive(self) -> Optional[Message]:
        """Receive a message from mailbox"""
        try:
            return self.mailbox.get_nowait()
        except queue.Empty:
            return None

    def send(self, message: Message):
        """Send a message to this actor"""
        self.mailbox.put(message)

    def tell(self, message_type: str, data: Any = None, reply_to: Optional['Actor'] = None):
        """Send a message to this actor"""
        message = Message(sender=None, type=message_type, data=data, reply_to=reply_to)
        self.send(message)

    def ask(self, message_type: str, data: Any = None, timeout: float = 5.0) -> Any:
        """Send message and wait for reply"""
        reply_channel = queue.Queue()
        message = Message(sender=None, type=message_type, data=data, reply_to=ReplyActor(reply_channel))
        self.send(message)

        try:
            return reply_channel.get(timeout=timeout)
        except queue.Empty:
            raise TimeoutError("Actor did not reply in time")

    def start(self):
        """Start the actor"""
        self.state = ActorState.STARTING
        self.thread = threading.Thread(target=self._run)
        self.thread.start()
        self.state = ActorState.RUNNING
        self.on_start()

    def stop(self):
        """Stop the actor"""
        self.state = ActorState.STOPPING
        for child in self.children:
            child.stop()
        self.state = ActorState.STOPPED
        self.on_stop()

    def _run(self):
        """Main actor loop"""
        while self.state == ActorState.RUNNING:
            message = self.receive()
            if message:
                try:
                    self.on_message(message)
                except Exception as e:
                    self.on_error(e)

    def spawn(self, actor_class, name: str, *args, **kwargs) -> 'Actor':
        """Spawn a child actor"""
        actor = actor_class(name, *args, **kwargs)
        actor.supervisor = self
        self.children.append(actor)
        actor.start()
        return actor


class ReplyActor(Actor):
    """Actor for reply channels"""

    def __init__(self, reply_channel: queue.Queue):
        super().__init__("reply")
        self.reply_channel = reply_channel

    def on_message(self, message: Message):
        """Forward reply to channel"""
        self.reply_channel.put(message.data)


class Supervisor(Actor):
    """Supervisor actor"""

    def __init__(self, name: str, strategy: SupervisorStrategy = SupervisorStrategy.ONE_FOR_ONE):
        super().__init__(name)
        self.strategy = strategy
        self.restart_policy = {}

    def supervise(self, actor: Actor, restart_policy: str = "permanent"):
        """Add actor to supervision"""
        self.restart_policy[actor.name] = restart_policy

    def on_error(self, error: Exception):
        """Handle child errors"""
        if self.strategy == SupervisorStrategy.ONE_FOR_ONE:
            # Restart only the failed actor
            pass
        elif self.strategy == SupervisorStrategy.ONE_FOR_ALL:
            # Restart all children
            for child in self.children:
                child.stop()
                child.start()


class ActorSystem:
    """Actor system for managing actors"""

    def __init__(self, name: str = "default"):
        self.name = name
        self.actors: Dict[str, Actor] = {}
        self.root_supervisor = Supervisor("root")

    def actor_of(self, props: 'Props', name: str) -> Actor:
        """Create an actor"""
        actor = props.create(name)
        actor.supervisor = self.root_supervisor
        self.actors[name] = actor
        actor.start()
        return actor

    def get_actor(self, name: str) -> Optional[Actor]:
        """Get an actor by name"""
        return self.actors.get(name)

    def stop(self):
        """Stop all actors"""
        for actor in self.actors.values():
            actor.stop()


class Props:
    """Actor properties"""

    def __init__(self, creator: Callable, dispatcher: Optional[str] = None):
        self.creator = creator
        self.dispatcher = dispatcher

    def create(self, name: str) -> Actor:
        """Create actor from props"""
        return self.creator(name)


def props(creator: Callable, dispatcher: Optional[str] = None) -> Props:
    """Create actor props"""
    return Props(creator, dispatcher)


class ActorRef:
    """Reference to an actor"""

    def __init__(self, actor: Actor):
        self.actor = actor

    def tell(self, message_type: str, data: Any = None):
        """Send message to actor"""
        self.actor.tell(message_type, data)

    def ask(self, message_type: str, data: Any = None, timeout: float = 5.0) -> Any:
        """Send message and wait for reply"""
        return self.actor.ask(message_type, data, timeout)

    def stop(self):
        """Stop the actor"""
        self.actor.stop()


def actor_system(name: str = "default") -> ActorSystem:
    """Create an actor system"""
    return ActorSystem(name)


class DistributedActor(Actor):
    """Distributed actor for remote communication"""

    def __init__(self, name: str, address: str, port: int):
        super().__init__(name)
        self.address = address
        self.port = port
        self.remote_actors: Dict[str, ActorRef] = {}

    def connect_to(self, address: str, port: int) -> ActorRef:
        """Connect to remote actor"""
        # In a real implementation, this would establish network connection
        return ActorRef(self)

    def send_remote(self, actor_name: str, message: Message):
        """Send message to remote actor"""
        # In a real implementation, this would send over network
        pass


class ActorSelection:
    """Selection of actors"""

    def __init__(self, system: ActorSystem, path: str):
        self.system = system
        self.path = path

    def actor(self) -> Optional[ActorRef]:
        """Get actor reference"""
        actor = self.system.get_actor(self.path)
        return ActorRef(actor) if actor else None


def actor_selection(system: ActorSystem, path: str) -> ActorSelection:
    """Create actor selection"""
    return ActorSelection(system, path)


class DeadLetterOffice(Actor):
    """Handles undeliverable messages"""

    def __init__(self):
        super().__init__("dead_letters")
        self.undelivered: List[Message] = []

    def on_message(self, message: Message):
        """Handle undelivered message"""
        self.undelivered.append(message)
        print(f"Dead letter: {message.type} from {message.sender}")


def main():
    """Main entry point for testing"""
    # Create actor system
    system = actor_system("test_system")

    # Define a simple actor
    class EchoActor(Actor):
        def __init__(self, name: str):
            super().__init__(name)

        def on_message(self, message: Message):
            if message.type == "echo":
                print(f"Echo: {message.data}")
            elif message.type == "ping":
                if message.reply_to:
                    message.reply_to.tell("pong", "pong")

    # Create actor
    echo = system.actor_of(props(EchoActor), "echo")

    # Send messages
    echo.tell("echo", "Hello World")

    # Ask pattern
    reply = echo.ask("ping", "ping")
    print(f"Reply: {reply}")

    # Stop system
    system.stop()

    print("\nActor model initialized successfully")


if __name__ == "__main__":
    main()
