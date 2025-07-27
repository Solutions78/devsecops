# DevSecOps Orchestrator

A full-stack application that orchestrates various AI agents for DevSecOps operations including code review, security auditing, test generation, and documentation.

## Architecture

This project follows a modern full-stack architecture with:
- **Backend**: FastAPI Python server with agent orchestration
- **Frontend**: React TypeScript application for real-time monitoring
- **Communication**: WebSocket for real-time updates, REST API for task submission

## Project Structure

### 🔧 Backend (`backend/`)

#### Orchestrator (`backend/orchestrator/`)
- **`app.py`** - FastAPI application with REST and WebSocket endpoints
- **`agent_manager.py`** - Manages agent lifecycle and task execution  
- **`event_bus.py`** - Pub/sub event system using asyncio queues
- **`task_router.py`** - Routes tasks to appropriate agents based on intent
- **`models.py`** - Pydantic models for tasks, agents, and status
- **`agents/`** - Individual agent implementations
  - **`base.py`** - Abstract base class for all agents
  - **`code_review.py`** - Code review agent
  - **`security_auditor.py`** - Security analysis agent
  - **`test_engineer.py`** - Test generation agent
  - **`docstring_generator.py`** - Documentation agent (currently non-functional)
  - **`execution_agent.py`** - Code execution agent
  - **`refactorer.py`** - Code refactoring agent
  - **`diff_annotator.py`** - Git diff explanation agent
  - **`pr_summarizer.py`** - Pull request summary agent
  - **`orchestrator_agent.py`** - Central coordination agent

#### API Layer
- **`routes/agents.ts`** - REST endpoints for agent management
- **`server.ts`** - Express/Fastify server entry point

### 🌍 Frontend (`src/`)

#### Components (`src/components/`)
- **`AgentCard.tsx`** - Individual agent status display
- **`AgentConfigModal.tsx`** - Agent configuration interface
- **`LogsPanel.tsx`** - Real-time agent output logs
- **`PipelineView.tsx`** - Visual CI/CD pipeline graph
- **`StatusIndicator.tsx`** - Agent status badges

#### Pages (`src/pages/`)
- **`Dashboard.tsx`** - Main orchestration interface

#### Services (`src/services/`)
- **`AgentOrchestrator.ts`** - Agent sequencing and delegation logic
- **`ClaudeAPI.ts`** - Claude Code CLI/API integration

#### Types (`src/types/`)
- **`agents.ts`** - TypeScript interfaces for agents, tasks, and status

#### Utilities (`src/utils/`)
- **`pipelineGraph.ts`** - Pipeline visualization logic

### 🌍 Static Assets
- **`public/`** - Static files including `index.html`

## Getting Started

### Prerequisites
- Python 3.8+
- Node.js 16+
- Git

### Backend Setup
```bash
cd backend/orchestrator
pip install -r requirements.txt
uvicorn app:app --reload
```

### Frontend Setup
```bash
npm install
npm run dev
```

## API Endpoints

### REST API
- **POST `/task`** - Submit a task for agent processing
  - `intent`: Task type (code_review, security_audit, etc.)
  - `files`: Optional list of files to process

### WebSocket
- **WS `/updates`** - Real-time agent status updates and task results

## Agent Types

1. **Code Review Agent** - Performs code quality analysis
2. **Security Auditor Agent** - Static security analysis
3. **Test Engineer Agent** - Generates and validates tests
4. **Execution Agent** - Executes code in sandboxed environment
5. **Refactorer Agent** - Suggests code improvements
6. **Diff Annotator Agent** - Explains code changes
7. **PR Summarizer Agent** - Creates pull request summaries
8. **Orchestrator Agent** - Coordinates multi-agent workflows

## Known Issues

### Docstring Generator Agent
**Status**: Non-functional as of 2025-07-27
- Reports successful docstring generation but makes no file changes
- Provides false positive feedback
- **Workaround**: Use direct file editing for documentation

## Development Tools

- **`test_git_sync.py`** - Validates git synchronization and remote connectivity
- **`agent_manager_docstring.txt`** - Documentation reference for AgentManager class

## Contributing

1. Ensure all changes are committed with descriptive messages
2. Use the provided git sync validation script to verify repository state
3. Follow existing code patterns and documentation standards
4. Test agent functionality before submitting changes

## License

[Add your license information here]