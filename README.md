# DevSecOps Orchestrator

A modern, enterprise-grade AI-powered platform for automating software development security and operations through specialized agents. Built with React + TypeScript frontend and FastAPI backend, featuring Azure Key Vault integration and real-time monitoring.

## System Architecture Diagram

```mermaid
flowchart TB
    %% User Layer
    User[User/Developer] --> Frontend

    %% Frontend Layer
    subgraph Frontend ["Frontend Layer - React + TypeScript"]
        WebApp[React Application<br/>Port 3005]
        Auth[Authentication Context]
        WebSocket[WebSocket Client]
        Router[React Router]
        
        WebApp --> Auth
        WebApp --> WebSocket
        WebApp --> Router
    end

    %% API Layer
    Frontend --> API

    subgraph API ["API Layer - FastAPI"]
        FastAPI[FastAPI Server<br/>Port 8001]
        AuthMW[Authentication Middleware]
        SecurityMW[Security Headers]
        CORS[CORS Middleware]
        WSEndpoint[WebSocket Endpoint /updates]
        
        FastAPI --> AuthMW
        FastAPI --> SecurityMW  
        FastAPI --> CORS
        FastAPI --> WSEndpoint
    end

    %% Core Services
    API --> Services

    subgraph Services ["Core Services"]
        AgentManager[Agent Manager]
        TaskRouter[Task Router]
        EventBus[Event Bus]
        UserMgmt[User Management]
    end

    %% AI Agents
    Services --> Agents

    subgraph Agents ["AI Agents (9 Types)"]
        CodeReview[Code Review Agent]
        TestEng[Test Engineer Agent]
        Security[Security Auditor Agent]
        Docstring[Docstring Generator Agent]
        Refactor[Refactorer Agent]
        DiffAnnot[Diff Annotator Agent]
        PRSumm[PR Summarizer Agent]
        Execution[Execution Agent]
        Orchestrator[Orchestrator Agent]
    end

    %% External Services
    subgraph External ["External Services"]
        Azure[Azure Key Vault<br/>Secret Management]
        Anthropic[Anthropic Claude API]
        OpenAI[OpenAI API]
        Git[Git Repositories]
    end

    %% Security Layer
    subgraph Security ["Security Layer"]
        SecretsMgr[Secrets Manager]
        AzureAuth[Azure Authentication]
        Keyring[System Keyring]
        FileEnc[Encrypted Files]
        
        SecretsMgr --> AzureAuth
        SecretsMgr --> Keyring
        SecretsMgr --> FileEnc
    end

    %% Connections
    Services --> Security
    Security --> Azure
    Agents --> Anthropic
    Agents --> OpenAI
    Agents --> Git
    
    %% Real-time Communication
    EventBus -.-> WSEndpoint
    WSEndpoint -.-> WebSocket

    %% Task Flow
    WebApp --> |Submit Task| FastAPI
    FastAPI --> |Route Task| TaskRouter
    TaskRouter --> |Assign Agent| AgentManager
    AgentManager --> |Execute Task| Agents
    Agents --> |Status Updates| EventBus
    EventBus --> |Real-time Updates| WSEndpoint
```

---

## 🚀 Latest Features (v2.0)

- ✅ **Professional React + TypeScript Frontend** with Material-UI dark theme
- ✅ **Complete Authentication System** with secure API key management
- ✅ **Real-time Agent Dashboard** with WebSocket live updates
- ✅ **Interactive Task Submission** with all 9 agent types
- ✅ **Azure Key Vault Integration** for enterprise secret management
- ✅ **Comprehensive Tooltips** throughout the entire interface
- ✅ **Responsive Design** optimized for desktop, tablet, and mobile
- ✅ **System Health Monitoring** with connection status indicators

## 🖥️ Frontend Features

### 🎨 Modern UI/UX

- **Dark Azure Theme** - Professional GitHub-inspired design with Azure blue accents
- **Material-UI Components** - Consistent, accessible interface components
- **Responsive Layout** - Optimized for all screen sizes
- **Real-time Updates** - Live agent status and task progress via WebSocket

### 🔐 Authentication & Security

- **Secure Login Page** - API key authentication with visibility toggle
- **Session Management** - Automatic logout and reconnection handling
- **Connection Status** - Live backend connectivity indicator
- **Bearer Token Auth** - Secure API communication

### 📊 Dashboard & Monitoring

- **Agent Status Cards** - Real-time monitoring of all 9 AI agents
- **Task Management** - Submit, track, and cancel tasks with detailed results
- **System Health** - CPU, memory, Azure connection monitoring
- **Metrics Visualization** - Performance and usage statistics

### 🛡️ Security Management

- **Azure Key Vault UI** - Full CRUD operations for secrets
- **API Key Rotation** - Secure key management interface
- **Secret Versioning** - Track and manage secret versions
- **Audit Logging** - Complete operation history

## 🤖 AI Agents Portfolio

### Core Development Agents

1. **Code Review Agent** (`code_review`) - Comprehensive code quality analysis with security vulnerability detection
2. **Test Engineer Agent** (`test_engineer`) - Integration test generation with 90% coverage targets
3. **Refactorer Agent** (`refactor`) - Cross-file refactoring opportunities and architectural improvements

### Security & Compliance Agents

4. **Security Auditor Agent** (`security_audit`) - OWASP Top 10 vulnerability detection and compliance checking
5. **Diff Annotator Agent** (`annotate_diff`) - Git diff explanations with impact assessment

### Documentation & Communication Agents

6. **Docstring Generator Agent** (`generate_docstrings`) - Batch Google-style documentation generation
7. **PR Summarizer Agent** (`pr_summary`) - Pull request summary generation

### Execution & Orchestration Agents

8. **Execution Agent** (`execute`) - Sandboxed code execution with runtime validation
9. **Orchestrator Agent** (`orchestrate`) - Multi-agent workflow coordination

## 🛠️ Quick Start Guide

### Prerequisites

- **Python 3.9+** with pip
- **Node.js 18+** with npm
- **Azure account** (optional, for Key Vault integration)

### 1. Environment Setup

```bash
# Copy environment template and configure
cp env.template .env

# Edit .env file with your configuration
# The defaults should work for local development
```

### 2. Quick Start (Recommended)

```bash
# Start backend (automatically loads .env)
./start_backend.sh

# In another terminal, start frontend
./start_frontend.sh
```

### 3. Manual Setup

#### Backend Setup

```bash
# Navigate to backend directory  
cd backend

# Install Python dependencies
pip install -r requirements.txt

# Generate and configure API key (if not in .env)
python -c "
import asyncio
import secrets
from utils.manage_secrets import set_secret

async def setup():
    api_key = secrets.token_urlsafe(32)
    await set_secret('API_KEY', api_key)
    print(f'🔑 Your API Key: {api_key}')
    print('📋 Save this key for frontend login!')

asyncio.run(setup())
"

# Start the backend server
uvicorn orchestrator.app:app --reload --host localhost --port 8001
```

#### Frontend Setup

```bash
# Navigate to frontend directory
cd frontend  

# Install Node.js dependencies
npm install

# Start the development server
npm run dev
```

### 3. Access the Application

1. **Open your browser** to `http://localhost:3005`
2. **Login** with your generated API key
3. **Explore the dashboard** - view agent status, submit tasks, manage secrets
4. **Submit your first task** - try a code review or security audit

## 📡 API Reference

### Authentication Endpoints

```bash
GET /health - Health check with authentication validation
```

### Agent Management

```bash
GET /agents - List all agents with status
GET /agents/{name} - Get specific agent details
```

### Task Management

```bash
POST /task - Submit new task to agents
GET /tasks - List all tasks with status
GET /tasks/{id} - Get specific task details
DELETE /tasks/{id} - Cancel running task
```

### Real-time Updates

```bash
WS /updates - WebSocket endpoint for live agent/task updates
```

### System Monitoring

```bash
GET /metrics - Prometheus-compatible metrics
```

### Example API Usage

```bash
# Authenticate and get agent status
curl -H "Authorization: Bearer YOUR_API_KEY" \
     http://localhost:8001/agents

# Submit a code review task
curl -X POST \
     -H "Authorization: Bearer YOUR_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{"intent":"code_review","params":{"directory":"/path/to/project"}}' \
     http://localhost:8001/task
```

## 🔐 Security Architecture

### Multi-Backend Secret Management

- **Azure Key Vault** - Enterprise HSM-backed storage with RBAC
- **System Keyring** - OS-native secure storage for development
- **Encrypted Files** - Fallback encrypted storage with strong cryptography

### Authentication & Authorization

- **Bearer Token Authentication** - All endpoints require valid API keys
- **Azure Active Directory** - Optional enterprise SSO integration
- **Session Management** - Secure token handling with automatic rotation

### Security Features

- **Input Validation** - Comprehensive sanitization preventing injection attacks
- **Sandboxed Execution** - Agents run in isolated environments with resource limits
- **Audit Logging** - Complete operation trails for compliance
- **Zero Secrets in Code** - All sensitive data stored securely

## 🏗️ Architecture Overview

### Frontend Architecture

```
React 18 + TypeScript + Vite
├── Material-UI v5 (Theme & Components)
├── React Query (Server State Management)
├── React Router v6 (Navigation)
├── Socket.io Client (Real-time Updates)
├── Axios (HTTP Client with Interceptors)
└── Custom Hooks (WebSocket, Authentication)
```

### Backend Architecture

```
FastAPI + Python 3.9+
├── Pydantic (Data Validation)
├── SQLAlchemy (Database ORM)
├── AsyncIO (Concurrent Processing)
├── WebSockets (Real-time Communication)
├── Prometheus (Metrics & Monitoring)
└── Azure SDK (Key Vault Integration)
```

## 🔧 Configuration & Deployment

### Environment Variables

The application uses environment variables for configuration. Copy `env.template` to `.env` and configure:

```bash
# Frontend Configuration
VITE_API_BASE=/api                    # API base path for frontend

# Backend Configuration  
BACKEND_HOST=localhost                # Backend server host
BACKEND_PORT=8001                    # Backend server port

# Core Configuration
API_KEY=your-generated-api-key       # Your DevSecOps API key
ANTHROPIC_API_KEY=your-claude-api-key # Optional: Claude API key
OPENAI_API_KEY=your-openai-api-key   # Optional: OpenAI API key

# Azure Key Vault (Enterprise)
AZURE_KEY_VAULT_URL=https://your-vault.vault.azure.net/
AZURE_TENANT_ID=your-tenant-id
AZURE_CLIENT_ID=your-client-id
AZURE_CLIENT_SECRET=your-client-secret

# Development
DEBUG=true
LOG_LEVEL=info
```

### Secret Management Commands

```bash
# Interactive setup
python backend/utils/manage_secrets.py setup

# List all stored secrets
python backend/utils/manage_secrets.py list-keys

# Set individual secrets
python backend/utils/manage_secrets.py set-key ANTHROPIC_API_KEY sk-your-key

# Rotate API keys
python backend/utils/manage_secrets.py rotate-key API_KEY

# Test Azure integration
python backend/utils/manage_secrets.py test-azure

# Setup Azure Key Vault
python backend/utils/manage_secrets.py setup-azure

# Create encrypted backup
python backend/utils/manage_secrets.py backup secrets-backup.enc
```

### Production Deployment

#### Docker Deployment

```bash
# Backend
docker build -t devsecops-backend ./backend
docker run -d -p 8001:8001 \
  -e AZURE_KEY_VAULT_URL=https://your-vault.vault.azure.net/ \
  devsecops-backend

# Frontend
docker build -t devsecops-frontend ./frontend
docker run -d -p 3005:3005 devsecops-frontend
```

#### Manual Deployment

```bash
# Backend Production
cd backend
pip install -r requirements.txt
gunicorn orchestrator.app:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8001

# Frontend Production
cd frontend
npm run build
npm run preview
```

## 📈 Monitoring & Observability

### Built-in Monitoring

- **Prometheus Metrics** - Request counts, response times, error rates
- **Health Checks** - Automated endpoint monitoring
- **Real-time Dashboards** - Live agent status and system metrics
- **WebSocket Monitoring** - Connection status and message tracking

### Key Metrics

- Agent processing times and success rates
- API endpoint performance and availability
- Authentication success/failure rates
- Secret management operations and audit trails

## 🚀 Advanced Usage

### Custom Agent Integration

```python
from backend.orchestrator.agents.base_agent import BaseAgent

class CustomAgent(BaseAgent):
    async def run(self, task: Task) -> AgentOutput:
        # Your custom agent logic
        return AgentOutput(result="Custom processing complete")
```

### Workflow Orchestration

```json
{
  "intent": "orchestrate",
  "params": {
    "workflow": "full_review",
    "agents": ["code_review", "security_audit", "test_engineer"],
    "parallel": false
  }
}
```

### Azure Key Vault Integration

```python
from backend.services.security.azure_auth import get_azure_authenticator

auth = get_azure_authenticator()
result = auth.test_authentication("service_principal")
```

## 📚 Documentation

- **[Agent Documentation](AGENTS.md)** - Detailed guide to all 9 AI agents
- **[Frontend Documentation](frontend/README.md)** - React application architecture
- **[API Documentation](http://localhost:8001/docs)** - Interactive OpenAPI docs
- **[Security Guide](SECURITY.md)** - Security best practices and configuration

## 🤝 Contributing

1. **Fork the repository** and clone locally
2. **Create a feature branch** from `main`
3. **Install dependencies** for both frontend and backend
4. **Make your changes** with comprehensive tests
5. **Update documentation** and add examples
6. **Submit a pull request** with detailed description

### Development Guidelines

- Follow TypeScript best practices for frontend
- Use async/await patterns for backend
- Add comprehensive error handling
- Include security considerations
- Write clear documentation and examples

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

## 🔗 Resources

- **[GitHub Repository](https://github.com/Solutions78/devsecops)** - Source code and issues
- **[Release Notes](https://github.com/Solutions78/devsecops/releases)** - Version history
- **[Azure Key Vault Docs](https://docs.microsoft.com/azure/key-vault/)** - Enterprise secret management
- **[FastAPI Documentation](https://fastapi.tiangolo.com/)** - Backend framework guide
- **[React Documentation](https://react.dev/)** - Frontend framework guide

## 🏆 Enterprise Ready

Built for **enterprise deployment** with:

- 🔒 **Azure Active Directory** integration
- 🛡️ **Hardware Security Module** backing
- 📊 **Comprehensive audit logging**
- 🔄 **Automated secret rotation**
- 📈 **Production monitoring** and alerting
- 🚀 **Horizontal scalability** support

**Transform your DevSecOps workflow with AI-powered automation today!**

<style>#mermaid-1753913332942{font-family:"trebuchet ms",verdana,arial;font-size:16px;fill:#ccc;}#mermaid-1753913332942 .error-icon{fill:#a44141;}#mermaid-1753913332942 .error-text{fill:#ddd;stroke:#ddd;}#mermaid-1753913332942 .edge-thickness-normal{stroke-width:2px;}#mermaid-1753913332942 .edge-thickness-thick{stroke-width:3.5px;}#mermaid-1753913332942 .edge-pattern-solid{stroke-dasharray:0;}#mermaid-1753913332942 .edge-pattern-dashed{stroke-dasharray:3;}#mermaid-1753913332942 .edge-pattern-dotted{stroke-dasharray:2;}#mermaid-1753913332942 .marker{fill:lightgrey;}#mermaid-1753913332942 .marker.cross{stroke:lightgrey;}#mermaid-1753913332942 svg{font-family:"trebuchet ms",verdana,arial;font-size:16px;}#mermaid-1753913332942 .label{font-family:"trebuchet ms",verdana,arial;color:#ccc;}#mermaid-1753913332942 .label text{fill:#ccc;}#mermaid-1753913332942 .node rect,#mermaid-1753913332942 .node circle,#mermaid-1753913332942 .node ellipse,#mermaid-1753913332942 .node polygon,#mermaid-1753913332942 .node path{fill:#1f2020;stroke:#81B1DB;stroke-width:1px;}#mermaid-1753913332942 .node .label{text-align:center;}#mermaid-1753913332942 .node.clickable{cursor:pointer;}#mermaid-1753913332942 .arrowheadPath{fill:lightgrey;}#mermaid-1753913332942 .edgePath .path{stroke:lightgrey;stroke-width:1.5px;}#mermaid-1753913332942 .flowchart-link{stroke:lightgrey;fill:none;}#mermaid-1753913332942 .edgeLabel{background-color:hsl(0,0%,34.4117647059%);text-align:center;}#mermaid-1753913332942 .edgeLabel rect{opacity:0.5;background-color:hsl(0,0%,34.4117647059%);fill:hsl(0,0%,34.4117647059%);}#mermaid-1753913332942 .cluster rect{fill:hsl(180,1.5873015873%,28.3529411765%);stroke:rgba(255,255,255,0.25);stroke-width:1px;}#mermaid-1753913332942 .cluster text{fill:#F9FFFE;}#mermaid-1753913332942 div.mermaidTooltip{position:absolute;text-align:center;max-width:200px;padding:2px;font-family:"trebuchet ms",verdana,arial;font-size:12px;background:hsl(20,1.5873015873%,12.3529411765%);border:1px solid rgba(255,255,255,0.25);border-radius:2px;pointer-events:none;z-index:100;}#mermaid-1753913332942:root{--mermaid-font-family:sans-serif;}#mermaid-1753913332942:root{--mermaid-alt-font-family:sans-serif;}#mermaid-1753913332942 flowchart{fill:apa;}</style>

## System Security Architecture Diagram

```mermaid
graph TD
    subgraph LogSources
        A[EDR] --- B[Windows Events]
        B --- C[Linux Audit]
        C --- D[Network Devices]
        D --- E[Cloud Logs]
        E --- F[Identity Logs]
        F --- G[Container Logs]
    end
    LogSources --> IngestionLayer
    subgraph IngestionLayer
        H[REST API Endpoints]
        I[Stream Processors]
        J[Batch Importers]
        H --> H1[ingest edr]
        H --> H2[ingest windows]
        H --> H3[ingest linux]
        I --> I1[WebSocket SSE]
        I --> I2[Kafka Consumer]
        I --> I3[Message Queue]
        J --> J1[File Upload]
        J --> J2[S3 Polling]
        J --> J3[SFTP Monitor]
    end
    IngestionLayer --> NormalizationEngine
    subgraph NormalizationEngine
        K[Priority Classification]
        L[Schema Mapping]
        M[Field Extraction]
        K --> K1[Priority 1 Critical]
        K --> K2[Priority 2 High]
        K --> K3[Priority 3 Medium]
        L --> L1[Common Event Schema CES]
        L --> L2[Custom Fields]
        M --> M1[Timestamp Parse]
        M --> M2[Host Extraction]
        M --> M3[User Extraction]
    end
    NormalizationEngine --> DataLayer
    subgraph DataLayer
        N[PostgreSQL Database]
        N --> N1[logs table]
        N --> N2[events index]
        N --> N3[metadata tables]
    end
    DataLayer --> APILayer
    subgraph APILayer
        O[FastAPI Backend]
        P[Authentication]
        Q[Query Engine]
        O --> O1[REST Endpoints]
        O --> O2[WebSocket]
        O --> O3[Pagination]
        P --> P1[JWT Tokens]
        P --> P2[Role Based Access Control]
        Q --> Q1[Time Range Filter]
        Q --> Q2[Severity Filter]
        Q --> Q3[Host Filter]
    end
    APILayer --> FrontendLayer
    subgraph FrontendLayer
        R[React Application]
        R --> R1[Dashboard]
        R --> R2[Log Browser]
        R --> R3[Log Details]
        R1 --> R1a[Metrics]
        R1 --> R1b[Charts]
        R1 --> R1c[Alerts]
        R2 --> R2a[Filters]
        R2 --> R2b[Search]
        R2 --> R2c[Export]
        R3 --> R3a[Raw View]
        R3 --> R3b[Context]
        R3 --> R3c[Timeline]
    end
```