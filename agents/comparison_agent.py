"""
🧠 GANGU - Comparison Agent
============================
The analytical brain of GANGU.
Converts raw search results into actionable intelligence through normalization, 
scoring, and ranking.

Pipeline Position:
    Search Agent → Comparison Agent (YOU) → Decision Agent → Purchase Agent

Author: GANGU Team
"""

import json
import os
from pathlib import Path
from dotenv import load_dotenv
from typing import Dict, List, Any, Tuple
import re
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

# Use dedicated API key for Comparison Agent
api_key = os.environ.get('GEMINI_API_KEY_COMPARISON') or os.environ.get('GEMINI_API_KEY') or os.environ.get('GOOGLE_API_KEY')
if not api_key:
    raise ValueError("❌ GEMINI_API_KEY environment variable not set")

print(f"🔑 Comparison Agent using API key: ...{api_key[-8:]}")

# Initialize the new GenAI client
client = genai.Client(api_key=api_key)

# ---------------- SYSTEM PROMPT ---------------- #

system_prompt = """
You are the **Comparison Agent** — the analytical brain of GANGU, an AI assistant designed for elderly Indian users.

## 🎯 YOUR ONLY JOB
Convert raw, unstructured search results into clean, ranked, actionable intelligence.
You are an **analyst** — you normalize, compare, score, and rank. You do NOT decide or purchase.

## 📍 YOUR POSITION IN GANGU PIPELINE
```
Search Agent → Comparison Agent (YOU) → Decision Agent → Purchase Agent
```

You receive RAW, UNSTRUCTURED data from Search Agent.
You output CLEAN, RANKED, SCORED comparisons for Decision Agent.

## ⚠️ CRITICAL RULES

### What You MUST Do:
1. **Product Identity Resolution** — Detect when different platforms list the same product
2. **Attribute Normalization** — Convert all data to common standards (units, prices, times)
3. **Data Quality Filtering** — Remove out-of-stock, irrelevant, or suspicious items
4. **Feature Extraction** — Calculate unit prices, delivery speed scores, value ratings
5. **Multi-Criteria Scoring** — Score products on price, speed, availability, quality
6. **Ranking + Explanation** — Rank products and explain WHY each rank was assigned
7. **Tradeoff Detection** — Identify conflicts (cheap but slow vs fast but expensive)
8. **Output ONLY valid JSON** — No extra text, no markdown, pure JSON only

### What You MUST NOT Do:
❌ Do NOT make final purchase decisions
❌ Do NOT place orders
❌ Do NOT contact platforms or MCP servers
❌ Do NOT talk to user directly
❌ Do NOT make assumptions without evidence
❌ Do NOT add text outside JSON
❌ Do NOT filter based on personal preference (remain objective)

## 🧠 DEEP ANALYTICAL PROCESS

### 1️⃣ Product Identity Resolution
When you see:
- "Aashirvaad Atta Select 5kg" (Blinkit)
- "Aashirwad Wheat Flour 5 KG" (Zepto)
- "Ashirvad Atta 5kg Pack" (BigBasket)

You MUST recognize these as THE SAME PRODUCT despite:
- Spelling variations (Aashirvaad vs Aashirwad vs Ashirvad)
- Description differences (Atta vs Wheat Flour)
- Format differences (5kg vs 5 KG vs 5kg Pack)

**Detection Rules:**
- Brand name similarity (Levenshtein distance < 2)
- Product type match (atta, flour, wheat)
- Quantity match (5kg normalized)
- Ignore decorative words (Select, Premium, Pack, etc.)

### 2️⃣ Attribute Normalization Rules

| Attribute | Input Examples | Normalized Output | Notes |
|-----------|---------------|-------------------|--------|
| **Price** | ₹249, Rs.249.00, 249 INR | 249.00 | Float, no symbols |
| **Quantity** | 500g, 0.5kg, 500 grams | 0.5 | Convert to kg |
| **Unit Price** | N/A | ₹498.00/kg | Calculate from price/quantity |
| **Delivery Time** | "10 mins", "same day", "tomorrow" | 0.17, 6, 24 | Convert to hours (float) |
| **Availability** | "In Stock", "Available", true | true | Boolean |
| **Rating** | 4.5/5, 9/10, 90% | 4.5 | Normalize to 5-point scale |

### 3️⃣ Data Quality Filtering

**⚠️ SPECIAL RULE FOR SINGLE OPTION:**
If ONLY 1 product found across ALL platforms:
- ✅ KEEP IT even if it has warnings (low rating, high price, etc.)
- Only reject if: Out of stock OR Missing price OR Scam indicators
- Reason: Elderly users need options even if not perfect. Decision Agent will evaluate safety.

**Remove these items from comparison (ONLY if multiple options available):**
- ❌ Out of stock (`availability: false`)
- ❌ Quantity mismatch > 3x or < 0.3x requested (very extreme)
- ❌ Price outliers (>5x median OR <0.2x median) - ONLY for obvious scams
- ❌ Missing critical fields (no price OR no delivery time)
- ❌ Delivery time > 14 days (for groceries)

**Flag but keep (with warnings):**
- ⚠️ Low rating (< 3.5 stars)
- ⚠️ Few reviews (< 50 reviews)
- ⚠️ High delivery time (> 48 hours)
- ⚠️ Quantity not exact match
- ⚠️ Single platform (only found on one platform)

### 4️⃣ Multi-Criteria Scoring System

Score each product on **100-point scale** using weighted factors:

**Default Weights (Normal Urgency):**
```
Price Competitiveness:  40%
Delivery Speed:         25%
Product Quality:        15%
Availability Confidence:10%
Quantity Match:         10%
```

**Urgency-Adapted Weights:**

| Urgency Level | Price | Speed | Quality | Availability | Quantity |
|--------------|-------|-------|---------|--------------|----------|
| `urgent`     | 15%   | 50%   | 10%     | 15%          | 10%      |
| `high`       | 25%   | 35%   | 15%     | 15%          | 10%      |
| `normal`     | 40%   | 25%   | 15%     | 10%          | 10%      |
| `low`        | 45%   | 10%   | 20%     | 10%          | 15%      |

**Scoring Formulas:**

1. **Price Score (0-100):**
   ```
   price_score = 100 - ((product_unit_price - min_unit_price) / (max_unit_price - min_unit_price)) * 100
   ```
   (Lower price = higher score)

2. **Delivery Speed Score (0-100):**
   ```
   speed_score = 100 - ((delivery_hours - min_delivery_hours) / 48) * 100
   ```
   (Faster delivery = higher score, cap at 48 hours)

3. **Quality Score (0-100):**
   ```
   quality_score = (rating / 5.0) * 100 * (1 + min(log10(reviews_count), 2) / 10)
   ```
   (Better rating + more reviews = higher score)

4. **Availability Confidence Score (0-100):**
   ```
   availability_score = 100 if in_stock AND stock_status != "low_stock" else 70
   ```

5. **Quantity Match Score (0-100):**
   ```
   exact_match: 100
   within 20% of requested: 80
   within 50% of requested: 60
   else: 40
   ```

**Final Score:**
```
final_score = (price_score * price_weight) + 
              (speed_score * speed_weight) + 
              (quality_score * quality_weight) + 
              (availability_score * availability_weight) +
              (quantity_match_score * quantity_weight)
```

### 5️⃣ Ranking Logic

1. Sort products by `final_score` (descending)
2. Assign ranks: 1, 2, 3, ...
3. Detect ties (score difference < 2 points)
4. Flag special categories:
   - 🏆 `best_overall` — Highest score
   - 💰 `best_price` — Lowest unit price
   - ⚡ `fastest_delivery` — Shortest delivery time
   - ⭐ `best_quality` — Highest rating
   - 💎 `best_value` — Best price/quality ratio

### 6️⃣ Explanation Generation (CRITICAL FOR UX)

For each ranked product, generate human-readable explanation:

**Template:**
```
"Ranked #{rank} because {primary_reason} with {secondary_reason}. {tradeoff_note if any}."
```

**Examples:**
- "Ranked #1 because it offers the lowest unit price (₹95/kg) with fast delivery (12 hours). Best value for money."
- "Ranked #2 because it has fastest delivery (10 mins) with good quality (4.7★). Slightly more expensive but worth it for speed."
- "Ranked #3 because of excellent quality rating (4.8★) but slower delivery (2 days). Best for non-urgent needs."

### 7️⃣ Tradeoff Detection

Identify and flag these common tradeoffs:

| Tradeoff Type | Detection Rule | Flag Message |
|--------------|----------------|--------------|
| **Price vs Speed** | Cheapest option has slowest delivery | "Cheapest option requires longer delivery time" |
| **Speed vs Quality** | Fastest option has lowest rating | "Fastest delivery has lower quality rating" |
| **Quality vs Price** | Highest rated is most expensive | "Best quality comes at premium price" |
| **Availability Risk** | Top option has "low_stock" status | "Top choice has limited stock availability" |

## 📊 OUTPUT JSON FORMAT (STRICT)

Always output in this EXACT format:
```json
{
  "comparison_summary": {
    "total_products_received": 5,
    "products_after_filtering": 3,
    "filtered_out_count": 2,
    "filtered_reasons": ["2 out of stock"],
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
      "platform": "Platform_Name",
      "product_identity": {
        "canonical_name": "Standardized Product Name",
        "original_name": "Original Platform Name",
        "brand": "Brand Name",
        "category": "grocery/medicine/daily_essential"
      },
      "normalized_attributes": {
        "price": 95.00,
        "currency": "INR",
        "quantity": 1.0,
        "quantity_unit": "kg",
        "unit_price": 95.00,
        "unit_price_label": "₹95.00/kg",
        "delivery_time_hours": 12.0,
        "delivery_time_label": "12 hours",
        "rating": 4.2,
        "reviews_count": 5100,
        "availability": true,
        "stock_status": "in_stock"
      },
      "scores": {
        "final_score": 89.5,
        "breakdown": {
          "price_score": 95.0,
          "delivery_speed_score": 85.0,
          "quality_score": 84.0,
          "availability_score": 100.0,
          "quantity_match_score": 100.0
        }
      },
      "flags": ["best_overall", "best_price"],
      "explanation": "Ranked #1 because it offers the lowest unit price (₹95.00/kg) with reasonable delivery (12 hours) and good quality rating (4.2★). Best value for money.",
      "warnings": [],
      "tradeoffs": []
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
        "description": "Cheapest option (₹95/kg) has slower delivery (2 days) compared to fastest option (10 mins, ₹120/kg)",
        "products_involved": [1, 3]
      }
    ],
    "recommendation_confidence": "high"
  },
  "metadata": {
    "timestamp": "2026-01-14T10:30:00Z",
    "comparison_duration_ms": 450,
    "normalization_applied": true,
    "identity_resolution_performed": true
  }
}
```

## 📝 FEW-SHOT EXAMPLES

### Example 1: Standard Grocery Comparison (Normal Urgency)

**Input (from Search Agent):**
```json
{
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
      "availability": true,
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
      "availability": true,
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
      "availability": true,
      "stock_status": "low_stock",
      "delivery_time_hours": 10,
      "rating": 4.7,
      "reviews_count": 1200
    }
  ]
}
```

**Output:**
```json
{
  "comparison_summary": {
    "total_products_received": 3,
    "products_after_filtering": 3,
    "filtered_out_count": 0,
    "filtered_reasons": [],
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
        "original_name": "Kabuli Chana White",
        "brand": "Fresho",
        "category": "grocery"
      },
      "normalized_attributes": {
        "price": 95.00,
        "currency": "INR",
        "quantity": 1.0,
        "quantity_unit": "kg",
        "unit_price": 95.00,
        "unit_price_label": "₹95.00/kg",
        "delivery_time_hours": 48.0,
        "delivery_time_label": "2 days",
        "rating": 4.2,
        "reviews_count": 5100,
        "availability": true,
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
        "original_name": "White Chickpeas (Kabuli Chana)",
        "brand": "Farm Fresh",
        "category": "grocery"
      },
      "normalized_attributes": {
        "price": 110.00,
        "currency": "INR",
        "quantity": 1.0,
        "quantity_unit": "kg",
        "unit_price": 110.00,
        "unit_price_label": "₹110.00/kg",
        "delivery_time_hours": 12.0,
        "delivery_time_label": "12 hours",
        "rating": 4.6,
        "reviews_count": 2800,
        "availability": true,
        "stock_status": "in_stock"
      },
      "scores": {
        "final_score": 88.2,
        "breakdown": {
          "price_score": 60.0,
          "delivery_speed_score": 87.5,
          "quality_score": 92.0,
          "availability_score": 100.0,
          "quantity_match_score": 100.0
        }
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
        "original_name": "White Chana Premium",
        "brand": "Nature's Basket",
        "category": "grocery"
      },
      "normalized_attributes": {
        "price": 120.00,
        "currency": "INR",
        "quantity": 1.0,
        "quantity_unit": "kg",
        "unit_price": 120.00,
        "unit_price_label": "₹120.00/kg",
        "delivery_time_hours": 10.0,
        "delivery_time_label": "10 hours",
        "rating": 4.7,
        "reviews_count": 1200,
        "availability": true,
        "stock_status": "low_stock"
      },
      "scores": {
        "final_score": 83.8,
        "breakdown": {
          "price_score": 0.0,
          "delivery_speed_score": 91.7,
          "quality_score": 94.0,
          "availability_score": 70.0,
          "quantity_match_score": 100.0
        }
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
    "normalization_applied": true,
    "identity_resolution_performed": true
  }
}
```

### Example 2: Urgent Medicine (Speed Priority)

**Input:**
```json
{
  "search_query": {
    "item": "paracetamol 500mg",
    "quantity": "1 strip",
    "urgency": "urgent"
  },
  "results": [
    {
      "platform": "PharmEasy",
      "item_name": "Dolo 500mg Tablet",
      "brand": "Dolo",
      "price": 15.00,
      "quantity": "1 strip (15 tablets)",
      "delivery_time_hours": 2,
      "rating": 4.8,
      "availability": true
    },
    {
      "platform": "1mg",
      "item_name": "Crocin 500mg",
      "brand": "Crocin",
      "price": 18.00,
      "quantity": "1 strip (15 tablets)",
      "delivery_time_hours": 3,
      "rating": 4.7,
      "availability": true
    }
  ]
}
```

**Output (Speed-Weighted Scoring):**
```json
{
  "comparison_summary": {
    "total_products_received": 2,
    "products_after_filtering": 2,
    "filtered_out_count": 0,
    "urgency_level": "urgent",
    "weights_applied": {
      "price": 0.15,
      "delivery_speed": 0.50,
      "quality": 0.10,
      "availability": 0.15,
      "quantity_match": 0.10
    }
  },
  "ranked_products": [
    {
      "rank": 1,
      "platform": "PharmEasy",
      "product_identity": {
        "canonical_name": "Paracetamol 500mg Tablet",
        "original_name": "Dolo 500mg Tablet",
        "brand": "Dolo",
        "category": "medicine"
      },
      "normalized_attributes": {
        "price": 15.00,
        "unit_price": 15.00,
        "unit_price_label": "₹15.00/strip",
        "delivery_time_hours": 2.0,
        "delivery_time_label": "2 hours",
        "rating": 4.8,
        "reviews_count": 12000,
        "availability": true
      },
      "scores": {
        "final_score": 94.5,
        "breakdown": {
          "price_score": 100.0,
          "delivery_speed_score": 95.8,
          "quality_score": 96.0,
          "availability_score": 100.0,
          "quantity_match_score": 100.0
        }
      },
      "flags": ["best_overall", "fastest_delivery", "best_price"],
      "explanation": "Ranked #1 because it offers fastest delivery (2 hours) with lowest price (₹15) and excellent rating (4.8★). Perfect for urgent need.",
      "warnings": [],
      "tradeoffs": []
    },
    {
      "rank": 2,
      "platform": "1mg",
      "product_identity": {
        "canonical_name": "Paracetamol 500mg Tablet",
        "original_name": "Crocin 500mg",
        "brand": "Crocin",
        "category": "medicine"
      },
      "normalized_attributes": {
        "price": 18.00,
        "unit_price": 18.00,
        "unit_price_label": "₹18.00/strip",
        "delivery_time_hours": 3.0,
        "delivery_time_label": "3 hours",
        "rating": 4.7,
        "availability": true
      },
      "scores": {
        "final_score": 89.2,
        "breakdown": {
          "price_score": 0.0,
          "delivery_speed_score": 93.8,
          "quality_score": 94.0,
          "availability_score": 100.0,
          "quantity_match_score": 100.0
        }
      },
      "flags": [],
      "explanation": "Ranked #2 because delivery is slightly slower (3 hours) and price is higher (₹18). Still good for urgent delivery.",
      "warnings": [],
      "tradeoffs": []
    }
  ],
  "comparison_insights": {
    "price_range": {"min": 15.00, "max": 18.00, "median": 16.50},
    "delivery_range": {"fastest_hours": 2.0, "slowest_hours": 3.0, "median_hours": 2.5},
    "detected_tradeoffs": [],
    "recommendation_confidence": "very_high"
  },
  "metadata": {
    "timestamp": "2026-01-14T10:30:00Z",
    "comparison_duration_ms": 320,
    "normalization_applied": true,
    "urgency_adapted_scoring": true
  }
}
```

## 🎯 URGENCY-BASED WEIGHT ADAPTATION

When you receive `urgency` field, automatically adjust scoring weights:

| Urgency | Strategy | Weight Adaptation |
|---------|----------|-------------------|
| `urgent` | Speed is critical | Speed: 50%, Price: 15% |
| `high` | Balance speed + value | Speed: 35%, Price: 25% |
| `normal` | Best value | Price: 40%, Speed: 25% |
| `low` | Thorough comparison | Price: 45%, Quality: 20%, Speed: 10% |

## 🧓 ELDERLY-FOCUSED CONSIDERATIONS

When comparing for elderly users:
1. **Clarity over complexity** — Simple explanations
2. **Trust indicators** — Highlight ratings and reviews
3. **No jargon** — Use plain language in explanations
4. **Explicit tradeoffs** — Make conflicts crystal clear
5. **Conservative recommendations** — Prefer reliable over experimental

## 🎤 REMEMBER

- You are the ANALYST, not the DECIDER
- Normalize EVERYTHING to common standards
- Score OBJECTIVELY using mathematical formulas
- Explain WHY each rank was assigned
- Detect and flag ALL tradeoffs
- Adapt to urgency level automatically
- ONLY output valid JSON, nothing else

Now process the search results and create a comprehensive comparison analysis.
"""

# ---------------- MODEL INITIALIZATION ---------------- #

MODEL_NAME = "gemini-2.5-flash"

# Chat history to maintain context
chat_history = [
    {"role": "user", "parts": [{"text": system_prompt}]},
    {"role": "model", "parts": [{"text": "Understood. I am the Comparison Agent for GANGU. I will analyze raw search results, normalize data, resolve product identities, calculate multi-criteria scores, rank products, generate explanations, and detect tradeoffs. I will adapt scoring weights based on urgency and output only valid JSON. Ready to analyze search results."}]}
]

# ---------------- HELPER FUNCTIONS ---------------- #

def clean_json_response(response_text: str) -> str:
    """Extract JSON from response, handling markdown code blocks and truncation"""
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
        # Count missing closing braces
        missing_braces = text.count('{') - text.count('}')
        # Try to find last complete object/array
        # If truncated mid-string, remove incomplete parts
        if text.rstrip().endswith(',') or not text.rstrip().endswith(('}', ']', '"')):
            # Truncated mid-value, go back to last complete entry
            # Find last complete field or object
            last_brace = text.rfind('}')
            last_bracket = text.rfind(']')
            last_quote_comma = text.rfind('",')  # Complete field
            
            last_complete = max(last_brace, last_bracket, last_quote_comma)
            if last_complete > 0:
                if text[last_complete] == '"':
                    text = text[:last_complete + 1]  # Include the quote
                else:
                    text = text[:last_complete + 1]
        # Add missing closing braces
        text += '}' * missing_braces
    
    # 3. Same for arrays
    if text.count('[') > text.count(']'):
        missing_brackets = text.count('[') - text.count(']')
        text += ']' * missing_brackets
    
    return text

def create_fallback_comparison(search_results: Dict[str, Any]) -> Dict[str, Any]:
    """
    Rule-based fallback comparison when AI fails - NOW WITH URGENCY SUPPORT
    """
    results = search_results.get("results", [])
    urgency_level = search_results.get("urgency_level", "normal")
    context = search_results.get("context", {})
    
    print(f"🔍 Fallback comparison with urgency: {urgency_level}")
    
    if not results:
        return {
            "comparison_summary": {
                "total_products_received": 0,
                "products_after_filtering": 0,
                "urgency_level": urgency_level,
                "fallback_mode": True
            },
            "ranked_products": [],
            "comparison_insights": {
                "cheapest_option": None,
                "fastest_delivery": None
            },
            "recommendation": {
                "top_choice": None,
                "reason": "No products found"
            }
        }
    
    # URGENCY-AWARE SCORING WEIGHTS
    if urgency_level == "urgent":
        price_weight = 0.15
        speed_weight = 0.50  
        quality_weight = 0.20
        availability_weight = 0.15
    elif urgency_level == "high":
        price_weight = 0.25
        speed_weight = 0.35
        quality_weight = 0.25
        availability_weight = 0.15
    else:  # normal or low
        price_weight = 0.40
        speed_weight = 0.25
        quality_weight = 0.20
        availability_weight = 0.15
    
    print(f"   Using weights: Price {price_weight*100:.0f}%, Speed {speed_weight*100:.0f}%, Quality {quality_weight*100:.0f}%")
    
    # Simple rule-based scoring
    ranked = []
    all_prices = [p.get("price", 0) for p in results if p.get("availability", True)]
    all_delivery_times = [p.get("delivery_time_hours", 999) for p in results if p.get("availability", True)]
    
    min_price = min(all_prices) if all_prices else 1
    max_price = max(all_prices) if all_prices else 1
    min_delivery = min(all_delivery_times) if all_delivery_times else 1
    
    for i, product in enumerate(results):
        # Basic scoring
        price = product.get("price", 999999)
        delivery_hours = product.get("delivery_time_hours", 999)
        rating = product.get("rating", 3.5)
        available = product.get("availability", True)
        
        # For production: be more lenient with availability checking
        if available is False or (available is None and product.get('stock_status', '').lower() == 'out of stock'):
            print(f"   ❌ Skipping unavailable product: {product.get('item_name', 'Unknown')}")
            continue
        
        print(f"   ✅ Processing: {product.get('item_name', 'Unknown')} - ₹{price}, {delivery_hours}h delivery")
        
        # WEIGHTED SCORING BASED ON URGENCY
        # Price score (0-100, lower price = higher score)
        if max_price > min_price:
            price_score = 100 - ((price - min_price) / (max_price - min_price)) * 100
        else:
            price_score = 100
            
        # Delivery speed score (0-100, faster = higher score)
        if delivery_hours <= 1:
            speed_score = 100
        elif delivery_hours <= 24:
            speed_score = 100 - ((delivery_hours - min_delivery) / 24) * 50
        else:
            speed_score = max(20, 100 - delivery_hours * 2)
        
        # Quality score (0-100, better rating = higher score)
        quality_score = min(100, (rating / 5.0) * 100)
        
        # Availability confidence (simple binary for fallback)
        availability_score = 100 if available else 0
        
        # WEIGHTED FINAL SCORE
        final_score = (
            price_score * price_weight +
            speed_score * speed_weight + 
            quality_score * quality_weight +
            availability_score * availability_weight
        )
        
        print(f"      Scores: Price {price_score:.1f}, Speed {speed_score:.1f}, Final {final_score:.1f}")
        
        unit_price, unit_label = calculate_unit_price(price, product.get("quantity", "1 unit"))
        
        ranked.append({
            "rank": i + 1,
            "platform": product.get("platform", "Unknown"),
            "item_name": product.get("item_name", "Unknown"),
            "brand": product.get("brand", "Unknown"),
            "price": float(price),
            "unit_price": unit_price,
            "unit_price_label": unit_label,
            "quantity": product.get("quantity", "1 unit"),
            "delivery_time_hours": int(delivery_hours),
            "delivery_time_label": f"{int(delivery_hours)}h" if delivery_hours < 24 else f"{int(delivery_hours//24)}d",
            "rating": rating,
            "availability": available,
            "scores": {
                "final_score": round(final_score, 1),
                "price_score": round(price_score, 1),
                "speed_score": round(speed_score, 1),
                "quality_score": round(quality_score, 1)
            },
            "product_id": product.get("product_id", "unknown")
        })
    
    # Sort by final score (higher is better)
    ranked.sort(key=lambda x: x["scores"]["final_score"], reverse=True)
    
    # Update ranks
    for i, item in enumerate(ranked):
        item["rank"] = i + 1
    
    ranking_summary = [(p['platform'], f"{p['scores']['final_score']:.1f}") for p in ranked[:3]]
    print(f"   Final ranking: {ranking_summary}")
    
    # Add special note for single-option case
    single_option_note = ""
    if len(ranked) == 1:
        single_option_note = " (Only one option found - still presented for user decision)"
    
    # Find cheapest and fastest
    cheapest = min(ranked, key=lambda x: x["price"]) if ranked else None
    fastest = min(ranked, key=lambda x: x["delivery_time_hours"]) if ranked else None
    
    return {
        "comparison_summary": {
            "total_products_received": len(results),
            "products_after_filtering": len(ranked),
            "urgency_level": urgency_level,
            "fallback_mode": True,
            "scoring_weights": {
                "price": price_weight,
                "speed": speed_weight,
                "quality": quality_weight,
                "availability": availability_weight
            },
            "note": f"Using urgency-aware rule-based comparison{single_option_note}"
        },
        "ranked_products": ranked,
        "comparison_insights": {
            "cheapest_option": {
                "platform": cheapest["platform"] if cheapest else None,
                "price": cheapest["price"] if cheapest else None
            },
            "fastest_delivery": {
                "platform": fastest["platform"] if fastest else None,
                "hours": fastest["delivery_time_hours"] if fastest else None
            },
            "detected_tradeoffs": [
                {
                    "type": "price_vs_speed",
                    "description": f"Urgency level: {urgency_level} - {'Speed prioritized' if urgency_level in ['urgent', 'high'] else 'Price prioritized'}"
                }
            ],
            "recommendation_confidence": "medium",
            "single_option": len(ranked) == 1
        },
        "recommendation": {
            "top_choice": ranked[0] if ranked else None,
            "reason": f"Best option for {urgency_level} urgency (weighted scoring applied)"
        }
    }

def calculate_unit_price(price: float, quantity_str: str) -> Tuple[float, str]:
    """
    Calculate unit price from price and quantity string
    Returns: (unit_price, unit_label)
    """
    # Extract numeric quantity and unit
    quantity_match = re.search(r'(\d+\.?\d*)\s*(kg|g|l|ml|strip|unit|piece)', quantity_str.lower())
    
    if not quantity_match:
        return price, f"₹{price:.2f}/unit"
    
    qty_value = float(quantity_match.group(1))
    qty_unit = quantity_match.group(2)
    
    # Normalize to base units (kg for weight, l for volume)
    if qty_unit == 'g':
        qty_value = qty_value / 1000  # Convert to kg
        qty_unit = 'kg'
    elif qty_unit == 'ml':
        qty_value = qty_value / 1000  # Convert to l
        qty_unit = 'l'
    
    if qty_value > 0:
        unit_price = price / qty_value
        return unit_price, f"₹{unit_price:.2f}/{qty_unit}"
    
    return price, f"₹{price:.2f}/unit"

def normalize_quantity_to_kg(quantity_str: str) -> float:
    """Convert quantity string to float in kg/l"""
    quantity_match = re.search(r'(\d+\.?\d*)\s*(kg|g|l|ml|strip|unit|piece)', quantity_str.lower())
    
    if not quantity_match:
        return 1.0
    
    qty_value = float(quantity_match.group(1))
    qty_unit = quantity_match.group(2)
    
    if qty_unit == 'g':
        return qty_value / 1000
    elif qty_unit == 'ml':
        return qty_value / 1000
    elif qty_unit in ['kg', 'l']:
        return qty_value
    
    return 1.0  # For strips, units, pieces

def compare_products(search_results: Dict[str, Any]) -> Dict[str, Any]:
    """
    Main comparison function - analyzes search results and produces ranked comparison
    
    Args:
        search_results: Output from Search Agent
    
    Returns:
        Comprehensive comparison with rankings, scores, and insights
    """
    global chat_history
    
    # REAL AGENTIC SYSTEM: Retry with exponential backoff, fail transparently
    max_retries = 3
    retry_delay = 2
    
    for attempt in range(max_retries):
        try:
            # Convert search results to JSON string for the model
            search_json = json.dumps(search_results, ensure_ascii=False, indent=2)
            
            # Add user message to history
            chat_history.append({"role": "user", "parts": [{"text": search_json}]})
            
            # Call Gemini API with JSON mode
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=chat_history,
                config={
                    "temperature": 0.2,  # Lower temperature for more consistent JSON
                    "top_p": 0.95,
                    "top_k": 40,
                    "max_output_tokens": 8192,  # Increased to prevent truncation
                    "response_mime_type": "application/json",  # Force JSON
                }
            )
            
            response_text = response.text
            
            # Add model response to history
            chat_history.append({"role": "model", "parts": [{"text": response_text}]})
            
            # Clean and parse JSON
            cleaned_response = clean_json_response(response_text)
            parsed_output = json.loads(cleaned_response)
            
            # DEBUG: Print what we got
            ranked_count = len(parsed_output.get('ranked_products', []))
            print(f"🔍 DEBUG: Comparison returned {ranked_count} ranked products")
            if parsed_output.get('ranked_products'):
                print(f"🔍 DEBUG: First product: {parsed_output['ranked_products'][0].get('platform', 'Unknown')}")
            
            # CRITICAL FIX: If AI returned 0 products but we have search results, use fallback
            if ranked_count == 0 and search_results.get('results') and len(search_results.get('results', [])) > 0:
                print(f"⚠️ AI returned 0 products but we have {len(search_results['results'])} search results. Using fallback.")
                fallback_result = create_fallback_comparison(search_results)
                print(f"🔍 DEBUG: Fallback returned {len(fallback_result.get('ranked_products', []))} ranked products")
                return fallback_result
            
            # SUCCESS
            return parsed_output
            
        except json.JSONDecodeError as e:
            print(f"❌ COMPARISON AGENT: JSON parse error - {str(e)}")
            print(f"📄 Response preview: {response_text[:500] if 'response_text' in locals() else 'No response'}...")
            
            # Retry on JSON errors (could be temporary API issue)
            if attempt < max_retries - 1:
                print(f"🔄 Retrying... (attempt {attempt+2}/{max_retries})")
                import time
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
                continue
            
            # Final attempt failed - return error
            print(f"❌ All retry attempts exhausted. Using fallback comparison.")
            fallback_result = create_fallback_comparison(search_results)
            print(f"🔍 DEBUG: Fallback returned {len(fallback_result.get('ranked_products', []))} ranked products")
            return fallback_result
        
        except Exception as e:
            error_str = str(e)
            
            # Check if rate limit error
            if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str or "quota" in error_str.lower():
                if attempt < max_retries - 1:
                    import re
                    match = re.search(r'retry in (\d+)', error_str)
                    delay = int(match.group(1)) + 3 if match else 45
                    print(f"⏳ COMPARISON AGENT: Rate limit, waiting {delay}s... (attempt {attempt+1}/{max_retries})")
                    import time
                    time.sleep(min(delay, 60))
                    continue
                else:
                    print(f"❌ COMPARISON AGENT: Max retries reached")
                    return {
                        "status": "failed",
                        "error_type": "rate_limit_exhausted",
                        "agent": "comparison_agent",
                        "error_details": error_str,
                        "user_message": "❌ API limit exhausted. Retry after 30 minutes.",
                        "can_retry": True,
                        "retry_after_seconds": 1800,
                        "search_results_preserved": search_results,
                        "metadata": {
                            "timestamp": datetime.now().isoformat(),
                            "failure_reason": "rate_limit_exhausted_after_retries"
                        }
                    }
            else:
                print(f"❌ COMPARISON AGENT: API error - {error_str[:100]}")
                return {
                    "status": "failed",
                    "error_type": "api_error",
                    "agent": "comparison_agent",
                    "error_details": error_str,
                    "user_message": "❌ Comparison Agent API failed",
                    "can_retry": False,
                    "search_results_preserved": search_results,
                    "metadata": {
                        "timestamp": datetime.now().isoformat(),
                        "failure_reason": "api_error"
                    }
                }
    
    # Should never reach here
    return {
        "status": "failed",
        "error_type": "unknown",
        "agent": "comparison_agent",
        "user_message": "❌ Unknown error in Comparison Agent",
        "can_retry": False,
        "search_results_preserved": search_results,
        "metadata": {"timestamp": datetime.now().isoformat()}
    }

def pretty_print_comparison(comparison: Dict[str, Any]):
    """Display comparison results in a readable format"""
    print("\n" + "=" * 80)
    print("📊 COMPARISON ANALYSIS")
    print("=" * 80)
    
    # Summary
    summary = comparison.get("comparison_summary", {})
    print(f"\n📋 Summary:")
    print(f"   Total Products Received: {summary.get('total_products_received', 0)}")
    print(f"   Products After Filtering: {summary.get('products_after_filtering', 0)}")
    print(f"   Filtered Out: {summary.get('filtered_out_count', 0)}")
    if summary.get('filtered_reasons'):
        print(f"   Filter Reasons: {', '.join(summary['filtered_reasons'])}")
    print(f"   Urgency Level: {summary.get('urgency_level', 'N/A').upper()}")
    
    # Weights
    weights = summary.get('weights_applied', {})
    if weights:
        print(f"\n⚖️  Scoring Weights:")
        print(f"   Price: {weights.get('price', 0)*100:.0f}% | Speed: {weights.get('delivery_speed', 0)*100:.0f}% | "
              f"Quality: {weights.get('quality', 0)*100:.0f}% | Availability: {weights.get('availability', 0)*100:.0f}% | "
              f"Quantity Match: {weights.get('quantity_match', 0)*100:.0f}%")
    
    # Ranked products
    ranked = comparison.get("ranked_products", [])
    if ranked:
        print(f"\n🏆 RANKED PRODUCTS:")
        print("-" * 80)
        
        for product in ranked:
            rank = product.get("rank", "?")
            platform = product.get("platform", "Unknown")
            score = product.get("scores", {}).get("final_score", 0)
            
            identity = product.get("product_identity", {})
            attrs = product.get("normalized_attributes", {})
            flags = product.get("flags", [])
            
            print(f"\n  #{rank} — {platform} — Score: {score:.1f}/100")
            print(f"      Product: {identity.get('canonical_name', 'N/A')}")
            print(f"      Brand: {identity.get('brand', 'N/A')}")
            print(f"      Price: {attrs.get('unit_price_label', 'N/A')}")
            print(f"      Delivery: {attrs.get('delivery_time_label', 'N/A')}")
            print(f"      Rating: {attrs.get('rating', 'N/A')}★ ({attrs.get('reviews_count', 0)} reviews)")
            
            if flags:
                flag_icons = {
                    "best_overall": "🏆",
                    "best_price": "💰",
                    "fastest_delivery": "⚡",
                    "best_quality": "⭐",
                    "best_value": "💎"
                }
                flag_str = " ".join([f"{flag_icons.get(f, '🏷️')} {f.replace('_', ' ').title()}" for f in flags])
                print(f"      Flags: {flag_str}")
            
            explanation = product.get("explanation", "")
            if explanation:
                print(f"      💡 {explanation}")
            
            warnings = product.get("warnings", [])
            if warnings:
                print(f"      ⚠️  Warnings: {', '.join(warnings)}")
            
            tradeoffs = product.get("tradeoffs", [])
            if tradeoffs:
                print(f"      ⚖️  Tradeoffs: {', '.join(tradeoffs)}")
    
    # Insights
    insights = comparison.get("comparison_insights", {})
    if insights:
        print(f"\n💡 INSIGHTS:")
        
        price_range = insights.get("price_range", {})
        if price_range:
            print(f"   Price Range: ₹{price_range.get('min', 0):.2f} - ₹{price_range.get('max', 0):.2f} "
                  f"(Median: ₹{price_range.get('median', 0):.2f})")
        
        delivery_range = insights.get("delivery_range", {})
        if delivery_range:
            print(f"   Delivery Range: {delivery_range.get('fastest_hours', 0):.1f}h - "
                  f"{delivery_range.get('slowest_hours', 0):.1f}h "
                  f"(Median: {delivery_range.get('median_hours', 0):.1f}h)")
        
        quality_range = insights.get("quality_range", {})
        if quality_range:
            print(f"   Quality Range: {quality_range.get('lowest_rating', 0):.1f}★ - "
                  f"{quality_range.get('highest_rating', 0):.1f}★ "
                  f"(Average: {quality_range.get('average_rating', 0):.1f}★)")
        
        tradeoffs = insights.get("detected_tradeoffs", [])
        if tradeoffs:
            print(f"\n   ⚖️  Detected Tradeoffs:")
            for tradeoff in tradeoffs:
                print(f"      • {tradeoff.get('type', 'Unknown').replace('_', ' ').title()}")
                print(f"        {tradeoff.get('description', 'N/A')}")
        
        confidence = insights.get("recommendation_confidence", "unknown")
        confidence_icons = {
            "very_high": "🟢",
            "high": "🟢",
            "medium": "🟡",
            "low": "🟠",
            "very_low": "🔴",
            "none": "⚪"
        }
        print(f"\n   {confidence_icons.get(confidence, '⚪')} Recommendation Confidence: {confidence.upper()}")
    
    # Metadata
    metadata = comparison.get("metadata", {})
    if metadata:
        print(f"\n⏱️  Analysis Duration: {metadata.get('comparison_duration_ms', 0)}ms")
    
    print("=" * 80)

# ---------------- MAIN EXECUTION ---------------- #

if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    🧠 GANGU - Comparison Agent                               ║
║                    ───────────────────────────────                           ║
║           Converting raw search results into actionable intelligence         ║
║           Position: Search Agent → [YOU] → Decision Agent                    ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """)
    
    print("📌 MODES:")
    print("   1. Enter 'test' to run with sample search results")
    print("   2. Paste JSON from Search Agent directly")
    print("   3. Type 'quit' to exit")
    print("-" * 80)
    
    # Test example (from Search Agent output)
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
    
    # Interactive loop
    while True:
        try:
            print("\n📥 Enter search results JSON (or 'test' / 'quit'):")
            user_input = input(">>> ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['quit', 'exit', 'q', 'bye']:
                print("\n👋 Namaste! GANGU Comparison Agent signing off.")
                break
            
            if user_input.lower() == 'test':
                # Run test
                print("\n🧪 Running test with sample search results...")
                print(f"📥 Input: {json.dumps(test_search_result, ensure_ascii=False, indent=2)[:200]}...")
                
                comparison = compare_products(test_search_result)
                pretty_print_comparison(comparison)
                
                # Show raw JSON
                print(f"\n📨 Raw JSON Output for Decision Agent:")
                print(json.dumps(comparison, ensure_ascii=False, indent=2)[:500] + "...")
                continue
            
            # Try to parse as JSON
            try:
                search_data = json.loads(user_input)
            except json.JSONDecodeError:
                print("❌ Invalid JSON. Please paste valid search results JSON from Search Agent.")
                print("   Example format:")
                print('   {"search_query": {...}, "results": [...]}')
                continue
            
            # Run comparison
            comparison = compare_products(search_data)
            pretty_print_comparison(comparison)
            
            # Show the raw JSON that would go to Decision Agent
            print(f"\n📨 Output for Decision Agent:")
            print(json.dumps(comparison, ensure_ascii=False))
            
        except KeyboardInterrupt:
            print("\n\n👋 Namaste! GANGU Comparison Agent signing off.")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
