from __future__ import annotations

import abc
from typing import Optional

# Support both package and standalone execution contexts
try:
    from ..models import AgentOutput, Task  # type: ignore
    from ..event_bus import EventBus  # type: ignore
except ImportError:  # Fallback when 'agents' is imported as top-level
    from backend.orchestrator.models import AgentOutput, Task  # type: ignore
    from backend.orchestrator.event_bus import EventBus  # type: ignore


class BaseAgent(abc.ABC):
    """Base class for Claude agents."""

    def __init__(self, name: str | None = None, event_bus: Optional[EventBus] = None) -> None:
        # Default to the concrete class name when not provided. This is
        # convenient for external unit-tests that instantiate an agent without
        # caring about its runtime registration name.
        self.name = name or self.__class__.__name__
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
