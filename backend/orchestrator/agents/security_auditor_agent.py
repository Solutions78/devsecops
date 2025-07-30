"""Security auditor agent for comprehensive security analysis using batch processing."""

from __future__ import annotations

import os
import glob
import ast
import re
from pathlib import Path
from typing import List, Dict, Optional, Set, Any
from collections import defaultdict
import json

try:
    from ..models import AgentOutput, Task  # type: ignore
except ImportError:
    from backend.orchestrator.models import AgentOutput, Task  # type: ignore

from .base_agent import BaseAgent
# Optional mixin stub
try:
    from ..services.claude_client import BatchProcessingMixin  # type: ignore
except ImportError:
    class BatchProcessingMixin:  # type: ignore
        """TODO: Add docstring."""
        pass


class SecurityAuditorAgent(BaseAgent, BatchProcessingMixin):
    """Agent that performs comprehensive security audits using batch processing for cost efficiency.
    
    This agent analyzes entire codebases for security vulnerabilities, compliance issues,
    and security best practices. It provides comprehensive security assessments that
    consider cross-file security implications and system-wide security architecture.
    
    Features:
    - Batch processing for comprehensive multi-file security analysis
    - OWASP Top 10 vulnerability detection across entire codebase
    - Cross-file security dependency analysis
    - Compliance checking (NIST, SOC2, GDPR data handling)
    - Authentication and authorization pattern analysis
    - Input validation and sanitization verification
    - Cryptographic implementation review
    - Infrastructure security configuration analysis
    """

    def _find_security_relevant_files(self, directory: str, extensions: Optional[List[str]] = None) -> Dict[str, List[str]]:
        """Find files relevant to security analysis categorized by type.
        
        Args:
            directory (str): Root directory to search for files
            extensions (List[str], optional): File extensions to include
            
        Returns:
            Dict[str, List[str]]: Categorized lists of security-relevant files
        """
        if extensions is None:
            extensions = ['.py', '.js', '.ts', '.tsx', '.jsx', '.java', '.php', '.rb', '.go', '.cs', '.cpp']
        
        security_files = {
            'source_code': [],
            'config_files': [],
            'database_files': [],
            'api_files': [],
            'auth_files': [],
            'crypto_files': [],
            'docker_files': [],
            'env_files': []
        }
        
        # Patterns for different file types
        config_patterns = ['*config*', '*settings*', '*env*', '*.ini', '*.conf', '*.yaml', '*.yml', '*.json']
        database_patterns = ['*migration*', '*model*', '*schema*', '*database*', '*db*']
        api_patterns = ['*api*', '*route*', '*endpoint*', '*controller*', '*handler*']
        auth_patterns = ['*auth*', '*login*', '*token*', '*jwt*', '*oauth*', '*session*']
        crypto_patterns = ['*crypto*', '*encrypt*', '*hash*', '*password*', '*key*', '*cert*']
        docker_patterns = ['Dockerfile*', 'docker-compose*', '*.dockerfile']
        env_patterns = ['.env*', '*.env', 'environment*']
        
        # Find source code files
        for ext in extensions:
            pattern = f"**/*{ext}"
            files = glob.glob(os.path.join(directory, pattern), recursive=True)
            
            for file_path in files:
                path_parts = Path(file_path).parts
                file_name = Path(file_path).name.lower()
                
                # Skip common non-security directories
                skip_dirs = {
                    'node_modules', '__pycache__', '.git', 'dist', 'build',
                    'target', '.pytest_cache', 'venv', 'env', 'tests'
                }
                
                if any(skip_dir in path_parts for skip_dir in skip_dirs):
                    continue
                
                # Categorize files
                security_files['source_code'].append(file_path)
                
                # Check for specific security-relevant patterns
                if any(self._matches_pattern(file_name, pattern) for pattern in database_patterns):
                    security_files['database_files'].append(file_path)
                elif any(self._matches_pattern(file_name, pattern) for pattern in api_patterns):
                    security_files['api_files'].append(file_path)
                elif any(self._matches_pattern(file_name, pattern) for pattern in auth_patterns):
                    security_files['auth_files'].append(file_path)
                elif any(self._matches_pattern(file_name, pattern) for pattern in crypto_patterns):
                    security_files['crypto_files'].append(file_path)
        
        # Find configuration files
        for pattern in config_patterns:
            files = glob.glob(os.path.join(directory, f"**/{pattern}"), recursive=True)
            security_files['config_files'].extend(files)
        
        # Find Docker files
        for pattern in docker_patterns:
            files = glob.glob(os.path.join(directory, f"**/{pattern}"), recursive=True)
            security_files['docker_files'].extend(files)
        
        # Find environment files
        for pattern in env_patterns:
            files = glob.glob(os.path.join(directory, f"**/{pattern}"), recursive=True)
            security_files['env_files'].extend(files)
        
        # Remove duplicates and sort
        for category in security_files:
            security_files[category] = sorted(list(set(security_files[category])))
        
        return security_files

    def _matches_pattern(self, filename: str, pattern: str) -> bool:
        """Check if filename matches a security pattern."""
        pattern = pattern.replace('*', '.*').lower()
        return re.search(pattern, filename) is not None

    def _analyze_file_security(self, file_path: str) -> Dict[str, Any]:
        """Analyze a single file for security vulnerabilities and issues.
        
        Args:
            file_path (str): Path to file to analyze
            
        Returns:
            Dict[str, Any]: Security analysis results for the file
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            file_analysis = {
                'path': file_path,
                'extension': Path(file_path).suffix.lower(),
                'size': len(content),
                'lines': len(content.split('\n')),
                'security_issues': [],
                'sensitive_patterns': [],
                'input_validation': [],
                'authentication_patterns': [],
                'crypto_usage': [],
                'database_queries': [],
                'api_endpoints': [],
                'potential_vulnerabilities': []
            }
            
            # Python-specific security analysis
            if file_analysis['extension'] == '.py':
                file_analysis.update(self._analyze_python_security(content, file_path))
            # JavaScript/TypeScript security analysis
            elif file_analysis['extension'] in ['.js', '.ts', '.jsx', '.tsx']:
                file_analysis.update(self._analyze_javascript_security(content, file_path))
            # Configuration file analysis
            elif file_analysis['extension'] in ['.json', '.yaml', '.yml', '.ini', '.conf']:
                file_analysis.update(self._analyze_config_security(content, file_path))
            
            return file_analysis
            
        except Exception as e:
            return {
                'path': file_path,
                'error': f'Could not analyze file: {str(e)}',
                'extension': Path(file_path).suffix.lower()
            }

    def _analyze_python_security(self, content: str, file_path: str) -> Dict[str, Any]:
        """Analyze Python file for security vulnerabilities."""
        analysis = {
            'security_issues': [],
            'sensitive_patterns': [],
            'input_validation': [],
            'authentication_patterns': [],
            'crypto_usage': [],
            'database_queries': [],
            'api_endpoints': [],
            'potential_vulnerabilities': []
        }
        
        try:
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                # Check for dangerous function calls
                if isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name):
                        func_name = node.func.id
                        
                        # Dangerous functions
                        if func_name in ['eval', 'exec', 'compile', '__import__']:
                            analysis['potential_vulnerabilities'].append({
                                'type': 'dangerous_function',
                                'function': func_name,
                                'line': node.lineno,
                                'severity': 'HIGH',
                                'description': f'Use of dangerous function {func_name} can lead to code injection'
                            })
                        
                        # SQL-related functions
                        elif func_name in ['execute', 'executemany', 'query']:
                            analysis['database_queries'].append({
                                'function': func_name,
                                'line': node.lineno,
                                'args': len(node.args)
                            })
                    
                    elif isinstance(node.func, ast.Attribute):
                        attr_name = node.func.attr
                        
                        # Database operations
                        if attr_name in ['execute', 'raw', 'extra']:
                            analysis['database_queries'].append({
                                'method': attr_name,
                                'line': node.lineno,
                                'potential_sql_injection': True
                            })
                
                # Check for hardcoded secrets
                elif isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name) and isinstance(node.value, ast.Str):
                            var_name = target.id.lower()
                            value = node.value.s
                            
                            # Check for potential secrets
                            secret_indicators = ['password', 'secret', 'key', 'token', 'api_key', 'private_key']
                            if any(indicator in var_name for indicator in secret_indicators):
                                analysis['sensitive_patterns'].append({
                                    'type': 'hardcoded_secret',
                                    'variable': target.id,
                                    'line': node.lineno,
                                    'severity': 'HIGH',
                                    'description': f'Potential hardcoded secret in variable {target.id}'
                                })
                
                # Check for function definitions that might handle sensitive data
                elif isinstance(node, ast.FunctionDef):
                    func_name = node.name.lower()
                    auth_indicators = ['login', 'authenticate', 'authorize', 'password', 'token']
                    
                    if any(indicator in func_name for indicator in auth_indicators):
                        analysis['authentication_patterns'].append({
                            'function': node.name,
                            'line': node.lineno,
                            'args': [arg.arg for arg in node.args.args],
                            'type': 'auth_function'
                        })
        
        except SyntaxError as e:
            analysis['security_issues'].append({
                'type': 'syntax_error',
                'description': f'Syntax error prevents security analysis: {str(e)}',
                'severity': 'MEDIUM'
            })
        
        # Pattern-based analysis for additional security issues
        analysis.update(self._pattern_based_security_analysis(content))
        
        return analysis

    def _analyze_javascript_security(self, content: str, file_path: str) -> Dict[str, Any]:
        """Analyze JavaScript/TypeScript file for security vulnerabilities."""
        analysis = {
            'security_issues': [],
            'sensitive_patterns': [],
            'potential_vulnerabilities': [],
            'xss_risks': [],
            'csrf_protection': []
        }
        
        # Check for dangerous JavaScript patterns
        dangerous_patterns = [
            (r'eval\s*\(', 'eval_usage', 'HIGH', 'Use of eval() can lead to XSS and code injection'),
            (r'innerHTML\s*=', 'innerHTML_assignment', 'MEDIUM', 'Direct innerHTML assignment can lead to XSS'),
            (r'document\.write\s*\(', 'document_write', 'MEDIUM', 'document.write() can be exploited for XSS'),
            (r'setTimeout\s*\(\s*["\']', 'setTimeout_string', 'MEDIUM', 'setTimeout with string argument can lead to code injection'),
            (r'setInterval\s*\(\s*["\']', 'setInterval_string', 'MEDIUM', 'setInterval with string argument can lead to code injection')
        ]
        
        for pattern, vuln_type, severity, description in dangerous_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                analysis['potential_vulnerabilities'].append({
                    'type': vuln_type,
                    'line': line_num,
                    'severity': severity,
                    'description': description,
                    'code_snippet': content[max(0, match.start()-20):match.end()+20]
                })
        
        return analysis

    def _analyze_config_security(self, content: str, file_path: str) -> Dict[str, Any]:
        """Analyze configuration files for security issues."""
        analysis = {
            'security_issues': [],
            'sensitive_patterns': [],
            'misconfigurations': []
        }
        
        # Check for exposed secrets in config files
        secret_patterns = [
            (r'password\s*[:=]\s*["\']?([^"\'\s]+)', 'exposed_password'),
            (r'secret\s*[:=]\s*["\']?([^"\'\s]+)', 'exposed_secret'),
            (r'api_key\s*[:=]\s*["\']?([^"\'\s]+)', 'exposed_api_key'),
            (r'private_key\s*[:=]\s*["\']?([^"\'\s]+)', 'exposed_private_key')
        ]
        
        for pattern, issue_type in secret_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                analysis['sensitive_patterns'].append({
                    'type': issue_type,
                    'line': line_num,
                    'severity': 'HIGH',
                    'description': f'Potentially exposed {issue_type.replace("_", " ")} in configuration'
                })
        
        return analysis

    def _pattern_based_security_analysis(self, content: str) -> Dict[str, Any]:
        """Perform pattern-based security analysis on file content."""
        patterns = {
            'crypto_usage': [],
            'input_validation': [],
            'security_issues': []
        }
        
        # Cryptographic usage patterns
        crypto_patterns = [
            (r'hashlib\.(md5|sha1)\(', 'weak_hash', 'MEDIUM', 'Use of weak hashing algorithm'),
            (r'random\.(random|randint)', 'weak_random', 'LOW', 'Use of weak random number generator for security'),
            (r'pickle\.(loads|load)', 'pickle_usage', 'HIGH', 'Pickle deserialization can lead to code execution'),
            (r'subprocess\.(call|run|Popen)', 'subprocess_usage', 'MEDIUM', 'Subprocess calls may be vulnerable to injection')
        ]
        
        for pattern, issue_type, severity, description in crypto_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                patterns['security_issues'].append({
                    'type': issue_type,
                    'line': line_num,
                    'severity': severity,
                    'description': description
                })
        
        return patterns

    def _analyze_cross_file_security(self, files_analysis: Dict[str, Dict]) -> Dict[str, Any]:
        """Analyze security patterns across multiple files."""
        cross_analysis = {
            'system_wide_vulnerabilities': [],
            'authentication_architecture': {},
            'data_flow_security': [],
            'compliance_issues': [],
            'security_recommendations': [],
            'risk_assessment': {}
        }
        
        # Aggregate vulnerability counts
        vuln_counts = defaultdict(int)
        high_severity_files = []
        
        for file_path, analysis in files_analysis.items():
            if 'error' in analysis:
                continue
                
            file_vulns = analysis.get('potential_vulnerabilities', []) + analysis.get('security_issues', [])
            high_severity_vulns = [v for v in file_vulns if v.get('severity') == 'HIGH']
            
            if high_severity_vulns:
                high_severity_files.append({
                    'file': file_path,
                    'high_severity_count': len(high_severity_vulns),
                    'vulnerabilities': high_severity_vulns[:3]  # Show top 3
                })
            
            for vuln in file_vulns:
                vuln_counts[vuln.get('type', 'unknown')] += 1
        
        # System-wide vulnerability analysis
        if vuln_counts:
            cross_analysis['system_wide_vulnerabilities'] = [
                {
                    'vulnerability_type': vuln_type,
                    'occurrence_count': count,
                    'risk_level': 'HIGH' if count > 5 else 'MEDIUM' if count > 2 else 'LOW'
                }
                for vuln_type, count in vuln_counts.most_common(10)
            ]
        
        # Authentication architecture analysis
        auth_files = [f for f, a in files_analysis.items() if a.get('authentication_patterns')]
        if auth_files:
            cross_analysis['authentication_architecture'] = {
                'auth_files_count': len(auth_files),
                'files': auth_files[:5],
                'centralized_auth': len(auth_files) <= 3,  # Heuristic for centralized auth
                'recommendation': 'Consider centralized authentication service' if len(auth_files) > 5 else 'Authentication appears centralized'
            }
        
        # Risk assessment
        total_files = len(files_analysis)
        total_vulnerabilities = sum(vuln_counts.values())
        
        cross_analysis['risk_assessment'] = {
            'overall_risk': 'HIGH' if total_vulnerabilities > 20 else 'MEDIUM' if total_vulnerabilities > 5 else 'LOW',
            'vulnerability_density': total_vulnerabilities / max(total_files, 1),
            'high_risk_files': len(high_severity_files),
            'total_vulnerabilities': total_vulnerabilities,
            'most_common_issues': list(vuln_counts.most_common(5))
        }
        
        # Generate security recommendations
        recommendations = []
        if vuln_counts.get('hardcoded_secret', 0) > 0:
            recommendations.append("Implement secure secret management (environment variables, key vaults)")
        if vuln_counts.get('dangerous_function', 0) > 0:
            recommendations.append("Replace dangerous functions (eval, exec) with safer alternatives")
        if vuln_counts.get('sql_injection', 0) > 0:
            recommendations.append("Implement parameterized queries to prevent SQL injection")
        if vuln_counts.get('weak_hash', 0) > 0:
            recommendations.append("Upgrade to stronger hashing algorithms (SHA-256, bcrypt)")
        
        cross_analysis['security_recommendations'] = recommendations
        
        return cross_analysis

    def _create_security_audit_prompt(self, files_analysis: Dict[str, Dict], cross_analysis: Dict) -> str:
        """Create comprehensive security audit prompt for batch processing."""
        prompt = """Please perform a comprehensive security audit of the following codebase.

## Security Audit Requirements:

1. **OWASP Top 10 Assessment**: Analyze for all OWASP Top 10 vulnerabilities
2. **Code Injection Risks**: SQL injection, command injection, code injection
3. **Authentication & Authorization**: Verify proper access controls
4. **Cryptographic Implementation**: Review encryption, hashing, key management
5. **Input Validation**: Check for proper sanitization and validation
6. **Configuration Security**: Review security configurations and settings
7. **Dependency Security**: Identify vulnerable dependencies
8. **Data Protection**: Verify sensitive data handling and storage
9. **Error Handling**: Ensure secure error messages
10. **Infrastructure Security**: Review deployment and infrastructure configurations

## Current Security Analysis:
"""
        
        # Risk assessment overview
        risk_assessment = cross_analysis.get('risk_assessment', {})
        prompt += f"- **Overall Risk Level**: {risk_assessment.get('overall_risk', 'UNKNOWN')}\n"
        prompt += f"- **Total Vulnerabilities Found**: {risk_assessment.get('total_vulnerabilities', 0)}\n"
        prompt += f"- **High-Risk Files**: {risk_assessment.get('high_risk_files', 0)}\n"
        prompt += f"- **Vulnerability Density**: {risk_assessment.get('vulnerability_density', 0):.2f} per file\n\n"
        
        # System-wide vulnerabilities
        if cross_analysis.get('system_wide_vulnerabilities'):
            prompt += "## System-wide Vulnerability Patterns:\n"
            for vuln in cross_analysis['system_wide_vulnerabilities'][:5]:
                prompt += f"- **{vuln['vulnerability_type']}**: {vuln['occurrence_count']} occurrences ({vuln['risk_level']} risk)\n"
            prompt += "\n"
        
        # Authentication architecture
        if cross_analysis.get('authentication_architecture'):
            auth_arch = cross_analysis['authentication_architecture']
            prompt += f"## Authentication Architecture:\n"
            prompt += f"- **Auth Files**: {auth_arch['auth_files_count']}\n"
            prompt += f"- **Centralized**: {auth_arch['centralized_auth']}\n"
            prompt += f"- **Recommendation**: {auth_arch['recommendation']}\n\n"
        
        # File-by-file analysis
        prompt += "## Files Analyzed:\n\n"
        
        file_count = 0
        for file_path, analysis in files_analysis.items():
            if file_count >= 20:  # Limit for token efficiency
                break
            file_count += 1
            
            if 'error' in analysis:
                prompt += f"**{file_path}** (ERROR: {analysis['error']})\n\n"
                continue
            
            prompt += f"**{file_path}**\n"
            
            # Security issues
            security_issues = analysis.get('security_issues', []) + analysis.get('potential_vulnerabilities', [])
            if security_issues:
                high_issues = [i for i in security_issues if i.get('severity') == 'HIGH']
                medium_issues = [i for i in security_issues if i.get('severity') == 'MEDIUM']
                prompt += f"- **Security Issues**: {len(high_issues)} HIGH, {len(medium_issues)} MEDIUM\n"
                
                # Show top issues
                for issue in security_issues[:2]:
                    prompt += f"  - Line {issue.get('line', '?')}: {issue.get('description', issue.get('type', 'Unknown issue'))}\n"
            
            # Other security-relevant information
            if analysis.get('sensitive_patterns'):
                prompt += f"- **Sensitive Patterns**: {len(analysis['sensitive_patterns'])} found\n"
            if analysis.get('database_queries'):
                prompt += f"- **Database Queries**: {len(analysis['database_queries'])} (check for SQL injection)\n"
            if analysis.get('authentication_patterns'):
                prompt += f"- **Auth Patterns**: {len(analysis['authentication_patterns'])} functions\n"
            
            prompt += "\n"
        
        if len(files_analysis) > 20:
            prompt += f"... and {len(files_analysis) - 20} more files\n\n"
        
        prompt += """
## Please Provide:

1. **Executive Security Summary**: Overall security posture and critical findings
2. **OWASP Top 10 Assessment**: Specific vulnerabilities found for each category
3. **Priority Vulnerability List**: Ranked by severity and exploitability
4. **Remediation Plan**: Step-by-step fixes for identified issues
5. **Security Architecture Review**: Recommendations for security improvements
6. **Compliance Assessment**: Alignment with security standards (NIST, OWASP, etc.)
7. **Secure Development Recommendations**: Best practices for ongoing development
8. **Infrastructure Security**: Deployment and configuration security recommendations

Focus on actionable recommendations with specific code examples where applicable.
Prioritize findings by risk level and potential business impact.
"""
        
        return prompt

    async def run(self, task: Task) -> AgentOutput:
        """Execute comprehensive security audit with batch processing.
        
        Args:
            task (Task): Task containing files to audit or directory to analyze
            
        Returns:
            AgentOutput: Results of the security audit analysis
        """
        await self.emit_status("running", "Starting comprehensive security audit")
        
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
            
            await self.emit_status("running", f"Scanning {directory} for security-relevant files")
            security_files = self._find_security_relevant_files(directory, task.params.get('extensions'))
            
            # Combine all files for analysis
            all_files = []
            for category, files in security_files.items():
                all_files.extend(files)
            
        elif task.files:
            all_files = task.files
            
        else:
            await self.emit_status("error", "No files or directory specified for security audit")
            return AgentOutput(
                agent_name=self.name,
                task_id=task.task_id,
                result={
                    "status": "FAILED",
                    "error": "No files or directory specified in task"
                }
            )
        
        if not all_files:
            await self.emit_status("complete", "No files found for security analysis")
            return AgentOutput(
                agent_name=self.name,
                task_id=task.task_id,
                result={
                    "status": "SUCCESS",
                    "files_found": 0,
                    "message": "No files found for security analysis"
                }
            )
        
        await self.emit_status("running", f"Analyzing {len(all_files)} files for security vulnerabilities")
        
        # Analyze all files
        files_analysis = {}
        for file_path in all_files:
            file_analysis = self._analyze_file_security(file_path)
            files_analysis[file_path] = file_analysis
        
        # Perform cross-file security analysis
        await self.emit_status("running", "Analyzing cross-file security patterns and system architecture")
        cross_analysis = self._analyze_cross_file_security(files_analysis)
        
        # Create comprehensive security audit prompt
        await self.emit_status("running", "Generating comprehensive security audit report")
        batch_prompt = self._create_security_audit_prompt(files_analysis, cross_analysis)
        
        # Process with Claude API if available
        claude_response = await self.process_with_claude(batch_prompt, "security_audit")
        
        await self.emit_status("complete", f"Security audit complete for {len(all_files)} files")
        
        return AgentOutput(
            agent_name=self.name,
            task_id=task.task_id,
            result={
                "status": "ANALYSIS_COMPLETE",
                "files_analyzed": len(all_files),
                "security_summary": {
                    "risk_assessment": cross_analysis.get('risk_assessment', {}),
                    "system_vulnerabilities": cross_analysis.get('system_wide_vulnerabilities', []),
                    "authentication_architecture": cross_analysis.get('authentication_architecture', {}),
                    "security_recommendations": cross_analysis.get('security_recommendations', [])
                },
                "batch_prompt": batch_prompt,
                "claude_response": claude_response,
                "analysis_scope": {
                    "directory": task.params.get('directory'),
                    "files": all_files[:10],  # First 10 files for reference
                    "total_files": len(all_files)
                },
                "next_step": "Review Claude API response for detailed security recommendations and remediation steps"
            }
        )
