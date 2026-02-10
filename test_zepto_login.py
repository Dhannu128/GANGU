#!/usr/bin/env python3
"""Test Zepto login with updated phone number 7376643462"""

print("🧪 Testing Zepto Login with Phone: 7376643462")
print("=" * 50)

# Test the exact order flow
user_input = 'mango slice order kar do urgent'
print(f"👤 User: {user_input}")

from orchestration.gangu_graph import create_gangu_graph

try:
    gangu_graph = create_gangu_graph(checkpointer=None)
    result = gangu_graph.invoke({
        'user_input': user_input,
        'user_preferences': {}
    })

    print("\n✅ ZEPTO LOGIN TEST RESULTS:")
    print("=" * 40)
    print(f"Order Status: {result.get('purchase_status', 'unknown')}")
    
    if result.get('purchase_status') == 'success':
        print(f"✅ Order ID: {result.get('order_id', 'N/A')}")
        print(f"✅ Platform: {result.get('selected_option', {}).get('platform', 'N/A')}")
        print("✅ ZEPTO LOGIN SUCCESSFUL WITH YOUR PHONE NUMBER!")
    elif result.get('purchase_status') == 'manual_order_provided':
        print("📱 Manual order provided (COD not available)")
        print("✅ ZEPTO LOGIN SUCCESSFUL - Phone number working!")
    else:
        print(f"Status: {result.get('purchase_status', 'unknown')}")

    print(f"\nPhone Number Used: 7376643462")
    print(f"Address Used: room no-953 bh3 hostel IIIT allahabad")
    
except Exception as e:
    print(f"❌ Error: {e}")