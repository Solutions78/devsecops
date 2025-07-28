from __future__ import annotations

from typing import Dict, Callable

try:
    from .models import Task
except ImportError:
    from models import Task


class TaskRouter:
    """Routes tasks to the appropriate agent based on intent."""

    def __init__(self) -> None:
        self.routing_table: Dict[str, str] = {}

    def register_route(self, intent: str, agent_name: str) -> None:
        """Register a mapping between task intent and agent name.
        
        Associates a specific task intent (e.g., 'code_review') with the name
        of the agent that should handle tasks of that type. This allows the
        router to automatically direct tasks to the appropriate agent.
        
        Args:
            intent (str): The task intent/type to register (e.g., 'generate_docstrings')
            agent_name (str): The name of the agent that handles this intent type
            
        Example:
            >>> router.register_route("security_audit", "security-auditor")
            >>> # Now all tasks with intent="security_audit" go to "security-auditor"
        """
        self.routing_table[intent] = agent_name

    def route(self, task: Task) -> str:
        """Route a task to the appropriate agent based on its intent.
        
        Looks up the task's intent in the routing table and returns the name
        of the agent that should handle this type of task. This enables
        automatic task delegation without manual agent selection.
        
        Args:
            task (Task): The task to be routed, containing an intent field
                that specifies the type of operation to perform
                
        Returns:
            str: The name of the agent that should handle this task
            
        Raises:
            ValueError: If no agent is registered for the task's intent type
            
        Example:
            >>> task = Task(task_id="123", intent="code_review", files=["app.py"])
            >>> agent_name = router.route(task)  # Returns "code-review-agent"
        """
        if task.intent not in self.routing_table:
            raise ValueError(f"No agent registered for intent {task.intent}")
        return self.routing_table[task.intent]
