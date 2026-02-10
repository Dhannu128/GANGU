#!/usr/bin/env python3
"""
Order Available Beverages through GANGU Pipeline
Test ordering beverages that are confirmed to be in stock
"""
import sys
from pathlib import Path

# Add GANGU directory to Python path
gangu_root = Path(__file__).parent
sys.path.insert(0, str(gangu_root))

def test_gangu_beverage_orders():
    """Test ordering available beverages through full GANGU pipeline"""
    
    # Available beverages from our catalog check
    available_beverages = [
        "adrak chai",
        "latte", 
        "cappuccino",
        "hot chocolate",
        "masala chai",
        "iced americano",
        "cold coffee"
    ]
    
    print("🥤 Testing GANGU Pipeline with Available Beverages")
    print("=" * 60)
    
    try:
        from orchestration.gangu_graph import create_gangu_graph
        
        # Initialize GANGU graph
        gangu_graph = create_gangu_graph(checkpointer=None)
        config = {"configurable": {"thread_id": "beverage_test_001"}}
        
        print(f"✅ GANGU pipeline initialized")
        print(f"📋 Testing {len(available_beverages)} beverages...")
        
        successful_orders = []
        failed_orders = []
        
        for i, beverage in enumerate(available_beverages, 1):
            print(f"\n[{i}/{len(available_beverages)}] 🧪 Testing: {beverage}")
            print("-" * 40)
            
            # Prepare state for beverage order
            test_state = {
                "user_input": f"{beverage} chahiye",
                "user_preferences": {}
            }
            
            try:
                # Run through full GANGU pipeline
                result = gangu_graph.invoke(test_state)
                
                # Check result
                decision_type = result.get("decision_type", "unknown")
                selected_option = result.get("selected_option", {})
                ai_response = result.get("ai_response", "No response")
                
                print(f"   📊 Decision Type: {decision_type}")
                print(f"   🏪 Selected Platform: {selected_option.get('platform', 'None')}")
                print(f"   💰 Price: {selected_option.get('normalized_attributes', {}).get('unit_price_label', 'N/A')}")
                
                if decision_type == "confirm_with_user":
                    print(f"   ✅ Ready for confirmation!")
                    
                    # Simulate "Yes" confirmation and order placement
                    from orchestration.gangu_main import handle_user_confirmation
                    
                    class MockGraph:
                        def invoke(self, state):
                            return state
                    
                    mock_graph = MockGraph()
                    
                    # Simulate user saying "Yes"
                    print(f"   🤖 Simulating user confirmation: Yes")
                    
                    # Mock result for confirmation
                    mock_result = {
                        "user_input": test_state["user_input"],
                        "item_name": beverage,
                        "quantity": "1",
                        "decision_type": "confirm_with_user", 
                        "purchase_status": "pending_confirmation",
                        "selected_option": selected_option
                    }
                    
                    # Process confirmation
                    confirmation_result = handle_user_confirmation(mock_graph, mock_result)
                    
                    if confirmation_result.get("purchase_status") == "success":
                        successful_orders.append({
                            "beverage": beverage,
                            "order_id": confirmation_result.get("order_id"),
                            "platform": selected_option.get("platform")
                        })
                        print(f"   🎉 Order Successful!")
                        print(f"   🆔 Order ID: {confirmation_result.get('order_id', 'N/A')}")
                    else:
                        failed_orders.append({
                            "beverage": beverage,
                            "reason": confirmation_result.get("ai_response", "Unknown error")
                        })
                        print(f"   ❌ Order Failed")
                
                elif decision_type == "auto_buy":
                    successful_orders.append({
                        "beverage": beverage,
                        "platform": selected_option.get("platform"),
                        "auto": True
                    })
                    print(f"   🚀 Auto-buy successful!")
                    
                else:
                    failed_orders.append({
                        "beverage": beverage,
                        "reason": f"Unexpected decision type: {decision_type}"
                    })
                    print(f"   ⚠️ Unexpected result: {decision_type}")
                
            except Exception as e:
                failed_orders.append({
                    "beverage": beverage,
                    "reason": str(e)
                })
                print(f"   ❌ Error: {str(e)[:50]}...")
        
        # Final Results
        print("\n" + "=" * 60)
        print("📊 GANGU BEVERAGE ORDERING RESULTS")
        print("=" * 60)
        
        if successful_orders:
            print(f"\n✅ SUCCESSFUL ORDERS ({len(successful_orders)}):")
            for i, order in enumerate(successful_orders, 1):
                print(f"   {i}. {order['beverage']}")
                print(f"      Platform: {order.get('platform', 'N/A')}")
                if order.get('order_id'):
                    print(f"      Order ID: {order['order_id']}")
                if order.get('auto'):
                    print(f"      Type: Auto-buy")
                print()
        
        if failed_orders:
            print(f"\n❌ FAILED ORDERS ({len(failed_orders)}):")
            for i, order in enumerate(failed_orders, 1):
                print(f"   {i}. {order['beverage']}")
                print(f"      Reason: {order['reason'][:60]}...")
                print()
        
        print(f"📈 Summary:")
        print(f"   • Successful: {len(successful_orders)}/{len(available_beverages)}")
        print(f"   • Failed: {len(failed_orders)}/{len(available_beverages)}")
        print(f"   • Success Rate: {(len(successful_orders)/len(available_beverages)*100):.1f}%")
        
        return successful_orders, failed_orders
        
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        return [], []

if __name__ == "__main__":
    print("""
╔════════════════════════════════════════════════════════════════════╗
║               🥤 GANGU BEVERAGE ORDERING TEST                      ║
║               ─────────────────────────────────────                ║
║   Testing full pipeline with confirmed available beverages        ║
║   Will simulate Yes/No confirmation and place real orders         ║
╚════════════════════════════════════════════════════════════════════╝
""")
    
    successful_orders, failed_orders = test_gangu_beverage_orders()
    
    if successful_orders:
        print(f"\n🎉 SUCCESS! {len(successful_orders)} beverages ordered through GANGU pipeline!")
        print(f"💳 All orders use Cash on Delivery (COD)")
    else:
        print(f"\n😔 No successful orders. Need to debug the pipeline.")