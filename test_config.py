#!/usr/bin/env python3
"""
Test script to verify DEFAULT_INBOUND_IDS parsing fix
"""

import os
import sys
from unittest.mock import patch

def test_inbound_ids_parsing():
    """Test different formats of DEFAULT_INBOUND_IDS"""
    
    print("🧪 Testing DEFAULT_INBOUND_IDS parsing...")
    
    # Add current directory to path for imports
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    from config import _parse_inbound_ids
    
    test_cases = [
        # (input, expected_output, description)
        ("1,2,3", [1, 2, 3], "Numeric IDs"),
        ("b9811fcd-f20b-45c2-912a-fb21ab6c7664", ["b9811fcd-f20b-45c2-912a-fb21ab6c7664"], "Single UUID"),
        ("b9811fcd-f20b-45c2-912a-fb21ab6c7664,another-uuid", ["b9811fcd-f20b-45c2-912a-fb21ab6c7664", "another-uuid"], "Multiple UUIDs"),
        ("1,b9811fcd-f20b-45c2-912a-fb21ab6c7664,3", [1, "b9811fcd-f20b-45c2-912a-fb21ab6c7664", 3], "Mixed format"),
        ("", [1], "Empty string"),
        ("  1  ,  2  ,  3  ", [1, 2, 3], "With spaces"),
        ("1,,3", [1, 3], "With empty values"),
    ]
    
    passed = 0
    total = len(test_cases)
    
    for input_val, expected, description in test_cases:
        try:
            result = _parse_inbound_ids(input_val)
            if result == expected:
                print(f"✅ {description}: {input_val!r} -> {result}")
                passed += 1
            else:
                print(f"❌ {description}: {input_val!r} -> {result} (expected {expected})")
        except Exception as e:
            print(f"💥 {description}: {input_val!r} -> ERROR: {e}")
    
    print(f"\n📊 Results: {passed}/{total} tests passed")
    return passed == total

def test_config_loading():
    """Test config loading with different environment variables"""
    
    print("\n🔧 Testing Config class loading...")
    
    test_envs = [
        {"DEFAULT_INBOUND_IDS": "1,2,3"},
        {"DEFAULT_INBOUND_IDS": "b9811fcd-f20b-45c2-912a-fb21ab6c7664"},
        {"DEFAULT_INBOUND_IDS": "1,uuid-test,3"},
    ]
    
    for env_vars in test_envs:
        with patch.dict(os.environ, env_vars, clear=False):
            try:
                # Reload config module to pick up new env vars
                if 'config' in sys.modules:
                    del sys.modules['config']
                
                from config import Config
                
                print(f"✅ Config loaded with DEFAULT_INBOUND_IDS={env_vars['DEFAULT_INBOUND_IDS']}")
                print(f"   Result: {Config.DEFAULT_INBOUND_IDS}")
                
            except Exception as e:
                print(f"❌ Config failed with DEFAULT_INBOUND_IDS={env_vars['DEFAULT_INBOUND_IDS']}: {e}")
                return False
    
    return True

def main():
    """Run all tests"""
    
    print("🚀 Configuration Parsing Tests")
    print("=" * 40)
    
    success = True
    
    # Test parsing function
    if not test_inbound_ids_parsing():
        success = False
    
    # Test config loading
    if not test_config_loading():
        success = False
    
    print("\n" + "=" * 40)
    if success:
        print("🎉 All tests passed! Configuration parsing is working correctly.")
        return 0
    else:
        print("❌ Some tests failed. Please check the configuration parsing logic.")
        return 1

if __name__ == "__main__":
    sys.exit(main())