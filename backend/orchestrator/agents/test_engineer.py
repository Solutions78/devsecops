from __future__ import annotations

from ..models import AgentOutput, Task
from .base import BaseAgent


class TestEngineerAgent(BaseAgent):
    """Agent that generates or validates tests."""

    async def run(self, task: Task) -> AgentOutput:
        await self.emit_status("running", "Generating tests")
        result = {"generated_tests_for": task.files}
        return AgentOutput(agent_name=self.name, task_id=task.task_id, result=result)
