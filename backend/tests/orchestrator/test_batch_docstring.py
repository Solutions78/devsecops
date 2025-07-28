#!/usr/bin/env python3
"""Test script for batch docstring processing functionality."""

import asyncio
import sys
import os
sys.path.append('backend/orchestrator')

from backend.orchestrator.models import Task
# Standard ``pytest-asyncio`` marker makes the coroutine test explicit and
# prevents collection-time warnings when that plugin is present.

from backend.orchestrator.agents.docstring_generator import DocstringGeneratorAgent


import pytest


@pytest.mark.asyncio
async def test_batch_processing():
    """Test the batch processing functionality of the DocstringGeneratorAgent."""
    print("🚀 Testing Batch Docstring Processing")
    print("=" * 50)
    
    agent = DocstringGeneratorAgent('test-docstring-agent')
    
    # Test with current orchestrator directory
    test_directory = os.path.abspath('backend/orchestrator')
    print(f"📂 Testing directory: {test_directory}")
    
    task = Task(
        task_id='test-123',
        intent='generate_docstrings',
        files=[],
        params={'directory': test_directory}
    )
    
    result = await agent.run(task)
    
    print("\n🔍 BATCH PROCESSING TEST RESULTS")
    print("-" * 40)
    print(f"Status: {result.result['status']}")
    print(f"Directory: {result.result['directory']}")
    print(f"Files found: {result.result['files_found']}")
    print(f"Files needing docstrings: {result.result['files_needing_docstrings']}")
    
    print("\n📋 FILES ANALYSIS")
    print("-" * 40)
    for file_path, analysis in result.result['files_analysis'].items():
        rel_path = os.path.relpath(file_path, test_directory)
        print(f"\n📄 {rel_path}:")
        if analysis.get('missing'):
            print(f"  ❌ Missing: {', '.join(analysis['missing'][:3])}{'...' if len(analysis['missing']) > 3 else ''}")
        if analysis.get('existing'):
            print(f"  ✅ Existing: {', '.join(analysis['existing'][:3])}{'...' if len(analysis['existing']) > 3 else ''}")
    
    print(f"\n📝 BATCH PROMPT PREVIEW")
    print("-" * 40)
    batch_prompt = result.result.get('batch_prompt', '')
    if batch_prompt:
        lines = batch_prompt.split('\n')
        for line in lines[:15]:  # Show first 15 lines
            print(line)
        if len(lines) > 15:
            print(f"... ({len(lines) - 15} more lines)")
    
    print(f"\n✨ Next Step: {result.result.get('next_step', 'Complete')}")
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(test_batch_processing())
