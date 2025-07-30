"""User Management System for DevSecOps Orchestrator.

This module provides role-based access control with two roles:
- administrators: Full access to all features including security page and agent configuration
- users: Limited access, cannot access security page or modify agent tools

The system stores user data in JSON format for persistence.
"""
import json
import secrets
import string
import os
from pathlib import Path
from typing import Dict, List, Optional, Literal
from pydantic import BaseModel
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Define user roles
UserRole = Literal["administrator", "user"]

class UserInfo(BaseModel):
    """User information model."""
    api_key: str
    role: UserRole
    created_at: str
    last_used: Optional[str] = None
    description: Optional[str] = None
    created_by: Optional[str] = None  # Which admin created this user

class UserManager:
    """Manages users and their roles for the DevSecOps orchestrator."""
    
    def __init__(self, users_file: Optional[str] = None):
        """Initialize the user manager.
        
        Args:
            users_file: Path to the users JSON file. If None, uses default location.
        """
        if users_file is None:
            # Store users file in the orchestrator directory
            self.users_file = Path(__file__).parent / "users.json"
        else:
            self.users_file = Path(users_file)
            
        self.users: Dict[str, UserInfo] = {}
        self._load_users()
        self._ensure_admin_user()
    
    def _load_users(self) -> None:
        """Load users from the JSON file."""
        try:
            if self.users_file.exists():
                with open(self.users_file, 'r') as f:
                    data = json.load(f)
                    self.users = {
                        api_key: UserInfo(**user_data) 
                        for api_key, user_data in data.items()
                    }
                logger.info(f"Loaded {len(self.users)} users from {self.users_file}")
            else:
                logger.info(f"Users file {self.users_file} does not exist, starting with empty user database")
        except Exception as e:
            logger.error(f"Error loading users from {self.users_file}: {e}")
            self.users = {}
    
    def _save_users(self) -> None:
        """Save users to the JSON file."""
        try:
            # Ensure directory exists
            self.users_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Convert to serializable format
            data = {
                api_key: user.dict() 
                for api_key, user in self.users.items()
            }
            
            with open(self.users_file, 'w') as f:
                json.dump(data, f, indent=2)
            logger.info(f"Saved {len(self.users)} users to {self.users_file}")
        except Exception as e:
            logger.error(f"Error saving users to {self.users_file}: {e}")
    
    def _ensure_admin_user(self) -> None:
        """Ensure the specified admin API key exists in the system."""
        admin_key = "IKsX1_nMs0a1cbwx2s1zOEeNtBqjkS1cBdzL__chYhY"
        
        if admin_key not in self.users:
            # Create the admin user
            admin_user = UserInfo(
                api_key=admin_key,
                role="administrator",
                created_at=datetime.now().isoformat(),
                description="Primary administrator - created automatically",
                created_by="system"
            )
            self.users[admin_key] = admin_user
            self._save_users()
            logger.info("Created primary administrator account")
        else:
            # Ensure existing user has admin role
            if self.users[admin_key].role != "administrator":
                self.users[admin_key].role = "administrator"
                self._save_users()
                logger.info("Updated primary user to administrator role")
    
    def generate_api_key(self, length: int = 43) -> str:
        """Generate a secure API key.
        
        Args:
            length: Length of the API key to generate.
            
        Returns:
            A secure random API key string.
        """
        # Use URL-safe characters for API keys
        alphabet = string.ascii_letters + string.digits + '-_'
        return ''.join(secrets.choice(alphabet) for _ in range(length))
    
    def create_user(
        self, 
        role: UserRole, 
        description: Optional[str] = None,
        created_by: Optional[str] = None
    ) -> str:
        """Create a new user with the specified role.
        
        Args:
            role: The role to assign to the new user.
            description: Optional description for the user.
            created_by: API key of the admin who created this user.
            
        Returns:
            The generated API key for the new user.
        """
        api_key = self.generate_api_key()
        
        # Ensure the key is unique
        while api_key in self.users:
            api_key = self.generate_api_key()
        
        user = UserInfo(
            api_key=api_key,
            role=role,
            created_at=datetime.now().isoformat(),
            description=description,
            created_by=created_by
        )
        
        self.users[api_key] = user
        self._save_users()
        
        logger.info(f"Created new {role} user with key ending in ...{api_key[-6:]}")
        return api_key
    
    def get_user_role(self, api_key: str) -> Optional[UserRole]:
        """Get the role for a given API key.
        
        Args:
            api_key: The API key to look up.
            
        Returns:
            The user's role, or None if the API key is not found.
        """
        user = self.users.get(api_key)
        if user:
            # Update last used timestamp
            user.last_used = datetime.now().isoformat()
            self._save_users()
            return user.role
        return None
    
    def is_administrator(self, api_key: str) -> bool:
        """Check if the given API key belongs to an administrator.
        
        Args:
            api_key: The API key to check.
            
        Returns:
            True if the user is an administrator, False otherwise.
        """
        return self.get_user_role(api_key) == "administrator"
    
    def is_valid_user(self, api_key: str) -> bool:
        """Check if the given API key is valid.
        
        Args:
            api_key: The API key to validate.
            
        Returns:
            True if the API key is valid, False otherwise.
        """
        return api_key in self.users
    
    def list_users(self) -> List[Dict]:
        """List all users (for admin use).
        
        Returns:
            List of user information (excluding full API keys for security).
        """
        users_list = []
        for api_key, user in self.users.items():
            user_dict = user.dict()
            # Mask the API key for security
            user_dict['api_key_masked'] = f"...{api_key[-6:]}"
            del user_dict['api_key']  # Remove full key
            users_list.append(user_dict)
        
        return users_list
    
    def delete_user(self, api_key: str, deleted_by: Optional[str] = None) -> bool:
        """Delete a user.
        
        Args:
            api_key: The API key of the user to delete.
            deleted_by: API key of the admin who deleted this user.
            
        Returns:
            True if the user was deleted, False if not found.
        """
        if api_key in self.users:
            # Prevent deletion of the primary admin
            if api_key == "IKsX1_nMs0a1cbwx2s1zOEeNtBqjkS1cBdzL__chYhY":
                logger.warning("Attempted to delete primary administrator - blocked")
                return False
            
            user = self.users[api_key]
            del self.users[api_key]
            self._save_users()
            
            logger.info(f"Deleted {user.role} user with key ending in ...{api_key[-6:]} by {deleted_by or 'unknown'}")
            return True
        return False

# Global user manager instance
user_manager = UserManager()