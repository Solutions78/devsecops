import asyncio
from typing import Any, Set


class EventBus:
    """A simple pub/sub event bus using asyncio queues.
    
    The EventBus implements a publish-subscribe pattern where components can
    subscribe to receive events and other components can publish events to
    all subscribers. It uses asyncio queues for thread-safe communication.
    
    Attributes:
        subscribers (Set[asyncio.Queue]): Set of queues representing active subscribers.
    
    Example:
        >>> bus = EventBus()
        >>> queue = bus.subscribe()
        >>> await bus.publish({"event": "test"})
        >>> event = await queue.get()
    """

    def __init__(self) -> None:
        """Initialize the EventBus with an empty set of subscribers."""
        self.subscribers: Set[asyncio.Queue] = set()

    def subscribe(self) -> asyncio.Queue:
        """Create a new subscription to the event bus.
        
        Creates a new asyncio queue and adds it to the subscribers set.
        Events published to the bus will be delivered to this queue.
        
        Returns:
            asyncio.Queue: A queue that will receive published events.
            
        Example:
            >>> queue = bus.subscribe()
            >>> # queue will now receive all published events
        """
        queue: asyncio.Queue = asyncio.Queue()
        self.subscribers.add(queue)
        return queue

    def unsubscribe(self, queue: asyncio.Queue) -> None:
        """Remove a subscription from the event bus.
        
        Removes the specified queue from the subscribers set. The queue
        will no longer receive published events. Uses discard() instead
        of remove() to avoid KeyError if queue is not in the set.
        
        Args:
            queue (asyncio.Queue): The queue to unsubscribe from events.
            
        Example:
            >>> queue = bus.subscribe()
            >>> bus.unsubscribe(queue)
            >>> # queue will no longer receive events
        """
        self.subscribers.discard(queue)

    async def publish(self, event: Any) -> None:
        """Publish an event to all subscribers.
        
        Sends the event to all currently subscribed queues. Creates a
        snapshot of subscribers using list() to avoid issues if the
        set changes during iteration.
        
        Args:
            event (Any): The event object to publish to all subscribers.
            
        Example:
            >>> await bus.publish({"type": "task_complete", "id": "123"})
            >>> # All subscribed queues will receive this event
        """
        for subscriber in list(self.subscribers):
            await subscriber.put(event)
