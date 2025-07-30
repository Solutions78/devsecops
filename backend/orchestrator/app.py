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
from typing import Optional, Dict

# Prometheus instrumentation
try:
    from prometheus_fastapi_instrumentator import Instrumentator
except ModuleNotFoundError:  # Package may be missing in some dev envs
    Instrumentator = None  # type: ignore
from fastapi.middleware.cors import CORSMiddleware

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Configuration from environment variables
BACKEND_HOST = os.getenv('BACKEND_HOST', 'localhost')
BACKEND_PORT = int(os.getenv('BACKEND_PORT', '8001'))

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
    allow_origins=["http://localhost:3005", "http://localhost:5173"],  # Specific frontend origins only
    allow_methods=["GET", "POST"],  # Only required methods
    allow_headers=["Content-Type", "Authorization"],  # Specific headers only
    allow_credentials=False
)


event_bus = EventBus()
manager = AgentManager(event_bus)
router = TaskRouter()

# Task storage for tracking submitted tasks
task_storage: Dict[str, dict] = {}

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


# Import user management
try:
    from .user_management import user_manager
except ImportError:
    from user_management import user_manager

# Security: Basic authentication
security = HTTPBearer(auto_error=False)

async def verify_api_key(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Secure API key verification using user management system."""
    # Require credentials
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify the provided key using user management
    if not user_manager.is_valid_user(credentials.credentials):
        logger.warning(f"Invalid API key attempt")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    
    return credentials

async def verify_admin_key(credentials: HTTPAuthorizationCredentials = Depends(verify_api_key)):
    """Verify that the API key belongs to an administrator."""
    if not user_manager.is_administrator(credentials.credentials):
        logger.warning(f"Non-admin user attempted to access admin endpoint")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrator access required"
        )
    
    return credentials

def get_current_user_role(credentials: HTTPAuthorizationCredentials = Depends(verify_api_key)) -> str:
    """Get the current user's role."""
    return user_manager.get_user_role(credentials.credentials) or "user"


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


@app.get("/health")
async def health_check(credentials: HTTPAuthorizationCredentials = Depends(verify_api_key)):
    """Health check endpoint for API validation."""
    return {
        "status": "healthy",
        "timestamp": asyncio.get_event_loop().time(),
        "message": "DevSecOps Orchestrator is running",
        "authenticated": True
    }

@app.get("/user/role")
async def get_user_role(role: str = Depends(get_current_user_role)):
    """Get the current user's role."""
    return {
        "data": {"role": role},
        "status": "success"
    }

@app.get("/users")
async def list_users(credentials: HTTPAuthorizationCredentials = Depends(verify_admin_key)):
    """List all users (admin only)."""
    try:
        users = user_manager.list_users()
        return {
            "data": users,
            "status": "success"
        }
    except Exception as e:
        logger.error(f"Error listing users: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list users"
        )

@app.post("/users")
async def create_user(
    request: dict = Body(...),
    credentials: HTTPAuthorizationCredentials = Depends(verify_admin_key)
):
    """Create a new user (admin only)."""
    try:
        role = request.get("role", "user")
        description = request.get("description")
        
        if role not in ["administrator", "user"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Role must be 'administrator' or 'user'"
            )
        
        api_key = user_manager.create_user(
            role=role,
            description=description,
            created_by=credentials.credentials
        )
        
        return {
            "data": {
                "api_key": api_key,
                "role": role,
                "description": description
            },
            "status": "success"
        }
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user"
        )

@app.delete("/users/{api_key}")
async def delete_user(
    api_key: str,
    credentials: HTTPAuthorizationCredentials = Depends(verify_admin_key)
):
    """Delete a user (admin only)."""
    try:
        success = user_manager.delete_user(api_key, credentials.credentials)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found or cannot be deleted"
            )
        
        return {
            "data": {"deleted": True},
            "status": "success"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete user"
        )

@app.get("/secrets/{secret_name}")
async def get_secret_value(
    secret_name: str,
    credentials: HTTPAuthorizationCredentials = Depends(verify_api_key)
):
    """Get a secret value from secure storage."""
    try:
        # Get the secret value from secure storage
        secret_value = await get_secret(secret_name)
        
        if not secret_value:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Secret '{secret_name}' not found"
            )
        
        return {
            "data": {
                "name": secret_name,
                "value": secret_value
            },
            "status": "success"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving secret '{secret_name}': {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve secret"
        )

@app.get("/secrets")
async def list_secrets(credentials: HTTPAuthorizationCredentials = Depends(verify_api_key)):
    """List all available secrets."""
    try:
        # This is a mock implementation - in a real system, you'd query your secret store
        secrets = [
            {
                "name": "API_KEY",
                "created": "2024-01-15T10:00:00Z",
                "updated": "2024-01-15T10:00:00Z",
                "version": "1"
            },
            {
                "name": "ANTHROPIC_API_KEY", 
                "created": "2024-01-16T11:00:00Z",
                "updated": "2024-01-20T14:30:00Z",
                "version": "2"
            },
            {
                "name": "DATABASE_URL",
                "created": "2024-01-10T09:00:00Z", 
                "updated": "2024-01-18T16:45:00Z",
                "version": "3"
            }
        ]
        
        return {
            "data": secrets,
            "status": "success"
        }
    except Exception as e:
        logger.error(f"Error listing secrets: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list secrets"
        )


@app.get("/agents")
async def get_agents(credentials: HTTPAuthorizationCredentials = Depends(verify_api_key)):
    """Get status of all agents."""
    agent_list = []
    
    # Get real agent status from manager
    for agent_key, agent in agents.items():
        # Use the agent's actual name (not the dictionary key) for status lookup
        status_info = await manager.get_agent_status(agent.name) if hasattr(manager, 'get_agent_status') else {
            "status": "idle",
            "last_updated": "2024-01-20T10:30:00Z",
            "tasks_completed": 0
        }
        
        agent_list.append({
            "name": agent.name,
            "status": status_info.get("status", "idle"),
            "last_updated": status_info.get("last_updated", "2024-01-20T10:30:00Z"),
            "tasks_completed": status_info.get("tasks_completed", 0),
            "current_task": status_info.get("current_task")
        })
    
    return {"data": agent_list, "status": "success"}


@app.get("/agents/configs")
async def get_agent_configs(credentials: HTTPAuthorizationCredentials = Depends(verify_api_key)):
    """Get configurations for all agents."""
    try:
        from .agent_config import config_manager
        configs = config_manager.get_all_configs()
        
        # Convert to list format for API response
        config_list = []
        for agent_id, config in configs.items():
            config_dict = config.dict()
            config_list.append(config_dict)
        
        return {"data": config_list, "status": "success"}
    except Exception as e:
        logger.error(f"Error getting agent configs: {e}")
        return {"data": [], "status": "error", "message": str(e)}


@app.get("/agents/configs/{agent_id}")
async def get_agent_config(
    agent_id: str, 
    credentials: HTTPAuthorizationCredentials = Depends(verify_api_key)
):
    """Get configuration for a specific agent."""
    try:
        from .agent_config import config_manager
        config = config_manager.get_config(agent_id)
        
        if not config:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Agent configuration not found: {agent_id}"
            )
        
        return {"data": config.dict(), "status": "success"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting agent config {agent_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get agent configuration"
        )


@app.put("/agents/configs/{agent_id}")
async def update_agent_config(
    agent_id: str,
    updates: dict = Body(...),
    credentials: HTTPAuthorizationCredentials = Depends(verify_admin_key)
):
    """Update configuration for a specific agent."""
    try:
        from .agent_config import config_manager
        
        # Validate agent exists
        if agent_id not in config_manager.configs:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Agent configuration not found: {agent_id}"
            )
        
        updated_config = config_manager.update_config(agent_id, updates)
        
        if not updated_config:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to update agent configuration"
            )
        
        return {"data": updated_config.dict(), "status": "success", "message": "Configuration updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating agent config {agent_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update agent configuration"
        )


@app.post("/agents/configs/initialize")
async def initialize_default_configs(
    force: bool = False,
    credentials: HTTPAuthorizationCredentials = Depends(verify_admin_key)
):
    """Initialize default configurations for all agents.
    
    Args:
        force: If True, clears existing configurations and recreates all defaults
    """
    try:
        from .agent_config import config_manager
        
        if force:
            # Clear existing configurations
            config_manager.configs.clear()
            # Remove config files from disk
            for config_file in config_manager.config_dir.glob("*.json"):
                config_file.unlink()
        
        config_manager.create_default_configs()
        
        configs = config_manager.get_all_configs()
        config_list = [config.dict() for config in configs.values()]
        
        return {
            "data": config_list, 
            "status": "success", 
            "message": f"{'Force-' if force else ''}Initialized {len(config_list)} agent configurations"
        }
    except Exception as e:
        logger.error(f"Error initializing agent configs: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to initialize agent configurations"
        )


@app.get("/tasks")
async def get_tasks(credentials: HTTPAuthorizationCredentials = Depends(verify_api_key)):
    """Get all tasks."""
    # Return real task data from storage
    tasks = list(task_storage.values())
    return {"data": tasks, "status": "success"}


@app.get("/metrics")
async def get_metrics(credentials: HTTPAuthorizationCredentials = Depends(verify_api_key)):
    """Get system metrics."""
    return {
        "cpu_usage": 25,
        "memory_usage": 68,
        "disk_usage": 45,
        "uptime": 86400,
        "status": "success"
    }


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
        
        # Store task information
        task_storage[task.task_id] = {
            "id": task.task_id,
            "intent": intent,
            "status": "pending",
            "agent_name": "",
            "created_at": str(uuid.uuid4()),  # Using UUID as timestamp placeholder
            "updated_at": str(uuid.uuid4()),  # Using UUID as timestamp placeholder
        }
        
        agent_name = router.route(task)
        task_storage[task.task_id]["agent_name"] = agent_name
        task_storage[task.task_id]["status"] = "queued"
        
        # Run task asynchronously and update status
        async def run_and_update_task():
            try:
                task_storage[task.task_id]["status"] = "running"
                result = await manager.run_task(agent_name, task)
                task_storage[task.task_id]["status"] = "completed"
                task_storage[task.task_id]["result"] = result.output if hasattr(result, 'output') else str(result)
            except Exception as e:
                task_storage[task.task_id]["status"] = "failed"
                task_storage[task.task_id]["error"] = str(e)
        
        asyncio.create_task(run_and_update_task())
        
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


# Main execution block for direct running
if __name__ == "__main__":
    import uvicorn
    logger.info(f"Starting DevSecOps Orchestrator on {BACKEND_HOST}:{BACKEND_PORT}")
    uvicorn.run(
        "orchestrator.app:app",
        host=BACKEND_HOST,
        port=BACKEND_PORT,
        reload=True,
        log_level="info"
    )
