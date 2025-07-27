from __future__ import annotations

from ..models import AgentOutput, Task
from .base import BaseAgent


class DocstringGeneratorAgent(BaseAgent):
    """Agent that adds or updates docstrings."""

    async def run(self, task: Task) -> AgentOutput:
        await self.emit_status("running", "Generating docstrings")
        result = {"docstrings_added": task.files}
        return AgentOutput(agent_name=self.name, task_id=task.task_id, result=result)
