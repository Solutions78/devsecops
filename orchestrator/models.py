from __future__ import annotations

from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class AgentStatusEnum(str, Enum):
    idle = "idle"
    running = "running"
    error = "error"
    complete = "complete"


class Task(BaseModel):
    task_id: str
    intent: str
    files: List[str] = Field(default_factory=list)
    params: dict = Field(default_factory=dict)


class AgentUpdate(BaseModel):
    agent_name: str
    status: AgentStatusEnum
    message: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class AgentOutput(BaseModel):
    agent_name: str
    task_id: str
    result: dict
    completed_at: datetime = Field(default_factory=datetime.utcnow)
