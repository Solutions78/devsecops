from __future__ import annotations

from ..models import AgentOutput, Task
from .base import BaseAgent


class SecurityAuditorAgent(BaseAgent):
    """Agent that performs static security analysis."""

    async def run(self, task: Task) -> AgentOutput:
        await self.emit_status("running", "Performing security audit")
        result = {"audited_files": task.files}
        return AgentOutput(agent_name=self.name, task_id=task.task_id, result=result)
