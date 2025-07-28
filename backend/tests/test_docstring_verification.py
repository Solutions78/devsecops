#!/usr/bin/env python3
"""Verification script to check if all docstrings have been added."""

import asyncio
import sys
import os
sys.path.append('backend/orchestrator')

from backend.orchestrator.models import Task
from backend.orchestrator.agents.docstring_generator import DocstringGeneratorAgent


async def verify_docstrings():
    """Verify that all missing docstrings have been added."""
    print("🔍 Verifying Docstring Completion")
    print("=" * 50)
    
    agent = DocstringGeneratorAgent('verify-docstring-agent')
    
    # Test with current orchestrator directory
    test_directory = os.path.abspath('backend/orchestrator')
    print(f"📂 Checking directory: {test_directory}")
    
    task = Task(
        task_id='verify-123',
        intent='generate_docstrings',
        files=[],
        params={'directory': test_directory}
    )
    
    result = await agent.run(task)
    
    print(f"\n📊 VERIFICATION RESULTS")
    print("-" * 40)
    print(f"Status: {result.result['status']}")
    print(f"Files found: {result.result['files_found']}")
    files_needing = result.result.get('files_needing_docstrings', 0)
    print(f"Files still needing docstrings: {files_needing}")
    
    if files_needing == 0:
        print("\n🎉 SUCCESS: All files now have comprehensive docstrings!")
        return True
    else:
        print(f"\n⚠️  Still missing docstrings in {result.result['files_needing_docstrings']} files:")
        for file_path, analysis in result.result['files_analysis'].items():
            if analysis.get('missing'):
                rel_path = os.path.relpath(file_path, test_directory)
                print(f"  📄 {rel_path}: {', '.join(analysis['missing'])}")
        return False


if __name__ == "__main__":
    success = asyncio.run(verify_docstrings())
    exit(0 if success else 1)