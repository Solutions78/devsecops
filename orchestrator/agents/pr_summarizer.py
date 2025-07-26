from __future__ import annotations

from ..models import AgentOutput, Task
from .base import BaseAgent


class PRSummarizerAgent(BaseAgent):
    """Agent that summarizes pull requests."""

    async def run(self, task: Task) -> AgentOutput:
        await self.emit_status("running", "Summarizing PR")
        result = {"summary_for": task.params.get("pr", "")}
        return AgentOutput(agent_name=self.name, task_id=task.task_id, result=result)
