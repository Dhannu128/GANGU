#!/usr/bin/env python3
"""Place urgent order for 1 Cadbury Bournville (real order)"""

print("🍫 URGENT: Ordering 1 Cadbury Bournville Chocolate")
print("=" * 60)
print("📱 Phone: 7376643462")
print("🏠 Address: Other")
print("💳 Payment: Cash on Delivery (COD)")
print("=" * 60)

user_input = "1 cadbury bournville order kar do urgent"
print(f"👤 User: {user_input}")

from orchestration.gangu_graph import create_gangu_graph

try:
    print("\n🚀 Starting GANGU pipeline...")
    gangu_graph = create_gangu_graph(checkpointer=None)

    result = gangu_graph.invoke({
        "user_input": user_input,
        "user_preferences": {
            "auto_confirm_urgent": True,
            "preferred_payment": "cod"
        }
    })

    print("\n📊 ORDER PROCESSING RESULTS:")
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

    if decision_type == 'auto_buy':
        order_status = result.get('purchase_status', 'unknown')
        print(f"\n💳 PURCHASE STATUS: {order_status}")
    elif decision_type == 'confirm_with_user':
        print("\n🤖 Order requires confirmation - Auto-confirming for urgent request...")
        from orchestration.gangu_main import handle_user_confirmation
        confirmed_result = handle_user_confirmation(gangu_graph, result)
        final_status = confirmed_result.get('purchase_status', 'unknown')
        print(f"💳 Final Status: {final_status}")
    else:
        print(f"⚠️ Unexpected decision type: {decision_type}")

except Exception as e:
    print(f"\n❌ Error during order: {e}")
    import traceback
    traceback.print_exc()

print("\n✅ 1 Cadbury Bournville chocolate order process completed!")
