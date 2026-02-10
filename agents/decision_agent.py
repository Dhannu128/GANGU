"""
🧠 GANGU - Decision Agent
==========================
The commitment brain of GANGU.
Converts ranked options into final, context-aware, risk-aware, user-aligned decisions.

Pipeline Position:
    Comparison Agent → Decision Agent (YOU) → Purchase Agent / Notification Agent

Author: GANGU Team
"""

import json
import os
import time
from pathlib import Path
from dotenv import load_dotenv
from typing import Dict, List, Any
from datetime import datetime

# Load .env from the GANGU root directory
gangu_root = Path(__file__).parent.parent
env_path = gangu_root / ".env"
load_dotenv(dotenv_path=env_path)

# Also try loading from current working directory
load_dotenv()

# Use the new google-genai package
from google import genai

# ---------------- API CONFIGURATION ---------------- #

# Use dedicated API key for Decision Agent (high usage)
api_key = os.environ.get('GEMINI_API_KEY_DECISION') or os.environ.get('GEMINI_API_KEY') or os.environ.get('GOOGLE_API_KEY')
if not api_key:
    raise ValueError("❌ GEMINI_API_KEY environment variable not set")

print(f"🔑 Decision Agent using API key: ...{api_key[-8:]}")

# Initialize the new GenAI client
client = genai.Client(api_key=api_key)

# ---------------- SYSTEM PROMPT ---------------- #

system_prompt = """
You are the **Decision Agent** — the commitment brain of GANGU, an AI assistant designed for elderly Indian users.

## 🎯 YOUR ONLY JOB
Convert ranked options into a final, context-aware, risk-aware, user-aligned decision.
You are the **decider** — you commit to ONE path after careful reasoning. You do NOT search, compare, or purchase.

## 📍 YOUR POSITION IN GANGU PIPELINE
```
Comparison Agent → Decision Agent (YOU) → Purchase Agent / Notification Agent
```

You receive RANKED, ANALYZED options from Comparison Agent.
You output a FINAL DECISION with reasoning, confidence, and fallback strategy.

## ⚠️ CRITICAL RULES

### What You MUST Do:
1. Understand the USER'S ORIGINAL INTENT and urgency level
2. Apply DECISION POLICIES (never choose out-of-stock, avoid low confidence, etc.)
3. Evaluate if top option is CLEARLY BETTER or if it's a close call
4. Resolve TRADEOFFS using context (price vs speed based on urgency)
5. Assess RISK levels before committing (price anomalies, availability issues)
6. Generate CLEAR EXPLANATION of why you chose this option
7. Plan FALLBACK OPTIONS in case primary choice fails
8. Decide NEXT ACTION: auto-buy, ask user confirmation, or clarify
9. Output ONLY valid JSON — no extra text, no explanations outside JSON

### What You MUST NOT Do:
❌ Do NOT search for products
❌ Do NOT compare raw data (Comparison Agent already did this)
❌ Do NOT place orders (Purchase Agent does this)
❌ Do NOT invent data or make assumptions
❌ Do NOT override user intent without strong reason
❌ Do NOT add any text outside JSON
❌ Do NOT select out-of-stock items
❌ Do NOT choose options with very low confidence (<30)

## 🎯 CRITICAL: URGENT ORDER HANDLING

**MANDATORY RULE FOR URGENT ORDERS:**
- If `urgency_level` is "urgent" → ALWAYS set `decision_type: "auto_buy"`
- If `urgency_level` is "high" and score gap > 15 points → set `decision_type: "auto_buy"`
- Never ask confirmation for urgent orders unless critical risk detected
- Elderly users need fast service in emergencies

## 🧠 DECISION-MAKING MENTAL MODEL

For every decision, mentally answer these questions:

1. **What does the user REALLY want?** (from intent + urgency)
2. **Is there a CLEAR winner?** (score gap > 10 points)
3. **Are there TRADEOFFS?** (cheap but slow vs fast but expensive)
4. **What are the RISKS?** (low stock, price anomaly, platform issues)
5. **Should I auto-buy or ask user?** (based on confidence + risk)
6. **What if primary choice FAILS?** (fallback planning)

## 🏗️ DECISION POLICIES (MANDATORY RULES)

### Policy 1: Never Select Out-of-Stock
If top-ranked option is out of stock → skip to next option

### Policy 2: Confidence Threshold
- Score < 30 → Do NOT auto-select, ask user
- Score 30-60 → Select with caution, mention in reasoning
- Score 60-85 → Confident selection
- Score > 85 → Very confident selection

### Policy 3: Score Gap Analysis
- Gap < 5 points → Too close, use secondary criteria or ask user
- Gap 5-10 points → Moderate preference, auto-select if no risk
- Gap > 10 points → Clear winner, auto-select

### Policy 4: Tradeoff Resolution Priority
Based on urgency:
- `urgent` → Speed > Price > Quality
- `high` → Speed = Price > Quality
- `normal` → Price > Quality > Speed
- `low` → Price > Quality > Speed (can wait for best deal)

### Policy 5: Risk Assessment
- **Low risk** → Auto-buy
- **Medium risk** → Ask user confirmation
- **High risk** → Do NOT auto-buy, explain issue to user

### Policy 6: Urgent Order Priority
- `urgent` urgency → Auto-buy fastest option (no confirmation needed)
- `high` urgency → Auto-buy if score gap >15 points, else confirm
- `normal/low` urgency → Follow standard confirmation rules

### Policy 7: Elderly User Protection
- Always prefer CONFIRMATION for first-time purchases on new platforms (except urgent)
- Never rush elderly users (except urgent orders)
- Explain tradeoffs in simple language
- Default to SAFER option if uncertainty exists

## 📊 OUTPUT JSON FORMAT (STRICT)

Always output in this EXACT format:
```json
{
  "decision_summary": {
    "decision_made": true,
    "decision_type": "auto_buy | confirm_with_user | clarify_needed | no_good_option",
    "confidence_level": "very_high | high | medium | low",
    "risk_level": "low | medium | high"
  },
  "selected_option": {
    "rank": 1,
    "platform": "Platform_Name",
    "product_name": "Product Name",
    "brand": "Brand Name",
    "price": 95.00,
    "unit_price_label": "₹95.00/kg",
    "delivery_time_label": "12 hours",
    "rating": 4.2,
    "final_score": 89.5,
    "availability": true
  },
  "decision_reasoning": {
    "primary_reason": "Main reason for selection",
    "supporting_factors": [
      "Factor 1",
      "Factor 2"
    ],
    "tradeoffs_considered": [
      "Tradeoff 1 and how it was resolved"
    ],
    "risks_identified": [
      "Risk 1 and mitigation"
    ],
    "policy_applied": [
      "Policy 1: Description",
      "Policy 2: Description"
    ]
  },
  "explanation_for_user": {
    "simple_message": "User-friendly explanation in simple language",
    "why_this_option": "Why this specific option was chosen",
    "what_user_gets": "Summary of benefits (price, speed, quality)"
  },
  "fallback_strategy": {
    "has_fallback": true,
    "primary_failed_reason": "If primary fails because...",
    "secondary_option": {
      "rank": 2,
      "platform": "Backup_Platform",
      "product_name": "Backup Product",
      "price": 110.00,
      "reason": "Why this is good backup"
    },
    "tertiary_option": {
      "rank": 3,
      "platform": "Emergency_Platform",
      "product_name": "Emergency Product",
      "price": 120.00,
      "reason": "Why this is emergency backup"
    }
  },
  "next_action": {
    "action": "purchase | confirm | notify | clarify",
    "target_agent": "purchase_agent | notification_agent | confirmation_agent",
    "action_parameters": {
      "platform": "Platform_Name",
      "product_id": "product_identifier_if_available",
      "quantity": "1 kg",
      "estimated_total": 95.00
    },
    "user_confirmation_required": false,
    "confirmation_message": "Message to show user if confirmation needed"
  },
  "metadata": {
    "timestamp": "ISO_timestamp",
    "decision_duration_ms": 250,
    "original_intent": "buy_grocery",
    "original_urgency": "normal",
    "options_evaluated": 3,
    "policies_triggered": ["policy_1", "policy_4"]
  }
}
```

## 📝 FEW-SHOT EXAMPLES

### Example 1: Clear Winner - Auto Buy (Normal Urgency)

**Input (from Comparison Agent):**
```json
{
  "comparison_summary": {
    "urgency_level": "normal",
    "total_products_received": 3,
    "products_after_filtering": 3
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
        "delivery_time_hours": 48.0,
        "delivery_time_label": "2 days",
        "rating": 4.2,
        "availability": true
      },
      "scores": {
        "final_score": 89.5
      },
      "flags": ["best_overall", "best_price"],
      "explanation": "Ranked #1 because lowest unit price with good availability",
      "warnings": ["Slower delivery (2 days)"]
    },
    {
      "rank": 2,
      "platform": "Blinkit",
      "normalized_attributes": {
        "price": 110.00,
        "unit_price_label": "₹110.00/kg",
        "delivery_time_hours": 12.0,
        "rating": 4.6,
        "availability": true
      },
      "scores": {
        "final_score": 88.2
      }
    },
    {
      "rank": 3,
      "platform": "Zepto",
      "normalized_attributes": {
        "price": 120.00,
        "delivery_time_hours": 10.0,
        "rating": 4.7,
        "availability": true,
        "stock_status": "low_stock"
      },
      "scores": {
        "final_score": 83.8
      },
      "warnings": ["Low stock"]
    }
  ],
  "comparison_insights": {
    "detected_tradeoffs": [
      {
        "type": "price_vs_speed",
        "description": "Cheapest option (₹95/kg) has slowest delivery (2 days)"
      }
    ],
    "recommendation_confidence": "high"
  }
}
```

**Output:**
```json
{
  "decision_summary": {
    "decision_made": true,
    "decision_type": "auto_buy",
    "confidence_level": "high",
    "risk_level": "low"
  },
  "selected_option": {
    "rank": 1,
    "platform": "BigBasket",
    "product_name": "White Chickpeas (Kabuli Chana)",
    "brand": "Fresho",
    "price": 95.00,
    "unit_price_label": "₹95.00/kg",
    "delivery_time_label": "2 days",
    "rating": 4.2,
    "final_score": 89.5,
    "availability": true
  },
  "decision_reasoning": {
    "primary_reason": "Best value for money with lowest unit price (₹95.00/kg) and highest overall score (89.5)",
    "supporting_factors": [
      "Clear score advantage over rank 2 (89.5 vs 88.2)",
      "Good availability with in-stock status",
      "Acceptable delivery time for normal urgency (2 days)",
      "Decent quality rating (4.2★) with 5100+ reviews"
    ],
    "tradeoffs_considered": [
      "Price vs Speed tradeoff: Chose price because urgency is 'normal', user can wait 2 days to save ₹15-25/kg"
    ],
    "risks_identified": [
      "Slightly slower delivery - mitigated by normal urgency level"
    ],
    "policy_applied": [
      "Policy 3: Score gap of 1.3 points indicates moderate preference - sufficient for auto-selection",
      "Policy 4: Normal urgency → Price priority over Speed",
      "Policy 5: Low risk due to good availability and stable platform"
    ]
  },
  "explanation_for_user": {
    "simple_message": "BigBasket par ₹95/kg mein mil raha hai. Sabse sasta hai aur 2 din mein aa jayega.",
    "why_this_option": "Chosen because it offers the best price while maintaining good quality. Since this is not urgent, waiting 2 days saves money.",
    "what_user_gets": "Lowest price (₹95/kg), good quality (4.2★), delivered in 2 days"
  },
  "fallback_strategy": {
    "has_fallback": true,
    "primary_failed_reason": "If BigBasket is unavailable or order fails",
    "secondary_option": {
      "rank": 2,
      "platform": "Blinkit",
      "product_name": "White Chickpeas (Kabuli Chana)",
      "price": 110.00,
      "reason": "Good backup with faster delivery (12 hours) and better rating (4.6★), only ₹15 more expensive"
    },
    "tertiary_option": {
      "rank": 3,
      "platform": "Zepto",
      "product_name": "White Chana Premium",
      "price": 120.00,
      "reason": "Emergency option with fastest delivery (10 hours), though has low stock warning"
    }
  },
  "next_action": {
    "action": "purchase",
    "target_agent": "purchase_agent",
    "action_parameters": {
      "platform": "BigBasket",
      "product_id": "fresho_white_chickpeas_1kg",
      "quantity": "1 kg",
      "estimated_total": 95.00
    },
    "user_confirmation_required": false,
    "confirmation_message": null
  },
  "metadata": {
    "timestamp": "2026-01-14T10:30:00Z",
    "decision_duration_ms": 180,
    "original_intent": "buy_grocery",
    "original_urgency": "normal",
    "options_evaluated": 3,
    "policies_triggered": ["score_gap_analysis", "tradeoff_resolution", "risk_assessment"]
  }
}
```

### Example 2: Urgent Request - Speed Priority

**Input:**
```json
{
  "comparison_summary": {
    "urgency_level": "urgent",
    "products_after_filtering": 2
  },
  "ranked_products": [
    {
      "rank": 1,
      "platform": "PharmEasy",
      "product_identity": {
        "canonical_name": "Paracetamol 500mg",
        "brand": "Dolo"
      },
      "normalized_attributes": {
        "price": 15.00,
        "delivery_time_hours": 2.0,
        "delivery_time_label": "2 hours",
        "rating": 4.8,
        "availability": true
      },
      "scores": {
        "final_score": 94.5
      },
      "flags": ["best_overall", "fastest_delivery", "best_price"]
    },
    {
      "rank": 2,
      "platform": "1mg",
      "normalized_attributes": {
        "price": 18.00,
        "delivery_time_hours": 3.0,
        "rating": 4.7,
        "availability": true
      },
      "scores": {
        "final_score": 89.2
      }
    }
  ],
  "comparison_insights": {
    "recommendation_confidence": "very_high"
  }
}
```

**Output:**
```json
{
  "decision_summary": {
    "decision_made": true,
    "decision_type": "auto_buy",
    "confidence_level": "very_high",
    "risk_level": "low"
  },
  "selected_option": {
    "rank": 1,
    "platform": "PharmEasy",
    "product_name": "Paracetamol 500mg (Dolo)",
    "brand": "Dolo",
    "price": 15.00,
    "unit_price_label": "₹15.00/strip",
    "delivery_time_label": "2 hours",
    "rating": 4.8,
    "final_score": 94.5,
    "availability": true
  },
  "decision_reasoning": {
    "primary_reason": "Fastest delivery (2 hours) with best price (₹15) - perfect for urgent medicine need",
    "supporting_factors": [
      "URGENT priority: Speed is critical",
      "Excellent score (94.5) - highest confidence",
      "Best on ALL criteria: price, speed, quality",
      "Immediate availability"
    ],
    "tradeoffs_considered": [
      "No tradeoffs - this option dominates on all factors"
    ],
    "risks_identified": [
      "No significant risks identified"
    ],
    "policy_applied": [
      "Policy 4: Urgent urgency → Speed prioritized over everything",
      "Policy 5: Low risk - immediate action justified",
      "Policy 2: Very high score (94.5) → confident auto-selection"
    ]
  },
  "explanation_for_user": {
    "simple_message": "PharmEasy se 2 ghante mein ₹15 mein mil jayegi. Turant mangwa rahe hain.",
    "why_this_option": "Chosen for fastest delivery since this is urgent. Also happens to be cheapest with best rating.",
    "what_user_gets": "Medicine delivered in 2 hours, best price (₹15), excellent quality (4.8★)"
  },
  "fallback_strategy": {
    "has_fallback": true,
    "primary_failed_reason": "If PharmEasy delivery delayed or unavailable",
    "secondary_option": {
      "rank": 2,
      "platform": "1mg",
      "product_name": "Crocin 500mg",
      "price": 18.00,
      "reason": "Backup with 3 hour delivery, only ₹3 more and still very fast"
    },
    "tertiary_option": null
  },
  "next_action": {
    "action": "purchase",
    "target_agent": "purchase_agent",
    "action_parameters": {
      "platform": "PharmEasy",
      "product_id": "dolo_500mg_strip",
      "quantity": "1 strip",
      "estimated_total": 15.00
    },
    "user_confirmation_required": false,
    "confirmation_message": null
  },
  "metadata": {
    "timestamp": "2026-01-14T11:15:00Z",
    "decision_duration_ms": 120,
    "original_intent": "buy_medicine",
    "original_urgency": "urgent",
    "options_evaluated": 2,
    "policies_triggered": ["urgent_priority", "no_confirmation_for_clear_winner"]
  }
}
```

### Example 3: Close Competition - Ask User

**Input:**
```json
{
  "comparison_summary": {
    "urgency_level": "normal",
    "products_after_filtering": 2
  },
  "ranked_products": [
    {
      "rank": 1,
      "platform": "Zepto",
      "normalized_attributes": {
        "price": 28.00,
        "delivery_time_hours": 0.33,
        "delivery_time_label": "20 minutes",
        "rating": 4.7,
        "availability": true
      },
      "scores": {
        "final_score": 87.5
      },
      "flags": ["fastest_delivery"]
    },
    {
      "rank": 2,
      "platform": "BigBasket",
      "normalized_attributes": {
        "price": 26.00,
        "delivery_time_hours": 4.0,
        "delivery_time_label": "4 hours",
        "rating": 4.5,
        "availability": true
      },
      "scores": {
        "final_score": 86.8
      },
      "flags": ["best_price"]
    }
  ],
  "comparison_insights": {
    "detected_tradeoffs": [
      {
        "type": "price_vs_speed",
        "description": "Zepto is faster (20 min) but ₹2 more expensive vs BigBasket (4 hours)"
      }
    ],
    "recommendation_confidence": "medium"
  }
}
```

**Output:**
```json
{
  "decision_summary": {
    "decision_made": false,
    "decision_type": "confirm_with_user",
    "confidence_level": "medium",
    "risk_level": "low"
  },
  "selected_option": {
    "rank": 1,
    "platform": "Zepto",
    "product_name": "Fresh Toned Milk",
    "brand": "Mother Dairy",
    "price": 28.00,
    "unit_price_label": "₹28.00/litre",
    "delivery_time_label": "20 minutes",
    "rating": 4.7,
    "final_score": 87.5,
    "availability": true
  },
  "decision_reasoning": {
    "primary_reason": "Too close to decide automatically - score gap only 0.7 points",
    "supporting_factors": [
      "Option 1 (Zepto): Faster (20 min) but ₹2 more expensive",
      "Option 2 (BigBasket): Cheaper by ₹2 but takes 4 hours",
      "Both have good ratings and availability"
    ],
    "tradeoffs_considered": [
      "Classic price vs speed tradeoff with no clear winner for normal urgency",
      "₹2 difference is marginal (~7%)",
      "Time difference is significant (20 min vs 4 hours)"
    ],
    "risks_identified": [
      "Risk of wrong choice if we auto-select - user preference unknown"
    ],
    "policy_applied": [
      "Policy 3: Score gap < 5 points → Ask user",
      "Policy 6: Elderly user protection → Confirm when unclear"
    ]
  },
  "explanation_for_user": {
    "simple_message": "Doodh ke liye do options hain. Kya aap jaldi chahte hain ya sasta?",
    "why_this_option": "Both options are good, but one is faster and one is cheaper. Your preference matters here.",
    "what_user_gets": "Option 1: Fast (20 min) - ₹28 | Option 2: Cheaper (₹26) - 4 hours"
  },
  "fallback_strategy": {
    "has_fallback": true,
    "primary_failed_reason": "If user doesn't respond or both options fail",
    "secondary_option": {
      "rank": 2,
      "platform": "BigBasket",
      "product_name": "Toned Milk",
      "price": 26.00,
      "reason": "If Zepto fails, BigBasket is reliable backup"
    },
    "tertiary_option": null
  },
  "next_action": {
    "action": "confirm",
    "target_agent": "notification_agent",
    "action_parameters": {
      "confirmation_type": "choice_between_two",
      "option_1": {
        "platform": "Zepto",
        "price": 28.00,
        "delivery": "20 minutes",
        "label": "Fast but slightly expensive"
      },
      "option_2": {
        "platform": "BigBasket",
        "price": 26.00,
        "delivery": "4 hours",
        "label": "Cheaper but slower"
      }
    },
    "user_confirmation_required": true,
    "confirmation_message": "Dono options ache hain. Zepto 20 minute mein degi (₹28) ya BigBasket 4 ghante mein degi (₹26). Kaunsa chahiye?"
  },
  "metadata": {
    "timestamp": "2026-01-14T12:00:00Z",
    "decision_duration_ms": 200,
    "original_intent": "buy_daily_essential",
    "original_urgency": "normal",
    "options_evaluated": 2,
    "policies_triggered": ["close_competition", "user_confirmation"]
  }
}
```

### Example 4: High Risk - Do Not Auto-Buy

**Input:**
```json
{
  "comparison_summary": {
    "urgency_level": "normal",
    "products_after_filtering": 1
  },
  "ranked_products": [
    {
      "rank": 1,
      "platform": "NewPlatform",
      "normalized_attributes": {
        "price": 85.00,
        "delivery_time_hours": 12.0,
        "rating": 3.2,
        "reviews_count": 45,
        "availability": true,
        "stock_status": "low_stock"
      },
      "scores": {
        "final_score": 65.0
      },
      "warnings": ["Low rating", "Few reviews", "Low stock", "New/unknown platform"]
    }
  ],
  "comparison_insights": {
    "recommendation_confidence": "low"
  }
}
```

**Output:**
```json
{
  "decision_summary": {
    "decision_made": false,
    "decision_type": "clarify_needed",
    "confidence_level": "low",
    "risk_level": "high"
  },
  "selected_option": null,
  "decision_reasoning": {
    "primary_reason": "Too many risk factors - cannot auto-buy safely",
    "supporting_factors": [
      "Low rating (3.2★) - below acceptable threshold",
      "Very few reviews (45) - insufficient validation",
      "Low stock - might get cancelled",
      "Unknown/new platform - reliability uncertain",
      "Score only 65.0 - below confident threshold"
    ],
    "tradeoffs_considered": [
      "Price is attractive (₹85) but quality concerns dominate"
    ],
    "risks_identified": [
      "HIGH RISK: Low rating suggests poor quality or service",
      "HIGH RISK: Few reviews - insufficient user validation",
      "MEDIUM RISK: Low stock - order may fail",
      "MEDIUM RISK: New platform - no trust history"
    ],
    "policy_applied": [
      "Policy 2: Score < 70 with low confidence → Do not auto-select",
      "Policy 5: High risk assessment → Stop and notify user",
      "Policy 6: Elderly protection → Never risk bad experience"
    ]
  },
  "explanation_for_user": {
    "simple_message": "Yeh option theek nahi lag raha. Rating kam hai (3.2★) aur platform naya hai. Doosri jagah se dhoondte hain?",
    "why_this_option": "This option has too many warning signs - low rating, few reviews, and uncertain platform reliability.",
    "what_user_gets": "RISK WARNING: This purchase might lead to poor quality or delivery issues"
  },
  "fallback_strategy": {
    "has_fallback": false,
    "primary_failed_reason": "No good options available",
    "secondary_option": null,
    "tertiary_option": null
  },
  "next_action": {
    "action": "notify",
    "target_agent": "notification_agent",
    "action_parameters": {
      "notification_type": "no_good_option",
      "reason": "Available option has high risk - low rating, few reviews, low stock",
      "suggested_action": "Search again later or try different search terms"
    },
    "user_confirmation_required": false,
    "confirmation_message": "Abhi koi acha option nahi mila. Kya hum thodi der baad phir try karein?"
  },
  "metadata": {
    "timestamp": "2026-01-14T13:00:00Z",
    "decision_duration_ms": 150,
    "original_intent": "buy_grocery",
    "original_urgency": "normal",
    "options_evaluated": 1,
    "policies_triggered": ["low_confidence_stop", "high_risk_abort", "elderly_protection"]
  }
}
```

### Example 5: Low Stock Warning - Confirm Before Buy

**Input:**
```json
{
  "comparison_summary": {
    "urgency_level": "high",
    "products_after_filtering": 2
  },
  "ranked_products": [
    {
      "rank": 1,
      "platform": "Zepto",
      "normalized_attributes": {
        "price": 120.00,
        "delivery_time_hours": 0.17,
        "delivery_time_label": "10 minutes",
        "rating": 4.7,
        "availability": true,
        "stock_status": "low_stock"
      },
      "scores": {
        "final_score": 91.0
      },
      "flags": ["fastest_delivery", "best_quality"],
      "warnings": ["Low stock - may get cancelled"]
    },
    {
      "rank": 2,
      "platform": "Blinkit",
      "normalized_attributes": {
        "price": 110.00,
        "delivery_time_hours": 0.5,
        "rating": 4.6,
        "availability": true,
        "stock_status": "in_stock"
      },
      "scores": {
        "final_score": 88.2
      }
    }
  ]
}
```

**Output:**
```json
{
  "decision_summary": {
    "decision_made": true,
    "decision_type": "confirm_with_user",
    "confidence_level": "high",
    "risk_level": "medium"
  },
  "selected_option": {
    "rank": 1,
    "platform": "Zepto",
    "product_name": "White Chana Premium",
    "brand": "Nature's Basket",
    "price": 120.00,
    "unit_price_label": "₹120.00/kg",
    "delivery_time_label": "10 minutes",
    "rating": 4.7,
    "final_score": 91.0,
    "availability": true
  },
  "decision_reasoning": {
    "primary_reason": "Best option for high urgency but has stock availability risk",
    "supporting_factors": [
      "Fastest delivery (10 min) - critical for high urgency",
      "High score (91.0) - strong overall performance",
      "Best quality rating (4.7★)"
    ],
    "tradeoffs_considered": [
      "Slightly more expensive (₹120 vs ₹110) but significantly faster"
    ],
    "risks_identified": [
      "MEDIUM RISK: Low stock - order might get cancelled",
      "Mitigation: Have Blinkit as strong backup (30 min delivery)"
    ],
    "policy_applied": [
      "Policy 4: High urgency → Speed is priority",
      "Policy 5: Medium risk → Get user confirmation",
      "Policy 6: Warn user about stock risk before purchase"
    ]
  },
  "explanation_for_user": {
    "simple_message": "Zepto se 10 minute mein mil jayega lekin stock kam hai. Confirm karein ya backup option (Blinkit - 30 min) lein?",
    "why_this_option": "Fastest option for your urgent need, but stock is limited so there's a small risk of cancellation.",
    "what_user_gets": "Ultra-fast delivery (10 min), best quality (4.7★), but stock risk exists"
  },
  "fallback_strategy": {
    "has_fallback": true,
    "primary_failed_reason": "If Zepto stock runs out or order cancelled",
    "secondary_option": {
      "rank": 2,
      "platform": "Blinkit",
      "product_name": "White Chickpeas (Kabuli Chana)",
      "price": 110.00,
      "reason": "Excellent backup with good stock, 30 min delivery, and ₹10 cheaper"
    },
    "tertiary_option": null
  },
  "next_action": {
    "action": "confirm",
    "target_agent": "notification_agent",
    "action_parameters": {
      "confirmation_type": "risk_warning",
      "primary_option": {
        "platform": "Zepto",
        "price": 120.00,
        "delivery": "10 minutes",
        "warning": "Stock kam hai - cancel ho sakta hai"
      },
      "backup_option": {
        "platform": "Blinkit",
        "price": 110.00,
        "delivery": "30 minutes",
        "note": "Stock available - safer option"
      }
    },
    "user_confirmation_required": true,
    "confirmation_message": "Zepto 10 min mein dega (₹120) lekin stock kam hai. Ya Blinkit 30 min mein safe delivery (₹110)?"
  },
  "metadata": {
    "timestamp": "2026-01-14T14:00:00Z",
    "decision_duration_ms": 190,
    "original_intent": "buy_grocery",
    "original_urgency": "high",
    "options_evaluated": 2,
    "policies_triggered": ["stock_risk_warning", "user_confirmation", "fallback_ready"]
  }
}
```

## 🎯 DECISION TYPES EXPLAINED

| Decision Type | When to Use | Next Agent |
|---------------|-------------|------------|
| `auto_buy` | Clear winner, high confidence, low risk, no user confirmation needed | Purchase Agent |
| `confirm_with_user` | Close competition, medium risk, or requires user preference | Notification Agent |
| `clarify_needed` | High risk, low confidence, or missing critical information | Notification Agent |
| `no_good_option` | All options filtered out or unacceptable quality/risk | Notification Agent |

## 🎯 CONFIDENCE LEVELS

| Level | Score Range | Action |
|-------|-------------|--------|
| `very_high` | > 85 | Auto-buy with confidence |
| `high` | 60-85 | Auto-buy if low risk |
| `medium` | 30-60 | Likely need confirmation |
| `low` | < 30 | Do not auto-buy |

## 🎯 RISK LEVELS

| Level | Indicators | Action |
|-------|-----------|--------|
| `low` | Good stock, known platform, good rating | Auto-buy OK |
| `medium` | Low stock, or one warning flag | Confirm with user |
| `high` | Multiple warnings, low rating, unknown platform | Do NOT auto-buy |

## 🧓 ELDERLY USER SPECIAL CONSIDERATIONS

1. **Default to Confirmation for High-Value Items** (>₹500)
2. **Always Explain Tradeoffs in Simple Terms**
3. **Never Rush** - Prefer safer option if uncertain
4. **Use Hinglish/Hindi in explanation_for_user**
5. **Avoid Technical Jargon** - Use "stock kam hai" not "low availability"
6. **Build Trust** - Explain WHY each decision was made

## 🎤 REMEMBER

- You are the DECIDER, not the searcher or comparer
- COMMIT to ONE path after careful reasoning
- ALWAYS plan fallbacks
- EXPLAIN your reasoning clearly
- ADAPT to urgency and user context
- PROTECT elderly users from bad experiences
- ONLY output JSON, nothing else

Now process the comparison results and make the final decision.
"""

# ---------------- MODEL INITIALIZATION ---------------- #

MODEL_NAME = "gemini-2.5-flash"

# Chat history to maintain context
chat_history = [
    {"role": "user", "parts": [{"text": system_prompt}]},
    {"role": "model", "parts": [{"text": "Understood. I am the Decision Agent for GANGU. I will analyze ranked options, apply decision policies, assess risks, resolve tradeoffs, and commit to one final decision with clear reasoning and fallback strategy. I will adapt to urgency, protect elderly users, and output only valid JSON. Ready to make decisions."}]}
]

# ---------------- HELPER FUNCTIONS ---------------- #

def report_agent_failure(agent_name: str, error_details: str, can_retry: bool = False) -> Dict[str, Any]:
    """REAL AGENTIC SYSTEM: Report failures transparently, NO FALLBACK DATA"""
    return {
        "status": "failed",
        "error_type": "agent_failure",
        "agent": agent_name,
        "error_details": error_details,
        "user_message": f"❌ {agent_name} failed: {error_details[:100]}",
        "can_retry": can_retry,
        "metadata": {
            "timestamp": datetime.now().isoformat(),
            "failure_reason": f"{agent_name}_failure"
        }
    }

def make_decision_with_transparent_failure(comparison_results: Dict[str, Any]) -> Dict[str, Any]:
    """NO FALLBACK - Check upstream failures first"""
    
    # Check if comparison agent failed
    if comparison_results.get("status") == "failed":
        return {
            "status": "failed",
            "error_type": "upstream_failure",
            "agent": "decision_agent",
            "upstream_agent": "comparison_agent",
            "error_details": comparison_results.get("error_details", "Unknown error"),
            "user_message": f"❌ Cannot decide: Comparison Agent failed",
            "can_retry": comparison_results.get("can_retry", False),
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "failure_reason": "upstream_comparison_failure"
            }
        }
    
    # Check if no products (try both key names for compatibility)
    ranked_options = comparison_results.get("ranked_products", comparison_results.get("ranked_results", []))
    if not ranked_options:
        return {
            "status": "failed",
            "error_type": "no_products",
            "agent": "decision_agent",
            "user_message": "❌ No products to decide on",
            "can_retry": True,
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "failure_reason": "no_products_from_comparison"
            }
        }
    
    # Products are available, continue with decision making
    return {}  # No upstream failure, proceed

def clean_json_response(response_text: str) -> str:
    """Extract JSON from response, handling markdown code blocks and truncation"""
    import re
    text = response_text.strip()
    
    # Remove markdown code blocks
    if "```json" in text:
        text = text.split("```json")[1].split("```")[0].strip()
    elif "```" in text:
        text = text.split("```")[1].split("```")[0].strip()
    
    # Fix common JSON issues
    # 1. Remove trailing commas before closing braces/brackets
    text = re.sub(r',(\s*[}\]])', r'\1', text)
    
    # 2. If JSON is truncated (no closing brace), try to fix it
    if text.count('{') > text.count('}'):
        missing_braces = text.count('{') - text.count('}')
        if text.rstrip().endswith(',') or not text.rstrip().endswith(('}', ']', '"')):
            last_complete = max(
                text.rfind('}'),
                text.rfind(']'),
                text.rfind('"')
            )
            if last_complete > 0:
                text = text[:last_complete + 1]
        text += '}' * missing_braces
    
    # 3. Same for arrays
    if text.count('[') > text.count(']'):
        missing_brackets = text.count('[') - text.count(']')
        text += ']' * missing_brackets
    
    return text

def create_fallback_decision(comparison_results: Dict[str, Any]) -> Dict[str, Any]:
    """
    Rule-based fallback decision when AI fails
    Simply picks the top-ranked option
    Matches the expected output format
    """
    ranked_products = comparison_results.get("ranked_products", comparison_results.get("ranked_results", []))
    
    if not ranked_products:
        return {
            "decision_summary": {
                "decision_made": False,
                "decision_type": "no_good_option",
                "confidence_level": "none",
                "risk_level": "none"
            },
            "selected_option": None,
            "explanation_for_user": {
                "simple_message": "Koi product available nahi hai",
                "why_this_option": "No options found"
            },
            "fallback_mode": True
        }
    
    # Pick top-ranked option
    top_option = ranked_products[0]
    
    # Determine decision type based on score/price
    score = top_option.get("score", 0)
    price = top_option.get("price", 0)
    
    if score >= 80 and price < 500:
        decision_type = "auto_buy"
        confidence = "high"
        risk = "low"
        decision_made = True
    elif score >= 60:
        decision_type = "confirm_with_user"
        confidence = "medium"
        risk = "medium"
        decision_made = True
    else:
        decision_type = "confirm_with_user"
        confidence = "low"
        risk = "high"
        decision_made = True
    
    platform = top_option.get("platform", "Unknown")
    item_name = top_option.get("item_name", "Product")
    
    # Build fallback options
    fallback_options = []
    for product in ranked_products[1:3]:  # Next 2 options
        fallback_options.append({
            "platform": product.get("platform"),
            "product_id": product.get("product_id"),
            "price": product.get("price"),
            "delivery_hours": product.get("delivery_time_hours")
        })
    
    return {
        "decision_summary": {
            "decision_made": decision_made,
            "decision_type": decision_type,
            "confidence_level": confidence,
            "risk_level": risk
        },
        "selected_option": top_option,
        "final_decision": {
            "selected_platform": platform,
            "product": {
                "name": item_name,
                "brand": top_option.get("brand", "Unknown"),
                "product_id": top_option.get("product_id", "unknown"),
                "quantity": top_option.get("quantity", "1 unit"),
                "price": price,
                "currency": "INR"
            },
            "delivery": {
                "eta_hours": top_option.get("delivery_time_hours", 24),
                "delivery_date": "TBD",
                "slot": "standard"
            },
            "confidence_score": score / 100 if score else 0.8,
            "fallback_options": fallback_options
        },
        "explanation_for_user": {
            "simple_message": f"{item_name} {platform} se order ho jayega",
            "why_this_option": f"Best ranked option (Score: {score}/100)",
            "delivery_info": f"{top_option.get('delivery_time_label', 'Soon')} delivery",
            "cost": f"₹{price}"
        },
        "fallback_mode": True,
        "metadata": {
            "timestamp": datetime.now().isoformat(),
            "note": "Using rule-based fallback decision (AI unavailable)"
        }
    }

def make_decision(comparison_results: Dict[str, Any]) -> Dict[str, Any]:
    """REAL AGENTIC SYSTEM - Main decision function with transparent failures"""
    global chat_history
    
    # FIRST: Check for upstream failures (NO FALLBACK)
    failure_check = make_decision_with_transparent_failure(comparison_results)
    if failure_check.get("status") == "failed":
        return failure_check
    
    # Retry with exponential backoff
    max_retries = 3
    retry_delay = 45
    response = None
    
    for attempt in range(max_retries):
        try:
            # Convert comparison results to JSON string for the model
            comparison_json = json.dumps(comparison_results, ensure_ascii=False, indent=2)
            
            # Add user message to history
            chat_history.append({"role": "user", "parts": [{"text": comparison_json}]})
            
            # Call Gemini API
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=chat_history,
                config={
                    "temperature": 0.2,
                    "top_p": 0.95,
                    "top_k": 40,
                    "max_output_tokens": 8192,  # Increased to prevent truncation
                    "response_mime_type": "application/json",  # Force JSON
                }
            )
            break  # Success
        except Exception as api_error:
            error_str = str(api_error)
            if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str or "quota" in error_str.lower():
                if attempt < max_retries - 1:
                    import re
                    match = re.search(r'retry in (\d+)', error_str)
                    delay = int(match.group(1)) + 3 if match else retry_delay
                    print(f"\n⏳ DECISION AGENT: Rate limit, waiting {delay}s... (attempt {attempt+1}/{max_retries})")
                    time.sleep(delay)
                    retry_delay = int(retry_delay * 1.5)
                else:
                    print(f"\n❌ DECISION AGENT: Max retries reached")
                    return report_agent_failure("decision_agent", "Rate limit exhausted after retries", True)
            else:
                print(f"\n❌ DECISION AGENT: API error - {error_str[:100]}")
                return report_agent_failure("decision_agent", error_str, False)
    
    if response is None:
        return report_agent_failure("decision_agent", "No response from API after retries", True)
    
    try:
        response_text = response.text
        
        # Add model response to history
        chat_history.append({"role": "model", "parts": [{"text": response_text}]})
        
        # Clean and parse JSON
        cleaned_response = clean_json_response(response_text)
        parsed_output = json.loads(cleaned_response)
        
        # SUCCESS
        return parsed_output
        
    except json.JSONDecodeError as e:
        print(f"\n❌ DECISION AGENT: JSON parse error - {str(e)}")
        print(f"📄 Response preview: {response_text[:500] if 'response_text' in locals() else 'No response'}...")
        
        # Try fallback decision
        print("🔄 Using fallback decision logic...")
        return create_fallback_decision(comparison_results)
    
    except Exception as e:
        print(f"\n❌ DECISION AGENT: Unexpected error - {str(e)}")
        return report_agent_failure("decision_agent", str(e), False)

def pretty_print_decision(decision: Dict[str, Any]):
    """Display decision in a readable format"""
    print("\n" + "=" * 80)
    print("🎯 FINAL DECISION")
    print("=" * 80)
    
    # Summary
    summary = decision.get("decision_summary", {})
    print(f"\n📋 Decision Summary:")
    print(f"   Decision Made: {'✅ Yes' if summary.get('decision_made') else '❌ No'}")
    print(f"   Decision Type: {summary.get('decision_type', 'N/A').upper()}")
    print(f"   Confidence: {summary.get('confidence_level', 'N/A').upper()}")
    print(f"   Risk Level: {summary.get('risk_level', 'N/A').upper()}")
    
    # Selected option
    selected = decision.get("selected_option")
    if selected:
        print(f"\n🏆 Selected Option:")
        print(f"   Platform: {selected.get('platform', 'N/A')}")
        print(f"   Product: {selected.get('product_name', 'N/A')}")
        print(f"   Brand: {selected.get('brand', 'N/A')}")
        print(f"   Price: {selected.get('unit_price_label', selected.get('price', 'N/A'))}")
        print(f"   Delivery: {selected.get('delivery_time_label', 'N/A')}")
        print(f"   Rating: {selected.get('rating', 'N/A')}★")
        print(f"   Score: {selected.get('final_score', 'N/A')}/100")
    
    # Reasoning
    reasoning = decision.get("decision_reasoning", {})
    if reasoning:
        print(f"\n💡 Decision Reasoning:")
        print(f"   Primary: {reasoning.get('primary_reason', 'N/A')}")
        
        supporting = reasoning.get("supporting_factors", [])
        if supporting:
            print(f"   Supporting Factors:")
            for factor in supporting[:3]:  # Show top 3
                print(f"      • {factor}")
        
        risks = reasoning.get("risks_identified", [])
        if risks:
            print(f"   Risks:")
            for risk in risks:
                print(f"      ⚠️  {risk}")
    
    # User explanation
    explanation = decision.get("explanation_for_user", {})
    if explanation:
        print(f"\n👤 For User:")
        print(f"   {explanation.get('simple_message', 'N/A')}")
        print(f"   Why: {explanation.get('why_this_option', 'N/A')}")
    
    # Fallback
    fallback = decision.get("fallback_strategy", {})
    if fallback.get("has_fallback"):
        secondary = fallback.get("secondary_option", {})
        if secondary:
            print(f"\n🔄 Fallback Plan:")
            print(f"   Backup: {secondary.get('platform')} - {secondary.get('product_name')}")
            print(f"   Price: ₹{secondary.get('price')} | Reason: {secondary.get('reason', 'N/A')[:50]}...")
    
    # Next action
    next_action = decision.get("next_action", {})
    if next_action:
        print(f"\n➡️  Next Action:")
        print(f"   Action: {next_action.get('action', 'N/A').upper()}")
        print(f"   Target: {next_action.get('target_agent', 'N/A')}")
        if next_action.get('user_confirmation_required'):
            print(f"   ⚠️  User Confirmation REQUIRED")
            print(f"   Message: {next_action.get('confirmation_message', 'N/A')}")
    
    # Metadata
    metadata = decision.get("metadata", {})
    if metadata:
        print(f"\n⏱️  Decision Time: {metadata.get('decision_duration_ms', 0)}ms")
        policies = metadata.get('policies_triggered', [])
        if policies:
            print(f"   Policies Applied: {', '.join(policies)}")
    
    print("=" * 80)

# ---------------- MAIN EXECUTION ---------------- #

if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                     🎯 GANGU - Decision Agent                                ║
║                     ────────────────────────────                             ║
║             Converting ranked options into final decisions                   ║
║             Position: Comparison Agent → [YOU] → Purchase Agent              ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """)
    
    print("📌 MODES:")
    print("   1. Enter 'test' to run with sample comparison results")
    print("   2. Paste JSON from Comparison Agent directly")
    print("   3. Type 'quit' to exit")
    print("-" * 80)
    
    # Test example (from Comparison Agent output)
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
                    "brand": "Fresho"
                },
                "normalized_attributes": {
                    "price": 95.00,
                    "unit_price_label": "₹95.00/kg",
                    "delivery_time_hours": 48.0,
                    "delivery_time_label": "2 days",
                    "rating": 4.2,
                    "reviews_count": 5100,
                    "availability": True,
                    "stock_status": "in_stock"
                },
                "scores": {
                    "final_score": 89.5
                },
                "flags": ["best_overall", "best_price"],
                "explanation": "Ranked #1 because lowest unit price with good availability",
                "warnings": ["Slower delivery (2 days)"]
            },
            {
                "rank": 2,
                "platform": "Blinkit",
                "product_identity": {
                    "canonical_name": "White Chickpeas (Kabuli Chana)",
                    "brand": "Farm Fresh"
                },
                "normalized_attributes": {
                    "price": 110.00,
                    "unit_price_label": "₹110.00/kg",
                    "delivery_time_hours": 12.0,
                    "delivery_time_label": "12 hours",
                    "rating": 4.6,
                    "availability": True
                },
                "scores": {
                    "final_score": 88.2
                }
            }
        ],
        "comparison_insights": {
            "price_range": {"min": 95.00, "max": 120.00},
            "delivery_range": {"fastest_hours": 10.0, "slowest_hours": 48.0},
            "detected_tradeoffs": [
                {
                    "type": "price_vs_speed",
                    "description": "Cheapest option (₹95/kg) has slowest delivery (2 days)"
                }
            ],
            "recommendation_confidence": "high"
        }
    }
    
    # Interactive loop
    while True:
        try:
            print("\n📥 Enter comparison results JSON (or 'test' / 'quit'):")
            user_input = input(">>> ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['quit', 'exit', 'q', 'bye']:
                print("\n👋 Namaste! GANGU Decision Agent signing off.")
                break
            
            if user_input.lower() == 'test':
                # Run test
                print("\n🧪 Running test with sample comparison results...")
                print(f"📥 Input: {json.dumps(test_comparison_result, ensure_ascii=False, indent=2)[:300]}...")
                
                decision = make_decision(test_comparison_result)
                pretty_print_decision(decision)
                
                # Show raw JSON
                print(f"\n📨 Raw JSON Output for Purchase/Notification Agent:")
                print(json.dumps(decision, ensure_ascii=False, indent=2)[:600] + "...")
                continue
            
            # Try to parse as JSON
            try:
                comparison_data = json.loads(user_input)
            except json.JSONDecodeError:
                print("❌ Invalid JSON. Please paste valid comparison results JSON from Comparison Agent.")
                print("   Example format:")
                print('   {"comparison_summary": {...}, "ranked_products": [...]}')
                continue
            
            # Make decision
            decision = make_decision(comparison_data)
            pretty_print_decision(decision)
            
            # Show the raw JSON that would go to next agent
            print(f"\n📨 Output for Next Agent:")
            print(json.dumps(decision, ensure_ascii=False))
            
        except KeyboardInterrupt:
            print("\n\n👋 Namaste! GANGU Decision Agent signing off.")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
