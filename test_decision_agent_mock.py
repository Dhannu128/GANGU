"""
Mock test for Decision Agent (without API calls)
"""

import json
from agents.decision_agent import pretty_print_decision

# Sample decision output (what the agent should produce)
mock_decision = {
    "decision_summary": {
        "decision_made": True,
        "decision_type": "auto_buy",
        "confidence_level": "very_high",
        "risk_level": "low",
        "urgency_acknowledged": "normal"
    },
    "selected_option": {
        "rank": 1,
        "platform": "BigBasket",
        "product_name": "White Chickpeas (Kabuli Chana)",
        "brand": "Fresho",
        "final_score": 89.5,
        "price": 95.00,
        "unit_price": 95.00,
        "unit_price_label": "₹95.00/kg",
        "delivery_time_hours": 48.0,
        "delivery_time_label": "2 days",
        "rating": 4.2,
        "reviews_count": 5100,
        "availability": True,
        "stock_status": "in_stock"
    },
    "decision_reasoning": {
        "primary_reason": "Clear best value option with lowest unit price (₹95/kg) and good availability",
        "supporting_factors": [
            "Lowest price among all options",
            "Strong availability with in_stock status",
            "Good quality rating (4.2★) with high review count (5100)",
            "Score gap of 1.3 points indicates clear winner",
            "Normal urgency allows prioritizing price over speed"
        ],
        "tradeoffs_considered": [
            {
                "tradeoff": "price_vs_speed",
                "resolution": "Prioritized price since urgency is normal",
                "reasoning": "User can wait 2 days to save ₹15-25 per kg"
            }
        ],
        "risks_identified": [],
        "policy_applied": [
            "Policy 1: Selected option is in stock ✅",
            "Policy 2: High confidence score (89.5 > 60) ✅",
            "Policy 3: Clear winner with score gap 1.3 points ✅",
            "Policy 5: Low risk assessment → auto-buy approved ✅"
        ]
    },
    "explanation_for_user": {
        "simple_message": "BigBasket par sabse sasta mila hai - ₹95 per kg. 2 din mein aa jayega. Quality bhi theek hai (4.2★).",
        "why_this_option": "This option saves you ₹15-25 per kg compared to faster options. Since urgency is normal, waiting 2 days for better price makes sense.",
        "what_user_gets": "1 kg White Chickpeas from BigBasket at ₹95, delivered in 2 days, good quality (4.2★, 5100 reviews)"
    },
    "fallback_strategy": {
        "has_fallback": True,
        "primary_choice": {
            "platform": "BigBasket",
            "reason": "Best price and availability"
        },
        "secondary_option": {
            "platform": "Blinkit",
            "reason": "If BigBasket out of stock, Blinkit offers good balance (₹110/kg, 12 hours)",
            "score": 88.2
        },
        "tertiary_option": {
            "platform": "Zepto",
            "reason": "Last resort if first two fail, fastest delivery but highest price and low stock",
            "score": 83.8,
            "warning": "Low stock risk"
        }
    },
    "next_action": {
        "action": "purchase",
        "target_agent": "purchase_agent",
        "action_parameters": {
            "platform": "BigBasket",
            "product_id": "fresho-white-chickpeas-1kg",
            "quantity": 1,
            "max_price": 105.00,
            "delivery_preference": "standard"
        },
        "user_confirmation_required": False,
        "estimated_action_time": "5 minutes"
    },
    "metadata": {
        "timestamp": "2026-01-14T10:30:15Z",
        "decision_duration_ms": 385,
        "model_used": "gemini-2.5-flash",
        "policies_triggered": ["policy_1", "policy_2", "policy_3", "policy_5"]
    }
}

if __name__ == "__main__":
    print("Testing GANGU Decision Agent (Mock Mode)")
    print("=" * 80)
    print("\nThis demonstrates what the Decision Agent should output")
    print("    when given ranked products from the Comparison Agent.")
    print("\n" + "=" * 80)
    
    # Display the mock decision
    pretty_print_decision(mock_decision)
    
    print("\n" + "=" * 80)
    print("Test Complete!")
    print("\nKey Features Demonstrated:")
    print("   - Clear decision (auto_buy)")
    print("   - High confidence (very_high)")
    print("   - Policy compliance (4 policies applied)")
    print("   - Tradeoff resolution (price vs speed)")
    print("   - Risk assessment (low risk)")
    print("   - User explanation (Hindi/Hinglish)")
    print("   - Fallback strategy (3-tier backup)")
    print("   - Next action routing (purchase_agent)")
    
    print("\nDecision Structure:")
    print(json.dumps(mock_decision, indent=2, ensure_ascii=False)[:800] + "...\n")
