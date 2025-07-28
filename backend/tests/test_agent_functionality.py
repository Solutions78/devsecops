#!/usr/bin/env python3
"""Test script to verify agent functionality and Claude API integration."""

import os
import sys
import asyncio
from pathlib import Path

# Add the orchestrator module to the path
sys.path.insert(0, str(Path(__file__).parent / "backend" / "orchestrator"))

from models import Task
from agents.docstring_generator import DocstringGeneratorAgent
from agents.code_review import CodeReviewAgent
from agents.security_auditor import SecurityAuditorAgent
from agents.test_engineer import TestEngineerAgent
from agents.refactorer import RefactorerAgent
from agents.diff_annotator import DiffAnnotatorAgent


async def test_claude_api_client():
    """Test Claude API client functionality."""
    print("🧪 Testing Claude API Client...")
    
    from services.claude_client import ClaudeAPIClient
    
    client = ClaudeAPIClient()
    api_key_available = bool(client.api_key)
    
    print(f"   - API Key Available: {'✅' if api_key_available else '❌'}")
    print(f"   - Model: {client.model}")
    print(f"   - Base URL: {client.base_url}")
    
    if api_key_available:
        # Test simple API call
        try:
            response = await client.process_batch_prompt("Hello, Claude! Please respond with 'API Working'.", max_tokens=50)
            if response["status"] == "SUCCESS":
                print("   - API Connection: ✅")
                print(f"   - Response: {response['response'][:50]}...")
            else:
                print(f"   - API Connection: ❌ ({response['status']})")
        except Exception as e:
            print(f"   - API Connection: ❌ (Error: {str(e)})")
    else:
        print("   - API Connection: ⚠️ (No API key - analysis-only mode)")
    
    return api_key_available


async def test_agent_functionality():
    """Test basic agent functionality."""
    print("\n🤖 Testing Agent Functionality...")
    
    test_directory = str(Path(__file__).parent / "backend" / "orchestrator" / "agents")
    
    # Test each agent
    agents = [
        ("DocstringGeneratorAgent", DocstringGeneratorAgent, {"directory": test_directory}),
        ("CodeReviewAgent", CodeReviewAgent, {"directory": test_directory}),
        ("SecurityAuditorAgent", SecurityAuditorAgent, {"directory": test_directory}),
        ("TestEngineerAgent", TestEngineerAgent, {"directory": test_directory}),
        ("RefactorerAgent", RefactorerAgent, {"directory": test_directory}),
        ("DiffAnnotatorAgent", DiffAnnotatorAgent, {"diff": "diff --git a/test.py b/test.py\nindex 123..456\n+print('hello')\n-print('world')"})
    ]
    
    for agent_name, agent_class, params in agents:
        print(f"\n   Testing {agent_name}...")
        try:
            agent = agent_class()
            task = Task(
                task_id=f"test-{agent_name.lower()}",
                intent=agent_name.lower(),
                files=[],
                params=params
            )
            
            result = await agent.run(task)
            
            # Check if agent has Claude integration
            has_claude_response = "claude_response" in result.result
            status = result.result.get("status", "UNKNOWN")
            
            print(f"      - Status: {status}")
            print(f"      - Claude Integration: {'✅' if has_claude_response else '❌'}")
            
            if has_claude_response:
                claude_status = result.result["claude_response"].get("status", "UNKNOWN")
                print(f"      - Claude API Status: {claude_status}")
            
            # Check for analysis data
            analysis_keys = [
                "files_analyzed", "files_reviewed", "files_found", "files_updated",
                "security_summary", "test_strategy", "architecture_overview", "diff_summary"
            ]
            
            analysis_found = any(key in result.result for key in analysis_keys)
            print(f"      - Analysis Data: {'✅' if analysis_found else '❌'}")
            
        except Exception as e:
            print(f"      - ❌ Failed: {str(e)}")


async def test_batch_processing():
    """Test batch processing capabilities."""
    print("\n📦 Testing Batch Processing...")
    
    test_directory = str(Path(__file__).parent / "backend" / "orchestrator")
    
    # Test with code review agent (comprehensive batch processor)
    agent = CodeReviewAgent()
    task = Task(
        task_id="test-batch-processing",
        intent="code_review",
        files=[],
        params={"directory": test_directory, "extensions": [".py"]}
    )
    
    try:
        result = await agent.run(task)
        
        files_reviewed = result.result.get("files_reviewed", 0)
        has_batch_prompt = "batch_prompt" in result.result
        batch_prompt_size = len(result.result.get("batch_prompt", "")) if has_batch_prompt else 0
        
        print(f"   - Files Processed: {files_reviewed}")
        print(f"   - Batch Prompt Generated: {'✅' if has_batch_prompt else '❌'}")
        print(f"   - Batch Prompt Size: {batch_prompt_size:,} characters")
        
        if batch_prompt_size > 0:
            print(f"   - Token Efficiency: ✅ (Single comprehensive prompt vs {files_reviewed} individual calls)")
        
    except Exception as e:
        print(f"   - ❌ Failed: {str(e)}")


def print_summary():
    """Print test summary and usage instructions."""
    print("\n" + "="*60)
    print("🎯 AGENT FUNCTIONALITY TEST SUMMARY")
    print("="*60)
    
    api_key_set = bool(os.getenv("ANTHROPIC_API_KEY"))
    
    if api_key_set:
        print("✅ Claude API Integration: ENABLED")
        print("   → All agents will provide full functionality")
        print("   → File modifications and comprehensive analysis available")
    else:
        print("⚠️  Claude API Integration: DISABLED")
        print("   → Agents will run in analysis-only mode")
        print("   → Set ANTHROPIC_API_KEY environment variable for full functionality")
    
    print("\n📋 Usage Examples:")
    print("   # Code Review")
    print('   curl -X POST "http://localhost:8000/task" -H "Content-Type: application/json" \\')
    print('     -d \'{"intent": "code_review", "params": {"directory": "/path/to/project"}}\'')
    
    print("\n   # Security Audit")
    print('   curl -X POST "http://localhost:8000/task" -H "Content-Type: application/json" \\')
    print('     -d \'{"intent": "security_audit", "params": {"directory": "/path/to/project"}}\'')
    
    print("\n   # Generate Docstrings")
    print('   curl -X POST "http://localhost:8000/task" -H "Content-Type: application/json" \\')
    print('     -d \'{"intent": "generate_docstrings", "params": {"directory": "/path/to/project"}}\'')
    
    print("\n🚀 Start the backend server:")
    print("   cd backend/orchestrator && uvicorn app:app --reload")


async def main():
    """Run all tests."""
    print("🔬 DevSecOps Orchestrator - Agent Functionality Test")
    print("="*60)
    
    api_available = await test_claude_api_client()
    await test_agent_functionality()
    await test_batch_processing()
    
    print_summary()


if __name__ == "__main__":
    asyncio.run(main())