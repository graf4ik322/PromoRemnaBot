#!/usr/bin/env python3
"""
Test script to debug user creation API issues
"""

import asyncio
import os
import sys
import logging
import inspect
from remnawave_api import RemnawaveSDK
from config import Config

# Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

async def test_user_creation():
    """Test user creation with different parameter combinations"""
    
    print("🧪 Testing User Creation API Methods...")
    print(f"Base URL: {Config.REMNAWAVE_BASE_URL}")
    print(f"Token: {Config.REMNAWAVE_TOKEN[:20]}..." if Config.REMNAWAVE_TOKEN else "No token")
    
    try:
        # Initialize SDK
        sdk = RemnawaveSDK(
            base_url=Config.REMNAWAVE_BASE_URL,
            token=Config.REMNAWAVE_TOKEN,
            caddy_token=Config.REMNAWAVE_CADDY_TOKEN
        )
        
        print("\n📡 Testing user creation methods...")
        
        # Test username for creation
        test_username = "test-user-debug-001"
        test_inbound_ids = Config.DEFAULT_INBOUND_IDS
        test_data_limit = 1024 * 1024 * 1024  # 1GB
        
        print(f"Test username: {test_username}")
        print(f"Test inbound IDs: {test_inbound_ids}")
        print(f"Test data limit: {test_data_limit}")
        
        # Method 1: Try with comprehensive parameters
        print("\n1. Testing Method 1 (comprehensive parameters)...")
        try:
            response = await sdk.users.create_user(
                username=test_username,
                data_limit=test_data_limit,
                expire_date=None,
                inbound_ids=test_inbound_ids,
                disabled=False
            )
            print(f"✅ Method 1 SUCCESS: {response}")
            return True
        except Exception as e:
            print(f"❌ Method 1 failed: {e}")
        
        # Method 2: Try with simpler structure
        print("\n2. Testing Method 2 (name parameter)...")
        try:
            response = await sdk.users.create_user(
                name=test_username,
                data_limit=test_data_limit,
                inbound_ids=test_inbound_ids
            )
            print(f"✅ Method 2 SUCCESS: {response}")
            return True
        except Exception as e:
            print(f"❌ Method 2 failed: {e}")
        
        # Method 3: Try minimal parameters
        print("\n3. Testing Method 3 (minimal parameters)...")
        try:
            response = await sdk.users.create_user(
                username=test_username,
                inbound_ids=test_inbound_ids
            )
            print(f"✅ Method 3 SUCCESS: {response}")
            return True
        except Exception as e:
            print(f"❌ Method 3 failed: {e}")
        
        # Method 4: Try with traffic_limit instead of data_limit
        print("\n4. Testing Method 4 (traffic_limit parameter)...")
        try:
            response = await sdk.users.create_user(
                username=test_username,
                traffic_limit=test_data_limit,
                inbound_ids=test_inbound_ids
            )
            print(f"✅ Method 4 SUCCESS: {response}")
            return True
        except Exception as e:
            print(f"❌ Method 4 failed: {e}")
        
        # Method 5: Check method signature
        print("\n5. Inspecting create_user method signature...")
        try:
            if hasattr(sdk.users, 'create_user'):
                method = getattr(sdk.users, 'create_user')
                sig = inspect.signature(method)
                print(f"create_user signature: {sig}")
                
                # Try calling with just required params based on signature
                params = list(sig.parameters.keys())
                print(f"Available parameters: {params}")
                
        except Exception as e:
            print(f"❌ Method inspection failed: {e}")
        
        print("\n❌ All user creation methods failed!")
        return False
        
    except Exception as e:
        print(f"💥 SDK initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_file_permissions():
    """Test file permission handling"""
    
    print("\n📁 Testing File Permissions...")
    
    from utils import FileManager
    
    try:
        file_manager = FileManager()
        print(f"Files directory: {file_manager.files_dir}")
        
        # Test writing a simple file
        test_links = [
            "vless://test1@example.com:443?security=tls",
            "vless://test2@example.com:443?security=tls"
        ]
        
        file_url = await file_manager.save_subscription_file("debug-test", test_links)
        
        if file_url:
            print(f"✅ File creation SUCCESS: {file_url}")
            return True
        else:
            print(f"❌ File creation FAILED")
            return False
            
    except Exception as e:
        print(f"💥 File test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main test function"""
    
    print("🚀 User Creation & File Permission Debug Test")
    print("=" * 60)
    
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
    
    # Test user creation
    user_success = await test_user_creation()
    
    # Test file permissions
    file_success = await test_file_permissions()
    
    print("\n" + "=" * 60)
    print("🎯 Test Results Summary:")
    print(f"  📤 User Creation: {'✅ SUCCESS' if user_success else '❌ FAILED'}")
    print(f"  📁 File Permissions: {'✅ SUCCESS' if file_success else '❌ FAILED'}")
    
    if user_success and file_success:
        print("🎉 All tests passed! The bot should work now.")
        return 0
    else:
        print("💥 Some tests failed. Check the output above for details.")
        return 1

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))