"""
Prim Channel Types
Provides channel-based communication, buffered and unbuffered channels,
select statements, and channel closing semantics.
"""

import asyncio
import queue
from typing import Dict, List, Optional, Any, Callable, Generic, TypeVar
from dataclasses import dataclass, field
from enum import Enum
import threading


T = TypeVar('T')


class ChannelType(Enum):
    """Channel types"""
    UNBUFFERED = "unbuffered"
    BUFFERED = "buffered"
    RENDEZVOUS = "rendezvous"


class ChannelState(Enum):
    """Channel states"""
    OPEN = "open"
    CLOSED = "closed"
    DRAINING = "draining"


@dataclass
class SelectCase:
    """Case for select statement"""
    channel: 'Channel'
    direction: str  # "send" or "receive"
    value: Any = None
    callback: Optional[Callable] = None


class Channel(Generic[T]):
    """Channel for communication"""

    def __init__(self, max_size: int = 0, channel_type: ChannelType = ChannelType.UNBUFFERED):
        self.max_size = max_size
        self.channel_type = channel_type
        self.state = ChannelState.OPEN
        self.queue = queue.Queue(maxsize=max_size)
        self.senders: List[Callable] = []
        self.receivers: List[Callable] = []
        self.lock = threading.Lock()

    async def send(self, value: T) -> bool:
        """Send a value through the channel"""
        if self.state == ChannelState.CLOSED:
            raise RuntimeError("Channel is closed")

        if self.channel_type == ChannelType.UNBUFFERED:
            # Wait for a receiver
            await self._wait_for_receiver()
            if self.state == ChannelState.CLOSED:
                return False

        try:
            await asyncio.get_event_loop().run_in_executor(
                None, self.queue.put, value
            )
            return True
        except queue.Full:
            return False

    async def receive(self) -> Optional[T]:
        """Receive a value from the channel"""
        if self.state == ChannelState.CLOSED and self.queue.empty():
            return None

        try:
            value = await asyncio.get_event_loop().run_in_executor(
                None, self.queue.get
            )
            return value
        except queue.Empty:
            return None

    def close(self):
        """Close the channel"""
        with self.lock:
            self.state = ChannelState.CLOSED

    def is_closed(self) -> bool:
        """Check if channel is closed"""
        return self.state == ChannelState.CLOSED

    async def _wait_for_receiver(self):
        """Wait for a receiver (rendezvous)"""
        while self.state == ChannelState.OPEN and not self.receivers:
            await asyncio.sleep(0.001)

    def __repr__(self):
        return f"Channel(type={self.channel_type.value}, state={self.state.value})"


class BufferedChannel(Channel[T]):
    """Buffered channel"""

    def __init__(self, buffer_size: int):
        super().__init__(max_size=buffer_size, channel_type=ChannelType.BUFFERED)


class UnbufferedChannel(Channel[T]):
    """Unbuffered channel (rendezvous)"""

    def __init__(self):
        super().__init__(max_size=0, channel_type=ChannelType.UNBUFFERED)


class Select:
    """Select statement for channel operations"""

    def __init__(self):
        self.cases: List[SelectCase] = []
        self.default_case: Optional[Callable] = None

    def case(self, channel: Channel, direction: str, value: Any = None, callback: Optional[Callable] = None):
        """Add a case to the select"""
        self.cases.append(SelectCase(channel, direction, value, callback))
        return self

    def default(self, callback: Callable):
        """Set default case"""
        self.default_case = callback
        return self

    async def select(self) -> Any:
        """Select the first ready case"""
        for case in self.cases:
            if case.direction == "send":
                if case.channel.state != ChannelState.CLOSED:
                    try:
                        await case.channel.send(case.value)
                        if case.callback:
                            return await case.callback()
                        return True
                    except:
                        continue
            elif case.direction == "receive":
                value = await case.channel.receive()
                if value is not None:
                    if case.callback:
                        return await case.callback(value)
                    return value

        # Default case
        if self.default_case:
            return await self.default_case()

        return None


class ChannelGroup:
    """Group of channels for fan-in/fan-out"""

    def __init__(self):
        self.channels: Dict[str, Channel] = {}

    def add_channel(self, name: str, channel: Channel):
        """Add a channel to the group"""
        self.channels[name] = channel

    def get_channel(self, name: str) -> Optional[Channel]:
        """Get a channel by name"""
        return self.channels.get(name)

    def close_all(self):
        """Close all channels"""
        for channel in self.channels.values():
            channel.close()


class FanIn:
    """Fan-in pattern - multiple channels to one"""

    def __init__(self, output_channel: Channel):
        self.output_channel = output_channel
        self.input_channels: List[Channel] = []

    def add_input(self, channel: Channel):
        """Add an input channel"""
        self.input_channels.append(channel)

    async def fan_in(self):
        """Fan in from input channels to output"""
        tasks = []
        for channel in self.input_channels:
            task = asyncio.create_task(self._forward(channel))
            tasks.append(task)

        await asyncio.gather(*tasks)

    async def _forward(self, channel: Channel):
        """Forward values from channel to output"""
        while not channel.is_closed():
            value = await channel.receive()
            if value is not None:
                await self.output_channel.send(value)


class FanOut:
    """Fan-out pattern - one channel to multiple"""

    def __init__(self, input_channel: Channel):
        self.input_channel = input_channel
        self.output_channels: List[Channel] = []

    def add_output(self, channel: Channel):
        """Add an output channel"""
        self.output_channels.append(channel)

    async def fan_out(self):
        """Fan out from input to output channels"""
        while not self.input_channel.is_closed():
            value = await self.input_channel.receive()
            if value is not None:
                tasks = []
                for channel in self.output_channels:
                    task = asyncio.create_task(channel.send(value))
                    tasks.append(task)
                await asyncio.gather(*tasks)


class Pipeline:
    """Pipeline for chained channel operations"""

    def __init__(self):
        self.stages: List[tuple] = []

    def add_stage(self, channel: Channel, transform: Optional[Callable] = None):
        """Add a stage to the pipeline"""
        self.stages.append((channel, transform))
        return self

    async def process(self, input_value: Any):
        """Process through the pipeline"""
        value = input_value

        for channel, transform in self.stages:
            if transform:
                value = transform(value)

            await channel.send(value)

        return value


def channel(max_size: int = 0) -> Channel:
    """Create a channel"""
    return Channel(max_size=max_size)


def buffered_channel(buffer_size: int) -> BufferedChannel:
    """Create a buffered channel"""
    return BufferedChannel(buffer_size)


def unbuffered_channel() -> UnbufferedChannel:
    """Create an unbuffered channel"""
    return UnbufferedChannel()


def select() -> Select:
    """Create a select statement"""
    return Select()


def main():
    """Main entry point for testing"""
    print("Testing channels...")

    # Test unbuffered channel
    unbuffered = unbuffered_channel()

    async def test_unbuffered():
        async def sender():
            await unbuffered.send("Hello")
            await unbuffered.send("World")

        async def receiver():
            msg1 = await unbuffered.receive()
            msg2 = await unbuffered.receive()
            return f"{msg1} {msg2}"

        await sender()
        result = await receiver()
        print(f"Unbuffered: {result}")

    asyncio.run(test_unbuffered())

    # Test buffered channel
    buffered = buffered_channel(2)

    async def test_buffered():
        await buffered.send("A")
        await buffered.send("B")

        msg1 = await buffered.receive()
        msg2 = await buffered.receive()

        return f"{msg1}{msg2}"

    result = asyncio.run(test_buffered())
    print(f"Buffered: {result}")

    # Test select
    sel = select()

    async def test_select():
        ch1 = channel()
        ch2 = channel()

        await ch1.send("from ch1")

        result = await sel.case(ch1, "receive").select()
        print(f"Select result: {result}")

    asyncio.run(test_select())

    print("\nChannel types initialized successfully")


if __name__ == "__main__":
    main()
