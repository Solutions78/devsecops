"""Agent Configuration Management System.

This module provides configuration management for AI agents, including
metadata, prompts, tool configurations, and runtime parameters.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from datetime import datetime


class ToolConfig(BaseModel):
    """Configuration for an agent tool."""
    name: str
    enabled: bool = True
    parameters: Dict[str, Any] = {}


class AgentPromptConfig(BaseModel):
    """Agent prompt configuration."""
    system_prompt: str
    user_prompt_template: str
    temperature: float = Field(default=0.1, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(default=None, gt=0)


class AgentConfig(BaseModel):
    """Complete agent configuration."""
    agent_id: str
    name: str
    display_name: str
    description: str
    category: str  # e.g., "security", "testing", "documentation"
    version: str = "1.0.0"
    enabled: bool = True
    
    # Prompt configuration
    prompt_config: AgentPromptConfig
    
    # Tool configuration
    available_tools: List[ToolConfig] = []
    
    # Runtime parameters
    max_concurrent_tasks: int = Field(default=1, ge=1)
    timeout_seconds: int = Field(default=300, ge=30)
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    author: str = "DevSecOps Team"
    tags: List[str] = []


class AgentConfigManager:
    """Manages agent configurations with persistence."""
    
    def __init__(self, config_dir: str = "data/agent_configs"):
        """Initialize the configuration manager.
        
        Args:
            config_dir: Directory to store configuration files
        """
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.configs: Dict[str, AgentConfig] = {}
        self.load_all_configs()
    
    def load_all_configs(self) -> None:
        """Load all agent configurations from disk."""
        for config_file in self.config_dir.glob("*.json"):
            try:
                with open(config_file, 'r') as f:
                    config_data = json.load(f)
                    config = AgentConfig(**config_data)
                    self.configs[config.agent_id] = config
            except Exception as e:
                print(f"Error loading config {config_file}: {e}")
    
    def save_config(self, config: AgentConfig) -> None:
        """Save an agent configuration to disk.
        
        Args:
            config: The agent configuration to save
        """
        config.updated_at = datetime.now()
        config_file = self.config_dir / f"{config.agent_id}.json"
        
        with open(config_file, 'w') as f:
            json.dump(config.dict(), f, indent=2, default=str)
        
        self.configs[config.agent_id] = config
    
    def get_config(self, agent_id: str) -> Optional[AgentConfig]:
        """Get configuration for a specific agent.
        
        Args:
            agent_id: The agent identifier
            
        Returns:
            Agent configuration or None if not found
        """
        return self.configs.get(agent_id)
    
    def get_all_configs(self) -> Dict[str, AgentConfig]:
        """Get all agent configurations.
        
        Returns:
            Dictionary of agent_id -> AgentConfig
        """
        return self.configs.copy()
    
    def update_config(self, agent_id: str, updates: Dict[str, Any]) -> Optional[AgentConfig]:
        """Update an existing agent configuration.
        
        Args:
            agent_id: The agent identifier
            updates: Dictionary of fields to update
            
        Returns:
            Updated configuration or None if agent not found
        """
        if agent_id not in self.configs:
            return None
        
        config = self.configs[agent_id]
        config_dict = config.dict()
        config_dict.update(updates)
        
        try:
            updated_config = AgentConfig(**config_dict)
            self.save_config(updated_config)
            return updated_config
        except Exception as e:
            print(f"Error updating config for {agent_id}: {e}")
            return None
    
    def delete_config(self, agent_id: str) -> bool:
        """Delete an agent configuration.
        
        Args:
            agent_id: The agent identifier
            
        Returns:
            True if deleted, False if not found
        """
        if agent_id not in self.configs:
            return False
        
        config_file = self.config_dir / f"{agent_id}.json"
        try:
            config_file.unlink()
            del self.configs[agent_id]
            return True
        except Exception as e:
            print(f"Error deleting config for {agent_id}: {e}")
            return False
    
    def create_default_configs(self) -> None:
        """Create default configurations for built-in agents."""
        default_configs = [
            {
                "agent_id": "code-review",
                "name": "code-review", 
                "display_name": "Code Review Agent",
                "description": "Performs comprehensive code quality analysis with security vulnerability detection",
                "category": "development",
                "prompt_config": {
                    "system_prompt": "You are a senior software engineer performing comprehensive code reviews. Focus on code quality, security vulnerabilities, performance issues, and best practices.",
                    "user_prompt_template": "Please review the following code files and provide detailed feedback:\n\n{content}",
                    "temperature": 0.1,
                    "max_tokens": 4000
                },
                "available_tools": [
                    {"name": "file_analysis", "enabled": True},
                    {"name": "security_scan", "enabled": True},
                    {"name": "dependency_check", "enabled": True}
                ],
                "tags": ["code", "review", "security", "quality"]
            },
            {
                "agent_id": "security-auditor",
                "name": "security-auditor",
                "display_name": "Security Auditor Agent", 
                "description": "OWASP Top 10 vulnerability detection and compliance checking",
                "category": "security",
                "prompt_config": {
                    "system_prompt": "You are a cybersecurity expert conducting thorough security audits. Focus on OWASP Top 10 vulnerabilities, secure coding practices, and compliance requirements.",
                    "user_prompt_template": "Perform a comprehensive security audit on the following codebase:\n\n{content}",
                    "temperature": 0.05,
                    "max_tokens": 5000
                },
                "available_tools": [
                    {"name": "vulnerability_scanner", "enabled": True},
                    {"name": "owasp_checker", "enabled": True},
                    {"name": "secret_detector", "enabled": True}
                ],
                "tags": ["security", "audit", "owasp", "compliance"]
            },
            {
                "agent_id": "test-engineer",
                "name": "test-engineer",
                "display_name": "Test Engineer Agent",
                "description": "Integration test generation with 90% coverage targets",
                "category": "testing",
                "prompt_config": {
                    "system_prompt": "You are a test automation expert. Generate comprehensive test suites with high coverage, including unit tests, integration tests, and edge cases.",
                    "user_prompt_template": "Generate comprehensive tests for the following code:\n\n{content}",
                    "temperature": 0.2,
                    "max_tokens": 3000
                },
                "available_tools": [
                    {"name": "test_generator", "enabled": True},
                    {"name": "coverage_analyzer", "enabled": True},
                    {"name": "mock_creator", "enabled": True}
                ],
                "tags": ["testing", "automation", "coverage", "quality"]
            },
            {
                "agent_id": "docstring-generator",
                "name": "docstring-generator",
                "display_name": "Documentation Generator Agent",
                "description": "Batch Google-style documentation generation",
                "category": "documentation",
                "prompt_config": {
                    "system_prompt": "You are a technical documentation expert. Generate clear, comprehensive docstrings following Google style guidelines.",
                    "user_prompt_template": "Generate Google-style docstrings for the following code:\n\n{content}",
                    "temperature": 0.1,
                    "max_tokens": 2000
                },
                "available_tools": [
                    {"name": "docstring_formatter", "enabled": True},
                    {"name": "type_analyzer", "enabled": True}
                ],
                "tags": ["documentation", "docstrings", "google-style"]
            },
            {
                "agent_id": "refactorer",
                "name": "refactorer", 
                "display_name": "Refactoring Agent",
                "description": "Cross-file refactoring opportunities and architectural improvements",
                "category": "development",
                "prompt_config": {
                    "system_prompt": "You are a software architect expert in code refactoring. Identify opportunities for improvement in code structure, design patterns, and maintainability.",
                    "user_prompt_template": "Analyze the following code for refactoring opportunities:\n\n{content}",
                    "temperature": 0.15,
                    "max_tokens": 3500
                },
                "available_tools": [
                    {"name": "pattern_detector", "enabled": True},
                    {"name": "complexity_analyzer", "enabled": True},
                    {"name": "dependency_mapper", "enabled": True}
                ],
                "tags": ["refactoring", "architecture", "patterns", "maintenance"]
            },
            {
                "agent_id": "execution-agent",
                "name": "execution-agent",
                "display_name": "Execution Agent",
                "description": "Sandboxed code execution with runtime validation",
                "category": "testing",
                "prompt_config": {
                    "system_prompt": "You are a code execution specialist. Execute code safely in sandboxed environments and provide detailed runtime analysis.",
                    "user_prompt_template": "Execute the following code and analyze the results:\n\n{content}",
                    "temperature": 0.05,
                    "max_tokens": 2000
                },
                "available_tools": [
                    {"name": "sandbox_executor", "enabled": True},
                    {"name": "runtime_validator", "enabled": True},
                    {"name": "output_analyzer", "enabled": True}
                ],
                "tags": ["execution", "sandbox", "runtime", "validation"]
            },
            {
                "agent_id": "diff-annotator",
                "name": "diff-annotator",
                "display_name": "Diff Annotator Agent",
                "description": "Git diff explanations with impact assessment",
                "category": "development",
                "prompt_config": {
                    "system_prompt": "You are a Git expert who explains code changes clearly. Analyze diffs and provide plain-English explanations of what changed and why it matters.",
                    "user_prompt_template": "Explain the following Git diff in plain English:\n\n{content}",
                    "temperature": 0.1,
                    "max_tokens": 3000
                },
                "available_tools": [
                    {"name": "diff_parser", "enabled": True},
                    {"name": "impact_analyzer", "enabled": True},
                    {"name": "change_summarizer", "enabled": True}
                ],
                "tags": ["git", "diff", "explanation", "impact"]
            },
            {
                "agent_id": "pr-summarizer",
                "name": "pr-summarizer", 
                "display_name": "PR Summarizer Agent",
                "description": "Pull request summary generation with structured output",
                "category": "documentation",
                "prompt_config": {
                    "system_prompt": "You are a technical writer who creates clear pull request summaries. Generate structured summaries that help reviewers understand changes quickly.",
                    "user_prompt_template": "Create a comprehensive pull request summary for:\n\n{content}",
                    "temperature": 0.1,
                    "max_tokens": 2500
                },
                "available_tools": [
                    {"name": "change_analyzer", "enabled": True},
                    {"name": "summary_formatter", "enabled": True},
                    {"name": "reviewer_helper", "enabled": True}
                ],
                "tags": ["pull-request", "summary", "review", "documentation"]
            },
            {
                "agent_id": "orchestrator-agent",
                "name": "orchestrator-agent",
                "display_name": "Orchestrator Agent", 
                "description": "Multi-agent workflow coordination and task management",
                "category": "orchestration",
                "prompt_config": {
                    "system_prompt": "You are a workflow orchestrator. Coordinate multiple agents to complete complex tasks efficiently and manage dependencies between different operations.",
                    "user_prompt_template": "Orchestrate the following multi-agent workflow:\n\n{content}",
                    "temperature": 0.1,
                    "max_tokens": 4000
                },
                "available_tools": [
                    {"name": "workflow_planner", "enabled": True},
                    {"name": "task_coordinator", "enabled": True},
                    {"name": "dependency_manager", "enabled": True},
                    {"name": "result_aggregator", "enabled": True}
                ],
                "tags": ["orchestration", "workflow", "coordination", "multi-agent"]
            }
        ]
        
        for config_data in default_configs:
            if config_data["agent_id"] not in self.configs:
                config = AgentConfig(**config_data)
                self.save_config(config)


# Global configuration manager instance
config_manager = AgentConfigManager()