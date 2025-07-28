# DevSecOps Orchestrator Frontend

A modern React + TypeScript frontend for the DevSecOps Orchestrator, providing a comprehensive dashboard for managing AI agents, monitoring tasks, and handling secure operations.

## 🚀 Features

- **Real-time Agent Monitoring** - Live status updates for all 9 AI agents
- **Task Management** - Submit, monitor, and track agent tasks
- **Azure Integration** - Native Azure Key Vault and Active Directory support
- **Security Dashboard** - Centralized security management interface
- **System Monitoring** - Performance metrics and health monitoring
- **Responsive Design** - Optimized for desktop, tablet, and mobile
- **Dark Theme** - Modern dark UI with Azure blue accents

## 🛠️ Tech Stack

- **React 18** - Modern React with hooks and concurrent features
- **TypeScript** - Type-safe development
- **Vite** - Fast development server and build tool
- **Material-UI v5** - Comprehensive component library
- **React Query** - Server state management and caching
- **Socket.io** - Real-time WebSocket communication
- **React Router v6** - Client-side routing
- **Axios** - HTTP client with interceptors

## 📦 Installation

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

The frontend will be available at `http://localhost:3000`

## 🔧 Configuration

### API Integration

The frontend connects to the backend API running on `http://localhost:8001`. The proxy configuration in `vite.config.ts` handles routing:

```typescript
proxy: {
  '/api': {
    target: 'http://localhost:8001',
    changeOrigin: true,
  },
  '/ws': {
    target: 'ws://localhost:8001',
    ws: true,
  },
}
```

### Authentication

The frontend uses Bearer token authentication. Set your API key in the application settings or localStorage:

```javascript
localStorage.setItem('devsecops_api_key', 'your-api-key-here')
```

## 📱 Pages & Features

### Dashboard (`/`)
- **Agent Overview** - Status cards for all agents
- **Task Summary** - Recent task activity
- **System Health** - CPU, memory, and Azure connection status
- **Quick Stats** - Key metrics at a glance

### Agents (`/agents`)
- **Agent Grid** - Detailed view of all AI agents
- **Status Monitoring** - Real-time status updates
- **Task History** - Completed tasks per agent

### Tasks (`/tasks`)
- **Task Submission** - Submit new tasks to agents
- **Task Queue** - Monitor pending and running tasks
- **Results Viewer** - View task outputs and reports

### Security (`/security`)
- **Azure Key Vault** - Secret management interface
- **API Keys** - Key rotation and management
- **Security Features** - Authentication and audit logs

### Monitoring (`/monitoring`)
- **System Metrics** - Performance dashboard
- **Prometheus Integration** - Real-time metrics
- **Health Checks** - System status monitoring

### Settings (`/settings`)
- **Configuration** - System and user preferences
- **API Settings** - Backend connection configuration

## 🔌 Real-time Updates

The frontend uses WebSocket connections for real-time updates:

```typescript
// Agent status updates
websocketService.onAgentUpdate((update) => {
  // Handle agent status change
})

// Task progress updates
websocketService.onTaskUpdate((update) => {
  // Handle task progress
})
```

## 🎨 Theming

The application uses a custom Material-UI theme with:

- **Dark mode** - GitHub-inspired dark background
- **Azure colors** - Primary blue (#0078d4) and secondary (#00bcf2)
- **Inter font** - Modern, readable typography
- **Custom components** - Styled cards, buttons, and navigation

## 📱 Responsive Design

The interface is fully responsive:

- **Desktop** - Full sidebar navigation with detailed views
- **Tablet** - Collapsible sidebar with optimized layouts
- **Mobile** - Drawer navigation with touch-friendly controls

## 🚀 Development

### Available Scripts

```bash
# Development server
npm run dev

# Production build
npm run build

# TypeScript checking
npm run type-check

# Linting
npm run lint

# Preview production build
npm run preview
```

### Project Structure

```
frontend/
├── src/
│   ├── components/          # Reusable components
│   │   ├── agents/         # Agent-related components
│   │   ├── layout/         # Layout components
│   │   ├── monitoring/     # Monitoring components
│   │   └── tasks/          # Task-related components
│   ├── hooks/              # Custom React hooks
│   ├── pages/              # Page components
│   ├── services/           # API and WebSocket services
│   ├── theme/              # Material-UI theme
│   └── types/              # TypeScript type definitions
├── public/                 # Static assets
└── package.json           # Dependencies and scripts
```

## 🔒 Security

- **Bearer Authentication** - All API requests include authorization headers
- **Input Validation** - Client-side validation for all forms
- **Secure Storage** - API keys stored in localStorage (consider more secure options for production)
- **HTTPS Ready** - Production builds support HTTPS deployment

## 🚢 Deployment

### Development
```bash
npm run dev
```

### Production Build
```bash
npm run build
npm run preview
```

### Docker Deployment
```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "run", "preview", "--", "--host", "0.0.0.0"]
```

## 🔄 Backend Integration

The frontend is designed to work with the DevSecOps Orchestrator backend:

- **API Endpoints** - Full integration with REST API
- **WebSocket Events** - Real-time agent and task updates
- **Azure Services** - Native support for Azure Key Vault and AD
- **Metrics** - Prometheus metrics visualization

## 📝 Contributing

1. Follow TypeScript best practices
2. Use Material-UI components when possible
3. Implement responsive design for all new features
4. Add proper error handling and loading states
5. Write type-safe code with proper interfaces

## 🐛 Troubleshooting

### Common Issues

**WebSocket Connection Failed**
- Ensure backend is running on port 8001
- Check if WebSocket endpoint `/updates` is available

**API Authentication Errors**
- Verify API key is set correctly
- Check backend authentication configuration

**Build Errors**
- Run `npm install` to ensure all dependencies are installed
- Check TypeScript errors with `npm run type-check`

## 📄 License

Part of the DevSecOps Orchestrator project. See main project for license information.