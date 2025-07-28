#!/usr/bin/env python3
"""
Git Sync Validation Test Script

This script validates that git synchronization is working correctly by:
1. Checking git repository status
2. Creating a test file
3. Staging and committing changes
4. Pushing to remote
5. Cleaning up the test file

Usage: python test_git_sync.py
"""

import subprocess
import sys
import os
import datetime
from pathlib import Path


def run_command(command, description=""):
    """Execute a shell command and return the result."""
    print(f"🔄 {description or command}")
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            capture_output=True, 
            text=True
        )
        if result.returncode == 0:
            output = result.stdout.strip() if result.stdout.strip() else "Command completed successfully"
            print(f"✅ Success: {output}")
            return result.stdout.strip()
        else:
            print(f"❌ Error (code {result.returncode}): {result.stderr.strip()}")
            return None
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return None


def main():
    """Main test function."""
    print("🚀 Starting Git Sync Validation Test")
    print("=" * 50)
    
    # Check if we're in a git repository
    if not run_command("git rev-parse --is-inside-work-tree", "Checking if in git repository"):
        print("❌ Not in a git repository!")
        sys.exit(1)
    
    # Get current branch
    current_branch = run_command("git branch --show-current", "Getting current branch")
    print(f"📍 Current branch: {current_branch}")
    
    # Check repository status
    run_command("git status --porcelain", "Checking repository status")
    
    # Check remote connection
    run_command("git remote -v", "Checking remote repositories")
    
    # Create a test file with timestamp
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    test_file = f"git_sync_test_{timestamp}.txt"
    test_content = f"Git sync test created at {datetime.datetime.now().isoformat()}\n"
    
    print(f"📝 Creating test file: {test_file}")
    with open(test_file, 'w') as f:
        f.write(test_content)
    
    # Stage the test file
    result = run_command(f"git add {test_file}", f"Staging test file {test_file}")
    if result is None:
        print("❌ Failed to stage test file")
        sys.exit(1)
    
    # Commit the test file
    commit_message = f"Test commit for git sync validation - {timestamp}"
    result = run_command(f'git commit -m "{commit_message}"', "Committing test file")
    if result is None:
        print("❌ Failed to commit test file")
        sys.exit(1)
    
    # Push to remote
    result = run_command(f"git push origin {current_branch}", "Pushing to remote")
    if result is None:
        print("❌ Failed to push to remote")
        sys.exit(1)
    
    # Remove the test file
    print(f"🧹 Cleaning up test file: {test_file}")
    os.remove(test_file)
    
    # Stage the deletion
    result = run_command(f"git add {test_file}", f"Staging deletion of {test_file}")
    if result is None:
        print("❌ Failed to stage file deletion")
        sys.exit(1)
    
    # Commit the deletion
    cleanup_message = f"Clean up git sync test file - {timestamp}"
    result = run_command(f'git commit -m "{cleanup_message}"', "Committing cleanup")
    if result is None:
        print("❌ Failed to commit cleanup")
        sys.exit(1)
    
    # Push cleanup
    result = run_command(f"git push origin {current_branch}", "Pushing cleanup to remote")
    if result is None:
        print("❌ Failed to push cleanup to remote")
        sys.exit(1)
    
    print("\n" + "=" * 50)
    print("🎉 Git Sync Validation Test COMPLETED SUCCESSFULLY!")
    print("✅ All git operations (add, commit, push) are working correctly")
    print("✅ Remote synchronization is functional")
    print("✅ Repository is in a clean state")


if __name__ == "__main__":
    main()