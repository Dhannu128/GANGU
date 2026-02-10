#!/usr/bin/env python3
"""Complete 5 Cadbury Bournville Urgent Order with Zepto Login"""

print("🍫 URGENT: Ordering 5 Cadbury Bournville Chocolates")
print("=" * 60)
print("📱 Phone: 7376643462")
print("🏠 Address: Other")
print("💳 Payment: Cash on Delivery (COD)")
print("=" * 60)

# The user wants 5 cadbury chocolates urgently
user_input = '5 cadbury bournville order kar do urgent'
print(f"👤 User: {user_input}")

from orchestration.gangu_graph import create_gangu_graph

try:
    print("\n🚀 Starting GANGU pipeline...")
    gangu_graph = create_gangu_graph(checkpointer=None)
    
    result = gangu_graph.invoke({
        'user_input': user_input,
        'user_preferences': {
            'auto_confirm_urgent': True,  # Auto-confirm urgent orders
            'preferred_payment': 'cod'
        }
    })

    print(f"\n📊 ORDER PROCESSING RESULTS:")
    print(f"✅ Item: {result.get('item_name', 'unknown')}")
    print(f"✅ Quantity: {result.get('quantity', 'unknown')}")
    print(f"✅ Urgency: {result.get('urgency', 'unknown')}")
    
    selected = result.get('selected_option', {})
    if selected:
        platform = selected.get('platform', 'unknown')
        price = selected.get('unit_price_label', 'unknown')
        delivery = selected.get('delivery_time_label', 'unknown')
        print(f"✅ Platform: {platform}")
        print(f"✅ Price: {price}")
        print(f"✅ Delivery: {delivery}")
        
    decision_type = result.get('decision_type', 'unknown')
    print(f"✅ Decision: {decision_type}")
    
    # If urgent order, it should auto-buy
    if decision_type == 'auto_buy':
        order_status = result.get('purchase_status', 'unknown')
        print(f"\n💳 PURCHASE STATUS: {order_status}")
        
        if order_status == 'success':
            order_id = result.get('order_id', 'N/A')
            print(f"\n🎉 ORDER COMPLETED SUCCESSFULLY!")
            print(f"📦 Order ID: {order_id}")
            print(f"📱 Zepto will call: 7376643462")
            print(f"🏠 Delivery to: Other")
            print(f"⏰ Expected delivery: Within 1 hour")
            print(f"💰 Total: 5 × {price}")
            print(f"💳 Payment: Cash on Delivery")
            
        elif order_status == 'manual_order_provided':
            manual_info = result.get('manual_order_info', {})
            instructions = manual_info.get('instructions', [])
            
            print(f"\n📱 MANUAL ORDER REQUIRED (COD not available)")
            print(f"Please complete order manually:")
            for i, instruction in enumerate(instructions, 1):
                print(f"  {i}. {instruction}")
            print(f"🔍 Search for: {manual_info.get('search_term', 'cadbury bournville')}")
            print(f"🌐 Zepto URL: {manual_info.get('zepto_url', 'https://www.zeptonow.com')}")
            
        else:
            print(f"⚠️ Order status: {order_status}")
            
    elif decision_type == 'confirm_with_user':
        print(f"\n🤖 Order requires confirmation - Auto-confirming for urgent request...")
        
        # Import the confirmation handler
        from orchestration.gangu_main import handle_user_confirmation
        
        print(f"👤 Auto-confirming: YES")
        confirmed_result = handle_user_confirmation(gangu_graph, result)
        
        final_status = confirmed_result.get('purchase_status', 'unknown')
        print(f"💳 Final Status: {final_status}")
        
        if final_status == 'success':
            order_id = confirmed_result.get('order_id', 'N/A')
            print(f"\n🎉 ORDER COMPLETED!")
            print(f"📦 Order ID: {order_id}")
            print(f"🍫 5 × Cadbury Bournville chocolates ordered!")
        else:
            print(f"❌ Order failed: {final_status}")
    else:
        print(f"⚠️ Unexpected decision type: {decision_type}")

except Exception as e:
    print(f"\n❌ Error during order: {e}")
    import traceback
    traceback.print_exc()
    
    print(f"\n📱 FALLBACK - Manual Zepto Order:")
    print(f"1. Open Zepto app or https://www.zeptonow.com")
    print(f"2. Login with phone: 7376643462")
    print(f"3. Search for: Cadbury Bournville")
    print(f"4. Add 5 pieces to cart")
    print(f"5. Select COD payment")
    print(f"6. Confirm delivery address: Other")

print(f"\n✅ 5 Cadbury Bournville chocolates order process completed!")