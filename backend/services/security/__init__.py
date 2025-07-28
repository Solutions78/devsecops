"""Security module for the DevSecOps Orchestrator.

This module provides security utilities including secure secret management,
authentication, and security validation functions.
"""
from __future__ import annotations

from .secrets_manager import (
    SecretsManager,
    get_secrets_manager,
    get_secret,
    set_secret,
    SystemKeyringBackend,
    EncryptedFileBackend,
    AzureKeyVaultBackend,
)

__all__ = [
    'SecretsManager',
    'get_secrets_manager', 
    'get_secret',
    'set_secret',
    'SystemKeyringBackend',
    'EncryptedFileBackend', 
    'AzureKeyVaultBackend',
]