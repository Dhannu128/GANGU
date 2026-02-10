#!/usr/bin/env python3
"""
Test script for GANGU confirmation flow
Tests the Yes/No confirmation and automatic COD order placement
"""

import sys
import json
from pathlib import Path

# Add GANGU directory to Python path
gangu_root = Path(__file__).parent
sys.path.insert(0, str(gangu_root))

def test_confirmation_flow():
    """Test the confirmation flow with mock data"""
    
    print("🧪 Testing GANGU Confirmation Flow")
    print("=" * 50)
    
    # Import our confirmation handler
    from orchestration.gangu_main import handle_user_confirmation
    
    # Create mock result data (simulating what decision agent returns)
    mock_result = {
        "user_input": "Tomatoes khareedna hai",
        "item_name": "Tomatoes",
        "quantity": "1kg",
        "decision_type": "confirm_with_user",
        "purchase_status": "pending_confirmation",
        "selected_option": {
            "platform": "Zepto",
            "normalized_attributes": {
                "unit_price_label": "₹30.00/kg",
                "delivery_time_label": "1 hour",
                "price": 30.00
            }
        },
        "ai_response": "Mock response for testing"
    }
    
    # Mock gangu_graph (we don't need real graph for testing)
    class MockGraph:
        def invoke(self, state):
            return state
    
    mock_graph = MockGraph()
    
    print("\n📊 Mock Data Created:")
    print(f"   Item: {mock_result['item_name']}")
    print(f"   Platform: {mock_result['selected_option']['platform']}")
    print(f"   Price: {mock_result['selected_option']['normalized_attributes']['unit_price_label']}")
    print(f"   Decision Type: {mock_result['decision_type']}")
    
    print(f"\n🎯 This test will:")
    print(f"   1. Show confirmation prompt")
    print(f"   2. Wait for your Yes/No response")
    print(f"   3. Process your choice")
    print(f"   4. Show result")
    
    print(f"\n⚠️  Note: This is a test - no real order will be placed")
    print(f"     (DRY_RUN_MODE is automatically enabled for testing)")
    
    # Set DRY RUN mode for testing
    import os
    os.environ['GANGU_DRY_RUN'] = 'true'
    
    try:
        # Test the confirmation flow
        result = handle_user_confirmation(mock_graph, mock_result)
        
        print(f"\n📤 Final Result:")
        print(f"   Purchase Status: {result.get('purchase_status', 'unknown')}")
        print(f"   User Confirmed: {result.get('user_confirmed', 'unknown')}")
        
        if result.get('ai_response'):
            print(f"\n🤖 GANGU Response:")
            print(f"{result['ai_response']}")
        
        return result
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_purchase_agent_directly():
    """Test purchase agent directly with COD"""
    
    print(f"\n🧪 Testing Purchase Agent (COD) Directly")
    print("=" * 50)
    
    try:
        from agents.purchase_agent import execute_purchase
        
        # Mock purchase input for COD order
        purchase_input = {
            "final_decision": {
                "selected_platform": "zepto",  # Lowercase triggers COD
                "product": {
                    "name": "Tomatoes",
                    "price": 30.00,
                    "quantity": "1kg",
                    "product_id": "tomatoes_1kg"
                },
                "delivery": {
                    "delivery_date": "today",
                    "slot": "within 1 hour"
                }
            },
            "user_context": {
                "payment_preference": "cash_on_delivery",
                "platform_preference": "zepto",
                "confirmed_by_user": True
            }
        }
        
        print(f"\n📊 Testing with:")
        print(f"   Platform: {purchase_input['final_decision']['selected_platform']}")
        print(f"   Product: {purchase_input['final_decision']['product']['name']}")
        print(f"   Payment: COD (Cash on Delivery)")
        
        # Execute purchase (in DRY RUN mode)
        result = execute_purchase(purchase_input)
        
        print(f"\n📤 Purchase Result:")
        print(f"   Status: {result.get('purchase_status')}")
        if result.get('execution_details'):
            print(f"   Order ID: {result['execution_details'].get('order_id')}")
            print(f"   Platform Used: {result['execution_details'].get('platform_used')}")
        
        print(f"\n💬 User Message:")
        print(f"   {result.get('user_message', 'No message')}")
        
        return result
        
    except Exception as e:
        print(f"\n❌ Purchase agent test failed: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    print("""
╔════════════════════════════════════════════════════════════════╗
║                🧪 GANGU CONFIRMATION FLOW TEST                 ║
║                ─────────────────────────────────                ║
║   Testing Yes/No confirmation and automatic COD order          ║
║   placement for Zepto platform                                 ║
╚════════════════════════════════════════════════════════════════╝
""")
    
    try:
        # Test 1: Purchase Agent Direct Test
        test_purchase_agent_directly()
        
        print(f"\n{'='*60}")
        
        # Test 2: Full Confirmation Flow
        test_confirmation_flow()
        
        print(f"\n✅ All tests completed!")
        
    except KeyboardInterrupt:
        print(f"\n\n👋 Tests interrupted by user")
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()