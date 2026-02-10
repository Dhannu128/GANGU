#!/usr/bin/env python3
"""
Test GANGU Pipeline with Confirmed Available Products
Test the complete pipeline with products that are guaranteed to be in stock
"""
import asyncio
import sys
from pathlib import Path

gangu_root = Path(__file__).parent
sys.path.append(str(gangu_root))

from orchestration.gangu_graph import create_gangu_graph
from orchestration.gangu_main import handle_user_confirmation
from mcp_clients.zepto_mcp_client import ZeptoMCPClient

async def test_single_query(gangu_graph, query, expected_product):
    """Test a single query through the GANGU pipeline"""
    
    try:
        # Prepare state
        initial_state = {
            "user_input": query,
            "user_preferences": {}
        }
        
        print(f"🔄 Processing: '{query}'")
        print(f"   Expected product: {expected_product}")
        
        # Run through pipeline
        result = gangu_graph.invoke(initial_state)
        
        # Check if confirmation is needed
        decision_type = result.get("decision_type", "")
        purchase_status = result.get("purchase_status", "")
        
        if decision_type == "confirm_with_user" and purchase_status == "pending_confirmation":
            print(f"   ⏳ Confirmation needed, auto-confirming with 'yes'")
            
            # Simulate user saying "yes" by modifying the confirmation handler
            # We'll add auto-confirmation logic
            original_input = __builtins__.get('input', input)
            
            def auto_yes(prompt):
                print(f"   🤖 Auto-responding: YES")
                return "yes"
            
            __builtins__['input'] = auto_yes
            
            try:
                result = handle_user_confirmation(gangu_graph, result)
            finally:
                __builtins__['input'] = original_input
        
        # Check results
        success = result.get("purchase_status", "") == "success"
        ai_response = result.get("ai_response", "")
        
        if success:
            print(f"   ✅ SUCCESS - Order processed!")
            print(f"   📝 Response: {ai_response[:100]}...")
            return True
        else:
            print(f"   ❌ FAILED - Status: {result.get('purchase_status', 'unknown')}")
            print(f"   📝 Response: {ai_response[:100]}...")
            return False
            
    except Exception as e:
        print(f"   ❌ ERROR - Exception: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_pipeline_with_available_products():
    """Test complete GANGU pipeline with products confirmed to be available"""
    
    # Create the GANGU graph
    print("📊 Initializing GANGU pipeline...")
    gangu_graph = create_gangu_graph(checkpointer=None)
    print("✅ GANGU pipeline initialized")
    
    # Test products from different categories (all confirmed available)
    test_scenarios = [
        # Beverages
        {
            "query": "I want to order tea from Zepto",
            "expected_product": "tea",
            "category": "Beverages"
        },
        {
            "query": "Order coffee for me on Zepto",
            "expected_product": "coffee", 
            "category": "Beverages"
        },
        
        # Vegetables
        {
            "query": "I need potatoes from Zepto",
            "expected_product": "potato",
            "category": "Vegetables"
        },
        
        # Dairy
        {
            "query": "Order milk from Zepto",
            "expected_product": "milk",
            "category": "Dairy"
        },
        
        # Staples
        {
            "query": "I want rice from Zepto",
            "expected_product": "rice",
            "category": "Staples"
        }
    ]
    
    print("\n🧪 Testing GANGU Pipeline with Confirmed Available Products")
    print("=" * 60)
    
    success_count = 0
    total_tests = len(test_scenarios)
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n🔍 Test {i}/{total_tests}: {scenario['category']}")
        print("-" * 40)
        
        try:
            # Run the test
            success = await test_single_query(
                gangu_graph, 
                scenario['query'], 
                scenario['expected_product']
            )
            
            if success:
                success_count += 1
                
        except Exception as e:
            print(f"   ❌ TEST ERROR - Exception: {e}")
            
        # Short delay between tests
        print(f"   ⏳ Waiting 3 seconds before next test...")
        await asyncio.sleep(3)
    
    print(f"\n🎯 TEST SUMMARY")
    print("=" * 40)
    print(f"Total Tests: {total_tests}")
    print(f"Successful: {success_count}")
    print(f"Failed: {total_tests - success_count}")
    print(f"Success Rate: {(success_count/total_tests)*100:.1f}%")
    
    if success_count == total_tests:
        print("🎉 ALL TESTS PASSED! Pipeline working with available products!")
    elif success_count > 0:
        print(f"⚠️ PARTIAL SUCCESS: {success_count}/{total_tests} tests passed")
    else:
        print("❌ ALL TESTS FAILED - Need to investigate pipeline issues")

async def quick_availability_check():
    """Quick check that our test products are still available"""
    print("🔍 Quick availability check before pipeline test...")
    
    test_products = ["tea", "coffee", "potato", "milk", "rice"]
    server_script_path = gangu_root / "zepto-cafe-mcp" / "zepto_mcp_server.py"
    zepto_client = ZeptoMCPClient(str(server_script_path))
    
    available_count = 0
    
    try:
        await zepto_client.connect()
        
        for product in test_products:
            try:
                result = await zepto_client.start_zepto_order(product)
                if isinstance(result, dict) and result.get('success', False):
                    available_count += 1
                    print(f"   ✅ {product} - Available")
                else:
                    print(f"   ❌ {product} - Not available")
            except Exception:
                print(f"   ❌ {product} - Error checking")
                
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False
    finally:
        await zepto_client.disconnect()
    
    if available_count >= 3:
        print(f"✅ {available_count}/{len(test_products)} products available - Proceeding with pipeline test")
        return True
    else:
        print(f"⚠️ Only {available_count}/{len(test_products)} products available - May have issues")
        return False

if __name__ == "__main__":
    print("🚀 Starting GANGU Pipeline Test with Available Products")
    
    async def main():
        # First check if products are still available
        if await quick_availability_check():
            print("\n" + "="*60)
            await test_pipeline_with_available_products()
        else:
            print("❌ Too many products unavailable - skipping pipeline test")
    
    asyncio.run(main())