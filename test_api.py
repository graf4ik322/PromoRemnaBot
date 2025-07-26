#!/usr/bin/env python3
"""
Test script to verify Remnawave API connectivity and methods
"""

import asyncio
import os
import sys
from remnawave_api import RemnawaveSDK
from config import Config

async def test_api():
    """Test basic API connectivity and methods"""
    
    print("🧪 Testing Remnawave API connectivity...")
    print(f"Base URL: {Config.REMNAWAVE_BASE_URL}")
    print(f"Token: {Config.REMNAWAVE_TOKEN[:20]}..." if Config.REMNAWAVE_TOKEN else "No token")
    
    try:
        # Initialize SDK
        sdk = RemnawaveSDK(
            base_url=Config.REMNAWAVE_BASE_URL,
            token=Config.REMNAWAVE_TOKEN,
            caddy_token=Config.REMNAWAVE_CADDY_TOKEN
        )
        
        print("\n📡 Testing API endpoints...")
        
        # Test 1: Get all users
        print("\n1. Testing get_all_users_v2()...")
        try:
            users_response = await sdk.users.get_all_users_v2()
            print(f"✅ Success! Got response: {type(users_response)}")
            
            if hasattr(users_response, 'users'):
                print(f"   Users count: {len(users_response.users)}")
                print(f"   Total: {getattr(users_response, 'total', 'N/A')}")
                
                # Show first few users
                if users_response.users:
                    print("   First 3 users:")
                    for i, user in enumerate(users_response.users[:3]):
                        username = getattr(user, 'username', 'No username')
                        disabled = getattr(user, 'disabled', 'Unknown')
                        print(f"     {i+1}. {username} (disabled: {disabled})")
                        
                        # Check if this is a promo user
                        if username.startswith(Config.DEFAULT_UUID_PREFIX):
                            parts = username.split('-')
                            if len(parts) >= 3:
                                tag = '-'.join(parts[2:])
                                print(f"        -> Promo tag: {tag}")
            else:
                print(f"   Response structure: {dir(users_response)}")
                
        except Exception as e:
            print(f"❌ get_all_users_v2() failed: {e}")
        
        # Test 2: Try old method for comparison
        print("\n2. Testing get_users() (old method)...")
        try:
            users_response_old = await sdk.users.get_users()
            print(f"✅ Old method works: {type(users_response_old)}")
        except Exception as e:
            print(f"❌ get_users() failed: {e}")
        
        # Test 3: Test user creation (dry run - don't actually create)
        print("\n3. Testing user creation methods availability...")
        try:
            # Just check if the method exists
            create_method = getattr(sdk.users, 'create_user', None)
            if create_method:
                print(f"✅ create_user method available")
            else:
                print(f"❌ create_user method not found")
                print(f"   Available methods: {[m for m in dir(sdk.users) if not m.startswith('_')]}")
        except Exception as e:
            print(f"❌ Error checking create_user: {e}")
        
        # Test 4: Get available tags
        print("\n4. Looking for existing promo tags...")
        try:
            users_response = await sdk.users.get_all_users_v2()
            tags = set()
            
            if hasattr(users_response, 'users'):
                for user in users_response.users:
                    username = getattr(user, 'username', '')
                    if username.startswith(Config.DEFAULT_UUID_PREFIX):
                        parts = username.split('-')
                        if len(parts) >= 3:
                            tag = '-'.join(parts[2:])
                            tags.add(tag)
            
            if tags:
                print(f"✅ Found {len(tags)} existing promo tags:")
                for tag in sorted(tags):
                    print(f"   - {tag}")
            else:
                print("ℹ️  No existing promo tags found")
                
        except Exception as e:
            print(f"❌ Error getting tags: {e}")
            
    except Exception as e:
        print(f"💥 SDK initialization failed: {e}")
        return False
    
    return True

async def main():
    """Main test function"""
    
    print("🚀 Remnawave API Test")
    print("=" * 50)
    
    # Check configuration
    if not Config.REMNAWAVE_BASE_URL:
        print("❌ REMNAWAVE_BASE_URL not configured")
        return 1
        
    if not Config.REMNAWAVE_TOKEN:
        print("❌ REMNAWAVE_TOKEN not configured")
        return 1
    
    try:
        # Validate configuration
        Config.validate()
        print("✅ Configuration is valid")
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return 1
    
    # Test API
    success = await test_api()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 API test completed! Check the results above.")
        return 0
    else:
        print("💥 API test failed!")
        return 1

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))