from __future__ import annotations

import asyncio
from typing import Dict

from .event_bus import EventBus
from .models import AgentOutput, Task, AgentStatusEnum
from .agents.base import BaseAgent


class AgentManager:
    def __init__(self, event_bus: EventBus) -> None:
        self.event_bus = event_bus
        self.agents: Dict[str, BaseAgent] = {}
        self.status: Dict[str, AgentStatusEnum] = {}

    def register_agent(self, agent: BaseAgent) -> None:
        self.agents[agent.name] = agent
        self.status[agent.name] = AgentStatusEnum.idle

    async def run_task(self, agent_name: str, task: Task) -> AgentOutput:
        agent = self.agents[agent_name]
        self.status[agent_name] = AgentStatusEnum.running
        await agent.emit_status(AgentStatusEnum.running.value, f"Started task {task.task_id}")
        try:
            output = await agent.run(task)
            self.status[agent_name] = AgentStatusEnum.complete
            await agent.emit_status(AgentStatusEnum.complete.value, f"Completed task {task.task_id}")
            return output
        except Exception as exc:
            self.status[agent_name] = AgentStatusEnum.error
            await agent.emit_status(AgentStatusEnum.error.value, str(exc))
            raise
