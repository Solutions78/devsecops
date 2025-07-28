from __future__ import annotations

import os
import glob
import ast
import re
from pathlib import Path
from typing import List, Dict, Optional, Set, Any, Tuple
from collections import defaultdict

# This module defines the *TestEngineerAgent* class.  Despite the filename
# starting with ``test_`` it is *not* a test file.  Setting the special
# ``__test__`` attribute to *False* prevents *pytest* from collecting it as a
# test module and silences collection warnings.

__test__: bool = False

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
        pass


class TestEngineerAgent(BaseAgent, BatchProcessingMixin):
    """Agent that generates comprehensive test suites with focus on integration testing.
    
    This agent analyzes entire codebases to generate comprehensive test suites that include
    both unit tests and integration tests. It understands cross-file dependencies and
    generates tests that validate module interactions, data flow, and system behavior
    across the full application stack.
    
    Features:
    - Batch processing for comprehensive cross-module test generation
    - Integration test suite creation for related modules
    - Cross-file dependency analysis for test planning
    - Positive and negative test case generation
    - Test coverage analysis across the full codebase
    - API endpoint testing and workflow validation
    - Database integration and data flow testing
    - Mock and fixture generation for complex dependencies
    """

    # Mark the class itself as *not* a test so that when it is imported into
    # real test modules (e.g. ``test_agent_functionality.py``) pytest does not
    # attempt to collect it as a test case.
    __test__: bool = False

    def _find_source_files(self, directory: str, extensions: Optional[List[str]] = None) -> List[str]:
        """Find all source code files for test generation.
        
        Args:
            directory (str): Root directory to search for source files
            extensions (List[str], optional): File extensions to include
            
        Returns:
            List[str]: List of source file paths found in the directory
        """
        if extensions is None:
            extensions = ['.py', '.js', '.ts', '.tsx', '.jsx', '.java', '.cpp', '.c', '.go']
        
        source_files = []
        test_patterns = ['test_*.py', '*_test.py', '*.test.js', '*.spec.js', '*.test.ts', '*.spec.ts']
        
        for ext in extensions:
            pattern = f"**/*{ext}"
            files = glob.glob(os.path.join(directory, pattern), recursive=True)
            
            # Filter out existing test files and unwanted directories
            filtered_files = []
            for file_path in files:
                path_parts = Path(file_path).parts
                file_name = Path(file_path).name
                
                # Skip directories that shouldn't be tested
                skip_dirs = {
                    'node_modules', '__pycache__', '.git', 'dist', 'build', 
                    'target', '.pytest_cache', 'venv', 'env', 'migrations', 'tests'
                }
                
                # Skip existing test files
                is_test_file = any(
                    file_name.startswith('test_') or 
                    file_name.endswith('_test' + ext) or
                    '.test.' in file_name or
                    '.spec.' in file_name
                    for ext in extensions
                )
                
                if not any(skip_dir in path_parts for skip_dir in skip_dirs) and not is_test_file:
                    filtered_files.append(file_path)
            
            source_files.extend(filtered_files)
        
        return sorted(list(set(source_files)))

    def _analyze_file_structure(self, file_path: str) -> Dict[str, Any]:
        """Analyze file structure to understand testable components.
        
        Args:
            file_path (str): Path to the source file to analyze
            
        Returns:
            Dict[str, Any]: Detailed analysis of file structure for test generation
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
                'module_name': Path(file_path).stem,
                'classes': [],
                'functions': [],
                'imports': [],
                'api_endpoints': [],
                'database_models': [],
                'async_functions': [],
                'test_complexity': 'medium',
                'integration_points': []
            }
            
            # Python-specific analysis
            if file_info['extension'] == '.py':
                file_info.update(self._analyze_python_file(content, file_path))
            # JavaScript/TypeScript analysis
            elif file_info['extension'] in ['.js', '.ts', '.jsx', '.tsx']:
                file_info.update(self._analyze_javascript_file(content, file_path))
            
            return file_info
            
        except Exception as e:
            return {
                'path': file_path,
                'error': f'Could not analyze file: {str(e)}',
                'extension': Path(file_path).suffix.lower(),
                'test_complexity': 'unknown'
            }

    def _analyze_python_file(self, content: str, file_path: str) -> Dict[str, Any]:
        """Analyze Python file for testable components and integration points.
        
        Args:
            content (str): File content to analyze
            file_path (str): Path to the file being analyzed
            
        Returns:
            Dict[str, Any]: Python-specific analysis for test generation
        """
        analysis = {
            'classes': [],
            'functions': [],
            'imports': [],
            'api_endpoints': [],
            'database_models': [],
            'async_functions': [],
            'integration_points': []
        }
        
        try:
            tree = ast.parse(content)
            
            # Track decorators that indicate special functionality
            api_decorators = ['@app.route', '@router.get', '@router.post', '@router.put', '@router.delete']
            db_base_classes = ['BaseModel', 'Model', 'Document', 'db.Model']
            
            for node in ast.walk(tree):
                # Analyze classes
                if isinstance(node, ast.ClassDef):
                    methods = []
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            methods.append({
                                'name': item.name,
                                'line': item.lineno,
                                'is_async': isinstance(item, ast.AsyncFunctionDef),
                                'args': len(item.args.args),
                                'has_decorators': len(item.decorator_list) > 0
                            })
                    
                    # Check if it's a database model
                    is_db_model = any(
                        self._get_node_name(base) in db_base_classes 
                        for base in node.bases
                    )
                    
                    class_info = {
                        'name': node.name,
                        'line': node.lineno,
                        'methods': methods,
                        'method_count': len(methods),
                        'bases': [self._get_node_name(base) for base in node.bases],
                        'is_database_model': is_db_model,
                        'has_decorators': len(node.decorator_list) > 0
                    }
                    
                    analysis['classes'].append(class_info)
                    
                    if is_db_model:
                        analysis['database_models'].append(class_info)
                
                # Analyze functions
                elif isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
                    is_async = isinstance(node, ast.AsyncFunctionDef)
                    
                    # Check for API endpoint decorators
                    is_api_endpoint = any(
                        any(decorator in ast.dump(dec) for decorator in api_decorators)
                        for dec in node.decorator_list
                    )
                    
                    func_info = {
                        'name': node.name,
                        'line': node.lineno,
                        'is_async': is_async,
                        'args': len(node.args.args),
                        'has_decorators': len(node.decorator_list) > 0,
                        'is_api_endpoint': is_api_endpoint,
                        'returns_value': self._has_return_statement(node)
                    }
                    
                    analysis['functions'].append(func_info)
                    
                    if is_async:
                        analysis['async_functions'].append(func_info)
                    
                    if is_api_endpoint:
                        analysis['api_endpoints'].append(func_info)
                
                # Analyze imports for integration points
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        import_info = {
                            'module': alias.name,
                            'alias': alias.asname,
                            'type': 'import'
                        }
                        analysis['imports'].append(import_info)
                        
                        # Identify integration points
                        if any(keyword in alias.name.lower() for keyword in 
                              ['database', 'db', 'sql', 'mongo', 'redis', 'api', 'http', 'requests']):
                            analysis['integration_points'].append({
                                'type': 'external_service',
                                'module': alias.name,
                                'line': node.lineno
                            })
                
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ''
                    for alias in node.names:
                        import_info = {
                            'module': f"{module}.{alias.name}" if module else alias.name,
                            'alias': alias.asname,
                            'from_module': module,
                            'type': 'from_import'
                        }
                        analysis['imports'].append(import_info)
            
        except Exception as e:
            analysis['parse_error'] = str(e)
        
        return analysis

    def _analyze_javascript_file(self, content: str, file_path: str) -> Dict[str, Any]:
        """Analyze JavaScript/TypeScript file for testable components.
        
        Args:
            content (str): File content to analyze
            file_path (str): Path to the file being analyzed
            
        Returns:
            Dict[str, Any]: JavaScript/TypeScript-specific analysis
        """
        analysis = {
            'classes': [],
            'functions': [],
            'imports': [],
            'api_endpoints': [],
            'components': [],
            'hooks': [],
            'integration_points': []
        }
        
        # Simple regex-based analysis for JavaScript/TypeScript
        # This could be enhanced with a proper JS/TS parser
        
        # Find function declarations
        func_patterns = [
            r'function\s+(\w+)\s*\(',
            r'const\s+(\w+)\s*=\s*\(',
            r'(\w+)\s*:\s*\([^)]*\)\s*=>', 
            r'async\s+function\s+(\w+)\s*\('
        ]
        
        for pattern in func_patterns:
            matches = re.finditer(pattern, content)
            for match in matches:
                analysis['functions'].append({
                    'name': match.group(1),
                    'line': content[:match.start()].count('\n') + 1,
                    'is_async': 'async' in match.group(0)
                })
        
        # Find React components
        component_patterns = [
            r'const\s+(\w+)\s*=\s*\([^)]*\)\s*=>\s*{',
            r'function\s+(\w+)\s*\([^)]*\)\s*{[^}]*return\s*\('
        ]
        
        for pattern in component_patterns:
            matches = re.finditer(pattern, content)
            for match in matches:
                analysis['components'].append({
                    'name': match.group(1),
                    'line': content[:match.start()].count('\n') + 1
                })
        
        # Find imports
        import_matches = re.finditer(r'import\s+.*?\s+from\s+[\'"]([^\'"]+)[\'"]', content)
        for match in import_matches:
            analysis['imports'].append({
                'module': match.group(1),
                'line': content[:match.start()].count('\n') + 1
            })
        
        return analysis

    def _has_return_statement(self, node: ast.FunctionDef) -> bool:
        """Check if function has return statements."""
        for child in ast.walk(node):
            if isinstance(child, ast.Return):
                return True
        return False

    def _get_node_name(self, node) -> str:
        """Extract name from AST node."""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._get_node_name(node.value)}.{node.attr}"
        else:
            return str(node)

    def _analyze_integration_relationships(self, files_data: List[Dict]) -> Dict[str, Any]:
        """Analyze relationships between modules for integration testing.
        
        Args:
            files_data (List[Dict]): List of file analysis data
            
        Returns:
            Dict[str, Any]: Integration analysis and test planning data
        """
        integration_analysis = {
            'module_dependencies': defaultdict(set),
            'api_workflows': [],
            'database_interactions': [],
            'cross_module_calls': [],
            'integration_test_suites': [],
            'test_coverage_plan': {},
            'mock_requirements': [],
            'test_complexity_assessment': {}
        }
        
        # Build dependency graph
        for file_data in files_data:
            file_path = file_data.get('path', '')
            module_name = file_data.get('module_name', '')
            
            for import_info in file_data.get('imports', []):
                if '.' in import_info['module']:  # Local imports
                    integration_analysis['module_dependencies'][module_name].add(import_info['module'])
        
        # Identify API workflows
        api_files = [f for f in files_data if f.get('api_endpoints')]
        for api_file in api_files:
            for endpoint in api_file['api_endpoints']:
                workflow = {
                    'endpoint': endpoint['name'],
                    'file': api_file['path'],
                    'dependencies': list(integration_analysis['module_dependencies'].get(api_file['module_name'], [])),
                    'test_scenarios': self._generate_api_test_scenarios(endpoint)
                }
                integration_analysis['api_workflows'].append(workflow)
        
        # Identify database interaction patterns
        db_files = [f for f in files_data if f.get('database_models')]
        for db_file in db_files:
            for model in db_file['database_models']:
                db_interaction = {
                    'model': model['name'],
                    'file': db_file['path'],
                    'crud_operations': [m['name'] for m in model['methods'] if any(crud in m['name'].lower() for crud in ['create', 'read', 'update', 'delete', 'save', 'find'])],
                    'test_scenarios': self._generate_db_test_scenarios(model)
                }
                integration_analysis['database_interactions'].append(db_interaction)
        
        # Plan integration test suites
        integration_analysis['integration_test_suites'] = self._plan_integration_test_suites(
            integration_analysis['api_workflows'],
            integration_analysis['database_interactions'],
            integration_analysis['module_dependencies']
        )
        
        # Assess test complexity and coverage
        integration_analysis['test_complexity_assessment'] = self._assess_test_complexity(files_data)
        
        return integration_analysis

    def _generate_api_test_scenarios(self, endpoint: Dict) -> List[Dict]:
        """Generate test scenarios for API endpoints.
        
        Args:
            endpoint (Dict): Endpoint information
            
        Returns:
            List[Dict]: List of test scenarios
        """
        scenarios = []
        
        # Basic positive test
        scenarios.append({
            'type': 'positive',
            'name': f'test_{endpoint["name"]}_success',
            'description': f'Test successful {endpoint["name"]} operation',
            'test_data': 'valid_data',
            'expected_result': 'success_response'
        })
        
        # Negative tests
        scenarios.extend([
            {
                'type': 'negative',
                'name': f'test_{endpoint["name"]}_invalid_input',
                'description': f'Test {endpoint["name"]} with invalid input',
                'test_data': 'invalid_data',
                'expected_result': 'error_response'
            },
            {
                'type': 'negative', 
                'name': f'test_{endpoint["name"]}_unauthorized',
                'description': f'Test {endpoint["name"]} without authorization',
                'test_data': 'valid_data_no_auth',
                'expected_result': 'unauthorized_error'
            }
        ])
        
        return scenarios

    def _generate_db_test_scenarios(self, model: Dict) -> List[Dict]:
        """Generate test scenarios for database models.
        
        Args:
            model (Dict): Database model information
            
        Returns:
            List[Dict]: List of database test scenarios
        """
        scenarios = []
        
        # CRUD operation tests
        crud_ops = ['create', 'read', 'update', 'delete']
        for op in crud_ops:
            scenarios.extend([
                {
                    'type': 'positive',
                    'name': f'test_{model["name"]}_{op}_success',
                    'description': f'Test successful {op} operation on {model["name"]}',
                    'operation': op
                },
                {
                    'type': 'negative',
                    'name': f'test_{model["name"]}_{op}_invalid_data',
                    'description': f'Test {op} operation with invalid data',
                    'operation': op
                }
            ])
        
        # Relationship tests
        scenarios.append({
            'type': 'integration',
            'name': f'test_{model["name"]}_relationships',
            'description': f'Test {model["name"]} model relationships and foreign keys',
            'operation': 'relationship_validation'
        })
        
        return scenarios

    def _plan_integration_test_suites(self, api_workflows: List, db_interactions: List, dependencies: Dict) -> List[Dict]:
        """Plan comprehensive integration test suites.
        
        Args:
            api_workflows (List): API workflow information
            db_interactions (List): Database interaction information  
            dependencies (Dict): Module dependency mapping
            
        Returns:
            List[Dict]: Planned integration test suites
        """
        test_suites = []
        
        # End-to-end workflow tests
        if api_workflows and db_interactions:
            test_suites.append({
                'name': 'end_to_end_workflow_tests',
                'type': 'integration',
                'description': 'Complete workflow tests from API to database',
                'components': ['api_endpoints', 'business_logic', 'database_models'],
                'test_scenarios': [
                    'test_complete_user_workflow',
                    'test_data_flow_integrity',
                    'test_transaction_rollback',
                    'test_concurrent_operations'
                ]
            })
        
        # Module integration tests
        for module, deps in dependencies.items():
            if len(deps) > 2:  # Only create integration tests for modules with multiple dependencies
                test_suites.append({
                    'name': f'{module}_integration_tests',
                    'type': 'module_integration',
                    'description': f'Integration tests for {module} with its dependencies',
                    'target_module': module,
                    'dependencies': list(deps),
                    'test_scenarios': [
                        f'test_{module}_dependency_injection',
                        f'test_{module}_error_handling',
                        f'test_{module}_data_validation'
                    ]
                })
        
        # Cross-service integration tests
        if any('api' in str(deps) or 'service' in str(deps) for deps in dependencies.values()):
            test_suites.append({
                'name': 'cross_service_integration_tests',
                'type': 'service_integration',
                'description': 'Tests for interactions between different services',
                'test_scenarios': [
                    'test_service_communication',
                    'test_service_failure_handling',
                    'test_service_timeout_handling',
                    'test_service_retry_logic'
                ]
            })
        
        return test_suites

    def _assess_test_complexity(self, files_data: List[Dict]) -> Dict[str, Any]:
        """Assess overall test complexity and coverage requirements.
        
        Args:
            files_data (List[Dict]): File analysis data
            
        Returns:
            Dict[str, Any]: Test complexity assessment
        """
        assessment = {
            'overall_complexity': 'medium',
            'high_complexity_files': [],
            'coverage_targets': {},
            'test_priorities': [],
            'estimated_test_count': 0
        }
        
        total_functions = sum(len(f.get('functions', [])) for f in files_data)
        total_classes = sum(len(f.get('classes', [])) for f in files_data)
        api_endpoints = sum(len(f.get('api_endpoints', [])) for f in files_data)
        db_models = sum(len(f.get('database_models', [])) for f in files_data)
        
        # Estimate test count (unit + integration)
        unit_tests = total_functions + (total_classes * 2)  # 2 tests per class on average
        integration_tests = api_endpoints * 3 + db_models * 4  # Multiple scenarios per component
        assessment['estimated_test_count'] = unit_tests + integration_tests
        
        # Determine complexity
        if api_endpoints > 10 or db_models > 5 or total_functions > 50:
            assessment['overall_complexity'] = 'high'
        elif api_endpoints > 5 or db_models > 2 or total_functions > 20:
            assessment['overall_complexity'] = 'medium'
        else:
            assessment['overall_complexity'] = 'low'
        
        # Set coverage targets
        assessment['coverage_targets'] = {
            'unit_test_coverage': '90%',
            'integration_test_coverage': '80%',
            'api_endpoint_coverage': '100%',
            'database_model_coverage': '95%'
        }
        
        # Prioritize test creation
        assessment['test_priorities'] = [
            'Critical API endpoints',
            'Database model operations',
            'Cross-module integrations',
            'Complex business logic functions',
            'Error handling and edge cases'
        ]
        
        return assessment

    def _create_comprehensive_test_prompt(self, files_data: List[Dict], integration_analysis: Dict) -> str:
        """Create comprehensive test generation prompt for batch processing.
        
        Args:
            files_data (List[Dict]): Source file analysis data
            integration_analysis (Dict): Integration analysis results
            
        Returns:
            str: Formatted test generation prompt
        """
        prompt = """Please generate comprehensive test suites for the following codebase, focusing on both unit tests and integration tests.

## Test Generation Requirements:

1. **Unit Tests**: Test individual functions, methods, and classes
2. **Integration Tests**: Test interactions between modules, APIs, and databases
3. **Positive Test Cases**: Verify expected behavior with valid inputs
4. **Negative Test Cases**: Test error handling, edge cases, and invalid inputs
5. **Mock and Fixture Generation**: Create necessary test data and mock objects
6. **Test Coverage**: Ensure comprehensive coverage across all critical paths

## Codebase Analysis:
"""
        
        # Overview
        total_files = len(files_data)
        total_functions = sum(len(f.get('functions', [])) for f in files_data)
        total_classes = sum(len(f.get('classes', [])) for f in files_data)
        api_endpoints = sum(len(f.get('api_endpoints', [])) for f in files_data)
        db_models = sum(len(f.get('database_models', [])) for f in files_data)
        
        prompt += f"- **Total Files**: {total_files}\n"
        prompt += f"- **Total Functions**: {total_functions}\n"
        prompt += f"- **Total Classes**: {total_classes}\n"
        prompt += f"- **API Endpoints**: {api_endpoints}\n"
        prompt += f"- **Database Models**: {db_models}\n"
        prompt += f"- **Estimated Tests**: {integration_analysis['test_complexity_assessment']['estimated_test_count']}\n\n"
        
        # Integration test suites
        if integration_analysis['integration_test_suites']:
            prompt += "## Planned Integration Test Suites:\n"
            for suite in integration_analysis['integration_test_suites']:
                prompt += f"- **{suite['name']}**: {suite['description']}\n"
        
        prompt += "\n## Source Files to Test:\n\n"
        
        # Include source file information
        for file_data in files_data[:10]:  # Limit for token efficiency
            if 'error' in file_data:
                prompt += f"**{file_data['path']}** (ERROR: {file_data['error']})\n\n"
                continue
            
            prompt += f"**{file_data['path']}**\n"
            if file_data.get('classes'):
                prompt += f"Classes: {', '.join(c['name'] for c in file_data['classes'])}\n"
            if file_data.get('functions'):
                prompt += f"Functions: {', '.join(f['name'] for f in file_data['functions'][:5])}\n"
            if file_data.get('api_endpoints'):
                prompt += f"API Endpoints: {', '.join(e['name'] for e in file_data['api_endpoints'])}\n"
            if file_data.get('database_models'):
                prompt += f"DB Models: {', '.join(m['name'] for m in file_data['database_models'])}\n"
            
            # Include content for smaller files
            if file_data.get('content') and file_data['lines'] < 50:
                prompt += "```" + file_data.get('extension', '').replace('.', '') + "\n"
                prompt += file_data['content'] + "\n```\n\n"
            else:
                prompt += f"({file_data['lines']} lines - see structure above)\n\n"
        
        if len(files_data) > 10:
            prompt += f"... and {len(files_data) - 10} more files\n\n"
        
        prompt += """
## Please Generate:

1. **Unit Test Files**: Complete test files for each source module
   - Test all public functions and methods
   - Include positive and negative test cases
   - Add edge case testing
   - Use appropriate assertions and test data

2. **Integration Test Suites**: Cross-module integration tests
   - API endpoint testing with various scenarios
   - Database integration tests with CRUD operations
   - Service interaction tests
   - End-to-end workflow validation

3. **Test Fixtures and Mocks**: Supporting test infrastructure
   - Mock data generators
   - Database fixtures
   - API response mocks
   - Test configuration files

4. **Test Configuration**: Setup and teardown procedures
   - Database setup/cleanup
   - Mock service configuration
   - Test environment variables
   - CI/CD integration setup

5. **Coverage Analysis**: Recommendations for test coverage
   - Critical path identification
   - Risk assessment for untested code
   - Coverage improvement suggestions

Format each test file with proper imports, setup/teardown, and clear test documentation.
"""
        
        return prompt

    async def run(self, task: Task) -> AgentOutput:
        """Execute comprehensive test generation with focus on integration testing.
        
        Args:
            task (Task): Task containing source files or directory to test
            
        Returns:
            AgentOutput: Results of the test generation analysis
        """
        await self.emit_status("running", "Starting comprehensive test generation analysis")
        
        files_to_test = []
        
        # Handle directory-based test generation
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
            
            await self.emit_status("running", f"Scanning {directory} for source files")
            files_to_test = self._find_source_files(directory, task.params.get('extensions'))
            
        # Handle file-list based test generation
        elif task.files:
            files_to_test = task.files
            
        else:
            await self.emit_status("error", "No files or directory specified for test generation")
            return AgentOutput(
                agent_name=self.name,
                task_id=task.task_id,
                result={
                    "status": "FAILED",
                    "error": "No files or directory specified in task"
                }
            )
        
        if not files_to_test:
            await self.emit_status("complete", "No source files found for test generation")
            return AgentOutput(
                agent_name=self.name,
                task_id=task.task_id,
                result={
                    "status": "SUCCESS",
                    "files_found": 0,
                    "message": "No source files found for test generation"
                }
            )
        
        await self.emit_status("running", f"Analyzing {len(files_to_test)} files for test generation")
        
        # Analyze all source files
        files_data = []
        for file_path in files_to_test:
            file_data = self._analyze_file_structure(file_path)
            files_data.append(file_data)
        
        # Analyze integration relationships
        await self.emit_status("running", "Analyzing integration relationships and dependencies")
        integration_analysis = self._analyze_integration_relationships(files_data)
        
        # Create comprehensive test generation prompt
        await self.emit_status("running", "Generating comprehensive test strategy")
        batch_prompt = self._create_comprehensive_test_prompt(files_data, integration_analysis)
        
        # Process with Claude API for comprehensive test generation
        await self.emit_status("running", "Processing test generation with Claude API")
        claude_response = await self.process_with_claude(batch_prompt, "test_generation")
        
        await self.emit_status("complete", f"Test generation complete for {len(files_to_test)} files")
        
        return AgentOutput(
            agent_name=self.name,
            task_id=task.task_id,
            result={
                "status": "TEST_GENERATION_COMPLETE",
                "files_analyzed": len(files_to_test),
                "test_strategy": {
                    "integration_test_suites": integration_analysis['integration_test_suites'],
                    "api_workflows": integration_analysis['api_workflows'],
                    "database_interactions": integration_analysis['database_interactions'],
                    "test_complexity": integration_analysis['test_complexity_assessment'],
                    "estimated_test_count": integration_analysis['test_complexity_assessment']['estimated_test_count']
                },
                "coverage_plan": integration_analysis['test_complexity_assessment']['coverage_targets'],
                "batch_prompt": batch_prompt,
                "claude_response": claude_response,
                "analysis_scope": {
                    "directory": task.params.get('directory'),
                    "files": files_to_test[:10],  # First 10 files for reference
                    "total_files": len(files_to_test)
                },
                "next_step": "Review Claude API response for generated test suites and implement test files"
            }
        )
