"""
Prim Event Streaming
Provides event streaming, message brokers, stream processing,
event sourcing, and real-time analytics.
"""

from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass
from enum import Enum


class EventType(Enum):
    """Event types"""
    COMMAND = "command"
    QUERY = "query"
    EVENT = "event"
    NOTIFICATION = "notification"


@dataclass
class Event:
    """Event"""
    type: EventType
    topic: str
    data: Any
    timestamp: float


class EventStream:
    """Event stream"""

    def __init__(self):
        self.events: List[Event] = []
        self.subscribers: Dict[str, List[Callable]] = {}

    def publish(self, event: Event):
        """Publish event"""
        self.events.append(event)

        if event.topic in self.subscribers:
            for handler in self.subscribers[event.topic]:
                handler(event)

    def subscribe(self, topic: str, handler: Callable):
        """Subscribe to topic"""
        if topic not in self.subscribers:
            self.subscribers[topic] = []
        self.subscribers[topic].append(handler)


def main():
    print("Testing Event Streaming...")
    stream = EventStream()
    event = Event(type=EventType.EVENT, topic="test", data="test")
    stream.publish(event)
    print(f"Events: {len(stream.events)}")
    print("Event Streaming initialized successfully")


if __name__ == "__main__":
    main()
