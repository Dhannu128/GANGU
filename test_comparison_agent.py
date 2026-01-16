"""
Quick test script for Comparison Agent
"""

import json
from agents.comparison_agent import compare_products, pretty_print_comparison

# Sample search results (from Search Agent)
test_search_result = {
    "search_query": {
        "item": "white chickpeas",
        "quantity": "1 kg",
        "urgency": "normal"
    },
    "platforms_searched": ["Blinkit", "BigBasket", "Zepto"],
    "total_results_found": 3,
    "results": [
        {
            "platform": "Blinkit",
            "item_name": "White Chickpeas (Kabuli Chana)",
            "brand": "Farm Fresh",
            "price": 110.00,
            "currency": "INR",
            "quantity": "1 kg",
            "availability": True,
            "stock_status": "in_stock",
            "delivery_time_hours": 12,
            "rating": 4.6,
            "reviews_count": 2800
        },
        {
            "platform": "BigBasket",
            "item_name": "Kabuli Chana White",
            "brand": "Fresho",
            "price": 95.00,
            "currency": "INR",
            "quantity": "1 kg",
            "availability": True,
            "stock_status": "in_stock",
            "delivery_time_hours": 48,
            "rating": 4.2,
            "reviews_count": 5100
        },
        {
            "platform": "Zepto",
            "item_name": "White Chana Premium",
            "brand": "Nature's Basket",
            "price": 120.00,
            "currency": "INR",
            "quantity": "1 kg",
            "availability": True,
            "stock_status": "low_stock",
            "delivery_time_hours": 10,
            "rating": 4.7,
            "reviews_count": 1200
        }
    ],
    "failed_platforms": [],
    "search_metadata": {
        "timestamp": "2026-01-14T10:30:00Z",
        "search_duration_ms": 1200,
        "synonyms_used": ["white chickpeas", "kabuli chana"]
    }
}

if __name__ == "__main__":
    print("🧪 Testing GANGU Comparison Agent...")
    print("=" * 80)
    
    # Run comparison
    print("\n📥 Input Search Results:")
    print(json.dumps(test_search_result, indent=2)[:300] + "...\n")
    
    print("🔄 Running comparison analysis...")
    comparison = compare_products(test_search_result)
    
    # Display results
    pretty_print_comparison(comparison)
    
    print("\n✅ Test completed successfully!")
