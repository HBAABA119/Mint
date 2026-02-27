"""
Prim Reactive Programming
Provides reactive streams, event handlers, observable patterns,
backpressure handling, and reactive operators.
"""

import threading
import queue
import time
from typing import List, Dict, Any, Optional, Callable, TypeVar, Generic
from dataclasses import dataclass, field
from enum import Enum

T = TypeVar('T')


class StreamState(Enum):
    """Stream states"""
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ERROR = "error"


@dataclass
class Event:
    """Event"""
    type: str
    data: Any = None
    timestamp: float = field(default_factory=time.time)


class Observable(Generic[T]):
    """Observable stream"""

    def __init__(self):
        self.subscribers: List[Callable[[T], None]] = []
        self.state = StreamState.ACTIVE
        self.buffer: List[T] = []
        self.buffer_size = 1000
        self.error: Optional[Exception] = None

    def subscribe(self, observer: Callable[[T], None]) -> 'Subscription':
        """Subscribe to observable"""
        self.subscribers.append(observer)

        # Emit buffered values
        for value in self.buffer:
            observer(value)

        return Subscription(self, observer)

    def next(self, value: T):
        """Emit next value"""
        if self.state != StreamState.ACTIVE:
            return

        self.buffer.append(value)

        # Maintain buffer size
        if len(self.buffer) > self.buffer_size:
            self.buffer = self.buffer[-self.buffer_size:]

        # Notify subscribers
        for subscriber in self.subscribers:
            try:
                subscriber(value)
            except Exception as e:
                self.error = e
                self.state = StreamState.ERROR

    def complete(self):
        """Complete stream"""
        self.state = StreamState.COMPLETED

    def error(self, exception: Exception):
        """Emit error"""
        self.error = exception
        self.state = StreamState.ERROR

    def map(self, transform: Callable[[T], Any]) -> 'Observable':
        """Map operator"""
        result = Observable()

        def observer(value):
            transformed = transform(value)
            result.next(transformed)

        self.subscribe(observer)
        return result

    def filter(self, predicate: Callable[[T], bool]) -> 'Observable':
        """Filter operator"""
        result = Observable()

        def observer(value):
            if predicate(value):
                result.next(value)

        self.subscribe(observer)
        return result

    def reduce(self, accumulator: Callable[[Any, T], Any],
              initial: Any) -> Observable:
        """Reduce operator"""
        result = Observable()
        acc = initial

        def observer(value):
            nonlocal acc
            acc = accumulator(acc, value)
            result.next(acc)

        self.subscribe(observer)
        return result

    def scan(self, accumulator: Callable[[Any, T], Any],
            initial: Any) -> 'Observable':
        """Scan operator"""
        result = Observable()
        acc = initial

        def observer(value):
            nonlocal acc
            acc = accumulator(acc, value)
            result.next(acc)

        self.subscribe(observer)
        return result

    def debounce(self, delay: float) -> 'Observable':
        """Debounce operator"""
        result = Observable()
        last_value = None
        last_time = 0

        def observer(value):
            nonlocal last_value, last_time
            last_value = value
            last_time = time.time()

            def delayed_emit():
                if time.time() - last_time >= delay:
                    result.next(last_value)

            threading.Timer(delay, delayed_emit).start()

        self.subscribe(observer)
        return result

    def throttle(self, interval: float) -> 'Observable':
        """Throttle operator"""
        result = Observable()
        last_emit = 0

        def observer(value):
            nonlocal last_emit
            now = time.time()

            if now - last_emit >= interval:
                result.next(value)
                last_emit = now

        self.subscribe(observer)
        return result


class Subscription:
    """Subscription"""

    def __init__(self, observable: Observable, observer: Callable[[T], None]):
        self.observable = observable
        self.observer = observer
        self.active = True

    def unsubscribe(self):
        """Unsubscribe from observable"""
        if self.active and self.observer in self.observable.subscribers:
            self.observable.subscribers.remove(self.observer)
        self.active = False


class Subject(Observable):
    """Subject"""

    def __init__(self):
        super().__init__()
        self.current_value: Optional[Any] = None

    def next(self, value: Any):
        """Emit next value"""
        self.current_value = value
        super().next(value)

    def as_observable(self) -> Observable:
        """Convert to observable"""
        return self


class BehaviorSubject(Subject):
    """Behavior subject with initial value"""

    def __init__(self, initial_value: Any):
        super().__init__()
        self.current_value = initial_value

    def get_value(self) -> Any:
        """Get current value"""
        return self.current_value


class ReplaySubject(Subject):
    """Replay subject"""

    def __init__(self, buffer_size: int = 10):
        super().__init__()
        self.buffer_size = buffer_size

    def next(self, value: Any):
        """Emit next value"""
        super().next(value)


class EventStream:
    """Event stream"""

    def __init__(self, name: str = "stream"):
        self.name = name
        self.observable = Observable()
        self.handlers: Dict[str, List[Callable]] = {}

    def on(self, event_type: str, handler: Callable):
        """Register event handler"""
        if event_type not in self.handlers:
            self.handlers[event_type] = []
        self.handlers[event_type].append(handler)

    def emit(self, event: Event):
        """Emit event"""
        if event.type in self.handlers:
            for handler in self.handlers[event.type]:
                handler(event)

    def to_observable(self) -> Observable:
        """Convert to observable"""
        return self.observable


class BackpressureHandler:
    """Backpressure handling"""

    def __init__(self, buffer_size: int = 1000):
        self.buffer_size = buffer_size
        self.buffer: queue.Queue = queue.Queue(maxsize=buffer_size)
        self.dropped = 0

    def push(self, value: Any) -> bool:
        """Push value to buffer"""
        try:
            self.buffer.put_nowait(value)
            return True
        except queue.Full:
            self.dropped += 1
            return False

    def pull(self) -> Optional[Any]:
        """Pull value from buffer"""
        try:
            return self.buffer.get_nowait()
        except queue.Empty:
            return None

    def get_stats(self) -> Dict[str, int]:
        """Get backpressure stats"""
        return {
            "buffer_size": self.buffer.qsize(),
            "dropped": self.dropped
        }


class ReactivePipeline:
    """Reactive pipeline"""

    def __init__(self):
        self.stages: List[Callable] = []
        self.observable: Optional[Observable] = None

    def add_stage(self, stage: Callable):
        """Add pipeline stage"""
        self.stages.append(stage)

    def build(self) -> Observable:
        """Build pipeline"""
        if not self.stages:
            raise RuntimeError("No stages defined")

        observable = Observable()

        # Connect stages
        current = observable
        for stage in self.stages:
            current = stage(current)

        self.observable = current
        return self.observable

    def execute(self, source: Observable) -> Observable:
        """Execute pipeline"""
        pipeline = self.build()

        def observer(value):
            pipeline.next(value)

        source.subscribe(observer)
        return pipeline


def create_observable() -> Observable:
    """Create observable"""
    return Observable()


def create_subject() -> Subject:
    """Create subject"""
    return Subject()


def main():
    """Main entry point for testing"""
    print("Testing Reactive Programming...")

    # Test Observable
    observable = create_observable()

    def observer(value):
        print(f"Received: {value}")

    subscription = observable.subscribe(observer)

    observable.next(1)
    observable.next(2)
    observable.next(3)

    # Test operators
    mapped = observable.map(lambda x: x * 2)
    filtered = mapped.filter(lambda x: x > 2)

    filtered.subscribe(observer)

    filtered.next(1)
    filtered.next(2)
    filtered.next(3)

    subscription.unsubscribe()

    # Test Subject
    subject = create_subject()
    subject.subscribe(observer)

    subject.next(10)
    subject.next(20)

    # Test Event Stream
    event_stream = EventStream("test_stream")

    def handler(event):
        print(f"Event: {event.type}")

    event_stream.on("test", handler)
    event_stream.emit(Event(type="test", data="data"))

    # Test Backpressure
    bp = BackpressureHandler(buffer_size=10)
    for i in range(15):
        bp.push(i)

    stats = bp.get_stats()
    print(f"Backpressure: {stats}")

    print("\nReactive Programming initialized successfully")


if __name__ == "__main__":
    main()
