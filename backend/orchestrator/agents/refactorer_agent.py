from __future__ import annotations

import os
import glob
import ast
from pathlib import Path
from typing import List, Dict, Optional, Set, Any
from collections import defaultdict, Counter

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


class RefactorerAgent(BaseAgent, BatchProcessingMixin):
    """Agent that proposes comprehensive refactoring suggestions using batch processing.
    
    This agent analyzes entire codebases to identify cross-file refactoring opportunities,
    architectural improvements, and code quality enhancements. It provides holistic
    refactoring suggestions that consider the relationships between modules, classes,
    and functions across the entire project.
    
    Features:
    - Batch processing for comprehensive cross-file analysis
    - Architectural pattern detection and improvement suggestions
    - Code duplication identification across multiple files
    - Dependency analysis and coupling reduction recommendations
    - Design pattern suggestions and architectural refactoring
    - Module organization and structure optimization
    - Performance optimization opportunities
    """

    def _find_code_files(self, directory: str, extensions: Optional[List[str]] = None) -> List[str]:
        """Find all code files in a directory recursively.
        
        Args:
            directory (str): Root directory to search for code files
            extensions (List[str], optional): File extensions to include
            
        Returns:
            List[str]: List of code file paths found in the directory
        """
        if extensions is None:
            extensions = ['.py', '.js', '.ts', '.tsx', '.jsx', '.java', '.cpp', '.c', '.h', '.go']
        
        code_files = []
        for ext in extensions:
            pattern = f"**/*{ext}"
            files = glob.glob(os.path.join(directory, pattern), recursive=True)
            
            # Filter out common directories that shouldn't be refactored
            filtered_files = []
            for file_path in files:
                path_parts = Path(file_path).parts
                skip_dirs = {
                    'node_modules', '__pycache__', '.git', 'dist', 'build', 
                    'target', '.pytest_cache', 'venv', 'env', 'migrations'
                }
                
                if not any(skip_dir in path_parts for skip_dir in skip_dirs):
                    filtered_files.append(file_path)
            
            code_files.extend(filtered_files)
        
        return sorted(list(set(code_files)))

    def _read_and_parse_file(self, file_path: str) -> Dict[str, Any]:
        """Read file and extract structural information for analysis.
        
        Args:
            file_path (str): Path to the file to analyze
            
        Returns:
            Dict[str, Any]: File metadata and structural information
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            file_info = {
                'path': file_path,
                'content': content,
                'size': len(content),
                'lines': len(content.split('\n')),
                'extension': Path(file_path).suffix.lower(),
                'classes': [],
                'functions': [],
                'imports': [],
                'complexity_indicators': {},
                'potential_issues': []
            }
            
            # Python-specific parsing
            if file_info['extension'] == '.py':
                file_info.update(self._parse_python_file(content, file_path))
            
            return file_info
            
        except Exception as e:
            return {
                'path': file_path,
                'error': f'Could not analyze file: {str(e)}',
                'extension': Path(file_path).suffix.lower()
            }

    def _parse_python_file(self, content: str, file_path: str) -> Dict[str, Any]:
        """Parse Python file to extract structural information.
        
        Args:
            content (str): File content to parse
            file_path (str): Path to the file being parsed
            
        Returns:
            Dict[str, Any]: Python-specific structural information
        """
        analysis = {
            'classes': [],
            'functions': [],
            'imports': [],
            'complexity_indicators': {},
            'potential_issues': []
        }
        
        try:
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                # Extract class information
                if isinstance(node, ast.ClassDef):
                    methods = [n.name for n in node.body if isinstance(n, ast.FunctionDef)]
                    analysis['classes'].append({
                        'name': node.name,
                        'line': node.lineno,
                        'methods': methods,
                        'method_count': len(methods),
                        'bases': [self._get_node_name(base) for base in node.bases]
                    })
                
                # Extract function information
                elif isinstance(node, ast.FunctionDef):
                    analysis['functions'].append({
                        'name': node.name,
                        'line': node.lineno,
                        'args': len(node.args.args),
                        'is_method': isinstance(node, ast.FunctionDef) and hasattr(node, 'parent_class')
                    })
                
                # Extract import information
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        analysis['imports'].append({
                            'module': alias.name,
                            'alias': alias.asname,
                            'type': 'import'
                        })
                
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ''
                    for alias in node.names:
                        analysis['imports'].append({
                            'module': f"{module}.{alias.name}" if module else alias.name,
                            'alias': alias.asname,
                            'from_module': module,
                            'type': 'from_import'
                        })
            
            # Calculate complexity indicators
            analysis['complexity_indicators'] = {
                'total_classes': len(analysis['classes']),
                'total_functions': len(analysis['functions']),
                'total_imports': len(analysis['imports']),
                'avg_methods_per_class': sum(c['method_count'] for c in analysis['classes']) / max(len(analysis['classes']), 1),
                'large_classes': [c['name'] for c in analysis['classes'] if c['method_count'] > 10],
                'complex_functions': [f['name'] for f in analysis['functions'] if f['args'] > 5]
            }
            
        except SyntaxError as e:
            analysis['potential_issues'].append(f"Syntax error: {str(e)}")
        except Exception as e:
            analysis['potential_issues'].append(f"Analysis error: {str(e)}")
        
        return analysis

    def _get_node_name(self, node) -> str:
        """Extract name from AST node."""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._get_node_name(node.value)}.{node.attr}"
        else:
            return str(node)

    def _analyze_cross_file_patterns(self, files_data: List[Dict]) -> Dict[str, Any]:
        """Analyze patterns and relationships across multiple files.
        
        Args:
            files_data (List[Dict]): List of file analysis data
            
        Returns:
            Dict[str, Any]: Cross-file analysis results and refactoring opportunities
        """
        analysis = {
            'architecture_overview': {},
            'refactoring_opportunities': [],
            'design_patterns': [],
            'dependency_analysis': {},
            'code_duplication': [],
            'module_organization': {},
            'performance_opportunities': [],
            'architectural_improvements': []
        }
        
        # Architecture overview
        total_files = len(files_data)
        total_classes = sum(len(f.get('classes', [])) for f in files_data)
        total_functions = sum(len(f.get('functions', [])) for f in files_data)
        
        analysis['architecture_overview'] = {
            'total_files': total_files,
            'total_classes': total_classes,
            'total_functions': total_functions,
            'avg_classes_per_file': total_classes / max(total_files, 1),
            'avg_functions_per_file': total_functions / max(total_files, 1)
        }
        
        # Analyze imports and dependencies
        all_imports = defaultdict(list)
        module_dependencies = defaultdict(set)
        
        for file_data in files_data:
            file_path = file_data.get('path', '')
            for imp in file_data.get('imports', []):
                all_imports[imp['module']].append(file_path)
                module_dependencies[file_path].add(imp['module'])
        
        # Identify highly coupled modules
        coupling_analysis = []
        for file_path, deps in module_dependencies.items():
            if len(deps) > 10:  # High coupling threshold
                coupling_analysis.append({
                    'file': file_path,
                    'dependency_count': len(deps),
                    'dependencies': list(deps)[:5]  # Show first 5
                })
        
        analysis['dependency_analysis'] = {
            'highly_coupled_files': coupling_analysis,
            'most_imported_modules': dict(Counter(all_imports.keys()).most_common(10))
        }
        
        # Identify refactoring opportunities
        refactoring_ops = []
        
        # Large files
        large_files = [f for f in files_data if f.get('lines', 0) > 500]
        if large_files:
            refactoring_ops.append({
                'type': 'split_large_files',
                'priority': 'high',
                'description': f'Split {len(large_files)} large files (>500 lines)',
                'files': [f['path'] for f in large_files[:5]],
                'suggestion': 'Consider breaking large files into smaller, focused modules'
            })
        
        # Classes with too many methods
        large_classes = []
        for file_data in files_data:
            for cls in file_data.get('classes', []):
                if cls['method_count'] > 15:
                    large_classes.append({
                        'class': cls['name'],
                        'file': file_data['path'],
                        'method_count': cls['method_count']
                    })
        
        if large_classes:
            refactoring_ops.append({
                'type': 'split_large_classes',
                'priority': 'medium',
                'description': f'Refactor {len(large_classes)} classes with >15 methods',
                'classes': large_classes[:5],
                'suggestion': 'Apply Single Responsibility Principle, extract related methods into separate classes'
            })
        
        # Duplicate class/function names
        class_names = defaultdict(list)
        function_names = defaultdict(list)
        
        for file_data in files_data:
            for cls in file_data.get('classes', []):
                class_names[cls['name']].append(file_data['path'])
            for func in file_data.get('functions', []):
                function_names[func['name']].append(file_data['path'])
        
        duplicate_classes = {name: files for name, files in class_names.items() if len(files) > 1}
        duplicate_functions = {name: files for name, files in function_names.items() if len(files) > 1 and name not in ['__init__', 'main']}
        
        if duplicate_classes or duplicate_functions:
            refactoring_ops.append({
                'type': 'resolve_naming_conflicts',
                'priority': 'medium',
                'description': 'Resolve duplicate class/function names across files',
                'duplicate_classes': dict(list(duplicate_classes.items())[:3]),
                'duplicate_functions': dict(list(duplicate_functions.items())[:3]),
                'suggestion': 'Use more specific names or organize into different namespaces'
            })
        
        analysis['refactoring_opportunities'] = refactoring_ops
        
        # Architectural improvements
        arch_improvements = []
        
        if analysis['architecture_overview']['avg_classes_per_file'] > 5:
            arch_improvements.append({
                'type': 'module_organization',
                'suggestion': 'Consider organizing classes into separate modules (current avg: {:.1f} classes/file)'.format(
                    analysis['architecture_overview']['avg_classes_per_file']
                )
            })
        
        if len(coupling_analysis) > 0:
            arch_improvements.append({
                'type': 'dependency_injection',
                'suggestion': 'Implement dependency injection to reduce tight coupling between modules'
            })
        
        analysis['architectural_improvements'] = arch_improvements
        
        return analysis

    def _create_batch_refactoring_prompt(self, files_data: List[Dict], analysis: Dict) -> str:
        """Create comprehensive refactoring prompt for batch processing.
        
        Args:
            files_data (List[Dict]): File analysis data
            analysis (Dict): Cross-file analysis results
            
        Returns:
            str: Formatted refactoring prompt
        """
        prompt = """Please analyze the following codebase and provide comprehensive refactoring suggestions.

Focus on:
1. **Architectural Improvements**: Overall structure, design patterns, module organization
2. **Cross-file Refactoring**: Opportunities that span multiple files
3. **Code Quality**: Maintainability, readability, and best practices
4. **Design Patterns**: Appropriate pattern applications and anti-pattern elimination
5. **Performance**: Optimization opportunities and resource efficiency
6. **Coupling Reduction**: Minimize dependencies and improve modularity
7. **Single Responsibility**: Ensure classes and functions have focused purposes

## Architecture Overview:
"""
        
        arch = analysis['architecture_overview']
        prompt += f"- **Total Files**: {arch['total_files']}\n"
        prompt += f"- **Total Classes**: {arch['total_classes']}\n" 
        prompt += f"- **Total Functions**: {arch['total_functions']}\n"
        prompt += f"- **Average Classes per File**: {arch['avg_classes_per_file']:.1f}\n"
        prompt += f"- **Average Functions per File**: {arch['avg_functions_per_file']:.1f}\n\n"
        
        # Current issues identified
        if analysis['refactoring_opportunities']:
            prompt += "## Identified Issues:\n"
            for i, opp in enumerate(analysis['refactoring_opportunities'], 1):
                prompt += f"{i}. **{opp['type'].replace('_', ' ').title()}** ({opp['priority']} priority)\n"
                prompt += f"   - {opp['description']}\n"
                prompt += f"   - Suggestion: {opp['suggestion']}\n\n"
        
        # Dependency analysis
        if analysis['dependency_analysis']['highly_coupled_files']:
            prompt += "## High Coupling Issues:\n"
            for coupling in analysis['dependency_analysis']['highly_coupled_files'][:3]:
                prompt += f"- **{Path(coupling['file']).name}**: {coupling['dependency_count']} dependencies\n"
        
        prompt += "\n## Codebase Files:\n\n"
        
        # Include file contents (limited for token efficiency)
        for file_data in files_data[:15]:  # Limit to 15 files
            if 'error' in file_data:
                prompt += f"**{file_data['path']}** (ERROR: {file_data['error']})\n\n"
                continue
            
            prompt += f"**{file_data['path']}** ({file_data['lines']} lines)\n"
            if file_data.get('classes'):
                prompt += f"Classes: {', '.join(c['name'] for c in file_data['classes'][:3])}\n"
            if file_data.get('functions'):
                prompt += f"Functions: {', '.join(f['name'] for f in file_data['functions'][:5])}\n"
            
            # Include actual content for smaller files
            if file_data.get('content') and file_data['lines'] < 100:
                prompt += "```" + file_data.get('extension', '').replace('.', '') + "\n"
                prompt += file_data['content'] + "\n```\n\n"
            else:
                prompt += f"(Large file - {file_data['lines']} lines, showing structure only)\n\n"
        
        if len(files_data) > 15:
            prompt += f"... and {len(files_data) - 15} more files\n\n"
        
        prompt += """
## Please provide:
1. **Priority Refactoring Plan**: Step-by-step refactoring approach
2. **Architectural Recommendations**: High-level structural improvements
3. **Cross-file Refactoring**: Specific opportunities spanning multiple files
4. **Design Pattern Applications**: Where patterns could improve the design
5. **Module Organization**: Suggestions for better file/package structure
6. **Performance Optimizations**: Code efficiency improvements
7. **Implementation Guide**: Detailed steps for major refactoring initiatives

Prioritize suggestions by impact and provide concrete, actionable recommendations.
"""
        
        return prompt

    async def run(self, task: Task) -> AgentOutput:
        """Execute comprehensive refactoring analysis with batch processing.
        
        Args:
            task (Task): Task containing files to refactor or directory to analyze
            
        Returns:
            AgentOutput: Results of the refactoring analysis with suggestions
        """
        await self.emit_status("running", "Starting comprehensive refactoring analysis")
        
        files_to_analyze = []
        
        # Handle directory-based analysis
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
            files_to_analyze = self._find_code_files(directory, task.params.get('extensions'))
            
        # Handle file-list based analysis
        elif task.files:
            files_to_analyze = task.files
            
        else:
            await self.emit_status("error", "No files or directory specified for refactoring analysis")
            return AgentOutput(
                agent_name=self.name,
                task_id=task.task_id,
                result={
                    "status": "FAILED",
                    "error": "No files or directory specified in task"
                }
            )
        
        if not files_to_analyze:
            await self.emit_status("complete", "No code files found to analyze")
            return AgentOutput(
                agent_name=self.name,
                task_id=task.task_id,
                result={
                    "status": "SUCCESS",
                    "files_found": 0,
                    "message": "No code files found for refactoring analysis"
                }
            )
        
        await self.emit_status("running", f"Analyzing {len(files_to_analyze)} files for refactoring opportunities")
        
        # Parse and analyze all files
        files_data = []
        for file_path in files_to_analyze:
            file_data = self._read_and_parse_file(file_path)
            files_data.append(file_data)
        
        # Perform cross-file analysis
        await self.emit_status("running", "Identifying cross-file refactoring opportunities")
        cross_file_analysis = self._analyze_cross_file_patterns(files_data)
        
        # Create comprehensive refactoring prompt
        await self.emit_status("running", "Generating refactoring recommendations")
        batch_prompt = self._create_batch_refactoring_prompt(files_data, cross_file_analysis)
        
        # Process with Claude API for comprehensive refactoring analysis
        await self.emit_status("running", "Processing refactoring analysis with Claude API")
        claude_response = await self.process_with_claude(batch_prompt, "refactoring")
        
        await self.emit_status("complete", f"Refactoring analysis complete for {len(files_to_analyze)} files")
        
        return AgentOutput(
            agent_name=self.name,
            task_id=task.task_id,
            result={
                "status": "REFACTORING_COMPLETE",
                "files_analyzed": len(files_to_analyze),
                "architecture_overview": cross_file_analysis['architecture_overview'],
                "refactoring_opportunities": cross_file_analysis['refactoring_opportunities'],
                "architectural_improvements": cross_file_analysis['architectural_improvements'],
                "dependency_analysis": cross_file_analysis['dependency_analysis'],
                "batch_prompt": batch_prompt,
                "claude_response": claude_response,
                "analysis_scope": {
                    "directory": task.params.get('directory'),
                    "files": files_to_analyze[:10],  # First 10 files for reference
                    "total_files": len(files_to_analyze)
                },
                "next_step": "Review Claude API response for detailed refactoring recommendations and implementation guidance"
            }
        )
