from __future__ import annotations

from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class AgentStatusEnum(str, Enum):
    """Enumeration of possible agent execution states.
    
    This enum defines the lifecycle states that agents can be in during
    task execution, providing standardized status tracking across the
    orchestrator system.
    
    Attributes:
        idle: Agent is registered but not currently executing any tasks
        running: Agent is actively processing a task
        error: Agent encountered an error during task execution
        complete: Agent successfully completed its assigned task
    """
    idle = "idle"
    running = "running"
    error = "error"
    complete = "complete"


class Task(BaseModel):
    """Represents a task to be executed by an agent in the orchestrator system.
    
    A Task encapsulates all the information needed for an agent to perform
    a specific operation, including the task type, files to process, and
    additional parameters for customization.
    
    Attributes:
        task_id (str): Unique identifier for the task, typically a UUID
        intent (str): The type of task to perform (e.g., 'code_review', 'generate_docstrings')
        files (List[str]): List of file paths to be processed by the agent
        params (dict): Additional parameters and configuration for the task execution
        
    Example:
        >>> task = Task(
        ...     task_id="abc-123",
        ...     intent="generate_docstrings",
        ...     files=["src/main.py"],
        ...     params={"directory": "/path/to/project"}
        ... )
    """
    task_id: str
    intent: str
    files: List[str] = Field(default_factory=list)
    params: dict = Field(default_factory=dict)


class AgentUpdate(BaseModel):
    """Represents a real-time status update from an agent during task execution.
    
    AgentUpdate objects are published to the event bus to provide real-time
    visibility into agent operations, allowing monitoring systems and UIs
    to track task progress and agent health.
    
    Attributes:
        agent_name (str): Name/identifier of the agent sending the update
        status (AgentStatusEnum): Current execution status of the agent
        message (Optional[str]): Human-readable status message or progress details
        timestamp (datetime): When this update was generated (auto-populated)
        
    Example:
        >>> update = AgentUpdate(
        ...     agent_name="code-review",
        ...     status=AgentStatusEnum.running,
        ...     message="Analyzing 5 Python files"
        ... )
    """
    agent_name: str
    status: AgentStatusEnum
    message: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class AgentOutput(BaseModel):
    """Represents the final output/result from an agent after task completion.
    
    AgentOutput encapsulates all results, artifacts, and metadata produced
    by an agent during task execution. This serves as the standardized
    return format for all agent operations.
    
    Attributes:
        agent_name (str): Name/identifier of the agent that produced this output
        task_id (str): Unique identifier of the task that was executed
        result (dict): Dictionary containing all results, artifacts, and metadata
            produced by the agent during task execution
        completed_at (datetime): Timestamp when the task completed (auto-populated)
        
    Example:
        >>> output = AgentOutput(
        ...     agent_name="security-auditor",
        ...     task_id="audit-123",
        ...     result={
        ...         "vulnerabilities_found": 2,
        ...         "files_analyzed": ["app.py", "models.py"],
        ...         "report": "Security analysis complete"
        ...     }
        ... )
    """
    agent_name: str
    task_id: str
    result: dict
    completed_at: datetime = Field(default_factory=datetime.utcnow)
