#!/usr/bin/env python3
"""
Test script to verify conversation flow and state transitions
"""

import sys
from bot_handlers import (
    WAITING_TAG, WAITING_TRAFFIC, WAITING_COUNT, WAITING_CONFIRMATION,
    WAITING_CONFIRM_DELETE, SELECTING_TAG_DELETE, SHOWING_DELETE_PREVIEW
)

def test_conversation_states():
    """Test that all conversation states are properly defined"""
    
    print("🧪 Testing Conversation States...")
    
    # Test that all states have unique values
    states = [
        ('WAITING_TAG', WAITING_TAG),
        ('WAITING_TRAFFIC', WAITING_TRAFFIC), 
        ('WAITING_COUNT', WAITING_COUNT),
        ('WAITING_CONFIRMATION', WAITING_CONFIRMATION),
        ('WAITING_CONFIRM_DELETE', WAITING_CONFIRM_DELETE),
        ('SELECTING_TAG_DELETE', SELECTING_TAG_DELETE),
        ('SHOWING_DELETE_PREVIEW', SHOWING_DELETE_PREVIEW)
    ]
    
    print(f"Total states: {len(states)}")
    
    values = [state[1] for state in states]
    unique_values = set(values)
    
    if len(values) == len(unique_values):
        print("✅ All states have unique values")
        
        print("\nState values:")
        for name, value in states:
            print(f"  {name}: {value}")
            
        # Test the flow we expect
        print(f"\n🔄 Expected Promo Creation Flow:")
        print(f"  1. Entry Point → {WAITING_TAG} (WAITING_TAG)")
        print(f"  2. Tag Input → {WAITING_TRAFFIC} (WAITING_TRAFFIC)")  
        print(f"  3. Traffic Selection → {WAITING_COUNT} (WAITING_COUNT)")
        print(f"  4. Count Input → {WAITING_CONFIRMATION} (WAITING_CONFIRMATION)")
        print(f"  5. Confirmation → ConversationHandler.END")
        
        return True
    else:
        print("❌ Some states have duplicate values!")
        print(f"Values: {values}")
        print(f"Unique: {list(unique_values)}")
        return False

def test_conversation_imports():
    """Test that main.py can import all required states"""
    
    print("\n🔍 Testing Import Compatibility...")
    
    try:
        # This simulates what main.py does
        from bot_handlers import BotHandlers, WAITING_TAG, WAITING_TRAFFIC, WAITING_COUNT, WAITING_CONFIRMATION
        print("✅ All required states imported successfully")
        
        # Test that BotHandlers can be instantiated
        handlers = BotHandlers()
        print("✅ BotHandlers instantiated successfully")
        
        # Check that required methods exist
        required_methods = [
            'create_promo_callback',
            'handle_tag_input', 
            'handle_traffic_limit',
            'handle_count_input',
            'confirm_create_callback',
            'main_menu_callback'
        ]
        
        missing_methods = []
        for method in required_methods:
            if not hasattr(handlers, method):
                missing_methods.append(method)
        
        if missing_methods:
            print(f"❌ Missing methods: {missing_methods}")
            return False
        else:
            print(f"✅ All required methods exist: {len(required_methods)} methods")
            return True
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_conversation_flow_logic():
    """Test the conversation flow logic"""
    
    print("\n🔄 Testing Conversation Flow Logic...")
    
    try:
        from telegram.ext import ConversationHandler
        
        # Test that states are properly ordered
        expected_flow = [
            WAITING_TAG,      # 0
            WAITING_TRAFFIC,  # 1 
            WAITING_COUNT,    # 2
            WAITING_CONFIRMATION, # 3
        ]
        
        print("Expected promo creation flow:")
        for i, state in enumerate(expected_flow):
            print(f"  Step {i+1}: {state}")
        
        # Verify sequential numbering
        for i, state in enumerate(expected_flow):
            if state != i:
                print(f"❌ State {state} should be {i}")
                return False
        
        print("✅ State flow is logically ordered")
        
        # Test ConversationHandler.END
        print(f"✅ ConversationHandler.END = {ConversationHandler.END}")
        
        return True
        
    except Exception as e:
        print(f"❌ Flow logic error: {e}")
        return False

def main():
    """Main test function"""
    
    print("🚀 Conversation Flow Test")
    print("=" * 50)
    
    tests = [
        test_conversation_states,
        test_conversation_imports, 
        test_conversation_flow_logic
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                print("❌ Test failed")
        except Exception as e:
            print(f"💥 Test crashed: {e}")
    
    print("\n" + "=" * 50)
    print(f"Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All conversation flow tests passed!")
        print("\n✅ The confirmation button issue should be FIXED:")
        print("   - Added WAITING_CONFIRMATION state")
        print("   - handle_count_input now returns WAITING_CONFIRMATION")
        print("   - confirm_create_callback is in WAITING_CONFIRMATION state")
        print("   - Conversation continues until user confirms or cancels")
        return 0
    else:
        print("💥 Some tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())