import asyncio
import pytest

from orchestrator.event_bus import EventBus


@pytest.mark.asyncio
async def test_event_bus_publish_subscribe():
    bus = EventBus()
    q1 = bus.subscribe()
    await bus.publish({"hello": "world"})
    event = await asyncio.wait_for(q1.get(), timeout=1)
    assert event == {"hello": "world"}
