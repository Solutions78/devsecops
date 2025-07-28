from __future__ import annotations

import asyncio
from typing import Dict

try:
    from .event_bus import EventBus
    from .models import AgentOutput, Task, AgentStatusEnum
    from .agents.base import BaseAgent
except ImportError:
    from event_bus import EventBus
    from models import AgentOutput, Task, AgentStatusEnum
    from agents.base import BaseAgent


class AgentManager:
    """Manages the lifecycle and execution of agents within the orchestrator system.
    
    The AgentManager is responsible for registering agents, tracking their status,
    and coordinating task execution across multiple agents. It provides a centralized
    interface for agent management and maintains state information for all registered
    agents.
    
    Attributes:
        event_bus (EventBus): The event bus instance for inter-component communication.
        agents (Dict[str, BaseAgent]): Dictionary mapping agent names to agent instances.
        status (Dict[str, AgentStatusEnum]): Dictionary tracking the current status of each agent.
    """
    
    def __init__(self, event_bus: EventBus) -> None:
        """Initialize the AgentManager with an event bus.
        
        Args:
            event_bus (EventBus): The event bus instance used for communication
                between components in the orchestrator system.
        """
        self.event_bus = event_bus
        self.agents: Dict[str, BaseAgent] = {}
        self.status: Dict[str, AgentStatusEnum] = {}

    def register_agent(self, agent: BaseAgent) -> None:
        """Register a new agent with the manager.
        
        Adds the agent to the internal registry and sets its initial status to idle.
        The agent is identified by its name attribute and can be referenced for
        task execution.
        
        Args:
            agent (BaseAgent): The agent instance to register. Must have a valid
                name attribute that will be used as the unique identifier.
        """
        self.agents[agent.name] = agent
        self.status[agent.name] = AgentStatusEnum.idle

    async def run_task(self, agent_name: str, task: Task) -> AgentOutput:
        """Execute a task using the specified agent.
        
        Coordinates the execution of a task by the named agent, including status
        tracking and event emission. The method handles the complete lifecycle
        of task execution from start to completion or error.
        
        Args:
            agent_name (str): The name of the registered agent to execute the task.
            task (Task): The task object containing all necessary information
                for task execution.
        
        Returns:
            AgentOutput: The result of the task execution, containing any output
                data, artifacts, or results produced by the agent.
        
        Raises:
            KeyError: If the specified agent_name is not found in the registered agents.
            Exception: Any exception raised during task execution is re-raised after
                updating the agent status and emitting error events.
        """
        agent = self.agents[agent_name]
        self.status[agent_name] = AgentStatusEnum.running
        await agent.emit_status(AgentStatusEnum.running.value, f"Started task {task.task_id}")
        try:
            output = await agent.run(task)
            self.status[agent_name] = AgentStatusEnum.complete
            await agent.emit_status(AgentStatusEnum.complete.value, f"Completed task {task.task_id}")
            return output
        except Exception as exc:
            self.status[agent_name] = AgentStatusEnum.error
            await agent.emit_status(AgentStatusEnum.error.value, str(exc))
            raise
