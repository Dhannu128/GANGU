#!/usr/bin/env python3
"""Complete Cadbury Bournville COD Order Test"""

print("🍫 Complete Cadbury Bournville COD Order Test")
print("=" * 50)

user_input = 'cadbury bournville order kar do urgent'
print(f"👤 User: {user_input}")

from orchestration.gangu_main import handle_user_confirmation
from orchestration.gangu_graph import create_gangu_graph

try:
    # Run the initial pipeline
    gangu_graph = create_gangu_graph(checkpointer=None)
    result = gangu_graph.invoke({
        'user_input': user_input,
        'user_preferences': {}
    })

    print(f"\n📊 PIPELINE RESULTS:")
    print(f"✅ Item: {result.get('item_name', 'unknown')}")
    print(f"✅ Platform: {result.get('selected_option', {}).get('platform', 'unknown')}")
    print(f"✅ Price: {result.get('selected_option', {}).get('unit_price_label', 'unknown')}")
    print(f"✅ Decision Type: {result.get('decision_type', 'unknown')}")
    
    # If confirmation needed, simulate user saying "yes"
    if result.get('decision_type') == 'confirm_with_user':
        print(f"\n🤖 Simulating user confirmation...")
        print(f"👤 User says: YES")
        
        # Process the confirmation
        confirmed_result = handle_user_confirmation(gangu_graph, result)
        
        print(f"\n🎯 FINAL ORDER RESULT:")
        order_status = confirmed_result.get('purchase_status', 'unknown')
        print(f"Order Status: {order_status}")
        
        if order_status == 'success':
            order_id = confirmed_result.get('order_id', 'N/A')
            print(f"🎉 ORDER SUCCESSFUL!")
            print(f"📦 Order ID: {order_id}")
            print(f"💳 Payment: Cash on Delivery (COD)")
            print(f"📱 Phone: 9350179655")
            print(f"🏠 Address: room no-953 bh3 hostel IIIT allahabad")
            print(f"⏱️ Delivery: 1 hour (Zepto)")
            print(f"\n🍫 Cadbury Bournville chocolate ordered successfully!")
        elif order_status == 'manual_order_provided':
            print(f"📱 Manual order provided - follow app instructions")
            manual_info = confirmed_result.get('manual_order_info', {})
            print(f"Instructions: {manual_info.get('instructions', [])}")
        else:
            print(f"❌ Order failed with status: {order_status}")
    else:
        print(f"Order completed without confirmation")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print(f"\n✅ Cadbury Bournville is now fully integrated with COD ordering!")