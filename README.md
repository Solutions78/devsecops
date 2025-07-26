# DevSecOps Orchestrator Backend

This repository contains a scaffold for a backend service orchestrating Claude agents across the secure code lifecycle. The new Python backend uses **FastAPI** and a simple event-driven architecture.

## Running

Install dependencies and start the server:

```bash
pip install -r orchestrator/requirements.txt
uvicorn orchestrator.app:app --reload
```

The API provides endpoints to submit tasks and a WebSocket for real-time updates.

See `AGENTS.md` for a list of available Claude agents.

## Tests

Run tests with `pytest`:

```bash
pytest orchestrator/tests
```
