"""
🧠 GANGU - Search Agent
========================
The eyes and ears of GANGU.
Retrieves and normalizes raw product data across platforms.

Pipeline Position:
    Task Planner → Search Agent (YOU) → Compare Agent → Decision Agent

Author: GANGU Team
"""

import json
import os
from pathlib import Path
from dotenv import load_dotenv
from typing import Dict, List, Any
import asyncio
import sys

# Load .env from the same directory as this script
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

# Also try loading from current working directory
load_dotenv()

# Use the new google-genai package
from google import genai

# Try to import Zepto MCP client
try:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from zepto_mcp_client import ZeptoMCPClient
    ZEPTO_MCP_AVAILABLE = True
    print("✅ Zepto MCP client loaded successfully")
except ImportError as e:
    ZEPTO_MCP_AVAILABLE = False
    print(f"⚠️ Zepto MCP client not available: {e}")

# ---------------- API CONFIGURATION ---------------- #

api_key = os.environ.get('GEMINI_API_KEY') or os.environ.get('GOOGLE_API_KEY')
if not api_key:
    raise ValueError("❌ GEMINI_API_KEY or GOOGLE_API_KEY environment variable not set")

# Initialize the new GenAI client
client = genai.Client(api_key=api_key)

# ---------------- SYSTEM PROMPT ---------------- #

system_prompt = """
You are the **Search Agent** — the eyes and ears of GANGU, an AI assistant designed for elderly Indian users.

## 🎯 YOUR ONLY JOB
Retrieve and normalize raw product data across multiple platforms.
You are a **data collector** — you find facts, you do NOT judge, compare, or decide.

## 📍 YOUR POSITION IN GANGU PIPELINE
```
Task Planner → Search Agent (YOU) → Compare Agent → Decision Agent
```

You receive PLANNED ACTIONS from Task Planner.
You output RAW, NORMALIZED DATA for Compare Agent.

## ⚠️ CRITICAL RULES

### What You MUST Do:
1. Search the requested item across ALL available platforms
2. Collect ONLY factual data (price, availability, delivery time, ratings)
3. Normalize data into a uniform schema regardless of platform
4. Return ALL options found (even if price is high, rating is low)
5. Handle failures gracefully (report unavailability)
6. Use RAG ONLY for synonym resolution (chana = chickpeas)
7. Output ONLY valid JSON — no extra text, no explanations

### What You MUST NOT Do:
❌ Do NOT compare prices
❌ Do NOT rank options
❌ Do NOT recommend platforms
❌ Do NOT make decisions
❌ Do NOT filter results based on quality
❌ Do NOT add opinions or judgments
❌ Do NOT hallucinate data
❌ Do NOT add text outside JSON

## 🏗️ PLATFORM SEARCH STRATEGY

For each search query:
1. Identify item name and quantity
2. Query ALL available platforms in parallel
3. Collect raw response from each
4. Normalize into common schema
5. Return exhaustive results

## 📊 OUTPUT JSON FORMAT (STRICT)

Always output in this EXACT format:
```json
{
  "search_query": {
    "item": "item name",
    "quantity": "amount with unit",
    "urgency": "urgency level"
  },
  "platforms_searched": ["Platform_A", "Platform_B", "Platform_C"],
  "total_results_found": 3,
  "results": [
    {
      "platform": "Platform_A",
      "item_name": "normalized item name",
      "brand": "brand name if available",
      "price": 95.00,
      "currency": "INR",
      "quantity": "1 kg",
      "availability": true,
      "stock_status": "in_stock",
      "delivery_time_hours": 48,
      "rating": 4.2,
      "reviews_count": 5100,
      "seller": "seller name",
      "product_url": "url if available",
      "last_updated": "timestamp"
    }
  ],
  "failed_platforms": [
    {
      "platform": "Platform_D",
      "availability": false,
      "reason": "Item not listed"
    }
  ],
  "search_metadata": {
    "timestamp": "ISO timestamp",
    "search_duration_ms": 1200,
    "synonyms_used": ["chana", "chickpeas", "kabuli chana"]
  }
}
```

## 🔍 DATA NORMALIZATION RULES

### Price Normalization:
- Convert all to INR
- Use float format (95.00 not "₹95")
- Include delivery charges if mentioned

### Availability Normalization:
- `true` = in stock and purchasable
- `false` = out of stock or not listed

### Delivery Time Normalization:
- Convert to hours (integer)
- "Same day" = 6 hours
- "Next day" = 24 hours
- "2-3 days" = 60 hours (average)

### Rating Normalization:
- Convert all to 5-point scale
- If 10-point, divide by 2
- If percentage, divide by 20

### Stock Status:
- `in_stock` = Available now
- `low_stock` = Limited quantity
- `out_of_stock` = Not available
- `not_listed` = Product doesn't exist on platform

## 📝 EXAMPLES

### Example 1: Standard Grocery Search
**Input:**
```json
{
  "action": "search_all_platforms",
  "item": "white chickpeas",
  "quantity": "1 kg",
  "urgency": "normal"
}
```

**Output:**
```json
{
  "search_query": {
    "item": "white chickpeas",
    "quantity": "1 kg",
    "urgency": "normal"
  },
  "platforms_searched": ["Blinkit", "Zepto", "BigBasket", "Amazon Fresh"],
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
      "reviews_count": 2800,
      "seller": "Blinkit",
      "product_url": "https://blinkit.com/...",
      "last_updated": "2026-01-12T10:30:00Z"
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
      "reviews_count": 5100,
      "seller": "BigBasket",
      "product_url": "https://bigbasket.com/...",
      "last_updated": "2026-01-12T10:30:00Z"
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
      "reviews_count": 1200,
      "seller": "Zepto",
      "product_url": "https://zepto.com/...",
      "last_updated": "2026-01-12T10:30:00Z"
    }
  ],
  "failed_platforms": [
    {
      "platform": "Amazon Fresh",
      "availability": false,
      "reason": "Service not available in user's area"
    }
  ],
  "search_metadata": {
    "timestamp": "2026-01-12T10:30:00Z",
    "search_duration_ms": 1200,
    "synonyms_used": ["white chickpeas", "kabuli chana", "safed chana"]
  }
}
```

### Example 2: Urgent Medicine Search
**Input:**
```json
{
  "action": "search_all_platforms",
  "item": "paracetamol 500mg",
  "quantity": "1 strip",
  "urgency": "urgent"
}
```

**Output:**
```json
{
  "search_query": {
    "item": "paracetamol 500mg",
    "quantity": "1 strip",
    "urgency": "urgent"
  },
  "platforms_searched": ["PharmEasy", "1mg", "Apollo 24/7", "Netmeds"],
  "total_results_found": 4,
  "results": [
    {
      "platform": "PharmEasy",
      "item_name": "Dolo 500mg Tablet",
      "brand": "Dolo",
      "price": 15.00,
      "currency": "INR",
      "quantity": "1 strip (15 tablets)",
      "availability": true,
      "stock_status": "in_stock",
      "delivery_time_hours": 2,
      "rating": 4.8,
      "reviews_count": 12000,
      "seller": "PharmEasy",
      "product_url": "https://pharmeasy.in/...",
      "last_updated": "2026-01-12T10:30:00Z"
    },
    {
      "platform": "1mg",
      "item_name": "Crocin 500mg",
      "brand": "Crocin",
      "price": 18.00,
      "currency": "INR",
      "quantity": "1 strip (15 tablets)",
      "availability": true,
      "stock_status": "in_stock",
      "delivery_time_hours": 3,
      "rating": 4.7,
      "reviews_count": 8500,
      "seller": "1mg",
      "product_url": "https://1mg.com/...",
      "last_updated": "2026-01-12T10:30:00Z"
    },
    {
      "platform": "Apollo 24/7",
      "item_name": "Paracetamol 500mg",
      "brand": "Apollo",
      "price": 12.00,
      "currency": "INR",
      "quantity": "1 strip (10 tablets)",
      "availability": true,
      "stock_status": "in_stock",
      "delivery_time_hours": 4,
      "rating": 4.5,
      "reviews_count": 6200,
      "seller": "Apollo Pharmacy",
      "product_url": "https://apollo247.com/...",
      "last_updated": "2026-01-12T10:30:00Z"
    },
    {
      "platform": "Netmeds",
      "item_name": "Calpol 500mg",
      "brand": "Calpol",
      "price": 16.50,
      "currency": "INR",
      "quantity": "1 strip (15 tablets)",
      "availability": true,
      "stock_status": "in_stock",
      "delivery_time_hours": 6,
      "rating": 4.6,
      "reviews_count": 4800,
      "seller": "Netmeds",
      "product_url": "https://netmeds.com/...",
      "last_updated": "2026-01-12T10:30:00Z"
    }
  ],
  "failed_platforms": [],
  "search_metadata": {
    "timestamp": "2026-01-12T10:30:00Z",
    "search_duration_ms": 800,
    "synonyms_used": ["paracetamol", "acetaminophen"]
  }
}
```

## 🎤 REMEMBER
- Collect, don't judge
- All platforms are equal
- Normalize everything
- Return ALL results
- No filtering, no opinions
- Be exhaustive and boring
- Let Compare Agent decide

Now process the search request and return raw, normalized data.
"""

# ---------------- MODEL INITIALIZATION ---------------- #

MODEL_NAME = "gemini-2.5-flash"

# Chat history to maintain context
chat_history = [
    {"role": "user", "parts": [{"text": system_prompt}]},
    {"role": "model", "parts": [{"text": "Understood. I am the Search Agent for GANGU. I will search all platforms, collect raw factual data, normalize it into a uniform schema, and return exhaustive results without any judgment or comparison. Ready to search."}]}
]

# ---------------- MOCK PLATFORM DATA (Phase-1) ---------------- #

# In production, this will be replaced with actual API calls/scrapers
MOCK_PLATFORM_DATA = {
    "grocery": {
        "white chickpeas": {
            "Blinkit": {
                "item_name": "White Chickpeas (Kabuli Chana)",
                "brand": "Farm Fresh",
                "price": 110.00,
                "delivery_time": "12 hours",
                "rating": 4.6,
                "reviews_count": 2800,
                "availability": True,
                "stock": "in_stock"
            },
            "BigBasket": {
                "item_name": "Kabuli Chana White",
                "brand": "Fresho",
                "price": 95.00,
                "delivery_time": "2 days",
                "rating": 4.2,
                "reviews_count": 5100,
                "availability": True,
                "stock": "in_stock"
            },
            "Zepto": {
                "item_name": "White Chana Premium",
                "brand": "Nature's Basket",
                "price": 120.00,
                "delivery_time": "10 hours",
                "rating": 4.7,
                "reviews_count": 1200,
                "availability": True,
                "stock": "low_stock"
            },
            "Amazon Fresh": {
                "availability": False,
                "reason": "Service not available in user's area"
            }
        },
        "rice": {
            "Blinkit": {
                "item_name": "Basmati Rice Premium",
                "brand": "India Gate",
                "price": 450.00,
                "delivery_time": "12 hours",
                "rating": 4.5,
                "reviews_count": 8900,
                "availability": True,
                "stock": "in_stock"
            },
            "BigBasket": {
                "item_name": "Basmati Rice Classic",
                "brand": "India Gate",
                "price": 420.00,
                "delivery_time": "1 day",
                "rating": 4.4,
                "reviews_count": 12000,
                "availability": True,
                "stock": "in_stock"
            },
            "Zepto": {
                "item_name": "Premium Basmati",
                "brand": "Daawat",
                "price": 480.00,
                "delivery_time": "8 hours",
                "rating": 4.6,
                "reviews_count": 5600,
                "availability": True,
                "stock": "in_stock"
            }
        },
        "milk": {
            "Blinkit": {
                "item_name": "Toned Milk",
                "brand": "Amul",
                "price": 28.00,
                "delivery_time": "30 minutes",
                "rating": 4.8,
                "reviews_count": 15000,
                "availability": True,
                "stock": "in_stock"
            },
            "Zepto": {
                "item_name": "Fresh Toned Milk",
                "brand": "Mother Dairy",
                "price": 27.00,
                "delivery_time": "20 minutes",
                "rating": 4.7,
                "reviews_count": 12000,
                "availability": True,
                "stock": "in_stock"
            },
            "BigBasket": {
                "item_name": "Toned Milk",
                "brand": "Nandini",
                "price": 26.00,
                "delivery_time": "4 hours",
                "rating": 4.5,
                "reviews_count": 8500,
                "availability": True,
                "stock": "in_stock"
            }
        }
    },
    "medicine": {
        "paracetamol": {
            "PharmEasy": {
                "item_name": "Dolo 500mg Tablet",
                "brand": "Dolo",
                "price": 15.00,
                "delivery_time": "2 hours",
                "rating": 4.8,
                "reviews_count": 12000,
                "availability": True,
                "stock": "in_stock"
            },
            "1mg": {
                "item_name": "Crocin 500mg",
                "brand": "Crocin",
                "price": 18.00,
                "delivery_time": "3 hours",
                "rating": 4.7,
                "reviews_count": 8500,
                "availability": True,
                "stock": "in_stock"
            },
            "Apollo 24/7": {
                "item_name": "Paracetamol 500mg",
                "brand": "Apollo",
                "price": 12.00,
                "delivery_time": "4 hours",
                "rating": 4.5,
                "reviews_count": 6200,
                "availability": True,
                "stock": "in_stock"
            },
            "Netmeds": {
                "item_name": "Calpol 500mg",
                "brand": "Calpol",
                "price": 16.50,
                "delivery_time": "6 hours",
                "rating": 4.6,
                "reviews_count": 4800,
                "availability": True,
                "stock": "in_stock"
            }
        }
    }
}

# Item synonyms for better search
ITEM_SYNONYMS = {
    "white chickpeas": ["kabuli chana", "safed chana", "white chana"],
    "rice": ["chawal", "basmati rice"],
    "milk": ["doodh"],
    "paracetamol": ["acetaminophen", "dolo", "crocin"],
    "dal": ["lentils", "daal"],
    "atta": ["wheat flour", "flour"]
}

# ---------------- HELPER FUNCTIONS ---------------- #

def normalize_delivery_time(delivery_str: str) -> int:
    """Convert delivery time string to hours"""
    delivery_str = delivery_str.lower()
    
    if "minute" in delivery_str or "min" in delivery_str:
        return 1  # Less than an hour
    elif "hour" in delivery_str:
        return int(delivery_str.split()[0])
    elif "day" in delivery_str:
        days = delivery_str.split()[0]
        if "-" in days:
            days = days.split("-")[0]
        return int(days) * 24
    else:
        return 24  # Default 1 day

def get_item_category(intent: str) -> str:
    """Determine category from intent"""
    if "medicine" in intent:
        return "medicine"
    else:
        return "grocery"

def find_item_in_mock_data(item: str, category: str) -> tuple:
    """Find item in mock data, handling synonyms"""
    item_lower = item.lower()
    
    # Direct match
    if item_lower in MOCK_PLATFORM_DATA.get(category, {}):
        return item_lower, []
    
    # Check synonyms
    for base_item, synonyms in ITEM_SYNONYMS.items():
        if item_lower in synonyms or item_lower == base_item:
            if base_item in MOCK_PLATFORM_DATA.get(category, {}):
                return base_item, synonyms
    
    return None, []


async def search_zepto_mcp(item_name: str) -> dict:
    """
    Search Zepto using MCP server - REAL DATA!
    Returns real product data from Zepto
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    server_path = os.path.join(script_dir, "zepto-cafe-mcp", "zepto_mcp_server.py")
    
    if not os.path.exists(server_path):
        raise FileNotFoundError(
            f"Zepto MCP server not found at {server_path}. "
            f"Run setup_zepto_mcp.ps1 first."
        )
    
    client = ZeptoMCPClient(server_path)
    
    try:
        await client.connect()
        result = await client.search_product(item_name)
        await client.disconnect()
        
        # Transform MCP result to GANGU format
        if result.get("found"):
            return {
                "platform": "Zepto",
                "found": True,
                "item_name": result.get("product_name"),
                "price": result.get("estimated_price", "₹30-60"),
                "availability": True,
                "stock_status": result.get("availability", "In Stock"),
                "delivery_time": result.get("delivery_time", "10-15 min"),
                "url": result.get("url"),
                "rating": 4.5,
                "reviews_count": 500,
                "elderly_friendly": True,
                "source": "mcp_server",
                "brand": "Zepto",
                "currency": "INR"
            }
        else:
            return {
                "platform": "Zepto",
                "found": False,
                "message": result.get("message"),
                "source": "mcp_server"
            }
    except Exception as e:
        raise Exception(f"Zepto MCP search failed: {e}")

def search_platforms(search_input: Dict[str, Any]) -> Dict[str, Any]:
    """
    Main search function - searches all platforms and returns normalized results
    NOW WITH ZEPTO MCP INTEGRATION!
    """
    import time
    from datetime import datetime
    
    start_time = time.time()
    
    item = search_input.get("item", "").lower()
    quantity = search_input.get("quantity", "1 unit")
    urgency = search_input.get("urgency", "normal")
    intent = search_input.get("intent", "buy_grocery")
    
    # Try Zepto MCP first if available
    zepto_mcp_result = None
    if ZEPTO_MCP_AVAILABLE:
        try:
            print("📡 Attempting Zepto MCP search...")
            zepto_mcp_result = asyncio.run(search_zepto_mcp(item))
            print(f"✅ Zepto MCP: {'Found' if zepto_mcp_result.get('found') else 'Not found'}")
        except Exception as e:
            print(f"⚠️ Zepto MCP error: {e}, falling back to mock data")
    
    # Determine category
    category = get_item_category(intent)
    
    # Find item in mock data (with synonym support)
    base_item, synonyms_used = find_item_in_mock_data(item, category)
    
    # If Zepto MCP found the item but mock data didn't, use Zepto result
    if zepto_mcp_result and zepto_mcp_result.get("found") and not base_item:
        return {
            "search_query": {
                "item": item,
                "quantity": quantity,
                "urgency": urgency
            },
            "platforms_searched": ["Zepto"],
            "total_results_found": 1,
            "results": [zepto_mcp_result],
            "failed_platforms": [],
            "search_metadata": {
                "timestamp": datetime.now().isoformat(),
                "search_duration_ms": int((time.time() - start_time) * 1000),
                "synonyms_used": [item],
                "zepto_mcp_used": True
            }
        }
    
    if not base_item:
        # Item not found in any platform
        return {
            "search_query": {
                "item": item,
                "quantity": quantity,
                "urgency": urgency
            },
            "platforms_searched": ["Zepto"] if zepto_mcp_result else [],
            "total_results_found": 0,
            "results": [],
            "failed_platforms": [
                {
                    "platform": "All Platforms",
                    "availability": False,
                    "reason": "Item not found in any platform"
                }
            ],
            "search_metadata": {
                "timestamp": datetime.now().isoformat(),
                "search_duration_ms": int((time.time() - start_time) * 1000),
                "synonyms_used": []
            }
        }
    
    # Get platform data
    platform_data = MOCK_PLATFORM_DATA[category][base_item]
    
    results = []
    failed_platforms = []
    platforms_searched = []
    
    # Add Zepto MCP result first if available and found
    if zepto_mcp_result and zepto_mcp_result.get("found"):
        results.append(zepto_mcp_result)
        platforms_searched.append("Zepto")
        print("✅ Added Zepto MCP result to results")
    
    # Process other platforms from mock data
    for platform_name, platform_info in platform_data.items():
        platforms_searched.append(platform_name)
        
        if not platform_info.get("availability", True):
            # Platform failed
            failed_platforms.append({
                "platform": platform_name,
                "availability": False,
                "reason": platform_info.get("reason", "Unknown error")
            })
        else:
            # Normalize and add result
            result = {
                "platform": platform_name,
                "item_name": platform_info["item_name"],
                "brand": platform_info["brand"],
                "price": platform_info["price"],
                "currency": "INR",
                "quantity": quantity,
                "availability": True,
                "stock_status": platform_info["stock"],
                "delivery_time_hours": normalize_delivery_time(platform_info["delivery_time"]),
                "rating": platform_info["rating"],
                "reviews_count": platform_info["reviews_count"],
                "seller": platform_name,
                "product_url": f"https://{platform_name.lower().replace(' ', '')}.com/product/{base_item.replace(' ', '-')}",
                "last_updated": datetime.now().isoformat()
            }
            results.append(result)
    
    # Calculate search duration
    search_duration = int((time.time() - start_time) * 1000)
    
    # Build final output
    output = {
        "search_query": {
            "item": item,
            "quantity": quantity,
            "urgency": urgency
        },
        "platforms_searched": platforms_searched,
        "total_results_found": len(results),
        "results": results,
        "failed_platforms": failed_platforms,
        "search_metadata": {
            "timestamp": datetime.now().isoformat(),
            "search_duration_ms": search_duration,
            "synonyms_used": [item] + synonyms_used if synonyms_used else [item]
        }
    }
    
    return output

def clean_json_response(response_text: str) -> str:
    """Extract JSON from response, handling markdown code blocks"""
    text = response_text.strip()
    
    # Remove markdown code blocks
    if "```json" in text:
        text = text.split("```json")[1].split("```")[0].strip()
    elif "```" in text:
        text = text.split("```")[1].split("```")[0].strip()
    
    return text

def pretty_print_results(search_output: Dict[str, Any]):
    """Display search results in a readable format"""
    print("\n" + "=" * 70)
    print("🔍 SEARCH RESULTS")
    print("=" * 70)
    
    query = search_output.get("search_query", {})
    print(f"\n📦 Search Query:")
    print(f"   Item: {query.get('item', 'N/A')}")
    print(f"   Quantity: {query.get('quantity', 'N/A')}")
    print(f"   Urgency: {query.get('urgency', 'N/A')}")
    
    print(f"\n🌐 Platforms Searched: {', '.join(search_output.get('platforms_searched', []))}")
    print(f"✅ Results Found: {search_output.get('total_results_found', 0)}")
    
    if search_output.get("results"):
        print(f"\n📊 DETAILED RESULTS:")
        print("-" * 70)
        for i, result in enumerate(search_output["results"], 1):
            print(f"\n{i}. {result['platform']}")
            print(f"   Product: {result['item_name']} ({result['brand']})")
            print(f"   Price: ₹{result['price']}")
            print(f"   Delivery: {result['delivery_time_hours']} hours")
            print(f"   Rating: {result['rating']}/5.0 ({result['reviews_count']} reviews)")
            print(f"   Stock: {result['stock_status']}")
    
    if search_output.get("failed_platforms"):
        print(f"\n❌ FAILED PLATFORMS:")
        for failed in search_output["failed_platforms"]:
            print(f"   • {failed['platform']}: {failed['reason']}")
    
    metadata = search_output.get("search_metadata", {})
    print(f"\n⏱️ Search Duration: {metadata.get('search_duration_ms', 0)}ms")
    print(f"🔤 Synonyms Used: {', '.join(metadata.get('synonyms_used', []))}")
    print("=" * 70)

# ---------------- MAIN EXECUTION ---------------- #

if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════╗
║        🧠 GANGU - Search Agent                               ║
║        ─────────────────────────────────────────             ║
║        Retrieving & normalizing product data                 ║
║        Position: Task Planner → [YOU] → Compare Agent       ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    print("📌 MODES:")
    print("   1. Enter 'test' to run with sample search requests")
    print("   2. Paste JSON from Task Planner step execution")
    print("   3. Type 'quit' to exit")
    print("-" * 60)
    
    # Test examples
    test_searches = [
        {
            "action": "search_all_platforms",
            "item": "white chickpeas",
            "quantity": "1 kg",
            "urgency": "normal",
            "intent": "buy_grocery"
        },
        {
            "action": "search_all_platforms",
            "item": "paracetamol",
            "quantity": "1 strip",
            "urgency": "urgent",
            "intent": "buy_medicine"
        },
        {
            "action": "search_all_platforms",
            "item": "milk",
            "quantity": "1 litre",
            "urgency": "high",
            "intent": "buy_daily_essential"
        }
    ]
    
    # Interactive loop
    while True:
        try:
            print("\n📥 Enter search request JSON (or 'test' / 'quit'):")
            user_input = input(">>> ").strip()
            
            if not user_input:
                continue
                
            if user_input.lower() in ['quit', 'exit', 'q', 'bye']:
                print("\n👋 Namaste! GANGU Search Agent signing off.")
                break
            
            if user_input.lower() == 'test':
                # Run test examples
                print("\n🧪 Running test searches...")
                for i, test_search in enumerate(test_searches[:2], 1):  # Run first 2 tests
                    print(f"\n--- Test {i} ---")
                    print(f"📥 Input: {json.dumps(test_search, ensure_ascii=False)}")
                    search_output = search_platforms(test_search)
                    pretty_print_results(search_output)
                continue
            
            # Try to parse as JSON
            try:
                search_input = json.loads(user_input)
            except json.JSONDecodeError:
                print("❌ Invalid JSON. Please paste valid search request JSON.")
                print("   Example format:")
                print('   {"action": "search_all_platforms", "item": "rice", "quantity": "5 kg", "urgency": "normal", "intent": "buy_grocery"}')
                continue
            
            # Perform search
            search_output = search_platforms(search_input)
            pretty_print_results(search_output)
            
            # Show the raw JSON that would go to Compare Agent
            print(f"\n📨 Output for Compare Agent:")
            print(json.dumps(search_output, ensure_ascii=False, indent=2))
            
        except KeyboardInterrupt:
            print("\n\n👋 Namaste! GANGU Search Agent signing off.")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
