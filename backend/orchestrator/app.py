from __future__ import annotations

import asyncio
import uuid
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from .event_bus import EventBus
from .models import Task
from .agent_manager import AgentManager
from .task_router import TaskRouter
from .agents import (
    CodeReviewAgent,
    TestEngineerAgent,
    ExecutionAgent,
    SecurityAuditorAgent,
    DocstringGeneratorAgent,
    RefactorerAgent,
    DiffAnnotatorAgent,
    PRSummarizerAgent,
    OrchestratorAgent,
)

app = FastAPI(title="DevSecOps Orchestrator")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


event_bus = EventBus()
manager = AgentManager(event_bus)
router = TaskRouter()

code_review = CodeReviewAgent("code-review", event_bus=event_bus)
test_engineer = TestEngineerAgent("test-engineer", event_bus=event_bus)
execution = ExecutionAgent("execution-agent", event_bus=event_bus)
security = SecurityAuditorAgent("security-auditor", event_bus=event_bus)
docstrings = DocstringGeneratorAgent("docstring-generator", event_bus=event_bus)
refactorer = RefactorerAgent("refactorer", event_bus=event_bus)
annotator = DiffAnnotatorAgent("diff-annotator", event_bus=event_bus)
summarizer = PRSummarizerAgent("pr-summarizer", event_bus=event_bus)
orchestrator_agent = OrchestratorAgent("orchestrator-agent", event_bus=event_bus)

for agent in [
    code_review,
    test_engineer,
    execution,
    security,
    docstrings,
    refactorer,
    annotator,
    summarizer,
    orchestrator_agent,
]:
    manager.register_agent(agent)

router.register_route("code_review", code_review.name)
router.register_route("test_engineer", test_engineer.name)
router.register_route("execute", execution.name)
router.register_route("security_audit", security.name)
router.register_route("generate_docstrings", docstrings.name)
router.register_route("refactor", refactorer.name)
router.register_route("annotate_diff", annotator.name)
router.register_route("pr_summary", summarizer.name)
router.register_route("orchestrate", orchestrator_agent.name)


@app.post("/task")
async def submit_task(intent: str, files: list[str] | None = None):
    task = Task(task_id=str(uuid.uuid4()), intent=intent, files=files or [])
    agent_name = router.route(task)
    asyncio.create_task(manager.run_task(agent_name, task))
    return {"task_id": task.task_id, "agent": agent_name}


@app.websocket("/updates")
async def updates(ws: WebSocket):
    await ws.accept()
    queue = event_bus.subscribe()
    try:
        while True:
            event = await queue.get()
            await ws.send_json(event.dict())
    except WebSocketDisconnect:
        event_bus.unsubscribe(queue)

