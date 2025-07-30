from __future__ import annotations

from typing import Dict, Callable

from .models import Task


class TaskRouter:
    """Routes tasks to the appropriate agent based on intent."""

    def __init__(self) -> None:
        self.routing_table: Dict[str, str] = {}

    def register_route(self, intent: str, agent_name: str) -> None:
        self.routing_table[intent] = agent_name

    def route(self, task: Task) -> str:
        if task.intent not in self.routing_table:
            raise ValueError(f"No agent registered for intent {task.intent}")
        return self.routing_table[task.intent]
