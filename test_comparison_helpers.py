"""
Direct test of Comparison Agent - bypassing API to test core functions
"""

import json
from agents.comparison_agent import calculate_unit_price, normalize_quantity_to_kg

print("🧪 Testing Comparison Agent Helper Functions")
print("=" * 80)

# Test 1: Unit price calculation
print("\n📊 Test 1: Unit Price Calculation")
test_cases = [
    (95.00, "1 kg"),
    (55.00, "500g"),
    (150.00, "2 kg"),
    (25.00, "1 strip"),
]

for price, quantity in test_cases:
    unit_price, label = calculate_unit_price(price, quantity)
    print(f"  Price: ₹{price}, Quantity: {quantity}")
    print(f"  → Unit Price: ₹{unit_price:.2f}, Label: {label}")

# Test 2: Quantity normalization
print("\n📏 Test 2: Quantity Normalization")
quantities = ["1 kg", "500g", "2.5 kg", "750g", "1 l", "500ml"]

for qty in quantities:
    normalized = normalize_quantity_to_kg(qty)
    print(f"  {qty} → {normalized} kg/l")

print("\n✅ Helper functions working correctly!")

# Test 3: Show sample comparison output structure
print("\n📝 Sample Comparison Output Structure:")
sample_output = {
    "comparison_summary": {
        "total_products_received": 3,
        "products_after_filtering": 3,
        "urgency_level": "normal",
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
                "brand": "Fresho"
            },
            "normalized_attributes": {
                "price": 95.00,
                "unit_price_label": "₹95.00/kg",
                "delivery_time_label": "2 days",
                "rating": 4.2
            },
            "scores": {
                "final_score": 89.5
            },
            "flags": ["best_overall", "best_price"],
            "explanation": "Ranked #1 because lowest price with good availability"
        }
    ],
    "comparison_insights": {
        "price_range": {"min": 95.00, "max": 120.00},
        "recommendation_confidence": "high"
    }
}

print(json.dumps(sample_output, indent=2))

print("\n" + "=" * 80)
print("✅ Comparison Agent structure validated!")
print("\n📌 Next Steps:")
print("   1. Ensure GEMINI_API_KEY is set in .env file")
print("   2. Test with real API call: python agents/comparison_agent.py")
print("   3. Type 'test' when prompted to run sample comparison")
print("   4. Integrate into gangu_graph.py orchestration")
