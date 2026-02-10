#!/usr/bin/env python3
"""Test the COD confirmation flow for GANGU"""

import json
from orchestration.gangu_graph import create_gangu_graph

def test_cod_flow():
    print('🚀 Testing GANGU with COD confirmation flow...')
    print('   (This will ask for Yes/No confirmation)')
    
    gangu_graph = create_gangu_graph(checkpointer=None)
    
    result = gangu_graph.invoke({
        'user_input': 'Mango slice order kar do urgent',
        'user_preferences': {}
    })

    print('\n📊 FINAL RESULTS:')
    print(f'Purchase Status: {result.get("purchase_status", "N/A")}')
    print(f'Decision Type: {result.get("decision_type", "N/A")}')
    print(f'Order ID: {result.get("order_id", "N/A")}')
    
    print(f'\n🤖 Final Response:')
    print(result.get("ai_response", "No response"))
    
    return result

if __name__ == "__main__":
    test_cod_flow()