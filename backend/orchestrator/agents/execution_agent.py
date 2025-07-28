from __future__ import annotations

try:
    from ..models import AgentOutput, Task  # type: ignore
except ImportError:
    from backend.orchestrator.models import AgentOutput, Task  # type: ignore

from .base_agent import BaseAgent


class ExecutionAgent(BaseAgent):
    """Agent that executes code or tests in a sandbox."""

    async def run(self, task: Task) -> AgentOutput:
        await self.emit_status("running", "Executing code")
        result = {"executed_files": task.files}
        return AgentOutput(agent_name=self.name, task_id=task.task_id, result=result)
