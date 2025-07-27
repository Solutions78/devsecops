"""Claude API client for processing batch prompts and generating responses."""

import os
import json
import httpx
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class ClaudeAPIClient:
    """Client for interacting with Claude API for batch processing."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "claude-3-5-sonnet-20241022"):
        """Initialize Claude API client.
        
        Args:
            api_key: Anthropic API key (defaults to environment variable)
            model: Claude model to use for processing
        """
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.model = model
        self.base_url = "https://api.anthropic.com/v1"
        
        if not self.api_key:
            logger.warning("No Claude API key found. Agent responses will be analysis-only.")
    
    async def process_batch_prompt(self, prompt: str, max_tokens: int = 4000) -> Dict[str, Any]:
        """Process a batch prompt using Claude API.
        
        Args:
            prompt: The comprehensive prompt to process
            max_tokens: Maximum tokens for the response
            
        Returns:
            Dict containing the response and metadata
        """
        if not self.api_key:
            return {
                "status": "API_UNAVAILABLE",
                "message": "No Claude API key configured",
                "response": None,
                "token_usage": None
            }
        
        try:
            headers = {
                "Content-Type": "application/json",
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01"
            }
            
            payload = {
                "model": self.model,
                "max_tokens": max_tokens,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.1  # Low temperature for consistent, focused responses
            }
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.base_url}/messages",
                    headers=headers,
                    json=payload
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return {
                        "status": "SUCCESS",
                        "response": result["content"][0]["text"],
                        "token_usage": {
                            "input_tokens": result.get("usage", {}).get("input_tokens", 0),
                            "output_tokens": result.get("usage", {}).get("output_tokens", 0)
                        },
                        "model": result.get("model", self.model)
                    }
                else:
                    error_detail = response.text
                    logger.error(f"Claude API error {response.status_code}: {error_detail}")
                    return {
                        "status": "API_ERROR",
                        "error": f"HTTP {response.status_code}: {error_detail}",
                        "response": None,
                        "token_usage": None
                    }
                    
        except httpx.TimeoutException:
            return {
                "status": "TIMEOUT",
                "error": "Request timeout - prompt may be too large or service unavailable",
                "response": None,
                "token_usage": None
            }
        except Exception as e:
            logger.error(f"Claude API client error: {str(e)}")
            return {
                "status": "ERROR", 
                "error": str(e),
                "response": None,
                "token_usage": None
            }
    
    async def process_code_review(self, prompt: str) -> Dict[str, Any]:
        """Process code review batch prompt with specialized handling."""
        return await self.process_batch_prompt(prompt, max_tokens=4000)
    
    async def process_refactoring(self, prompt: str) -> Dict[str, Any]:
        """Process refactoring batch prompt with specialized handling.""" 
        return await self.process_batch_prompt(prompt, max_tokens=4000)
    
    async def process_test_generation(self, prompt: str) -> Dict[str, Any]:
        """Process test generation batch prompt with specialized handling."""
        return await self.process_batch_prompt(prompt, max_tokens=6000)
    
    async def process_docstring_generation(self, prompt: str) -> Dict[str, Any]:
        """Process docstring generation with file modification instructions."""
        system_prompt = """You are a Python documentation expert. Given a batch prompt about adding docstrings to Python files, respond with a JSON object where:
- Keys are absolute file paths
- Values are the complete updated file contents with Google-style docstrings added

Only include files that need docstring updates. Ensure proper indentation and formatting."""
        
        full_prompt = f"{system_prompt}\n\n{prompt}"
        return await self.process_batch_prompt(full_prompt, max_tokens=8000)
    
    async def process_security_audit(self, prompt: str) -> Dict[str, Any]:
        """Process security audit batch prompt with specialized handling."""
        return await self.process_batch_prompt(prompt, max_tokens=5000)
    
    async def process_diff_annotation(self, prompt: str) -> Dict[str, Any]:
        """Process diff annotation batch prompt with specialized handling."""
        return await self.process_batch_prompt(prompt, max_tokens=3000)


class BatchProcessingMixin:
    """Mixin to add Claude API batch processing to agents."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.claude_client = ClaudeAPIClient()
    
    async def process_with_claude(self, prompt: str, agent_type: str = "general") -> Dict[str, Any]:
        """Process prompt using Claude API with agent-specific handling.
        
        Args:
            prompt: The batch prompt to process
            agent_type: Type of agent processing (code_review, refactoring, etc.)
            
        Returns:
            Dict containing Claude's response and metadata
        """
        processor_map = {
            "code_review": self.claude_client.process_code_review,
            "refactoring": self.claude_client.process_refactoring, 
            "test_generation": self.claude_client.process_test_generation,
            "docstring_generation": self.claude_client.process_docstring_generation,
            "security_audit": self.claude_client.process_security_audit,
            "diff_annotation": self.claude_client.process_diff_annotation
        }
        
        processor = processor_map.get(agent_type, self.claude_client.process_batch_prompt)
        return await processor(prompt)