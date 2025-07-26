import asyncio
from typing import Any, Set


class EventBus:
    """A simple pub/sub event bus using asyncio queues."""

    def __init__(self) -> None:
        self.subscribers: Set[asyncio.Queue] = set()

    def subscribe(self) -> asyncio.Queue:
        queue: asyncio.Queue = asyncio.Queue()
        self.subscribers.add(queue)
        return queue

    def unsubscribe(self, queue: asyncio.Queue) -> None:
        self.subscribers.discard(queue)

    async def publish(self, event: Any) -> None:
        for subscriber in list(self.subscribers):
            await subscriber.put(event)
