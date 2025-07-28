"""Secure secrets management system for the DevSecOps Orchestrator.

This module provides secure key storage and retrieval using multiple backends
including system keyring, cloud key management services, and encrypted local storage.
It replaces the insecure .env file approach with production-grade secret management.
"""
from __future__ import annotations

import os
import json
import hashlib
import secrets
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from pathlib import Path
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import logging

logger = logging.getLogger(__name__)


class SecretBackend(ABC):
    """Abstract base class for secret storage backends."""
    
    @abstractmethod
    async def get_secret(self, key: str) -> Optional[str]:
        """Retrieve a secret by key."""
        pass
    
    @abstractmethod
    async def set_secret(self, key: str, value: str) -> bool:
        """Store a secret by key."""
        pass
    
    @abstractmethod
    async def delete_secret(self, key: str) -> bool:
        """Delete a secret by key."""
        pass
    
    @abstractmethod
    async def list_secrets(self) -> list[str]:
        """List all available secret keys."""
        pass


class SystemKeyringBackend(SecretBackend):
    """System keyring backend using the operating system's secure storage."""
    
    def __init__(self, service_name: str = "devsecops-orchestrator"):
        self.service_name = service_name
        try:
            import keyring
            self.keyring = keyring
            self.available = True
        except ImportError:
            logger.warning("keyring package not available, system keyring backend disabled")
            self.available = False
    
    async def get_secret(self, key: str) -> Optional[str]:
        """Retrieve secret from system keyring."""
        if not self.available:
            return None
        
        try:
            return self.keyring.get_password(self.service_name, key)
        except Exception as e:
            logger.error(f"Error retrieving secret from keyring: {e}")
            return None
    
    async def set_secret(self, key: str, value: str) -> bool:
        """Store secret in system keyring."""
        if not self.available:
            return False
        
        try:
            self.keyring.set_password(self.service_name, key, value)
            return True
        except Exception as e:
            logger.error(f"Error storing secret in keyring: {e}")
            return False
    
    async def delete_secret(self, key: str) -> bool:
        """Delete secret from system keyring."""
        if not self.available:
            return False
        
        try:
            self.keyring.delete_password(self.service_name, key)
            return True
        except Exception as e:
            logger.error(f"Error deleting secret from keyring: {e}")
            return False
    
    async def list_secrets(self) -> list[str]:
        """List secrets (not supported by keyring)."""
        return []


class EncryptedFileBackend(SecretBackend):
    """Encrypted file backend for secure local storage."""
    
    def __init__(self, secrets_dir: str = "~/.devsecops/secrets"):
        self.secrets_dir = Path(secrets_dir).expanduser()
        self.secrets_dir.mkdir(parents=True, exist_ok=True)
        self.secrets_file = self.secrets_dir / "secrets.enc"
        self.key_file = self.secrets_dir / "master.key"
        
        # Set restrictive permissions
        try:
            os.chmod(self.secrets_dir, 0o700)  # Only owner can access
        except Exception as e:
            logger.warning(f"Could not set directory permissions: {e}")
    
    def _get_encryption_key(self) -> bytes:
        """Get or create encryption key."""
        if self.key_file.exists():
            try:
                with open(self.key_file, 'rb') as f:
                    return f.read()
            except Exception as e:
                logger.error(f"Error reading encryption key: {e}")
                raise
        else:
            # Generate new key
            key = Fernet.generate_key()
            try:
                with open(self.key_file, 'wb') as f:
                    f.write(key)
                os.chmod(self.key_file, 0o600)  # Only owner can read/write
                return key
            except Exception as e:
                logger.error(f"Error creating encryption key: {e}")
                raise
    
    def _load_secrets(self) -> Dict[str, str]:
        """Load and decrypt secrets from file."""
        if not self.secrets_file.exists():
            return {}
        
        try:
            key = self._get_encryption_key()
            fernet = Fernet(key)
            
            with open(self.secrets_file, 'rb') as f:
                encrypted_data = f.read()
            
            decrypted_data = fernet.decrypt(encrypted_data)
            return json.loads(decrypted_data.decode('utf-8'))
        except Exception as e:
            logger.error(f"Error loading secrets: {e}")
            return {}
    
    def _save_secrets(self, secrets: Dict[str, str]) -> bool:
        """Encrypt and save secrets to file."""
        try:
            key = self._get_encryption_key()
            fernet = Fernet(key)
            
            data = json.dumps(secrets).encode('utf-8')
            encrypted_data = fernet.encrypt(data)
            
            with open(self.secrets_file, 'wb') as f:
                f.write(encrypted_data)
            
            os.chmod(self.secrets_file, 0o600)  # Only owner can read/write
            return True
        except Exception as e:
            logger.error(f"Error saving secrets: {e}")
            return False
    
    async def get_secret(self, key: str) -> Optional[str]:
        """Retrieve secret from encrypted file."""
        secrets = self._load_secrets()
        return secrets.get(key)
    
    async def set_secret(self, key: str, value: str) -> bool:
        """Store secret in encrypted file."""
        secrets = self._load_secrets()
        secrets[key] = value
        return self._save_secrets(secrets)
    
    async def delete_secret(self, key: str) -> bool:
        """Delete secret from encrypted file."""
        secrets = self._load_secrets()
        if key in secrets:
            del secrets[key]
            return self._save_secrets(secrets)
        return True
    
    async def list_secrets(self) -> list[str]:
        """List all secret keys."""
        secrets = self._load_secrets()
        return list(secrets.keys())


class AWSSecretsManagerBackend(SecretBackend):
    """AWS Secrets Manager backend for cloud-based secret storage."""
    
    def __init__(self, region: str = "us-east-1", prefix: str = "devsecops/"):
        self.region = region
        self.prefix = prefix
        try:
            import boto3
            self.client = boto3.client('secretsmanager', region_name=region)
            self.available = True
        except ImportError:
            logger.warning("boto3 not available, AWS Secrets Manager backend disabled")
            self.available = False
        except Exception as e:
            logger.warning(f"AWS Secrets Manager not available: {e}")
            self.available = False
    
    async def get_secret(self, key: str) -> Optional[str]:
        """Retrieve secret from AWS Secrets Manager."""
        if not self.available:
            return None
        
        try:
            response = self.client.get_secret_value(SecretId=f"{self.prefix}{key}")
            return response['SecretString']
        except Exception as e:
            logger.debug(f"Secret not found in AWS Secrets Manager: {key}")
            return None
    
    async def set_secret(self, key: str, value: str) -> bool:
        """Store secret in AWS Secrets Manager."""
        if not self.available:
            return False
        
        try:
            secret_id = f"{self.prefix}{key}"
            try:
                # Try to update existing secret
                self.client.update_secret(SecretId=secret_id, SecretString=value)
            except self.client.exceptions.ResourceNotFoundException:
                # Create new secret
                self.client.create_secret(Name=secret_id, SecretString=value)
            return True
        except Exception as e:
            logger.error(f"Error storing secret in AWS Secrets Manager: {e}")
            return False
    
    async def delete_secret(self, key: str) -> bool:
        """Delete secret from AWS Secrets Manager."""
        if not self.available:
            return False
        
        try:
            self.client.delete_secret(SecretId=f"{self.prefix}{key}", ForceDeleteWithoutRecovery=True)
            return True
        except Exception as e:
            logger.error(f"Error deleting secret from AWS Secrets Manager: {e}")
            return False
    
    async def list_secrets(self) -> list[str]:
        """List secrets in AWS Secrets Manager."""
        if not self.available:
            return []
        
        try:
            response = self.client.list_secrets()
            secrets = []
            for secret in response.get('SecretList', []):
                name = secret['Name']
                if name.startswith(self.prefix):
                    secrets.append(name[len(self.prefix):])
            return secrets
        except Exception as e:
            logger.error(f"Error listing secrets from AWS Secrets Manager: {e}")
            return []


class SecretsManager:
    """Main secrets manager with multiple backend support and fallback."""
    
    def __init__(self, backends: Optional[list[SecretBackend]] = None):
        """Initialize secrets manager with backends in priority order."""
        if backends is None:
            # Default backends in priority order
            backends = [
                SystemKeyringBackend(),
                EncryptedFileBackend(),
                AWSSecretsManagerBackend(),
            ]
        
        self.backends = backends
        logger.info(f"Initialized SecretsManager with {len(backends)} backends")
    
    async def get_secret(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Retrieve secret from the first available backend."""
        for backend in self.backends:
            try:
                value = await backend.get_secret(key)
                if value is not None:
                    logger.debug(f"Retrieved secret '{key}' from {backend.__class__.__name__}")
                    return value
            except Exception as e:
                logger.warning(f"Error retrieving secret from {backend.__class__.__name__}: {e}")
                continue
        
        logger.debug(f"Secret '{key}' not found in any backend, using default")
        return default
    
    async def set_secret(self, key: str, value: str) -> bool:
        """Store secret in all available backends."""
        success = False
        for backend in self.backends:
            try:
                if await backend.set_secret(key, value):
                    logger.debug(f"Stored secret '{key}' in {backend.__class__.__name__}")
                    success = True
                else:
                    logger.warning(f"Failed to store secret '{key}' in {backend.__class__.__name__}")
            except Exception as e:
                logger.warning(f"Error storing secret in {backend.__class__.__name__}: {e}")
                continue
        
        return success
    
    async def delete_secret(self, key: str) -> bool:
        """Delete secret from all backends."""
        success = False
        for backend in self.backends:
            try:
                if await backend.delete_secret(key):
                    logger.debug(f"Deleted secret '{key}' from {backend.__class__.__name__}")
                    success = True
            except Exception as e:
                logger.warning(f"Error deleting secret from {backend.__class__.__name__}: {e}")
                continue
        
        return success
    
    async def list_secrets(self) -> list[str]:
        """List all available secrets from all backends."""
        all_secrets = set()
        for backend in self.backends:
            try:
                secrets = await backend.list_secrets()
                all_secrets.update(secrets)
            except Exception as e:
                logger.warning(f"Error listing secrets from {backend.__class__.__name__}: {e}")
                continue
        
        return sorted(list(all_secrets))
    
    async def rotate_secret(self, key: str, generator=None) -> Optional[str]:
        """Rotate a secret by generating a new value."""
        if generator is None:
            # Default: Generate secure random API key
            new_value = secrets.token_urlsafe(32)
        else:
            new_value = generator()
        
        if await self.set_secret(key, new_value):
            logger.info(f"Successfully rotated secret '{key}'")
            return new_value
        else:
            logger.error(f"Failed to rotate secret '{key}'")
            return None
    
    async def migrate_from_env(self, env_file: str = ".env") -> Dict[str, bool]:
        """Migrate secrets from .env file to secure storage."""
        results = {}
        
        if not os.path.exists(env_file):
            logger.info(f"No {env_file} file found to migrate")
            return results
        
        try:
            with open(env_file, 'r') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    
                    if '=' not in line:
                        logger.warning(f"Invalid line {line_num} in {env_file}: {line}")
                        continue
                    
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip().strip('"\'')
                    
                    # Only migrate keys that look like secrets
                    if any(keyword in key.upper() for keyword in ['KEY', 'SECRET', 'TOKEN', 'PASSWORD']):
                        success = await self.set_secret(key, value)
                        results[key] = success
                        if success:
                            logger.info(f"Migrated secret '{key}' from {env_file}")
                        else:
                            logger.error(f"Failed to migrate secret '{key}' from {env_file}")
        
        except Exception as e:
            logger.error(f"Error migrating from {env_file}: {e}")
        
        return results


# Global secrets manager instance
_secrets_manager: Optional[SecretsManager] = None


def get_secrets_manager() -> SecretsManager:
    """Get the global secrets manager instance."""
    global _secrets_manager
    if _secrets_manager is None:
        _secrets_manager = SecretsManager()
    return _secrets_manager


async def get_secret(key: str, default: Optional[str] = None) -> Optional[str]:
    """Convenience function to get a secret."""
    manager = get_secrets_manager()
    return await manager.get_secret(key, default)


async def set_secret(key: str, value: str) -> bool:
    """Convenience function to set a secret."""
    manager = get_secrets_manager()
    return await manager.set_secret(key, value)