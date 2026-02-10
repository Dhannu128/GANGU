#!/usr/bin/env python3
"""Test the urgent fix for GANGU"""

import json
from orchestration.gangu_graph import create_gangu_graph

def test_urgent_fix():
    print('🚀 Testing GANGU with urgent multiple items...')
    gangu_graph = create_gangu_graph(checkpointer=None)
    
    result = gangu_graph.invoke({
        'user_input': 'Mango slice order kar do and lays bhi urgent',
        'user_preferences': {}
    })

    print('\n📊 RESULTS:')
    print(f'Intent detected: {result.get("detected_intent", "N/A")}')
    print(f'Item extracted: {result.get("item_name", "N/A")}')
    print(f'Urgency level: {result.get("urgency", "N/A")}')
    print(f'Decision type: {result.get("decision_type", "N/A")}')
    
    if result.get('ranked_products'):
        print(f'\n🏆 Top 3 ranked options:')
        for i, prod in enumerate(result['ranked_products'][:3], 1):
            platform = prod.get('platform', 'Unknown')
            score = prod.get('scores', {}).get('final_score', 0)
            delivery = prod.get('delivery_time_label', 'Unknown')
            price = prod.get('unit_price_label', 'Unknown')
            print(f'  {i}. {platform}: Score {score}/100 | {price} | {delivery}')

    selected_option = result.get('selected_option', {})
    if selected_option:
        print(f'\n✅ SELECTED: {selected_option.get("platform", "Unknown")}')
        print(f'   Price: {selected_option.get("unit_price_label", "Unknown")}')
        print(f'   Delivery: {selected_option.get("delivery_time_label", "Unknown")}')

    print(f'\n🤖 AI Response:')
    print(result.get("ai_response", "No response")[:400])
    
    return result

if __name__ == "__main__":
    test_urgent_fix()