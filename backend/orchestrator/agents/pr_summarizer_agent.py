from __future__ import annotations

try:
    from ..models import AgentOutput, Task  # type: ignore
except ImportError:
    from backend.orchestrator.models import AgentOutput, Task  # type: ignore

from .base_agent import BaseAgent


class PRSummarizerAgent(BaseAgent):
    """Agent that summarizes pull requests."""

    async def run(self, task: Task) -> AgentOutput:
        await self.emit_status("running", "Summarizing PR")
        result = {"summary_for": task.params.get("pr", "")}
        return AgentOutput(agent_name=self.name, task_id=task.task_id, result=result)
