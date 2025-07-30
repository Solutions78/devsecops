from __future__ import annotations

import os
import glob
from pathlib import Path
from typing import List, Dict, Optional, Set

try:
    from ..models import AgentOutput, Task  # type: ignore
except ImportError:
    import sys
    import os
    # Add the backend directory to Python path
    backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    if backend_dir not in sys.path:
        sys.path.insert(0, backend_dir)
    from orchestrator.models import AgentOutput, Task  # type: ignore

from .base_agent import BaseAgent
# Optional mixin for external Claude client
try:
    from ..services.claude_client import BatchProcessingMixin  # type: ignore
except ImportError:
    class BatchProcessingMixin:  # type: ignore
        """Stub mixin when claude_client is unavailable."""

        pass


class CodeReviewAgent(BaseAgent, BatchProcessingMixin):
    """Agent that performs comprehensive code review using batch processing for cost efficiency.
    
    This agent analyzes code files in batches to provide holistic code review that considers
    cross-file dependencies, architectural patterns, and overall code quality. It examines
    code style consistency, identifies potential issues, and provides actionable feedback.
    
    Features:
    - Batch processing to reduce API costs and improve context awareness
    - Cross-file dependency analysis
    - Architectural pattern detection
    - Code style consistency checking
    - Security vulnerability identification
    - Performance optimization suggestions
    - Best practices validation
    """

    def _find_code_files(self, directory: str, extensions: Optional[List[str]] = None) -> List[str]:
        """Find all code files in a directory recursively.
        
        Args:
            directory (str): Root directory to search for code files
            extensions (List[str], optional): File extensions to include (e.g., ['.py', '.js', '.ts'])
            
        Returns:
            List[str]: List of code file paths found in the directory
        """
        if extensions is None:
            extensions = ['.py', '.js', '.ts', '.tsx', '.jsx', '.java', '.cpp', '.c', '.h', '.go', '.rs']
        
        code_files = []
        for ext in extensions:
            pattern = f"**/*{ext}"
            files = glob.glob(os.path.join(directory, pattern), recursive=True)
            
            # Filter out common non-source directories
            filtered_files = []
            for file_path in files:
                path_parts = Path(file_path).parts
                skip_dirs = {'node_modules', '__pycache__', '.git', 'dist', 'build', 'target', '.pytest_cache'}
                
                if not any(skip_dir in path_parts for skip_dir in skip_dirs):
                    filtered_files.append(file_path)
            
            code_files.extend(filtered_files)
        
        return sorted(list(set(code_files)))  # Remove duplicates and sort

    def _read_file_content(self, file_path: str) -> Dict[str, str]:
        """Read and return file content with metadata.
        
        Args:
            file_path (str): Path to the file to read
            
        Returns:
            Dict[str, str]: Dictionary containing file content and metadata
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return {
                'path': file_path,
                'content': content,
                'size': len(content),
                'lines': len(content.split('\n')),
                'extension': Path(file_path).suffix.lower()
            }
        except Exception as e:
            return {
                'path': file_path,
                'error': f'Could not read file: {str(e)}',
                'size': 0,
                'lines': 0,
                'extension': Path(file_path).suffix.lower()
            }

    def _analyze_file_patterns(self, files_data: List[Dict]) -> Dict[str, any]:
        """Analyze patterns across multiple files.
        
        Args:
            files_data (List[Dict]): List of file data dictionaries
            
        Returns:
            Dict[str, any]: Analysis results including patterns, issues, and metrics
        """
        analysis = {
            'total_files': len(files_data),
            'total_lines': sum(f.get('lines', 0) for f in files_data),
            'file_types': {},
            'large_files': [],
            'empty_files': [],
            'potential_issues': []
        }
        
        # Analyze file distribution
        for file_data in files_data:
            ext = file_data.get('extension', 'unknown')
            analysis['file_types'][ext] = analysis['file_types'].get(ext, 0) + 1
            
            # Flag large files (>500 lines)
            if file_data.get('lines', 0) > 500:
                analysis['large_files'].append({
                    'path': file_data['path'],
                    'lines': file_data['lines']
                })
            
            # Flag empty files
            if file_data.get('lines', 0) == 0:
                analysis['empty_files'].append(file_data['path'])
        
        return analysis

    def _create_batch_review_prompt(self, files_data: List[Dict], analysis: Dict) -> str:
        """Create a comprehensive batch review prompt.
        
        Args:
            files_data (List[Dict]): List of file data to review
            analysis (Dict): Pre-analysis of file patterns
            
        Returns:
            str: Formatted prompt for batch code review
        """
        prompt = """Please perform a comprehensive code review of the following codebase. 

Focus on:
1. **Code Quality**: Readability, maintainability, and adherence to best practices
2. **Architecture**: Overall structure, design patterns, and module organization
3. **Cross-file Dependencies**: How components interact and potential coupling issues
4. **Security**: Potential vulnerabilities and security best practices
5. **Performance**: Optimization opportunities and resource usage
6. **Consistency**: Coding style, naming conventions, and patterns across files
7. **Documentation**: Code comments, docstrings, and inline documentation quality

## Codebase Overview:
"""
        
        prompt += f"- **Total Files**: {analysis['total_files']}\n"
        prompt += f"- **Total Lines**: {analysis['total_lines']}\n"
        prompt += f"- **File Types**: {', '.join([f'{ext}({count})' for ext, count in analysis['file_types'].items()])}\n"
        
        if analysis['large_files']:
            prompt += f"- **Large Files** (>500 lines): {len(analysis['large_files'])}\n"
        
        prompt += "\n## Files to Review:\n\n"
        
        # Include file contents
        for file_data in files_data[:20]:  # Limit to first 20 files to manage token usage
            if 'error' in file_data:
                prompt += f"**{file_data['path']}** (ERROR: {file_data['error']})\n\n"
                continue
                
            prompt += f"**{file_data['path']}** ({file_data['lines']} lines)\n"
            prompt += "```" + file_data.get('extension', '').replace('.', '') + "\n"
            
            # Truncate very long files
            content = file_data['content']
            if len(content) > 3000:  # Limit individual file content
                lines = content.split('\n')
                content = '\n'.join(lines[:100]) + f"\n\n... (truncated, showing first 100 of {len(lines)} lines)"
            
            prompt += content + "\n```\n\n"
        
        if len(files_data) > 20:
            prompt += f"... and {len(files_data) - 20} more files (truncated for token efficiency)\n\n"
        
        prompt += """
## Please provide:
1. **Overall Assessment**: Summary of code quality and architecture
2. **Critical Issues**: High-priority problems that need immediate attention
3. **Improvement Suggestions**: Specific recommendations for enhancement
4. **Security Concerns**: Any potential security vulnerabilities
5. **Best Practices**: Areas where code could better follow established patterns
6. **Cross-file Analysis**: Dependencies, coupling, and architectural observations

Format your response with clear sections and actionable recommendations.
"""
        
        return prompt

    async def run(self, task: Task) -> AgentOutput:
        """Execute the code review task with batch processing.
        
        Args:
            task (Task): Task containing files to review or directory to scan
            
        Returns:
            AgentOutput: Results of the comprehensive code review
        """
        await self.emit_status("running", "Starting batch code review")
        
        files_to_review = []
        
        # Handle directory-based review
        if task.params.get('directory'):
            directory = task.params['directory']
            if not os.path.exists(directory):
                await self.emit_status("error", f"Directory does not exist: {directory}")
                return AgentOutput(
                    agent_name=self.name,
                    task_id=task.task_id,
                    result={
                        "status": "FAILED",
                        "error": f"Directory not found: {directory}"
                    }
                )
            
            await self.emit_status("running", f"Scanning {directory} for code files")
            files_to_review = self._find_code_files(directory, task.params.get('extensions'))
            
        # Handle file-list based review
        elif task.files:
            files_to_review = task.files
            
        else:
            await self.emit_status("error", "No files or directory specified for review")
            return AgentOutput(
                agent_name=self.name,
                task_id=task.task_id,
                result={
                    "status": "FAILED",
                    "error": "No files or directory specified in task"
                }
            )
        
        if not files_to_review:
            await self.emit_status("complete", "No code files found to review")
            return AgentOutput(
                agent_name=self.name,
                task_id=task.task_id,
                result={
                    "status": "SUCCESS",
                    "files_found": 0,
                    "message": "No code files found for review"
                }
            )
        
        await self.emit_status("running", f"Reading {len(files_to_review)} files for analysis")
        
        # Read all file contents
        files_data = []
        for file_path in files_to_review:
            file_data = self._read_file_content(file_path)
            files_data.append(file_data)
        
        # Analyze patterns across files
        await self.emit_status("running", "Analyzing code patterns and structure")
        analysis = self._analyze_file_patterns(files_data)
        
        # Create batch review prompt
        await self.emit_status("running", "Generating comprehensive review prompt")
        batch_prompt = self._create_batch_review_prompt(files_data, analysis)
        
        # Process with Claude API for comprehensive code review
        await self.emit_status("running", "Processing code review with Claude API")
        claude_response = await self.process_with_claude(batch_prompt, "code_review")
        
        await self.emit_status("complete", f"Code review complete for {len(files_to_review)} files")
        
        return AgentOutput(
            agent_name=self.name,
            task_id=task.task_id,
            result={
                "status": "REVIEW_COMPLETE",
                "files_reviewed": len(files_to_review),
                "analysis": analysis,
                "batch_prompt": batch_prompt,
                "claude_response": claude_response,
                "review_scope": {
                    "directory": task.params.get('directory'),
                    "files": files_to_review[:10],  # First 10 files for reference
                    "total_files": len(files_to_review)
                },
                "next_step": "Review Claude API response for detailed code review findings and recommendations"
            }
        )
