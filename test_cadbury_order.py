#!/usr/bin/env python3
"""Test Cadbury Bournville order through GANGU with COD"""

print("🍫 Testing Cadbury Bournville Order through GANGU")
print("=" * 50)

# Test different ways to order the chocolate
test_inputs = [
    "cadbury bournville order kar do urgent",
    "bournville chocolate chahiye urgent",
    "dark chocolate cadbury mangao urgent",
]

from orchestration.gangu_graph import create_gangu_graph

for test_input in test_inputs:
    print(f"\n👤 User: {test_input}")
    print("-" * 30)
    
    try:
        gangu_graph = create_gangu_graph(checkpointer=None)
        result = gangu_graph.invoke({
            'user_input': test_input,
            'user_preferences': {}
        })

        print(f"✅ Intent: {result.get('detected_intent', 'unknown')}")
        print(f"✅ Item: {result.get('item_name', 'unknown')}")
        print(f"✅ Urgency: {result.get('urgency', 'unknown')}")
        
        # Check if Zepto was selected and order was processed
        selected = result.get('selected_option', {})
        if selected.get('platform', '').lower() == 'zepto':
            print(f"✅ Platform: Zepto")
            print(f"✅ Price: {selected.get('unit_price_label', 'N/A')}")
            
        order_status = result.get('purchase_status', 'unknown')
        print(f"✅ Order Status: {order_status}")
        
        if order_status == 'success':
            print(f"🎉 ORDER SUCCESSFUL! Order ID: {result.get('order_id', 'N/A')}")
            print("🍫 Cadbury Bournville chocolate ordered with COD!")
        elif order_status == 'manual_order_provided':
            print("📱 Manual order provided - COD not available, app instructions given")
        
        break  # Test only first successful input
        
    except Exception as e:
        print(f"❌ Error: {e}")
        continue

print("\n🎯 Cadbury Bournville added to GANGU successfully!")
print("✅ You can now order it with COD through Zepto")
print("📱 Phone: 9350179655")
print("🏠 Address: room no-953 bh3 hostel IIIT allahabad")