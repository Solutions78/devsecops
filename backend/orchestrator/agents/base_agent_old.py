from __future__ import annotations

import abc
from typing import Optional

from ..models import AgentOutput, Task
from ..event_bus import EventBus


class BaseAgent(abc.ABC):
    """Base class for Claude agents."""

    def __init__(self, name: str, event_bus: Optional[EventBus] = None) -> None:
        self.name = name
        self.event_bus = event_bus

    async def emit_status(self, status: str, message: Optional[str] = None) -> None:
        if not self.event_bus:
            return
        from ..models import AgentStatusEnum, AgentUpdate

        update = AgentUpdate(agent_name=self.name, status=AgentStatusEnum(status), message=message)
        await self.event_bus.publish(update)

    @abc.abstractmethod
    async def run(self, task: Task) -> AgentOutput:
        """Run the agent on the given task."""
        raise NotImplementedError
