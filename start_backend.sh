#!/bin/bash

# DevSecOps Orchestrator Backend Startup Script
# This script starts the backend server with environment configuration

echo "🚀 Starting DevSecOps Orchestrator Backend..."

# Navigate to project root
cd "$(dirname "$0")"

# Load environment variables
if [ -f .env ]; then
    echo "📋 Loading environment variables from .env"
    export $(cat .env | grep -v '^#' | xargs)
else
    echo "⚠️  No .env file found, using defaults"
fi

# Activate virtual environment if it exists
if [ -d "devsecops/bin" ]; then
    echo "🐍 Activating Python virtual environment"
    source devsecops/bin/activate
fi

# Navigate to backend directory
cd backend

# Start the server using environment variables
echo "🌐 Starting server on ${BACKEND_HOST:-localhost}:${BACKEND_PORT:-8001}"
uvicorn orchestrator.app:app --reload --host ${BACKEND_HOST:-localhost} --port ${BACKEND_PORT:-8001}