"""DevSecOps Orchestrator FastAPI Application.

This module provides the main FastAPI application for the DevSecOps orchestrator,
which manages various AI agents for code review, testing, security auditing, and
other development operations.

The application provides REST and WebSocket endpoints for task submission and
real-time status updates.
"""
from __future__ import annotations

import asyncio
import uuid
import logging
import re
import os
from pathlib import Path
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, status, Depends, Header, Body
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional

# Prometheus instrumentation
try:
    from prometheus_fastapi_instrumentator import Instrumentator
except ModuleNotFoundError:  # Package may be missing in some dev envs
    Instrumentator = None  # type: ignore
from fastapi.middleware.cors import CORSMiddleware

# Handle both relative and absolute imports
try:
    # Try relative imports first (when run as module)
    from .event_bus import EventBus
    from .models import Task, AgentUpdate
    from .agent_manager import AgentManager
    from .task_router import TaskRouter
    # Import security from the backend services directory
    import sys
    import os
    backend_dir = os.path.dirname(os.path.dirname(__file__))
    if backend_dir not in sys.path:
        sys.path.insert(0, backend_dir)
    from services.security import get_secret
except ImportError:
    # Fall back to absolute imports (when run directly)
    import sys
    import os
    # Add both orchestrator and backend directories to path
    current_dir = os.path.dirname(__file__)
    backend_dir = os.path.dirname(current_dir)
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)
    if backend_dir not in sys.path:
        sys.path.insert(0, backend_dir)
    from event_bus import EventBus
    from models import Task, AgentUpdate
    from agent_manager import AgentManager
    from task_router import TaskRouter
    from services.security import get_secret
# Import available agents - some may be placeholder classes
def safe_import_agent(agent_name, class_name):
    """Safely import an agent class, return None if not available."""
    try:
        try:
            # Try relative import first
            module = __import__(f"orchestrator.agents.{agent_name}", fromlist=[class_name])
        except ImportError:
            # Try absolute import
            module = __import__(f"agents.{agent_name}", fromlist=[class_name])
        
        return getattr(module, class_name, None)
    except (ImportError, AttributeError):
        return None

# Import available agents
CodeReviewAgent = safe_import_agent("code_review_agent", "CodeReviewAgent")
TestEngineerAgent = safe_import_agent("test_engineer_agent", "TestEngineerAgent")
ExecutionAgent = safe_import_agent("execution_agent", "ExecutionAgent")
SecurityAuditorAgent = safe_import_agent("security_auditor_agent", "SecurityAuditorAgent")
DocstringGeneratorAgent = safe_import_agent("docstring_generator_agent", "DocstringGeneratorAgent")
RefactorerAgent = safe_import_agent("refactorer_agent", "RefactorerAgent")
DiffAnnotatorAgent = safe_import_agent("diff_annotator_agent", "DiffAnnotatorAgent")
PRSummarizerAgent = safe_import_agent("pr_summarizer_agent", "PRSummarizerAgent")
OrchestratorAgent = safe_import_agent("orchestrator_agent", "OrchestratorAgent")

app = FastAPI(
    title="DevSecOps Orchestrator",
    description="AI-powered DevSecOps orchestration platform with agent-based task processing",
    version="1.0.0"
)

# Security: Request size middleware
class RequestSizeMiddleware:
    """Middleware to check request size and prevent DoS attacks."""
    
    def __init__(self, app, max_size: int = 10 * 1024 * 1024):
        self.app = app
        self.max_size = max_size
    
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            headers = dict(scope["headers"])
            content_length = headers.get(b"content-length", b"0")
            try:
                size = int(content_length.decode())
                if size > self.max_size:
                    response = JSONResponse(
                        status_code=413,
                        content={"error": "Request too large", "detail": f"Maximum request size is {self.max_size} bytes"}
                    )
                    await response(scope, receive, send)
                    return
            except ValueError:
                pass
        
        await self.app(scope, receive, send)

# Add request size limits
app.add_middleware(RequestSizeMiddleware, max_size=10 * 1024 * 1024)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Register /metrics endpoint if instrumentation is available
if Instrumentator is not None:
    Instrumentator().instrument(app).expose(app)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # Specific frontend origins only
    allow_methods=["GET", "POST"],  # Only required methods
    allow_headers=["Content-Type", "Authorization"],  # Specific headers only
    allow_credentials=False
)


event_bus = EventBus()
manager = AgentManager(event_bus)
router = TaskRouter()

# Create agent instances (only for available agents)
agents = {}
routes = {}

if CodeReviewAgent:
    agents["code_review"] = CodeReviewAgent("code-review", event_bus=event_bus)
    routes["code_review"] = "code-review"

if TestEngineerAgent:
    agents["test_engineer"] = TestEngineerAgent("test-engineer", event_bus=event_bus)
    routes["test_engineer"] = "test-engineer"

if ExecutionAgent:
    agents["execution"] = ExecutionAgent("execution-agent", event_bus=event_bus)
    routes["execute"] = "execution-agent"

if SecurityAuditorAgent:
    agents["security"] = SecurityAuditorAgent("security-auditor", event_bus=event_bus)
    routes["security_audit"] = "security-auditor"

if DocstringGeneratorAgent:
    agents["docstrings"] = DocstringGeneratorAgent("docstring-generator", event_bus=event_bus)
    routes["generate_docstrings"] = "docstring-generator"

if RefactorerAgent:
    agents["refactorer"] = RefactorerAgent("refactorer", event_bus=event_bus)
    routes["refactor"] = "refactorer"

if DiffAnnotatorAgent:
    agents["annotator"] = DiffAnnotatorAgent("diff-annotator", event_bus=event_bus)
    routes["annotate_diff"] = "diff-annotator"

if PRSummarizerAgent:
    agents["summarizer"] = PRSummarizerAgent("pr-summarizer", event_bus=event_bus)
    routes["pr_summary"] = "pr-summarizer"

if OrchestratorAgent:
    agents["orchestrator"] = OrchestratorAgent("orchestrator-agent", event_bus=event_bus)
    routes["orchestrate"] = "orchestrator-agent"

# Register available agents
for agent in agents.values():
    manager.register_agent(agent)

# Register available routes
for route_name, agent_name in routes.items():
    router.register_route(route_name, agent_name)


# Security: Basic authentication
security = HTTPBearer(auto_error=False)

async def verify_api_key(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Secure API key verification using secrets manager."""
    # Get API key from secure storage
    api_key = await get_secret('API_KEY')
    
    # If no API key is configured, allow access (development mode)
    if not api_key:
        logger.warning("No API key configured - running in development mode")
        return credentials
    
    # Require credentials when API key is set
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify the provided key
    if credentials.credentials != api_key:
        logger.warning(f"Invalid API key attempt from user")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    
    logger.debug("API key verified successfully")
    return credentials


# Security: Add security headers middleware
@app.middleware("http")
async def add_security_headers(request, call_next):
    """Add security headers to all responses."""
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    return response


# Request models
class TaskRequest(BaseModel):
    """Request model for task submission."""
    intent: str
    files: Optional[list[str]] = None
    params: Optional[dict] = None


# Security validation functions
def validate_file_path(file_path: str) -> bool:
    """Validate file path to prevent path traversal attacks."""
    # Normalize the path and check for dangerous patterns
    normalized = os.path.normpath(file_path)
    
    # Reject paths that try to escape current directory
    if normalized.startswith('/') or normalized.startswith('\\') or '..' in normalized:
        return False
    
    # Only allow safe characters
    if not re.match(r'^[a-zA-Z0-9._/\-]+$', normalized):
        return False
    
    return True


def validate_intent(intent: str) -> bool:
    """Validate task intent against allowed values."""
    allowed_intents = {
        'code_review', 'test_engineer', 'security_audit', 'generate_docstrings',
        'refactor', 'annotate_diff', 'pr_summary', 'execute', 'orchestrate'
    }
    return intent in allowed_intents


def sanitize_params(params: dict) -> dict:
    """Sanitize task parameters to prevent injection attacks."""
    if not params:
        return {}
    
    sanitized = {}
    for key, value in params.items():
        # Only allow safe parameter keys
        if not re.match(r'^[a-zA-Z0-9_]+$', key):
            continue
            
        # Sanitize string values
        if isinstance(value, str):
            # Limit length to prevent DoS
            if len(value) > 1000:
                value = value[:1000]
            # Remove potentially dangerous characters
            value = re.sub(r'[;&|`$()]', '', value)
        
        sanitized[key] = value
    
    return sanitized


@app.exception_handler(ValueError)
async def value_error_handler(request, exc):
    """Handle ValueError exceptions (e.g., unknown task intent)."""
    logger.error(f"ValueError: {exc}")
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"error": "Invalid request", "detail": str(exc)}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle unexpected exceptions with secure error responses."""
    # Log detailed error internally
    error_id = str(uuid.uuid4())
    logger.error(f"Error ID {error_id}: {type(exc).__name__}: {exc}", exc_info=True)
    
    # Return generic error to client without exposing internal details
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal server error", 
            "detail": "An unexpected error occurred",
            "error_id": error_id  # For support purposes only
        }
    )


@app.post("/task", 
          summary="Submit a task for agent processing",
          response_description="Task submission confirmation with task ID and assigned agent")
async def submit_task(
    request: TaskRequest,
    credentials: HTTPAuthorizationCredentials = Depends(verify_api_key)
):
    """Submit a task to be processed by an appropriate agent.

    Creates a new task with a unique ID and routes it to the appropriate agent
    based on the provided intent. The task is executed asynchronously and updates
    are streamed via the WebSocket endpoint.

    **Supported intents:**
    - `code_review`: Comprehensive code quality analysis
    - `test_engineer`: Integration test generation  
    - `security_audit`: Security vulnerability analysis
    - `generate_docstrings`: Documentation generation
    - `refactor`: Code refactoring recommendations
    - `annotate_diff`: Git diff explanations
    - `pr_summary`: Pull request summaries
    - `execute`: Code execution in sandbox
    - `orchestrate`: Multi-agent workflow coordination

    Args:
        intent: The type of task to perform. Must be one of the supported intents above.
        files: Optional list of file paths to be processed by the agent.
        params: Optional dictionary of parameters for the agent (e.g., {'directory': '/path/to/code'}).

    Returns:
        dict: Contains the generated task_id and the name of the assigned agent.

    Raises:
        HTTPException: 400 if intent is invalid or parameters are malformed.
        HTTPException: 500 if an unexpected error occurs during task creation.
    """
    try:
        # Extract values from request
        intent = request.intent
        files = request.files
        params = request.params
        
        # Validate intent
        if not intent or not isinstance(intent, str):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Intent must be a non-empty string"
            )
        
        # Security: Validate intent against allowed values
        if not validate_intent(intent):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid intent. Allowed values: {list(router.routing_table.keys())}"
            )
        
        # Validate and sanitize files parameter
        if files is not None:
            if not isinstance(files, list):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Files must be a list of strings"
                )
            
            # Security: Validate each file path
            validated_files = []
            for file_path in files:
                if not isinstance(file_path, str):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="All file paths must be strings"
                    )
                
                if not validate_file_path(file_path):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Invalid file path: {file_path}"
                    )
                
                validated_files.append(file_path)
            
            files = validated_files
        
        # Validate and sanitize params parameter
        if params is not None:
            if not isinstance(params, dict):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Params must be a dictionary"
                )
            
            # Security: Sanitize parameters to prevent injection
            params = sanitize_params(params)

        task = Task(
            task_id=str(uuid.uuid4()), 
            intent=intent, 
            files=files or [],
            params=params or {}
        )
        
        agent_name = router.route(task)
        asyncio.create_task(manager.run_task(agent_name, task))
        
        # Security: Log without exposing sensitive parameters
        logger.info(f"Task {task.task_id} submitted with intent '{intent}' to agent '{agent_name}'")
        
        return {
            "task_id": task.task_id, 
            "agent": agent_name,
            "status": "queued",
            "message": f"Task queued for processing by {agent_name}"
        }
        
    except ValueError as e:
        # Router will raise ValueError for unknown intents
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown task intent: {intent}. Supported intents: {list(router.routing_table.keys())}"
        )
    except Exception as e:
        logger.error(f"Error creating task: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create task"
        )


@app.websocket("/updates")
async def updates(ws: WebSocket):
    """WebSocket endpoint for receiving real-time agent status updates.

    Establishes a WebSocket connection and streams agent status updates
    and task completion events to the connected client in real-time.

    **Message Format:**
    ```json
    {
        "agent_name": "code-review",
        "status": "running|complete|error|idle", 
        "message": "Human-readable status message",
        "timestamp": "2024-01-01T00:00:00.000Z"
    }
    ```

    **Connection Lifecycle:**
    1. Client connects and receives immediate confirmation
    2. All subsequent agent updates are streamed in real-time
    3. Connection automatically cleaned up on disconnect

    Args:
        ws: WebSocket connection instance.

    Note:
        The connection is automatically cleaned up when the client disconnects.
        All events are sent as JSON-serialized objects following the AgentUpdate model.
    """
    queue = None
    try:
        await ws.accept()
        logger.info("WebSocket connection established")
        
        # Send connection confirmation
        await ws.send_json({
            "type": "connection",
            "status": "connected",
            "message": "WebSocket connection established successfully",
            "timestamp": str(uuid.uuid4())  # Using UUID as timestamp placeholder
        })
        
        queue = event_bus.subscribe()
        
        while True:
            try:
                event = await queue.get()
                # Ensure event has dict() method (should be AgentUpdate or similar)
                if hasattr(event, 'dict'):
                    await ws.send_json(event.dict())
                else:
                    # Fallback for raw dict events
                    await ws.send_json(event)
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error sending WebSocket message: {e}")
                # Send error notification to client
                try:
                    await ws.send_json({
                        "type": "error",
                        "status": "error", 
                        "message": "Error occurred while streaming updates",
                        "timestamp": str(uuid.uuid4())
                    })
                except:
                    # If we can't send error message, connection is likely broken
                    break
                    
    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}", exc_info=True)
    finally:
        # Clean up subscription
        if queue:
            event_bus.unsubscribe(queue)
            logger.info("WebSocket subscription cleaned up")
