"""
Quick test script for Decision Agent
"""

import json
from agents.decision_agent import make_decision, pretty_print_decision

# Sample comparison results (from Comparison Agent)
test_comparison_result = {
    "comparison_summary": {
        "urgency_level": "normal",
        "total_products_received": 3,
        "products_after_filtering": 3,
        "weights_applied": {
            "price": 0.40,
            "delivery_speed": 0.25,
            "quality": 0.15,
            "availability": 0.10,
            "quantity_match": 0.10
        }
    },
    "ranked_products": [
        {
            "rank": 1,
            "platform": "BigBasket",
            "product_identity": {
                "canonical_name": "White Chickpeas (Kabuli Chana)",
                "brand": "Fresho",
                "category": "grocery"
            },
            "normalized_attributes": {
                "price": 95.00,
                "quantity": 1.0,
                "quantity_unit": "kg",
                "unit_price": 95.00,
                "unit_price_label": "₹95.00/kg",
                "delivery_time_hours": 48.0,
                "delivery_time_label": "2 days",
                "rating": 4.2,
                "reviews_count": 5100,
                "availability": True,
                "stock_status": "in_stock"
            },
            "scores": {
                "final_score": 89.5,
                "breakdown": {
                    "price_score": 100.0,
                    "delivery_speed_score": 50.0,
                    "quality_score": 84.0,
                    "availability_score": 100.0,
                    "quantity_match_score": 100.0
                }
            },
            "flags": ["best_overall", "best_price"],
            "explanation": "Ranked #1 because it offers the lowest unit price (₹95.00/kg) with good availability and decent quality rating (4.2★). Best value for normal urgency purchases.",
            "warnings": ["Slower delivery (2 days) compared to other options"],
            "tradeoffs": ["Cheapest but slowest delivery"]
        },
        {
            "rank": 2,
            "platform": "Blinkit",
            "product_identity": {
                "canonical_name": "White Chickpeas (Kabuli Chana)",
                "brand": "Farm Fresh",
                "category": "grocery"
            },
            "normalized_attributes": {
                "price": 110.00,
                "unit_price": 110.00,
                "unit_price_label": "₹110.00/kg",
                "delivery_time_hours": 12.0,
                "delivery_time_label": "12 hours",
                "rating": 4.6,
                "reviews_count": 2800,
                "availability": True,
                "stock_status": "in_stock"
            },
            "scores": {
                "final_score": 88.2
            },
            "flags": ["best_value"],
            "explanation": "Ranked #2 because it balances price (₹110/kg), speed (12 hours), and quality (4.6★). Good middle-ground option.",
            "warnings": [],
            "tradeoffs": []
        },
        {
            "rank": 3,
            "platform": "Zepto",
            "product_identity": {
                "canonical_name": "White Chickpeas (Kabuli Chana)",
                "brand": "Nature's Basket",
                "category": "grocery"
            },
            "normalized_attributes": {
                "price": 120.00,
                "unit_price": 120.00,
                "unit_price_label": "₹120.00/kg",
                "delivery_time_hours": 10.0,
                "delivery_time_label": "10 hours",
                "rating": 4.7,
                "reviews_count": 1200,
                "availability": True,
                "stock_status": "low_stock"
            },
            "scores": {
                "final_score": 83.8
            },
            "flags": ["fastest_delivery", "best_quality"],
            "explanation": "Ranked #3 because it offers fastest delivery (10 hours) and best quality (4.7★) but at highest price (₹120/kg). Premium option for urgent needs.",
            "warnings": ["Low stock availability", "Highest price"],
            "tradeoffs": ["Fastest but most expensive", "Limited stock availability"]
        }
    ],
    "comparison_insights": {
        "price_range": {
            "min": 95.00,
            "max": 120.00,
            "median": 110.00,
            "unit": "INR"
        },
        "delivery_range": {
            "fastest_hours": 10.0,
            "slowest_hours": 48.0,
            "median_hours": 12.0
        },
        "quality_range": {
            "highest_rating": 4.7,
            "lowest_rating": 4.2,
            "average_rating": 4.5
        },
        "detected_tradeoffs": [
            {
                "type": "price_vs_speed",
                "description": "Cheapest option (₹95/kg) has slowest delivery (2 days) vs fastest option (10 hours) costs ₹120/kg",
                "products_involved": [1, 3]
            },
            {
                "type": "availability_risk",
                "description": "Fastest option (Zepto) has low stock availability",
                "products_involved": [3]
            }
        ],
        "recommendation_confidence": "high"
    },
    "metadata": {
        "timestamp": "2026-01-14T10:30:00Z",
        "comparison_duration_ms": 450,
        "normalization_applied": True,
        "identity_resolution_performed": True
    }
}

if __name__ == "__main__":
    print("🧪 Testing GANGU Decision Agent...")
    print("=" * 80)
    
    # Run decision
    print("\n📥 Input Comparison Results:")
    print(json.dumps(test_comparison_result, indent=2)[:400] + "...\n")
    
    print("🔄 Making final decision...")
    decision = make_decision(test_comparison_result)
    
    # Display results
    pretty_print_decision(decision)
    
    print("\n✅ Test completed successfully!")
    
    # Show key decision points
    print("\n📊 Key Decision Insights:")
    print(f"   Decision Made: {decision.get('decision_summary', {}).get('decision_made')}")
    
    selected = decision.get('selected_option')
    if selected:
        print(f"   Selected Platform: {selected.get('platform', 'N/A')}")
    else:
        print(f"   Selected Platform: None")
    
    print(f"   Confidence: {decision.get('decision_summary', {}).get('confidence_level', 'N/A')}")
    print(f"   Next Action: {decision.get('next_action', {}).get('action', 'N/A')}")
    print(f"   Fallback Available: {decision.get('fallback_strategy', {}).get('has_fallback', False)}")
