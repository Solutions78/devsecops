#!/usr/bin/env python3
"""Setup script for migrating to secure key management.

This script helps migrate the DevSecOps Orchestrator from insecure .env files
to secure key management using system keyring, encrypted files, or cloud storage.

Run this script after updating the codebase to use the new secrets manager.
"""
import asyncio
import sys
import os
from pathlib import Path

# Ensure we can import from backend
sys.path.insert(0, str(Path(__file__).parent / "backend" / "orchestrator"))

try:
    from security.secrets_manager import get_secrets_manager
except ImportError as e:
    print(f"❌ Error importing secrets manager: {e}")
    print("Make sure you have installed the required dependencies:")
    print("pip install cryptography keyring boto3")
    sys.exit(1)

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def check_current_setup():
    """Check the current key management setup."""
    print("🔍 Checking current key management setup...")
    
    # Check for .env file
    env_file = Path(".env")
    if env_file.exists():
        print(f"⚠️  Found .env file with potential secrets")
        
        # Read and check for API keys
        with open(env_file, 'r') as f:
            content = f.read()
            
        api_keys_found = []
        for line in content.splitlines():
            if '=' in line and any(keyword in line.upper() for keyword in ['KEY', 'SECRET', 'TOKEN']):
                key_name = line.split('=')[0].strip()
                api_keys_found.append(key_name)
        
        if api_keys_found:
            print(f"🔑 Found {len(api_keys_found)} potential API keys:")
            for key in api_keys_found:
                print(f"   • {key}")
        else:
            print("ℹ️  No API keys detected in .env file")
    else:
        print("✅ No .env file found")
    
    # Check secure storage
    manager = get_secrets_manager()
    secrets = await manager.list_secrets()
    
    if secrets:
        print(f"🔐 Found {len(secrets)} secrets in secure storage:")
        for secret in secrets:
            print(f"   • {secret}")
    else:
        print("❌ No secrets found in secure storage")
    
    return env_file.exists(), len(secrets) > 0


async def migrate_keys():
    """Migrate keys from .env to secure storage."""
    print("\n🚀 Starting secure key migration...")
    
    manager = get_secrets_manager()
    
    # Migrate from .env if it exists
    env_file = Path(".env")
    if env_file.exists():
        print(f"\n📦 Migrating from {env_file}...")
        results = await manager.migrate_from_env(str(env_file))
        
        if results:
            successful = sum(1 for success in results.values() if success)
            total = len(results)
            print(f"✅ Successfully migrated {successful}/{total} secrets")
            
            if successful < total:
                print("⚠️  Some secrets failed to migrate. Check the logs above.")
            
            # Ask about .env file
            print(f"\n🛡️  Security Recommendation:")
            print(f"   The .env file contains sensitive information and should be secured.")
            
            choice = input("What would you like to do with .env file? (b)ackup and delete, (k)eep, (d)elete: ").lower()
            
            if choice == 'b':
                backup_path = env_file.with_suffix('.env.backup')
                env_file.rename(backup_path)
                print(f"✅ Moved {env_file} to {backup_path}")
                print("   Please store the backup file securely or delete it after verification")
            elif choice == 'd':
                env_file.unlink()
                print(f"✅ Deleted {env_file}")
            else:
                print(f"⚠️  Keeping {env_file} - please secure it manually")
        else:
            print("❌ No secrets found to migrate")
    
    # Check if we need to set up basic keys
    secrets = await manager.list_secrets()
    if 'API_KEY' not in secrets:
        print(f"\n🔑 Setting up API_KEY for orchestrator authentication...")
        
        choice = input("Generate a new API key automatically? (Y/n): ").lower()
        if choice != 'n':
            import secrets as python_secrets
            api_key = python_secrets.token_urlsafe(32)
            await manager.set_secret('API_KEY', api_key)
            print(f"✅ Generated and stored API_KEY: {api_key}")
            print("   Save this key securely - you'll need it to authenticate API requests")
        else:
            api_key = input("Enter your API key: ")
            if api_key:
                await manager.set_secret('API_KEY', api_key)
                print("✅ Stored API_KEY")
    
    print(f"\n🎉 Migration complete!")
    return True


async def verify_setup():
    """Verify the secure key management setup."""
    print("\n🔍 Verifying secure key management setup...")
    
    manager = get_secrets_manager()
    
    # Test key storage and retrieval
    test_key = "TEST_KEY"
    test_value = "test_value_12345"
    
    print("🧪 Testing key storage...")
    success = await manager.set_secret(test_key, test_value)
    if not success:
        print("❌ Failed to store test key")
        return False
    
    print("🧪 Testing key retrieval...")
    retrieved = await manager.get_secret(test_key)
    if retrieved != test_value:
        print("❌ Failed to retrieve test key correctly")
        return False
    
    print("🧪 Testing key deletion...")
    success = await manager.delete_secret(test_key)
    if not success:
        print("❌ Failed to delete test key")
        return False
    
    print("✅ All tests passed - secure key management is working!")
    
    # List final secrets
    secrets = await manager.list_secrets()
    if secrets:
        print(f"\n📋 Current secrets in secure storage:")
        for secret in secrets:
            print(f"   • {secret}")
    
    return True


async def show_usage_instructions():
    """Show instructions for using the new secure key management."""
    print(f"\n📚 Using Secure Key Management:")
    print(f"")
    print(f"🔧 Command Line Management:")
    print(f"   python backend/orchestrator/scripts/manage_secrets.py list-keys")
    print(f"   python backend/orchestrator/scripts/manage_secrets.py set-key KEY_NAME value")
    print(f"   python backend/orchestrator/scripts/manage_secrets.py rotate-key API_KEY")
    print(f"")
    print(f"🚀 Starting the Orchestrator:")
    print(f"   cd backend && uvicorn orchestrator.app:app --reload --port 8001")
    print(f"")
    print(f"🔐 API Authentication:")
    print(f"   curl -H 'Authorization: Bearer YOUR_API_KEY' http://localhost:8001/task")
    print(f"")
    print(f"🛡️  Security Best Practices:")
    print(f"   • Never commit API keys to version control")
    print(f"   • Rotate keys regularly using the management script")
    print(f"   • Use environment-specific keys for different deployments")
    print(f"   • Monitor key usage and audit access logs")


async def main():
    """Main setup function."""
    print("🔐 DevSecOps Orchestrator - Secure Key Management Setup")
    print("=" * 60)
    
    try:
        # Check current setup
        has_env, has_secure = await check_current_setup()
        
        if has_secure and not has_env:
            print("\n✅ Secure key management is already set up!")
            choice = input("Do you want to verify the setup? (Y/n): ")
            if choice.lower() != 'n':
                await verify_setup()
        else:
            # Migrate if needed
            if has_env or not has_secure:
                await migrate_keys()
            
            # Verify setup
            await verify_setup()
        
        # Show usage instructions
        await show_usage_instructions()
        
        print(f"\n🎉 Setup complete! Your API keys are now securely managed.")
        
    except KeyboardInterrupt:
        print(f"\n❌ Setup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        logger.error(f"Setup error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    asyncio.run(main())