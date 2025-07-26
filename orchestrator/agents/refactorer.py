from __future__ import annotations

from ..models import AgentOutput, Task
from .base import BaseAgent


class RefactorerAgent(BaseAgent):
    """Agent that proposes refactors."""

    async def run(self, task: Task) -> AgentOutput:
        await self.emit_status("running", "Proposing refactors")
        result = {"refactored_files": task.files}
        return AgentOutput(agent_name=self.name, task_id=task.task_id, result=result)
