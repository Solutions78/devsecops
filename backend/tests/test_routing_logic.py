"""Unit-tests that focus on the *backend* routing and agent lifecycle logic.

These tests purposely avoid hitting the real Claude API or any heavy file-system
interaction.  Instead, they rely on *dummy* in-memory agents so that the core
orchestrator infrastructure can be validated quickly and deterministically.
"""

from __future__ import annotations

import asyncio

import pytest

# The backend package lives one directory below the project root.  Add it to the
# import path so that ``pytest`` discovers the modules no matter where it is
# executed from.
import sys
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = ROOT_DIR / "backend" / "orchestrator"
sys.path.insert(0, str(BACKEND_DIR))

# Now we can safely import backend modules.
# Import through the *public* alias so that the test-suite exercises the same
# API consumers would use.
from orchestrator.agent_manager import AgentManager  # type: ignore  # noqa: E402
from orchestrator.event_bus import EventBus  # type: ignore  # noqa: E402
from orchestrator.task_router import TaskRouter  # type: ignore  # noqa: E402
from orchestrator.models import AgentOutput, AgentStatusEnum, Task  # type: ignore  # noqa: E402
from orchestrator.agents.base import BaseAgent  # type: ignore  # noqa: E402


class DummyAgent(BaseAgent):
    """A lightweight agent used exclusively for unit-testing."""

    async def run(self, task: Task) -> AgentOutput:  # type: ignore[override]
        await self.emit_status("running", "dummy agent executing task")

        # Simulate some asynchronous workload – *very* short to keep the test
        # suite snappy while still exercising the event loop machinery.
        await asyncio.sleep(0)

        await self.emit_status("complete", "task finished")
        return AgentOutput(agent_name=self.name, task_id=task.task_id, result={"echo": task.intent})


class FailingAgent(BaseAgent):
    """Agent that always raises an error – used to verify error propagation."""

    async def run(self, task: Task) -> AgentOutput:  # type: ignore[override]
        await self.emit_status("running", "about to fail")
        raise RuntimeError("intentional failure for testing")


# ---------------------------------------------------------------------------
# TaskRouter
# ---------------------------------------------------------------------------


def test_task_router_basic_routing():
    """Ensure the router returns the correct agent for a registered intent."""

    router = TaskRouter()
    router.register_route("dummy_intent", "dummy-agent")

    task = Task(task_id="t-1", intent="dummy_intent")
    assert router.route(task) == "dummy-agent"


def test_task_router_unknown_intent_raises():
    """An unregistered intent should raise *ValueError*."""

    router = TaskRouter()
    with pytest.raises(ValueError):
        router.route(Task(task_id="t-2", intent="missing"))


# ---------------------------------------------------------------------------
# AgentManager + EventBus
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_agent_manager_successful_run():
    """The happy-path – status transitions idle→running→complete are published."""

    event_bus = EventBus()
    manager = AgentManager(event_bus)

    agent = DummyAgent(name="dummy-agent", event_bus=event_bus)
    manager.register_agent(agent)

    # Subscribe *before* running the task so that we don't miss any updates.
    queue = event_bus.subscribe()

    task = Task(task_id="t-success", intent="does_not_matter")
    output = await manager.run_task("dummy-agent", task)

    assert output.agent_name == "dummy-agent"
    assert output.task_id == "t-success"
    assert manager.status["dummy-agent"] is AgentStatusEnum.complete

    # Collect *all* events that were emitted for this task.  The exact amount
    # depends on how many status updates the concrete agent sends, therefore we
    # read from the queue until it is empty for a short grace-period.

    statuses: list[AgentStatusEnum] = []

    async def _drain() -> None:
        while True:
            try:
                update = await asyncio.wait_for(queue.get(), timeout=0.05)
                statuses.append(update.status)
            except asyncio.TimeoutError:
                break

    await _drain()

    # The manager *must* publish at least one ``running`` and one ``complete``
    # status.
    assert AgentStatusEnum.running in statuses
    assert AgentStatusEnum.complete in statuses


@pytest.mark.asyncio
async def test_agent_manager_error_flow():
    """If the agent raises an error the manager should mark the status *error*."""

    event_bus = EventBus()
    manager = AgentManager(event_bus)

    agent = FailingAgent(name="failing-agent", event_bus=event_bus)
    manager.register_agent(agent)

    queue = event_bus.subscribe()
    task = Task(task_id="t-fail", intent="whatever")

    with pytest.raises(RuntimeError):
        await manager.run_task("failing-agent", task)

    assert manager.status["failing-agent"] is AgentStatusEnum.error

    statuses: list[AgentStatusEnum] = []

    async def _drain_err() -> None:
        while True:
            try:
                update = await asyncio.wait_for(queue.get(), timeout=0.05)
                statuses.append(update.status)
            except asyncio.TimeoutError:
                break

    await _drain_err()

    assert AgentStatusEnum.running in statuses
    assert AgentStatusEnum.error in statuses
