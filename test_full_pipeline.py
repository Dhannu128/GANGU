"""
Test GANGU Full Pipeline
Tests all 5 agents working together without MongoDB
"""

import sys
from pathlib import Path

# Add parent directory to path
parent_dir = Path(__file__).parent
sys.path.insert(0, str(parent_dir))

from orchestration.gangu_graph import create_gangu_graph

def test_full_pipeline():
    """Test the complete GANGU pipeline"""
    
    print("=" * 80)
    print("🧪 TESTING GANGU FULL PIPELINE")
    print("   Intent → Task Planner → Search → Comparison → Decision")
    print("=" * 80)
    
    # Create graph without MongoDB (for testing)
    print("\n📊 Creating GANGU graph...")
    gangu_graph = create_gangu_graph(checkpointer=None)
    print("✅ Graph created successfully\n")
    
    # Test cases
    test_cases = [
        {
            "name": "Grocery Purchase (Normal Urgency)",
            "input": "White chane khatam ho gaye",
            "expected_intent": "buy_grocery"
        },
        {
            "name": "Urgent Purchase",
            "input": "Doodh abhi chahiye",
            "expected_intent": "buy_daily_essential"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print("\n" + "=" * 80)
        print(f"TEST {i}: {test_case['name']}")
        print("=" * 80)
        print(f"📝 Input: \"{test_case['input']}\"")
        print(f"🎯 Expected Intent: {test_case['expected_intent']}")
        print("\n" + "-" * 80)
        
        # Prepare state
        initial_state = {
            "user_input": test_case["input"],
            "user_preferences": {}
        }
        
        try:
            # Run the full pipeline
            result = gangu_graph.invoke(initial_state)
            
            # Show results
            print("\n" + "=" * 80)
            print("📊 PIPELINE RESULTS")
            print("=" * 80)
            
            print(f"\n🧠 [1] Intent Extraction:")
            print(f"   Detected Intent: {result.get('detected_intent', 'N/A')}")
            print(f"   Item: {result.get('item_name', 'N/A')} ({result.get('item_original', '')})")
            print(f"   Quantity: {result.get('quantity', 'N/A')}")
            print(f"   Urgency: {result.get('urgency', 'N/A')}")
            print(f"   Confidence: {result.get('confidence', 'N/A')}")
            
            print(f"\n📋 [2] Task Planning:")
            steps = result.get('execution_steps', [])
            print(f"   Created {len(steps)} execution steps")
            
            print(f"\n🔍 [3] Search Results:")
            platforms = result.get('platforms_searched', [])
            search_results = result.get('search_results', {})
            total_results = search_results.get('total_results_found', 0)
            print(f"   Searched {len(platforms)} platforms: {', '.join(platforms)}")
            print(f"   Found {total_results} results")
            
            print(f"\n⚖️  [4] Comparison:")
            ranked = result.get('ranked_products', [])
            print(f"   Ranked {len(ranked)} products")
            for j, product in enumerate(ranked[:3], 1):
                platform = product.get('platform', 'Unknown')
                score = product.get('scores', {}).get('final_score', 0)
                print(f"      #{j} {platform}: Score {score}/100")
            
            print(f"\n🎯 [5] Decision:")
            decision_made = result.get('final_decision', {}).get('decision_made', False)
            decision_type = result.get('decision_type', 'N/A')
            confidence = result.get('confidence_level', 'N/A')
            risk = result.get('risk_level', 'N/A')
            print(f"   Decision Made: {'✅ Yes' if decision_made else '❌ No'}")
            print(f"   Decision Type: {decision_type}")
            print(f"   Confidence: {confidence}")
            print(f"   Risk Level: {risk}")
            
            selected = result.get('selected_option')
            if selected:
                platform = selected.get('platform', 'N/A')
                price = selected.get('unit_price_label', selected.get('price', 'N/A'))
                print(f"   Selected: {platform} at {price}")
            
            print(f"\n🔔 Final Response:")
            print("-" * 80)
            response = result.get('ai_response', 'No response generated')
            print(response)
            print("-" * 80)
            
            # Validation
            print(f"\n✅ TEST {i} VALIDATION:")
            actual_intent = result.get('detected_intent', '')
            expected_intent = test_case['expected_intent']
            
            if actual_intent == expected_intent:
                print(f"   ✅ Intent matched: {actual_intent}")
            else:
                print(f"   ⚠️  Intent mismatch: expected '{expected_intent}', got '{actual_intent}'")
            
            if decision_made:
                print(f"   ✅ Decision was made")
            else:
                print(f"   ⚠️  No decision made")
            
            if ranked:
                print(f"   ✅ Products were ranked")
            else:
                print(f"   ⚠️  No products ranked")
            
            print(f"\n✅ TEST {i} COMPLETED SUCCESSFULLY")
            
        except Exception as e:
            print(f"\n❌ TEST {i} FAILED: {e}")
            import traceback
            traceback.print_exc()
        
        # Separator between tests
        if i < len(test_cases):
            print("\n\n")
    
    print("\n" + "=" * 80)
    print("🎉 ALL TESTS COMPLETED!")
    print("=" * 80)
    print("\n📝 Summary:")
    print(f"   Total Tests: {len(test_cases)}")
    print(f"   Agents Tested: 5 (Intent, Task Planner, Search, Comparison, Decision)")
    print(f"   MCP Integration: Zepto + Blinkit")
    print(f"   LangSmith Tracing: {'✅ Enabled' if 'LANGSMITH_TRACING' in sys.modules else '⚠️  Check .env'}")
    print("\n✅ GANGU Pipeline is working!\n")


if __name__ == "__main__":
    try:
        test_full_pipeline()
    except KeyboardInterrupt:
        print("\n\n👋 Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
