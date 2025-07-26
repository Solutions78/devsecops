from __future__ import annotations

from ..models import AgentOutput, Task
from .base import BaseAgent


class ExecutionAgent(BaseAgent):
    """Agent that executes code or tests in a sandbox."""

    async def run(self, task: Task) -> AgentOutput:
        await self.emit_status("running", "Executing code")
        result = {"executed_files": task.files}
        return AgentOutput(agent_name=self.name, task_id=task.task_id, result=result)
