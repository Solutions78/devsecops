from __future__ import annotations

import os
import re
import subprocess
import shlex
from pathlib import Path
from typing import List, Dict, Optional, Set, Any, Tuple
from collections import defaultdict

try:
    from ..models import AgentOutput, Task  # type: ignore
except ImportError:
    from backend.orchestrator.models import AgentOutput, Task  # type: ignore

from .base import BaseAgent
# Optional mixin stub
try:
    from ..services.claude_client import BatchProcessingMixin  # type: ignore
except ImportError:
    class BatchProcessingMixin:  # type: ignore
        """TODO: Add docstring."""
        pass


def validate_git_ref(ref: str) -> bool:
    """Validate git reference (commit hash, branch name, tag) for security."""
    if not ref or len(ref) > 100:  # Reasonable length limit
        return False
    # Allow alphanumeric, dots, hyphens, underscores, and slashes for refs
    return bool(re.match(r'^[a-zA-Z0-9._/-]+$', ref))


def validate_repository_path(path: str) -> bool:
    """Validate repository path to prevent path traversal."""
    if not path:
        return False
    # Normalize and check for dangerous patterns
    normalized = os.path.normpath(path)
    # Reject absolute paths and parent directory references
    if normalized.startswith('/') or normalized.startswith('\\') or '..' in normalized:
        return False
    return bool(re.match(r'^[a-zA-Z0-9._/-]+$', normalized))


class DiffAnnotatorAgent(BaseAgent, BatchProcessingMixin):
    """Agent that explains diffs between commits using batch processing for complex multi-file changes.
    
    This agent analyzes git diffs across multiple files to provide comprehensive explanations
    of changes, their relationships, and cross-file impacts. It excels at explaining complex
    multi-file changes, architectural modifications, and coordinated updates across the codebase.
    
    Features:
    - Batch processing for large diffs spanning multiple files
    - Cross-file impact analysis and relationship mapping
    - Architectural change detection and explanation
    - Coordinated change pattern recognition
    - Breaking change identification and impact assessment
    - Refactoring pattern detection across files
    - Dependency update impact analysis
    """

    def _parse_git_diff(self, diff_content: str) -> Dict[str, Any]:
        """Parse git diff content to extract structured information about changes.
        
        Args:
            diff_content (str): Raw git diff output
            
        Returns:
            Dict[str, Any]: Structured diff information with file-level details
        """
        diff_info = {
            'files_changed': [],
            'total_additions': 0,
            'total_deletions': 0,
            'file_details': {},
            'binary_files': [],
            'renamed_files': [],
            'deleted_files': [],
            'new_files': []
        }
        
        # Split diff into individual file sections
        file_sections = re.split(r'^diff --git', diff_content, flags=re.MULTILINE)
        
        for section in file_sections[1:]:  # Skip empty first section
            file_info = self._parse_file_diff_section('diff --git' + section)
            if file_info:
                file_path = file_info['file_path']
                diff_info['files_changed'].append(file_path)
                diff_info['file_details'][file_path] = file_info
                diff_info['total_additions'] += file_info['additions']
                diff_info['total_deletions'] += file_info['deletions']
                
                # Categorize file changes
                if file_info['is_binary']:
                    diff_info['binary_files'].append(file_path)
                elif file_info['is_new_file']:
                    diff_info['new_files'].append(file_path)
                elif file_info['is_deleted']:
                    diff_info['deleted_files'].append(file_path)
                elif file_info['old_path'] != file_info['file_path']:
                    diff_info['renamed_files'].append({
                        'old_path': file_info['old_path'],
                        'new_path': file_info['file_path']
                    })
        
        return diff_info

    def _parse_file_diff_section(self, section: str) -> Optional[Dict[str, Any]]:
        """Parse a single file's diff section.
        
        Args:
            section (str): Git diff section for a single file
            
        Returns:
            Optional[Dict[str, Any]]: File diff information or None if parse fails
        """
        lines = section.strip().split('\n')
        if not lines:
            return None
        
        # Extract file paths from git diff header
        header_match = re.match(r'diff --git a/(.+) b/(.+)', lines[0])
        if not header_match:
            return None
        
        old_path = header_match.group(1)
        new_path = header_match.group(2)
        
        file_info = {
            'file_path': new_path,
            'old_path': old_path,
            'additions': 0,
            'deletions': 0,
            'is_binary': False,
            'is_new_file': False,
            'is_deleted': False,
            'chunks': [],
            'function_changes': [],
            'class_changes': [],
            'import_changes': []
        }
        
        # Parse file metadata
        for line in lines[1:]:
            if line.startswith('new file mode'):
                file_info['is_new_file'] = True
            elif line.startswith('deleted file mode'):
                file_info['is_deleted'] = True
            elif line.startswith('Binary files'):
                file_info['is_binary'] = True
                return file_info
            elif line.startswith('@@'):
                # Parse hunk header
                chunk_match = re.match(r'@@ -(\d+),?(\d+)? \+(\d+),?(\d+)? @@(.*)', line)
                if chunk_match:
                    chunk_info = {
                        'old_start': int(chunk_match.group(1)),
                        'old_count': int(chunk_match.group(2) or 1),
                        'new_start': int(chunk_match.group(3)),
                        'new_count': int(chunk_match.group(4) or 1),
                        'context': chunk_match.group(5).strip(),
                        'changes': []
                    }
                    file_info['chunks'].append(chunk_info)
            elif line.startswith('+') and not line.startswith('+++'):
                file_info['additions'] += 1
                if file_info['chunks']:
                    file_info['chunks'][-1]['changes'].append(('add', line[1:]))
            elif line.startswith('-') and not line.startswith('---'):
                file_info['deletions'] += 1
                if file_info['chunks']:
                    file_info['chunks'][-1]['changes'].append(('delete', line[1:]))
            elif line.startswith(' ') and file_info['chunks']:
                file_info['chunks'][-1]['changes'].append(('context', line[1:]))
        
        # Analyze semantic changes
        file_info.update(self._analyze_semantic_changes(file_info))
        
        return file_info

    def _analyze_semantic_changes(self, file_info: Dict[str, Any]) -> Dict[str, List[str]]:
        """Analyze semantic changes in the file (functions, classes, imports).
        
        Args:
            file_info (Dict[str, Any]): File diff information
            
        Returns:
            Dict[str, List[str]]: Semantic changes categorized by type
        """
        semantic_changes = {
            'function_changes': [],
            'class_changes': [],
            'import_changes': [],
            'variable_changes': [],
            'config_changes': []
        }
        
        for chunk in file_info.get('chunks', []):
            for change_type, line in chunk.get('changes', []):
                if change_type in ['add', 'delete']:
                    line = line.strip()
                    
                    # Function definitions
                    if re.match(r'(def|function|async def)\s+\w+', line):
                        func_match = re.search(r'(def|function|async def)\s+(\w+)', line)
                        if func_match:
                            action = 'added' if change_type == 'add' else 'removed'
                            semantic_changes['function_changes'].append(f"{action}: {func_match.group(2)}")
                    
                    # Class definitions
                    elif re.match(r'class\s+\w+', line):
                        class_match = re.search(r'class\s+(\w+)', line)
                        if class_match:
                            action = 'added' if change_type == 'add' else 'removed'
                            semantic_changes['class_changes'].append(f"{action}: {class_match.group(1)}")
                    
                    # Import statements
                    elif re.match(r'(import|from)\s+', line):
                        action = 'added' if change_type == 'add' else 'removed'
                        semantic_changes['import_changes'].append(f"{action}: {line}")
                    
                    # Variable assignments
                    elif re.match(r'\w+\s*=', line) and not line.startswith('#'):
                        var_match = re.search(r'(\w+)\s*=', line)
                        if var_match:
                            action = 'added' if change_type == 'add' else 'removed'
                            semantic_changes['variable_changes'].append(f"{action}: {var_match.group(1)}")
                    
                    # Configuration changes (common config file patterns)
                    elif any(pattern in line.lower() for pattern in ['config', 'setting', 'env', 'port', 'host', 'url']):
                        action = 'added' if change_type == 'add' else 'removed'
                        semantic_changes['config_changes'].append(f"{action}: {line[:50]}...")
        
        return semantic_changes

    def _analyze_cross_file_relationships(self, diff_info: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze relationships and impacts between changed files.
        
        Args:
            diff_info (Dict[str, Any]): Parsed diff information
            
        Returns:
            Dict[str, Any]: Cross-file relationship analysis
        """
        relationship_analysis = {
            'coordinated_changes': [],
            'dependency_updates': [],
            'architectural_patterns': [],
            'breaking_changes': [],
            'refactoring_patterns': [],
            'impact_assessment': {},
            'change_categories': defaultdict(list)
        }
        
        files_changed = diff_info['files_changed']
        file_details = diff_info['file_details']
        
        # Group files by directory and type
        directories = defaultdict(list)
        file_types = defaultdict(list)
        
        for file_path in files_changed:
            directory = str(Path(file_path).parent)
            file_type = Path(file_path).suffix.lower()
            directories[directory].append(file_path)
            file_types[file_type].append(file_path)
            
            # Categorize by likely purpose
            if any(pattern in file_path.lower() for pattern in ['test', 'spec']):
                relationship_analysis['change_categories']['tests'].append(file_path)
            elif any(pattern in file_path.lower() for pattern in ['config', 'setting']):
                relationship_analysis['change_categories']['configuration'].append(file_path)
            elif any(pattern in file_path.lower() for pattern in ['model', 'schema']):
                relationship_analysis['change_categories']['data_models'].append(file_path)
            elif any(pattern in file_path.lower() for pattern in ['api', 'route', 'endpoint']):
                relationship_analysis['change_categories']['api'].append(file_path)
            else:
                relationship_analysis['change_categories']['core_logic'].append(file_path)
        
        # Detect coordinated changes
        for directory, files in directories.items():
            if len(files) > 1:
                relationship_analysis['coordinated_changes'].append({
                    'directory': directory,
                    'files': files,
                    'pattern': f"Multiple files changed in {directory}"
                })
        
        # Detect dependency updates
        for file_path, details in file_details.items():
            import_changes = details.get('import_changes', [])
            if import_changes:
                relationship_analysis['dependency_updates'].append({
                    'file': file_path,
                    'changes': import_changes
                })
        
        # Detect architectural patterns
        if 'package.json' in files_changed or 'requirements.txt' in files_changed:
            relationship_analysis['architectural_patterns'].append("Dependency management update")
        
        if any('migration' in f.lower() for f in files_changed):
            relationship_analysis['architectural_patterns'].append("Database schema migration")
        
        if len(relationship_analysis['change_categories']['api']) > 0 and len(relationship_analysis['change_categories']['data_models']) > 0:
            relationship_analysis['architectural_patterns'].append("API and data model coordination")
        
        # Detect potential breaking changes
        for file_path, details in file_details.items():
            function_changes = details.get('function_changes', [])
            class_changes = details.get('class_changes', [])
            
            for change in function_changes + class_changes:
                if change.startswith('removed:'):
                    relationship_analysis['breaking_changes'].append({
                        'file': file_path,
                        'change': change,
                        'impact': 'Potential breaking change - removed public interface'
                    })
        
        # Detect refactoring patterns
        if diff_info['renamed_files']:
            relationship_analysis['refactoring_patterns'].append("File/module restructuring")
        
        if len(files_changed) > 5 and diff_info['total_additions'] > diff_info['total_deletions'] * 2:
            relationship_analysis['refactoring_patterns'].append("Feature addition across multiple modules")
        elif len(files_changed) > 3 and diff_info['total_deletions'] > diff_info['total_additions']:
            relationship_analysis['refactoring_patterns'].append("Code cleanup or feature removal")
        
        return relationship_analysis

    def _create_comprehensive_diff_prompt(self, diff_info: Dict[str, Any], relationship_analysis: Dict[str, Any], original_diff: str) -> str:
        """Create comprehensive diff annotation prompt for batch processing.
        
        Args:
            diff_info (Dict[str, Any]): Parsed diff information
            relationship_analysis (Dict[str, Any]): Cross-file relationship analysis
            original_diff (str): Original diff content
            
        Returns:
            str: Formatted diff annotation prompt
        """
        prompt = """Please provide a comprehensive analysis and explanation of the following git diff, focusing on:

1. **Change Summary**: High-level overview of what was changed and why
2. **Cross-file Impact**: How changes in different files relate to each other
3. **Architectural Implications**: Structural or design pattern changes
4. **Breaking Changes**: Potential compatibility issues or API changes
5. **Business Logic Impact**: How the changes affect application functionality
6. **Risk Assessment**: Potential issues or concerns with the changes
7. **Testing Recommendations**: What should be tested based on these changes

## Diff Overview:
"""
        
        # Summary statistics
        prompt += f"- **Files Changed**: {len(diff_info['files_changed'])}\n"
        prompt += f"- **Total Additions**: +{diff_info['total_additions']} lines\n"
        prompt += f"- **Total Deletions**: -{diff_info['total_deletions']} lines\n"
        prompt += f"- **Net Change**: {diff_info['total_additions'] - diff_info['total_deletions']:+d} lines\n\n"
        
        # File categorization
        if relationship_analysis['change_categories']:
            prompt += "## Change Categories:\n"
            for category, files in relationship_analysis['change_categories'].items():
                if files:
                    prompt += f"- **{category.replace('_', ' ').title()}**: {len(files)} files\n"
            prompt += "\n"
        
        # Coordinated changes
        if relationship_analysis['coordinated_changes']:
            prompt += "## Coordinated Changes:\n"
            for coord_change in relationship_analysis['coordinated_changes']:
                prompt += f"- **{coord_change['directory']}**: {len(coord_change['files'])} files modified together\n"
            prompt += "\n"
        
        # Architectural patterns
        if relationship_analysis['architectural_patterns']:
            prompt += "## Architectural Patterns Detected:\n"
            for pattern in relationship_analysis['architectural_patterns']:
                prompt += f"- {pattern}\n"
            prompt += "\n"
        
        # Breaking changes
        if relationship_analysis['breaking_changes']:
            prompt += "## Potential Breaking Changes:\n"
            for breaking_change in relationship_analysis['breaking_changes'][:5]:  # Limit to 5
                prompt += f"- **{breaking_change['file']}**: {breaking_change['change']}\n"
            prompt += "\n"
        
        # File-by-file details
        prompt += "## File-by-File Analysis:\n\n"
        for file_path in diff_info['files_changed'][:10]:  # Limit to 10 files
            details = diff_info['file_details'][file_path]
            prompt += f"### {file_path}\n"
            prompt += f"- **Changes**: +{details['additions']} -{details['deletions']}\n"
            
            if details['is_new_file']:
                prompt += "- **Status**: New file\n"
            elif details['is_deleted']:
                prompt += "- **Status**: Deleted file\n"
            elif details['old_path'] != details['file_path']:
                prompt += f"- **Status**: Renamed from {details['old_path']}\n"
            
            # Semantic changes
            for change_type in ['function_changes', 'class_changes', 'import_changes']:
                changes = details.get(change_type, [])
                if changes:
                    prompt += f"- **{change_type.replace('_', ' ').title()}**: {', '.join(changes[:3])}\n"
                    if len(changes) > 3:
                        prompt += f"  ... and {len(changes) - 3} more\n"
            
            prompt += "\n"
        
        if len(diff_info['files_changed']) > 10:
            prompt += f"... and {len(diff_info['files_changed']) - 10} more files\n\n"
        
        # Include the actual diff (truncated for large diffs)
        prompt += "## Diff Content:\n\n"
        if len(original_diff) > 10000:  # Truncate very large diffs
            lines = original_diff.split('\n')
            prompt += '\n'.join(lines[:200]) + f"\n\n... (truncated, showing first 200 of {len(lines)} lines)\n"
        else:
            prompt += original_diff
        
        prompt += """

## Please provide:
1. **Executive Summary**: What was changed and why (2-3 sentences)
2. **Cross-file Impact Analysis**: How the changes work together
3. **Architectural Assessment**: Design and structural implications
4. **Risk Analysis**: Potential issues or concerns
5. **Testing Strategy**: What should be tested to validate these changes
6. **Deployment Considerations**: Any special deployment or rollback considerations

Focus on explaining the relationships between changes across different files and their combined impact.
"""
        
        return prompt

    async def run(self, task: Task) -> AgentOutput:
        """Execute comprehensive diff annotation with batch processing for multi-file changes.
        
        Args:
            task (Task): Task containing diff content or git parameters
            
        Returns:
            AgentOutput: Results of the diff annotation analysis
        """
        await self.emit_status("running", "Starting comprehensive diff analysis")
        
        # Get diff content from various sources
        diff_content = ""
        
        if task.params.get('diff'):
            # Direct diff content provided
            diff_content = task.params['diff']
            await self.emit_status("running", "Analyzing provided diff content")
            
        elif task.params.get('commit_range'):
            # Git commit range provided
            commit_range = task.params['commit_range']
            
            # Security: Validate commit range
            if not validate_git_ref(commit_range):
                await self.emit_status("error", f"Invalid commit range format: {commit_range}")
                return AgentOutput(
                    agent_name=self.name,
                    task_id=task.task_id,
                    result={
                        "error": "Invalid commit range format",
                        "message": "Commit range contains invalid characters",
                        "status": "failed"
                    }
                )
            
            # Security: Validate repository path
            repo_path = task.params.get('repository_path', '.')
            if not validate_repository_path(repo_path):
                await self.emit_status("error", f"Invalid repository path: {repo_path}")
                return AgentOutput(
                    agent_name=self.name,
                    task_id=task.task_id,
                    result={
                        "error": "Invalid repository path",
                        "message": "Repository path contains dangerous characters",
                        "status": "failed"
                    }
                )
            
            try:
                # Security: Use safe subprocess execution with explicit args
                result = subprocess.run(
                    ['git', 'diff', commit_range],
                    capture_output=True,
                    text=True,
                    cwd=repo_path,
                    timeout=30  # Prevent hanging
                )
                if result.returncode == 0:
                    diff_content = result.stdout
                    await self.emit_status("running", f"Retrieved diff for commit range: {commit_range}")
                else:
                    await self.emit_status("error", f"Failed to get diff for range {commit_range}")
                    return AgentOutput(
                        agent_name=self.name,
                        task_id=task.task_id,
                        result={
                            "status": "FAILED",
                            "error": f"Git diff failed: {result.stderr}"
                        }
                    )
            except Exception as e:
                await self.emit_status("error", f"Git command failed: {str(e)}")
                return AgentOutput(
                    agent_name=self.name,
                    task_id=task.task_id,
                    result={
                        "status": "FAILED",
                        "error": f"Git execution error: {str(e)}"
                    }
                )
                
        elif task.params.get('commit_hash'):
            # Single commit provided
            commit_hash = task.params['commit_hash']
            
            # Security: Validate commit hash
            if not validate_git_ref(commit_hash):
                await self.emit_status("error", f"Invalid commit hash format: {commit_hash}")
                return AgentOutput(
                    agent_name=self.name,
                    task_id=task.task_id,
                    result={
                        "error": "Invalid commit hash format",
                        "message": "Commit hash contains invalid characters",
                        "status": "failed"
                    }
                )
            
            # Security: Validate repository path
            repo_path = task.params.get('repository_path', '.')
            if not validate_repository_path(repo_path):
                await self.emit_status("error", f"Invalid repository path: {repo_path}")
                return AgentOutput(
                    agent_name=self.name,
                    task_id=task.task_id,
                    result={
                        "error": "Invalid repository path",
                        "message": "Repository path contains dangerous characters",
                        "status": "failed"
                    }
                )
            
            try:
                # Security: Use safe subprocess execution with explicit args
                result = subprocess.run(
                    ['git', 'show', '--format=', commit_hash],
                    capture_output=True,
                    text=True,
                    cwd=repo_path,
                    timeout=30  # Prevent hanging
                )
                if result.returncode == 0:
                    diff_content = result.stdout
                    await self.emit_status("running", f"Retrieved diff for commit: {commit_hash}")
                else:
                    await self.emit_status("error", f"Failed to get diff for commit {commit_hash}")
                    return AgentOutput(
                        agent_name=self.name,
                        task_id=task.task_id,
                        result={
                            "status": "FAILED",
                            "error": f"Git show failed: {result.stderr}"
                        }
                    )
            except Exception as e:
                await self.emit_status("error", f"Git command failed: {str(e)}")
                return AgentOutput(
                    agent_name=self.name,
                    task_id=task.task_id,
                    result={
                        "status": "FAILED",
                        "error": f"Git execution error: {str(e)}"
                    }
                )
        else:
            await self.emit_status("error", "No diff content, commit range, or commit hash provided")
            return AgentOutput(
                agent_name=self.name,
                task_id=task.task_id,
                result={
                    "status": "FAILED",
                    "error": "No diff source specified in task parameters"
                }
            )
        
        if not diff_content.strip():
            await self.emit_status("complete", "No changes found in diff")
            return AgentOutput(
                agent_name=self.name,
                task_id=task.task_id,
                result={
                    "status": "SUCCESS",
                    "message": "No changes found in diff",
                    "files_changed": 0
                }
            )
        
        # Parse the diff content
        await self.emit_status("running", "Parsing diff structure and changes")
        diff_info = self._parse_git_diff(diff_content)
        
        # Analyze cross-file relationships
        await self.emit_status("running", "Analyzing cross-file relationships and impacts")
        relationship_analysis = self._analyze_cross_file_relationships(diff_info)
        
        # Create comprehensive annotation prompt
        await self.emit_status("running", "Generating comprehensive diff analysis prompt")
        batch_prompt = self._create_comprehensive_diff_prompt(diff_info, relationship_analysis, diff_content)
        
        # Process with Claude API for comprehensive diff annotation
        await self.emit_status("running", "Processing diff annotation with Claude API")
        claude_response = await self.process_with_claude(batch_prompt, "diff_annotation")
        
        await self.emit_status("complete", f"Diff annotation complete for {len(diff_info['files_changed'])} files")
        
        return AgentOutput(
            agent_name=self.name,
            task_id=task.task_id,
            result={
                "status": "ANNOTATION_COMPLETE",
                "diff_summary": {
                    "files_changed": len(diff_info['files_changed']),
                    "total_additions": diff_info['total_additions'],
                    "total_deletions": diff_info['total_deletions'],
                    "net_change": diff_info['total_additions'] - diff_info['total_deletions'],
                    "binary_files": len(diff_info['binary_files']),
                    "new_files": len(diff_info['new_files']),
                    "deleted_files": len(diff_info['deleted_files']),
                    "renamed_files": len(diff_info['renamed_files'])
                },
                "cross_file_analysis": {
                    "coordinated_changes": len(relationship_analysis['coordinated_changes']),
                    "architectural_patterns": relationship_analysis['architectural_patterns'],
                    "breaking_changes": len(relationship_analysis['breaking_changes']),
                    "change_categories": dict(relationship_analysis['change_categories'])
                },
                "batch_prompt": batch_prompt,
                "claude_response": claude_response,
                "files_analyzed": diff_info['files_changed'][:10],  # First 10 for reference
                "next_step": "Review Claude API response for detailed diff explanation and impact analysis"
            }
        )
