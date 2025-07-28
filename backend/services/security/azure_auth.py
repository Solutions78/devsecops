"""Azure Active Directory authentication module for DevSecOps Orchestrator.

This module provides seamless integration with Azure AD for authentication
and secure access to Azure resources including Key Vault.
"""
from __future__ import annotations

import os
import logging
from typing import Optional, Dict, Any, Union
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class AzureConfig:
    """Azure configuration settings."""
    tenant_id: Optional[str] = None
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    key_vault_url: Optional[str] = None
    resource_group: Optional[str] = None
    subscription_id: Optional[str] = None
    
    @classmethod
    def from_environment(cls) -> 'AzureConfig':
        """Load Azure configuration from environment variables."""
        return cls(
            tenant_id=os.getenv('AZURE_TENANT_ID'),
            client_id=os.getenv('AZURE_CLIENT_ID'), 
            client_secret=os.getenv('AZURE_CLIENT_SECRET'),
            key_vault_url=os.getenv('AZURE_KEY_VAULT_URL'),
            resource_group=os.getenv('AZURE_RESOURCE_GROUP'),
            subscription_id=os.getenv('AZURE_SUBSCRIPTION_ID')
        )


class AzureAuthenticator:
    """Azure Active Directory authentication manager."""
    
    def __init__(self, config: Optional[AzureConfig] = None):
        """Initialize Azure authenticator with configuration."""
        self.config = config or AzureConfig.from_environment()
        self._credential = None
        self._available = self._check_availability()
    
    def _check_availability(self) -> bool:
        """Check if Azure SDK is available and properly configured."""
        try:
            from azure.identity import DefaultAzureCredential, ClientSecretCredential
            from azure.core.exceptions import AzureError
            return True
        except ImportError:
            logger.warning("Azure SDK not available. Install: pip install azure-identity azure-keyvault-secrets")
            return False
    
    @property
    def available(self) -> bool:
        """Check if Azure authentication is available."""
        return self._available
    
    def get_credential(self, auth_method: str = "default") -> Optional[Any]:
        """
        Get Azure credential based on authentication method.
        
        Args:
            auth_method: Authentication method ('default', 'service_principal', 'managed_identity')
            
        Returns:
            Azure credential object or None if unavailable
        """
        if not self.available:
            return None
        
        try:
            from azure.identity import (
                DefaultAzureCredential, 
                ClientSecretCredential,
                ManagedIdentityCredential,
                AzureCliCredential,
                ChainedTokenCredential
            )
            
            if auth_method == "service_principal":
                if not all([self.config.tenant_id, self.config.client_id, self.config.client_secret]):
                    logger.warning("Service principal credentials incomplete, falling back to default")
                    return DefaultAzureCredential()
                
                logger.info("Using Azure service principal authentication")
                return ClientSecretCredential(
                    tenant_id=self.config.tenant_id,
                    client_id=self.config.client_id,
                    client_secret=self.config.client_secret
                )
            
            elif auth_method == "managed_identity":
                logger.info("Using Azure managed identity authentication")
                return ManagedIdentityCredential()
            
            elif auth_method == "cli":
                logger.info("Using Azure CLI authentication")
                return AzureCliCredential()
            
            elif auth_method == "chain":
                # Try multiple authentication methods in order
                logger.info("Using chained Azure authentication")
                credentials = []
                
                # 1. Try managed identity (for Azure resources)
                credentials.append(ManagedIdentityCredential())
                
                # 2. Try service principal (for CI/CD)
                if all([self.config.tenant_id, self.config.client_id, self.config.client_secret]):
                    credentials.append(ClientSecretCredential(
                        tenant_id=self.config.tenant_id,
                        client_id=self.config.client_id,
                        client_secret=self.config.client_secret
                    ))
                
                # 3. Try Azure CLI (for development)
                credentials.append(AzureCliCredential())
                
                return ChainedTokenCredential(*credentials)
            
            else:  # "default"
                logger.info("Using default Azure authentication")
                return DefaultAzureCredential()
                
        except Exception as e:
            logger.error(f"Error creating Azure credential: {e}")
            return None
    
    def test_authentication(self, auth_method: str = "default") -> Dict[str, Any]:
        """
        Test Azure authentication and return status information.
        
        Returns:
            Dictionary with authentication test results
        """
        result = {
            "available": self.available,
            "authenticated": False,
            "method": auth_method,
            "tenant_id": None,
            "error": None
        }
        
        if not self.available:
            result["error"] = "Azure SDK not available"
            return result
        
        try:
            credential = self.get_credential(auth_method)
            if not credential:
                result["error"] = "Failed to create credential"
                return result
            
            # Test authentication by getting a token
            from azure.core.credentials import AccessToken
            token = credential.get_token("https://management.azure.com/.default")
            
            if token and token.token:
                result["authenticated"] = True
                
                # Try to get tenant information if possible
                if self.config.tenant_id:
                    result["tenant_id"] = self.config.tenant_id
                
                logger.info(f"Azure authentication successful using {auth_method} method")
            else:
                result["error"] = "Failed to obtain access token"
                
        except Exception as e:
            result["error"] = str(e)
            logger.error(f"Azure authentication test failed: {e}")
        
        return result
    
    def setup_environment_variables(self, vault_url: str, tenant_id: str, 
                                  client_id: str, client_secret: str) -> bool:
        """
        Set up Azure environment variables for authentication.
        
        Args:
            vault_url: Azure Key Vault URL
            tenant_id: Azure AD tenant ID
            client_id: Azure AD application client ID
            client_secret: Azure AD application client secret
            
        Returns:
            True if setup successful
        """
        try:
            os.environ['AZURE_KEY_VAULT_URL'] = vault_url
            os.environ['AZURE_TENANT_ID'] = tenant_id
            os.environ['AZURE_CLIENT_ID'] = client_id
            os.environ['AZURE_CLIENT_SECRET'] = client_secret
            
            # Update config
            self.config = AzureConfig.from_environment()
            
            logger.info("Azure environment variables configured successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error setting up Azure environment: {e}")
            return False
    
    def get_key_vault_client(self, vault_url: Optional[str] = None, 
                           auth_method: str = "default"):
        """
        Get Azure Key Vault client with proper authentication.
        
        Args:
            vault_url: Key Vault URL (optional, uses config if not provided)
            auth_method: Authentication method to use
            
        Returns:
            SecretClient instance or None
        """
        if not self.available:
            return None
        
        vault_url = vault_url or self.config.key_vault_url
        if not vault_url:
            logger.error("Azure Key Vault URL not configured")
            return None
        
        try:
            from azure.keyvault.secrets import SecretClient
            
            credential = self.get_credential(auth_method)
            if not credential:
                return None
            
            client = SecretClient(vault_url=vault_url, credential=credential)
            logger.info(f"Created Azure Key Vault client for {vault_url}")
            return client
            
        except Exception as e:
            logger.error(f"Error creating Key Vault client: {e}")
            return None


# Global Azure authenticator instance
_azure_auth: Optional[AzureAuthenticator] = None


def get_azure_authenticator() -> AzureAuthenticator:
    """Get global Azure authenticator instance."""
    global _azure_auth
    if _azure_auth is None:
        _azure_auth = AzureAuthenticator()
    return _azure_auth


def test_azure_connection() -> Dict[str, Any]:
    """Test Azure AD connection and return detailed status."""
    auth = get_azure_authenticator()
    
    # Test different authentication methods
    methods = ["default", "service_principal", "managed_identity", "cli", "chain"]
    results = {}
    
    for method in methods:
        try:
            result = auth.test_authentication(method)
            results[method] = result
            
            # If one method works, we're good
            if result["authenticated"]:
                results["recommended_method"] = method
                break
                
        except Exception as e:
            results[method] = {
                "available": False,
                "authenticated": False,
                "method": method,
                "error": str(e)
            }
    
    # Overall status
    results["overall_status"] = any(r.get("authenticated", False) for r in results.values() if isinstance(r, dict))
    
    return results