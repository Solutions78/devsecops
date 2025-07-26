from __future__ import annotations

from ..models import AgentOutput, Task
from .base import BaseAgent


class CodeReviewAgent(BaseAgent):
    """Agent that performs basic code review."""

    async def run(self, task: Task) -> AgentOutput:
        await self.emit_status("running", f"Reviewing {len(task.files)} files")
        result = {"reviewed_files": task.files, "intent": task.intent}
        return AgentOutput(agent_name=self.name, task_id=task.task_id, result=result)
