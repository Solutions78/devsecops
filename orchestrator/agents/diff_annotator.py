from __future__ import annotations

from ..models import AgentOutput, Task
from .base import BaseAgent


class DiffAnnotatorAgent(BaseAgent):
    """Agent that explains diffs between commits."""

    async def run(self, task: Task) -> AgentOutput:
        await self.emit_status("running", "Annotating diffs")
        result = {"annotated_diff": task.params.get("diff", "")}
        return AgentOutput(agent_name=self.name, task_id=task.task_id, result=result)
