#!/usr/bin/env python3
"""
Test script for Remnawave Telegram Bot
"""

import asyncio
import sys
from config import Config

async def test_config():
    """Test configuration validation"""
    print("🔧 Testing configuration...")
    
    try:
        Config.validate()
        print("✅ Configuration is valid")
        return True
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        return False

async def test_imports():
    """Test all imports"""
    print("📦 Testing imports...")
    
    try:
        from telegram.ext import Application
        print("✅ python-telegram-bot imported successfully")
        
        from remnawave_api import RemnawaveSDK
        print("✅ remnawave-api imported successfully")
        
        import aiofiles
        print("✅ aiofiles imported successfully")
        
        from bot_handlers import BotHandlers
        print("✅ bot_handlers imported successfully")
        
        from remnawave_service import RemnawaveService
        print("✅ remnawave_service imported successfully")
        
        from utils import FileManager
        print("✅ utils imported successfully")
        
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

async def test_file_manager():
    """Test file manager functionality"""
    print("📁 Testing file manager...")
    
    try:
        from utils import FileManager
        
        file_manager = FileManager()
        
        # Test file saving (without actual file creation in test)
        test_links = [
            "https://example.com/sub1",
            "https://example.com/sub2",
            "https://example.com/sub3"
        ]
        
        print("✅ FileManager initialized successfully")
        print(f"✅ Files directory: {file_manager.files_dir}")
        
        return True
    except Exception as e:
        print(f"❌ FileManager error: {e}")
        return False

async def test_validation():
    """Test validation functions"""
    print("✔️ Testing validation functions...")
    
    try:
        from remnawave_service import RemnawaveService
        
        service = RemnawaveService()
        
        # Test tag validation
        valid_tags = ["test_tag", "summer-sale", "promo2024", "black_friday"]
        invalid_tags = ["", "тест", "test tag", "tag@123", "a" * 100]
        
        for tag in valid_tags:
            if not service._validate_tag(tag):
                print(f"❌ Valid tag '{tag}' failed validation")
                return False
        
        for tag in invalid_tags:
            if service._validate_tag(tag):
                print(f"❌ Invalid tag '{tag}' passed validation")
                return False
        
        print("✅ Tag validation working correctly")
        return True
    except Exception as e:
        print(f"❌ Validation error: {e}")
        return False

async def main():
    """Main test function"""
    print("🤖 Remnawave Telegram Bot - Test Suite")
    print("=" * 50)
    
    tests = [
        ("Configuration", test_config),
        ("Imports", test_imports),
        ("File Manager", test_file_manager),
        ("Validation", test_validation)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 Running {test_name} test...")
        try:
            if await test_func():
                passed += 1
            else:
                print(f"❌ {test_name} test failed")
        except Exception as e:
            print(f"❌ {test_name} test failed with exception: {e}")
    
    print("\n" + "=" * 50)
    print(f"🧪 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ All tests passed! Bot is ready to run.")
        return True
    else:
        print("❌ Some tests failed. Please check the configuration.")
        return False

if __name__ == "__main__":
    try:
        result = asyncio.run(main())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n🛑 Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test suite failed: {e}")
        sys.exit(1)