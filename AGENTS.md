# DevSecOps Orchestrator Agents

This document provides detailed information about the AI agents available in the DevSecOps Orchestrator system.

## Agent Architecture

All agents inherit from the `BaseAgent` class (`backend/orchestrator/agents/base_agent.py`) and implement the following interface:

```python
class BaseAgent(abc.ABC):
    async def run(self, task: Task) -> AgentOutput:
        """Run the agent on the given task."""
        raise NotImplementedError
```

## Available Agents

### 1. Code Review Agent (`code_review_agent.py`)
**Intent**: `code_review`
**Status**: ✅ Fully functional with Claude API integration

**Purpose**: Comprehensive code quality analysis with batch processing for cost optimization.

**Features**:
- Cross-file dependency analysis
- Architectural pattern detection  
- Style consistency checking
- Large file detection and complexity metrics
- Security vulnerability identification

**Multi-language Support**:
- Python, JavaScript, TypeScript, Java, C++, Go, Rust

**Usage**:
```json
{
  "intent": "code_review",
  "params": {
    "directory": "/path/to/project",
    "extensions": [".py", ".js", ".ts"]
  }
}
```

**Output**: Detailed code review report with findings categorized by severity and file location.

---

### 2. Test Engineer Agent (`test_engineer_agent.py`)
**Intent**: `test_engineer`
**Status**: ✅ Fully functional with Claude API integration

**Purpose**: Integration testing with comprehensive test suite generation.

**Features**:
- Cross-module test generation
- API workflow testing
- Database integration tests
- Mock generation
- End-to-end workflow testing

**Coverage Targets**:
- Unit tests: 90%
- Integration tests: 80%  
- API endpoints: 100%
- Database models: 95%

**Usage**:
```json
{
  "intent": "test_engineer",
  "params": {
    "directory": "/path/to/project",
    "test_types": ["unit", "integration", "api"]
  }
}
```

**Output**: Complete test suite with positive/negative test cases and setup instructions.

---

### 3. Security Auditor Agent (`security_auditor_agent.py`)
**Intent**: `security_audit`
**Status**: ✅ Fully functional with Claude API integration

**Purpose**: Comprehensive security analysis with OWASP Top 10 vulnerability detection.

**Features**:
- OWASP Top 10 detection
- Cross-file security analysis
- Compliance checking (NIST, DoD standards)
- Authentication architecture review
- System-wide vulnerability patterns

**Security Standards**:
- OWASP Top Ten vulnerabilities
- NIST 800-53 compliance
- Joint Cybersecurity Information AI Data Security Guidance
- DoD secure coding standards

**Usage**:
```json
{
  "intent": "security_audit",
  "params": {
    "directory": "/path/to/project",
    "compliance_standards": ["owasp", "nist"]
  }
}
```

**Output**: Risk-ranked vulnerability assessment with actionable mitigation guidance.

---

### 4. Refactorer Agent (`refactorer_agent.py`)
**Intent**: `refactor`
**Status**: ✅ Fully functional with Claude API integration

**Purpose**: Cross-file refactoring opportunities and architectural improvements.

**Features**:
- Batch processing for comprehensive analysis
- Design pattern suggestions
- Code duplication identification
- Dependency analysis
- Coupling reduction recommendations
- Module organization improvements

**Analysis Types**:
- Performance optimization opportunities
- Architectural refactoring suggestions
- Code maintainability improvements
- Design pattern implementations

**Usage**:
```json
{
  "intent": "refactor",
  "params": {
    "directory": "/path/to/project",
    "focus_areas": ["performance", "maintainability", "architecture"]
  }
}
```

**Output**: Detailed refactoring recommendations with before/after code examples.

---

### 5. Docstring Generator Agent (`docstring_generator_agent.py`)
**Intent**: `generate_docstrings`
**Status**: ✅ Fully functional with Claude API integration

**Purpose**: Batch documentation generation with actual file modifications.

**Features**:
- Batch processing for cost efficiency
- Smart file filtering
- Missing docstring analysis
- Google-style docstring generation
- Automatic file updates

**Analysis Capabilities**:
- Identifies classes/functions missing documentation
- Creates comprehensive batch prompts
- Follows Google docstring style guide
- Preserves existing documentation

**Usage**:
```json
{
  "intent": "generate_docstrings",
  "params": {
    "directory": "/path/to/project",
    "style": "google",
    "update_files": true
  }
}
```

**Output**: Updated source files with comprehensive docstrings and generation report.

---

### 6. Diff Annotator Agent (`diff_annotator_agent.py`)
**Intent**: `annotate_diff`
**Status**: ✅ Fully functional with Claude API integration

**Purpose**: Git diff explanation and cross-file impact analysis.

**Features**:
- Multi-file diff processing
- Architectural change detection
- Breaking change identification
- Cross-file relationship analysis
- Semantic change detection

**Input Methods**:
- Git commit hash
- Raw diff content
- File path comparisons

**Usage**:
```json
{
  "intent": "annotate_diff",
  "params": {
    "commit_hash": "abc123def456"
  }
}
```

**OR**:
```json
{
  "intent": "annotate_diff",
  "params": {
    "diff": "git diff content here..."
  }
}
```

**Output**: Plain-English explanation of changes with impact assessment.

---

### 7. Execution Agent (`execution_agent.py`)
**Intent**: `execute`
**Status**: ✅ Fully functional

**Purpose**: Code execution in sandboxed environment with runtime validation.

**Features**:
- Sandboxed Python code execution
- Runtime behavior validation
- Output capture and analysis
- Exception handling
- Security constraints

**Safety Features**:
- Restricted execution environment
- Timeout controls
- Resource limitations
- Output sanitization

**Usage**:
```json
{
  "intent": "execute",
  "params": {
    "code": "print('Hello, World!')",
    "timeout": 30
  }
}
```

**Output**: Execution results, output, and runtime observations.

---

### 8. PR Summarizer Agent (`pr_summarizer_agent.py`)
**Intent**: `pr_summary`
**Status**: ✅ Fully functional with Claude API integration

**Purpose**: Pull request summary generation with structured analysis.

**Features**:
- Aggregated change analysis
- Impact assessment
- Structured Markdown reports
- Integration with review agents
- Release note generation

**Analysis Includes**:
- Code changes summary
- Breaking changes identification
- Testing recommendations
- Deployment considerations

**Usage**:
```json
{
  "intent": "pr_summary",
  "params": {
    "pr_number": 123,
    "repository": "owner/repo"
  }
}
```

**Output**: Comprehensive PR summary in Markdown format.

---

### 9. Orchestrator Agent (`orchestrator_agent.py`)
**Intent**: `orchestrate`
**Status**: ✅ Fully functional

**Purpose**: Multi-agent workflow coordination and pipeline management.

**Features**:
- Agent sequencing and delegation
- Workflow state management
- Cross-agent communication
- Error handling and recovery
- Pipeline visualization

**Workflow Types**:
- Sequential agent execution
- Parallel processing coordination
- Conditional branching
- Error recovery workflows

**Usage**:
```json
{
  "intent": "orchestrate",
  "params": {
    "workflow": "full_review",
    "agents": ["code_review", "security_audit", "test_engineer"]
  }
}
```

**Output**: Orchestrated workflow results with agent coordination logs.

---

## Agent Communication

### Event Bus System
All agents communicate through the centralized event bus (`backend/orchestrator/event_bus.py`):

```python
class EventBus:
    async def publish(self, event: AgentUpdate) -> None
    def subscribe(self) -> asyncio.Queue
    def unsubscribe(self, queue: asyncio.Queue) -> None
```

### Status Updates
Agents emit real-time status updates:
- `idle` - Agent is ready for tasks
- `running` - Agent is processing a task
- `complete` - Task completed successfully
- `error` - Task failed with error

### Task Routing
The `TaskRouter` class (`backend/orchestrator/task_router.py`) automatically routes tasks to appropriate agents based on intent:

```python
router.register_route("code_review", "code-review")
router.register_route("security_audit", "security-auditor")
router.register_route("test_engineer", "test-engineer")
router.register_route("generate_docstrings", "docstring-generator")
router.register_route("refactor", "refactorer")
router.register_route("annotate_diff", "diff-annotator")
router.register_route("execute", "execution")
router.register_route("pr_summary", "pr-summarizer")
router.register_route("orchestrate", "orchestrator")
```

## Agent Management

### Registration
Agents are registered with the `AgentManager` (`backend/orchestrator/agent_manager.py`):

```python
manager = AgentManager(event_bus)
manager.register_agent(code_review_agent)
manager.register_agent(security_auditor_agent)
manager.register_agent(test_engineer_agent)
# ... etc
```

### Task Execution
Tasks are executed asynchronously:

```python
output = await manager.run_task(agent_name, task)
```

## Security Features

### Input Validation
All agents implement secure input validation:
- File path validation to prevent directory traversal
- Parameter sanitization
- Content length limits
- Command injection prevention

### Authentication
API endpoints require Bearer token authentication:
```bash
curl -H "Authorization: Bearer your-api-key" ...
```

### Secure Secrets Management
Agents use the secure secrets management system:
- System keyring storage
- Encrypted file backup
- Azure Key Vault integration with Azure AD authentication
- Zero secrets in code

## Monitoring and Metrics

### Prometheus Integration
All agents are monitored via Prometheus metrics:
- Request counts by agent and status
- Response times and latency
- Error rates and types
- Resource utilization

### Real-time Updates
WebSocket endpoint provides real-time agent status:
```javascript
const ws = new WebSocket('ws://localhost:8001/updates');
ws.onmessage = (event) => {
  const update = JSON.parse(event.data);
  console.log(`Agent ${update.agent_name}: ${update.status}`);
};
```

## Development Guidelines

### Adding New Agents

1. **Inherit from BaseAgent**:
```python
from .base_agent import BaseAgent

class MyAgent(BaseAgent):
    async def run(self, task: Task) -> AgentOutput:
        # Implementation here
        pass
```

2. **Register with Manager**:
```python
my_agent = MyAgent("my-agent", event_bus=event_bus)
manager.register_agent(my_agent)
router.register_route("my_intent", my_agent.name)
```

3. **Implement Security**:
- Validate all inputs
- Sanitize parameters
- Implement timeout controls
- Add proper error handling

4. **Add Documentation**:
- Update this AGENTS.md file
- Add docstrings following Google style
- Include usage examples
- Document security considerations

### Testing Agents

Use the provided test utilities:
```python
# Test agent functionality
python test_agent_functionality.py

# Verify agent registration
python -c "from agent_manager import AgentManager; print(manager.agents.keys())"
```

## Batch Processing Benefits

### Cost Optimization
- **60-80% token reduction** through batch processing
- Single API calls instead of per-file processing
- Smart content truncation for large projects
- Token limits to prevent excessive costs

### Enhanced Analysis
- Cross-file context awareness
- Holistic architectural understanding
- Integration-focused testing
- System-wide pattern detection

### Quality Improvements
- Comprehensive coverage across modules
- Architectural improvements spanning multiple files
- Risk assessment with full codebase context
- Coordinated refactoring recommendations

---

For more information, see the main [README.md](README.md) file and the API documentation.