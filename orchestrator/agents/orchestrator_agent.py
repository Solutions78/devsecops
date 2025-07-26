from __future__ import annotations

from ..models import AgentOutput, Task
from .base import BaseAgent


class OrchestratorAgent(BaseAgent):
    """Central control agent orchestrating other agents."""

    async def run(self, task: Task) -> AgentOutput:
        await self.emit_status("running", "Coordinating workflow")
        result = {"orchestrated_task": task.intent}
        return AgentOutput(agent_name=self.name, task_id=task.task_id, result=result)
