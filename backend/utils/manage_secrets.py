#!/usr/bin/env python3
"""Command-line utility for managing secrets in the DevSecOps Orchestrator.

This script provides commands for migrating from .env files, managing API keys,
and performing key rotation operations.

Usage:
    python manage_secrets.py migrate --env-file .env
    python manage_secrets.py set-key API_KEY your-api-key-here
    python manage_secrets.py rotate-key API_KEY
    python manage_secrets.py list-keys
    python manage_secrets.py get-key API_KEY
    python manage_secrets.py delete-key OLD_KEY
"""
import asyncio
import argparse
import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.security.secrets_manager import get_secrets_manager, SecretsManager
from services.security.azure_auth import get_azure_authenticator, test_azure_connection
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


async def migrate_from_env(env_file: str):
    """Migrate secrets from .env file to secure storage."""
    print(f"🔄 Migrating secrets from {env_file} to secure storage...")
    
    manager = get_secrets_manager()
    results = await manager.migrate_from_env(env_file)
    
    if not results:
        print(f"❌ No secrets found in {env_file} or file does not exist")
        return
    
    print(f"✅ Migration results:")
    for key, success in results.items():
        status = "✅ SUCCESS" if success else "❌ FAILED"
        print(f"   {key}: {status}")
    
    successful = sum(1 for success in results.values() if success)
    total = len(results)
    print(f"\n📊 Migrated {successful}/{total} secrets successfully")
    
    if successful > 0:
        print(f"\n⚠️  IMPORTANT: Consider removing or securing {env_file} file after migration")
        print("   You can backup and delete it, or move it to a secure location")


async def set_secret(key: str, value: str):
    """Set a secret in secure storage."""
    print(f"🔐 Setting secret: {key}")
    
    manager = get_secrets_manager()
    success = await manager.set_secret(key, value)
    
    if success:
        print(f"✅ Secret '{key}' stored successfully")
    else:
        print(f"❌ Failed to store secret '{key}'")
        sys.exit(1)


async def get_secret(key: str):
    """Retrieve and display a secret."""
    print(f"🔍 Retrieving secret: {key}")
    
    manager = get_secrets_manager()
    value = await manager.get_secret(key)
    
    if value:
        print(f"✅ Secret '{key}': {value[:10]}{'...' if len(value) > 10 else ''}")
        print(f"   Full value: {value}")
    else:
        print(f"❌ Secret '{key}' not found")
        sys.exit(1)


async def list_secrets():
    """List all available secrets."""
    print("📋 Listing all secrets...")
    
    manager = get_secrets_manager()
    secrets = await manager.list_secrets()
    
    if secrets:
        print(f"✅ Found {len(secrets)} secrets:")
        for secret in secrets:
            print(f"   • {secret}")
    else:
        print("❌ No secrets found")


async def delete_secret(key: str):
    """Delete a secret from storage."""
    print(f"🗑️  Deleting secret: {key}")
    
    # Confirm deletion
    confirm = input(f"Are you sure you want to delete '{key}'? (y/N): ")
    if confirm.lower() != 'y':
        print("❌ Deletion cancelled")
        return
    
    manager = get_secrets_manager()
    success = await manager.delete_secret(key)
    
    if success:
        print(f"✅ Secret '{key}' deleted successfully")
    else:
        print(f"❌ Failed to delete secret '{key}'")
        sys.exit(1)


async def rotate_secret(key: str):
    """Rotate a secret by generating a new value."""
    print(f"🔄 Rotating secret: {key}")
    
    manager = get_secrets_manager()
    
    # Check if secret exists
    old_value = await manager.get_secret(key)
    if not old_value:
        print(f"❌ Secret '{key}' not found")
        sys.exit(1)
    
    # Generate new value
    new_value = await manager.rotate_secret(key)
    
    if new_value:
        print(f"✅ Secret '{key}' rotated successfully")
        print(f"   New value: {new_value}")
        print(f"   🚨 Make sure to update any services using this key!")
    else:
        print(f"❌ Failed to rotate secret '{key}'")
        sys.exit(1)


async def setup_initial_keys():
    """Set up initial API keys for the system."""
    print("🚀 Setting up initial API keys for DevSecOps Orchestrator")
    print()
    
    manager = get_secrets_manager()
    
    # Setup API_KEY for the orchestrator
    api_key = input("Enter API key for orchestrator authentication (or press Enter to generate): ")
    if not api_key:
        import secrets
        api_key = secrets.token_urlsafe(32)
        print(f"Generated API key: {api_key}")
    
    await manager.set_secret('API_KEY', api_key)
    print("✅ API_KEY stored")
    
    # Setup ANTHROPIC_API_KEY
    anthropic_key = input("Enter Anthropic/Claude API key (or press Enter to skip): ")
    if anthropic_key:
        await manager.set_secret('ANTHROPIC_API_KEY', anthropic_key)
        print("✅ ANTHROPIC_API_KEY stored")
    
    print("\n🎉 Initial setup complete!")
    print("\nYou can now start the orchestrator with secure key management.")


async def test_azure_auth():
    """Test Azure Active Directory authentication."""
    print("🔍 Testing Azure Active Directory authentication...")
    print()
    
    results = test_azure_connection()
    
    print("📊 Azure Authentication Test Results:")
    print("=" * 50)
    
    for method, result in results.items():
        if method in ['overall_status', 'recommended_method']:
            continue
            
        status = "✅ SUCCESS" if result.get('authenticated', False) else "❌ FAILED"
        print(f"{method:20} {status}")
        
        if result.get('error'):
            print(f"{'':20} Error: {result['error']}")
        
        if result.get('tenant_id'):
            print(f"{'':20} Tenant: {result['tenant_id']}")
        
        print()
    
    overall_status = results.get('overall_status', False)
    if overall_status:
        recommended = results.get('recommended_method', 'default')
        print(f"✅ Azure authentication is working!")
        print(f"💡 Recommended method: {recommended}")
    else:
        print("❌ Azure authentication failed for all methods")
        print("💡 Make sure you have:")
        print("   - Azure CLI installed (az login)")
        print("   - Service principal configured (AZURE_TENANT_ID, AZURE_CLIENT_ID, AZURE_CLIENT_SECRET)")
        print("   - Managed identity enabled (when running on Azure)")


async def setup_azure_keyvault():
    """Interactive setup for Azure Key Vault integration."""
    print("🔐 Setting up Azure Key Vault integration")
    print()
    
    # Get Azure configuration
    vault_url = input("Enter Azure Key Vault URL (https://your-vault.vault.azure.net/): ")
    if not vault_url:
        print("❌ Key Vault URL is required")
        return
    
    print("\nChoose authentication method:")
    print("1. Azure CLI (for development)")
    print("2. Service Principal (for CI/CD)")
    print("3. Managed Identity (for Azure resources)")
    
    choice = input("Enter choice (1-3): ")
    
    if choice == "1":
        print("\n💡 Make sure you're logged in with: az login")
        os.environ['AZURE_KEY_VAULT_URL'] = vault_url
        
    elif choice == "2":
        tenant_id = input("Enter Azure Tenant ID: ")
        client_id = input("Enter Azure Client ID: ")
        client_secret = input("Enter Azure Client Secret: ")
        
        if not all([tenant_id, client_id, client_secret]):
            print("❌ All service principal credentials are required")
            return
        
        os.environ['AZURE_KEY_VAULT_URL'] = vault_url
        os.environ['AZURE_TENANT_ID'] = tenant_id
        os.environ['AZURE_CLIENT_ID'] = client_id
        os.environ['AZURE_CLIENT_SECRET'] = client_secret
        
    elif choice == "3":
        print("\n💡 Managed Identity authentication will be used")
        os.environ['AZURE_KEY_VAULT_URL'] = vault_url
        
    else:
        print("❌ Invalid choice")
        return
    
    # Test the configuration
    print("\n🧪 Testing Azure Key Vault connection...")  
    auth = get_azure_authenticator()
    test_result = auth.test_authentication()
    
    if test_result.get('authenticated'):
        print("✅ Azure Key Vault setup successful!")
        print(f"🔐 Vault URL: {vault_url}")
        print(f"🎫 Auth method: {test_result.get('method', 'unknown')}")
    else:
        print("❌ Azure Key Vault setup failed")
        print(f"Error: {test_result.get('error', 'Unknown error')}")


async def backup_secrets(backup_file: str):
    """Create an encrypted backup of all secrets."""
    print(f"💾 Creating encrypted backup: {backup_file}")
    
    manager = get_secrets_manager()
    secrets_list = await manager.list_secrets()
    
    if not secrets_list:
        print("❌ No secrets to backup")
        return
    
    backup_data = {}
    for key in secrets_list:
        value = await manager.get_secret(key)
        if value:
            backup_data[key] = value
    
    # Encrypt and save backup
    import json
    from cryptography.fernet import Fernet
    
    backup_key = Fernet.generate_key()
    fernet = Fernet(backup_key)
    
    encrypted_data = fernet.encrypt(json.dumps(backup_data).encode())
    
    with open(backup_file, 'wb') as f:
        f.write(encrypted_data)
    
    key_file = f"{backup_file}.key"
    with open(key_file, 'wb') as f:
        f.write(backup_key)
    
    print(f"✅ Backup created: {backup_file}")
    print(f"✅ Backup key saved: {key_file}")
    print(f"📊 Backed up {len(backup_data)} secrets")
    print("\n⚠️  Keep the .key file secure - you need it to restore the backup!")


def main():
    """Main command-line interface."""
    parser = argparse.ArgumentParser(
        description="Manage secrets for DevSecOps Orchestrator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s migrate --env-file .env
  %(prog)s set-key API_KEY sk-your-api-key-here
  %(prog)s rotate-key API_KEY
  %(prog)s list-keys
  %(prog)s setup
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Migrate command
    migrate_parser = subparsers.add_parser('migrate', help='Migrate secrets from .env file')
    migrate_parser.add_argument('--env-file', default='.env', help='Path to .env file')
    
    # Set secret command
    set_parser = subparsers.add_parser('set-key', help='Set a secret')
    set_parser.add_argument('key', help='Secret key name')
    set_parser.add_argument('value', help='Secret value')
    
    # Get secret command
    get_parser = subparsers.add_parser('get-key', help='Get a secret')
    get_parser.add_argument('key', help='Secret key name')
    
    # List secrets command
    subparsers.add_parser('list-keys', help='List all secrets')
    
    # Delete secret command
    delete_parser = subparsers.add_parser('delete-key', help='Delete a secret')
    delete_parser.add_argument('key', help='Secret key name')
    
    # Rotate secret command
    rotate_parser = subparsers.add_parser('rotate-key', help='Rotate a secret')
    rotate_parser.add_argument('key', help='Secret key name')
    
    # Setup command
    subparsers.add_parser('setup', help='Set up initial API keys')
    
    # Azure commands
    subparsers.add_parser('test-azure', help='Test Azure AD authentication')
    subparsers.add_parser('setup-azure', help='Setup Azure Key Vault integration')
    
    # Backup command
    backup_parser = subparsers.add_parser('backup', help='Create encrypted backup')
    backup_parser.add_argument('file', help='Backup file path')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Run the appropriate command
    try:
        if args.command == 'migrate':
            asyncio.run(migrate_from_env(args.env_file))
        elif args.command == 'set-key':
            asyncio.run(set_secret(args.key, args.value))
        elif args.command == 'get-key':
            asyncio.run(get_secret(args.key))
        elif args.command == 'list-keys':
            asyncio.run(list_secrets())
        elif args.command == 'delete-key':
            asyncio.run(delete_secret(args.key))
        elif args.command == 'rotate-key':
            asyncio.run(rotate_secret(args.key))
        elif args.command == 'setup':
            asyncio.run(setup_initial_keys())
        elif args.command == 'backup':
            asyncio.run(backup_secrets(args.file))
        elif args.command == 'test-azure':
            asyncio.run(test_azure_auth())
        elif args.command == 'setup-azure':
            asyncio.run(setup_azure_keyvault())
        
    except KeyboardInterrupt:
        print("\n❌ Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        logger.error(f"Command failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()