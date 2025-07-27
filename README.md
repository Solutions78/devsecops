###Current Folder Structure
🔧 backend/
routes/agents.ts – API endpoints for listing, invoking, or managing Claude agents

server.ts – Express or Fastify server entry point

devsecops/ – Placeholder? May want to clarify intent or merge with routes/ or services/

🌍 public/
Static files like index.html

🧩 src/components/
UI components:

AgentCard.tsx – Displays agent name, status, icon

AgentConfigModal.tsx – Agent customization pop-up

LogsPanel.tsx – Output logs from each agent

PipelineView.tsx – Your visual CI/CD graph canvas

StatusIndicator.tsx – Active/inactive/errored state badges

📋 src/pages/
Dashboard.tsx – Main page for orchestrating agents and viewing real-time status

🔌 src/services/
AgentOrchestrator.ts – Likely where you'll sequence agent calls and handle delegation

ClaudeAPI.ts – Direct wrapper around Claude Code CLI or HTTP API for agent execution

🧠 types/
agents.ts – TS interfaces for agents, tasks, logs, status enums

⚙️ utils/
pipelineGraph.ts – Graphviz/NodeGraph logic for rendering flow between agents