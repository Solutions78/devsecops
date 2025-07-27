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
  - **`code_review.py`** - **Batch processing** code review with cross-file analysis
  - **`refactorer.py`** - **Batch processing** refactoring with architectural improvements
  - **`test_engineer.py`** - **Batch processing** integration test generation
  - **`docstring_generator.py`** - **Batch processing** documentation generation (analysis-only)
  - **`security_auditor.py`** - Security analysis agent
  - **`execution_agent.py`** - Code execution agent
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
  - `params`: Optional dictionary of parameters (e.g., `{'directory': '/path/to/code'}`)

### WebSocket
- **WS `/updates`** - Real-time agent status updates and task results

## Agent Types

### 🔄 **Batch Processing Agents** (Cost-Optimized)

1. **Code Review Agent** - Comprehensive code quality analysis with batch processing
   - **Features**: Cross-file dependency analysis, architectural pattern detection, style consistency checking
   - **Multi-language Support**: Python, JavaScript, TypeScript, Java, C++, Go, Rust
   - **Analysis**: Large file detection, complexity metrics, security vulnerability identification
   - **Usage**: `{"intent": "code_review", "params": {"directory": "/path/to/project"}}`

2. **Refactorer Agent** - Cross-file refactoring opportunities and architectural improvements
   - **Features**: Batch processing for comprehensive cross-file analysis, design pattern suggestions
   - **Analysis**: Code duplication identification, dependency analysis, coupling reduction recommendations
   - **Improvements**: Module organization, performance optimization, architectural refactoring
   - **Usage**: `{"intent": "refactor", "params": {"directory": "/path/to/project"}}`

3. **Test Engineer Agent** - Integration testing with comprehensive test suite generation
   - **Features**: Cross-module test generation, API workflow testing, database integration tests
   - **Coverage**: Unit tests (90%), Integration tests (80%), API endpoints (100%), DB models (95%)
   - **Test Types**: End-to-end workflows, positive/negative test cases, mock generation
   - **Usage**: `{"intent": "test_engineer", "params": {"directory": "/path/to/project"}}`

4. **Docstring Generator Agent** - Batch documentation generation (with known issues)
   - **Features**: Batch processing for cost efficiency, smart file filtering, missing docstring analysis
   - **Analysis**: Identifies classes/functions missing documentation, creates comprehensive batch prompts
   - **Status**: ⚠️ **Currently produces analysis only** - requires Claude API integration for file modifications
   - **Usage**: `{"intent": "generate_docstrings", "params": {"directory": "/path/to/project"}}`

### 🎯 **Individual Processing Agents**

5. **Security Auditor Agent** - Static security analysis
6. **Execution Agent** - Code execution in sandboxed environment
7. **Diff Annotator Agent** - Git diff explanation and analysis
8. **PR Summarizer Agent** - Pull request summary generation
9. **Orchestrator Agent** - Multi-agent workflow coordination

## Batch Processing Benefits

### 💰 **Cost Optimization**
- **Single API calls** instead of per-file processing
- **Token limits** to prevent excessive costs while maintaining quality
- **Smart content truncation** for large files and projects

### 🧠 **Enhanced Analysis**
- **Cross-file context** for better architectural understanding
- **Holistic code review** considering module interactions
- **Integration testing** with full system awareness
- **Dependency analysis** across entire codebase

### 📊 **Coverage & Quality**
- **Comprehensive test coverage** with integration focus
- **Architectural improvements** spanning multiple modules
- **Pattern detection** across the entire project
- **Risk assessment** with full codebase context

## Usage Examples

### Code Review (Batch)
```bash
curl -X POST "http://localhost:8000/task" \
  -H "Content-Type: application/json" \
  -d '{
    "intent": "code_review",
    "params": {"directory": "/path/to/project", "extensions": [".py", ".js"]}
  }'
```

### Integration Test Generation
```bash
curl -X POST "http://localhost:8000/task" \
  -H "Content-Type: application/json" \
  -d '{
    "intent": "test_engineer", 
    "params": {"directory": "/path/to/project"}
  }'
```

### Architectural Refactoring Analysis
```bash
curl -X POST "http://localhost:8000/task" \
  -H "Content-Type: application/json" \
  -d '{
    "intent": "refactor",
    "params": {"directory": "/path/to/project"}
  }'
```

## Known Issues

### Docstring Generator Agent
**Status**: Analysis-only as of 2025-07-27
- Successfully analyzes files and creates comprehensive batch prompts
- Identifies missing docstrings and generates optimization strategies
- **Current Limitation**: Requires Claude API integration for actual file modifications
- **Workaround**: Use generated batch prompts with Claude API manually

## Development Tools

- **`test_git_sync.py`** - Validates git synchronization and remote connectivity
- **`test_docstring_verification.py`** - Verifies docstring completion across codebase
- **`agent_manager_docstring.txt`** - Documentation reference for AgentManager class

## Contributing

1. Ensure all changes are committed with descriptive messages
2. Use the provided git sync validation script to verify repository state
3. Follow existing code patterns and documentation standards
4. Test agent functionality before submitting changes

## License

[Add your license information here]