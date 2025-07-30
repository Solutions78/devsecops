#!/bin/bash

# DevSecOps Orchestrator Frontend Startup Script
# This script starts the frontend development server with environment configuration

echo "🎨 Starting DevSecOps Orchestrator Frontend..."

# Navigate to project root
cd "$(dirname "$0")"

# Load environment variables
if [ -f .env ]; then
    echo "📋 Loading environment variables from .env"
    export $(cat .env | grep -v '^#' | xargs)
else
    echo "⚠️  No .env file found, using defaults"
fi

# Navigate to frontend directory
cd frontend

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing npm dependencies..."
    npm install
fi

# Start the development server
echo "🌐 Starting frontend development server on http://localhost:3005"
echo "📡 API requests will be proxied to ${BACKEND_HOST:-localhost}:${BACKEND_PORT:-8001}"
npm run dev
