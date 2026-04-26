"""
🧠 GANGU - Intent & Extraction Agent
=====================================
The first brain layer of GANGU.
Converts unstructured human speech into structured, actionable intent.

Author: GANGU Team
"""

import json
import os
import time
import re
from pathlib import Path
from dotenv import load_dotenv

# Load .env from the GANGU root directory
gangu_root = Path(__file__).parent.parent
env_path = gangu_root / ".env"
load_dotenv(dotenv_path=env_path)

# Also try loading from current working directory
load_dotenv()

# Use the new google-genai package
from google import genai

# ---------------- API CONFIGURATION ---------------- #

# Use dedicated API key for Intent Extraction Agent (high usage)
api_key = os.environ.get('GEMINI_API_KEY_INTENT') or os.environ.get('GEMINI_API_KEY') or os.environ.get('GOOGLE_API_KEY')
if not api_key:
    raise ValueError("❌ GEMINI_API_KEY environment variable not set")

print(f"🔑 Intent Agent using API key: ...{api_key[-8:]}")

# Initialize the new GenAI client
client = genai.Client(api_key=api_key)

# ---------------- SYSTEM PROMPT ---------------- #

system_prompt = """
You are the **Intent & Extraction Agent** — the first brain layer of GANGU, an AI assistant designed for elderly Indian users.

## 🎯 YOUR ONLY JOB
Convert unstructured human speech into structured, machine-readable JSON.
You are a **gatekeeper** — you extract meaning, you do NOT make decisions.

## ⚠️ CRITICAL RULES

### What You MUST Do:
1. Extract the user's TRUE intent (even if not explicitly stated)
2. Identify the item/product mentioned
3. Detect quantity (use "1 unit" as default if not mentioned)
4. Assess urgency level from context
5. Handle Hindi, Hinglish, and English seamlessly
6. Interpret indirect/emotional speech (elderly users don't give commands)
7. Output ONLY valid JSON — no extra text, no explanations

### What You MUST NOT Do:
❌ Do NOT check prices
❌ Do NOT select platforms
❌ Do NOT make purchase decisions
❌ Do NOT plan tasks
❌ Do NOT add any text outside JSON
❌ Do NOT hallucinate items not mentioned

## 🧠 SEMANTIC UNDERSTANDING (Not Keyword Matching)

When user says indirect things, understand the REAL meaning:

| User Says | Real Meaning |
|-----------|--------------|
| "khatam ho gaye" | Need to buy/reorder |
| "nahi bachi" | Need to buy |
| "le aao" | Buy and deliver |
| "bas thodi si bachi hai" | Running low, need to buy |
| "ghar pe nahi hai" | Need to buy |

## 🏷️ INTENT CATEGORIES

Use these exact intent values:
- `buy_grocery` — Food items, kitchen supplies
- `buy_utility` — Household items, cleaning supplies
- `buy_medicine` — Medical/health products
- `buy_daily_essential` — Milk, bread, eggs, etc.
- `reorder` — Item they've bought before
- `inquiry` — Asking about something (not buying)
- `unclear` — Cannot determine intent

## 📊 OUTPUT JSON FORMAT (STRICT)

Always output in this EXACT format:
```json
{
  "intent": "buy_grocery | buy_utility | buy_medicine | buy_daily_essential | reorder | inquiry | unclear",
  "item": "extracted item name in English",
  "item_original": "item as user said it",
  "quantity": "amount with unit (default: 1 unit)",
  "urgency": "low | normal | high | urgent",
  "confidence": "low | medium | high",
  "needs_clarification": true/false,
  "clarification_question": "question to ask if needs_clarification is true, else null",
  "language_detected": "hindi | english | hinglish"
}
```

## 📝 EXAMPLES

### Example 1: Clear grocery request
User: "White chane khatam ho gaye"
```json
{
  "intent": "buy_grocery",
  "item": "white chickpeas",
  "item_original": "white chane",
  "quantity": "1 kg",
  "urgency": "normal",
  "confidence": "high",
  "needs_clarification": false,
  "clarification_question": null,
  "language_detected": "hinglish"
}
```

### Example 2: Indirect request
User: "Daal bas thodi si bachi hai"
```json
{
  "intent": "buy_grocery",
  "item": "dal",
  "item_original": "daal",
  "quantity": "1 kg",
  "urgency": "normal",
  "confidence": "high",
  "needs_clarification": true,
  "clarification_question": "Kaunsi daal chahiye? Arhar, moong, ya masoor?",
  "language_detected": "hindi"
}
```

### Example 3: Urgent request
User: "Gangu, doodh abhi chahiye"
```json
{
  "intent": "buy_daily_essential",
  "item": "milk",
  "item_original": "doodh",
  "quantity": "1 litre",
  "urgency": "urgent",
  "confidence": "high",
  "needs_clarification": false,
  "clarification_question": null,
  "language_detected": "hinglish"
}
```

### Example 4: Ambiguous request
User: "Kuch laana hai ghar ke liye"
```json
{
  "intent": "unclear",
  "item": null,
  "item_original": null,
  "quantity": null,
  "urgency": "normal",
  "confidence": "low",
  "needs_clarification": true,
  "clarification_question": "Kya laana hai? Grocery, medicine, ya kuch aur?",
  "language_detected": "hindi"
}
```

### Example 5: Medicine request
User: "Sar dard ki goli chahiye"
```json
{
  "intent": "buy_medicine",
  "item": "headache medicine",
  "item_original": "sar dard ki goli",
  "quantity": "1 strip",
  "urgency": "high",
  "confidence": "high",
  "needs_clarification": false,
  "clarification_question": null,
  "language_detected": "hindi"
}
```

## 🎤 REMEMBER
- Elderly users speak INDIRECTLY
- "Shortage" = "Need to buy"
- Always be empathetic in clarification questions
- Use respectful Hindi for clarification questions
- ONLY output JSON, nothing else

Now process the user's input and extract intent.
"""

# ---------------- MODEL INITIALIZATION ---------------- #

# Model name for the new API
MODEL_NAME = "gemini-2.5-flash"

# Chat history to maintain context
chat_history = [
    {"role": "user", "parts": [{"text": system_prompt}]},
    {"role": "model", "parts": [{"text": "Understood. I am the Intent & Extraction Agent for GANGU. I will extract intent from user speech and output only structured JSON. Ready to process."}]}
]

# ---------------- HELPER FUNCTIONS ---------------- #

def clean_json_response(response_text: str) -> str:
    """Extract JSON from response, handling markdown code blocks"""
    text = response_text.strip()
    
    # Remove markdown code blocks
    if "```json" in text:
        text = text.split("```json")[1].split("```")[0].strip()
    elif "```" in text:
        text = text.split("```")[1].split("```")[0].strip()
    
    return text

def simple_fallback_parser(user_input: str) -> dict:
    """Simple rule-based parser for common grocery items"""
    text_lower = user_input.lower()
    
    # Common items
    items = {
        "rice": ["rice", "chawal"], "dal": ["dal"], "atta": ["atta", "flour"],
        "besan": ["besan", "gram flour"], "milk": ["milk", "doodh"],
        "bread": ["bread"], "oil": ["oil", "tel"], "sugar": ["sugar", "chini"],
        "salt": ["salt", "namak"], "onion": ["onion", "pyaz"],
        "potato": ["potato", "aloo"], "tomato": ["tomato", "tamatar"],
        "eggs": ["egg", "anda"], "paneer": ["paneer"], "curd": ["curd", "dahi"],
        "ghee": ["ghee"], "butter": ["butter"], "tea": ["tea", "chai"]
    }
    
    detected_item = None
    for standard, variants in items.items():
        if any(v in text_lower for v in variants):
            detected_item = standard
            break
    
    if not detected_item:
        return None
    
    buy_keywords = ["khatam", "order", "buy", "le ao", "lao", "chahiye", "mangao", "want", "need", "get", "from zepto", "through zepto"]
    has_buy_intent = any(kw in text_lower for kw in buy_keywords)
    
    urgent_keywords = ["urgent", "jaldi", "abhi", "turant"]
    urgency = "high" if any(kw in text_lower for kw in urgent_keywords) else "normal"
    
    return {
        "intent": "buy_grocery" if has_buy_intent else "query_product_info",
        "item": detected_item,
        "item_original": user_input,
        "quantity": "1 unit",
        "urgency": urgency,
        "confidence": "medium",
        "needs_clarification": False,
        "clarification_question": None,
        "language_detected": "hinglish",
        "fallback_mode": True
    }

def extract_intent(user_input: str) -> dict:
    """
    Main function to extract intent from user input.
    Returns structured JSON output.
    """
    global chat_history
    
    # Try fallback parser first if API might be rate-limited
    fallback = simple_fallback_parser(user_input)
    
    try:
        # Add user message to history
        chat_history.append({"role": "user", "parts": [{"text": user_input}]})
        
        # Call the new API
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=chat_history,
            config={
                "temperature": 0.1,  # Low temperature for consistent extraction
                "top_p": 0.95,
                "top_k": 40,
                "max_output_tokens": 1024,
            }
        )
        
        response_text = response.text
        
        # Add model response to history
        chat_history.append({"role": "model", "parts": [{"text": response_text}]})
        
        cleaned_response = clean_json_response(response_text)
        parsed_output = json.loads(cleaned_response)
        return parsed_output
    except json.JSONDecodeError as e:
        if fallback:
            return fallback
        return {
            "intent": "unclear",
            "item": None,
            "item_original": None,
            "quantity": None,
            "urgency": "normal",
            "confidence": "low",
            "needs_clarification": True,
            "clarification_question": "Mujhe samajh nahi aaya. Kya aap phir se bata sakte hain?",
            "language_detected": "unknown",
            "error": f"JSON parsing failed: {str(e)}"
        }
    except Exception as e:
        if fallback:
            return fallback
        return {
            "intent": "unclear",
            "item": None,
            "item_original": None,
            "quantity": None,
            "urgency": "normal",
            "confidence": "low",
            "needs_clarification": True,
            "clarification_question": "Kuch gadbad ho gayi. Kya aap phir se bol sakte hain?",
            "language_detected": "unknown",
            "error": str(e)
        }

def pretty_print_result(result: dict):
    """Display extracted intent in a readable format"""
    print("\n" + "=" * 50)
    print("📤 EXTRACTED INTENT")
    print("=" * 50)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    print("=" * 50)
    
    # Human readable summary
    if result.get("intent") != "unclear":
        print(f"\n🎯 Intent: {result.get('intent', 'N/A')}")
        print(f"📦 Item: {result.get('item', 'N/A')} ({result.get('item_original', '')})")
        print(f"📊 Quantity: {result.get('quantity', 'N/A')}")
        print(f"⚡ Urgency: {result.get('urgency', 'N/A')}")
        print(f"✅ Confidence: {result.get('confidence', 'N/A')}")
        
    if result.get("needs_clarification"):
        print(f"\n❓ Clarification Needed: {result.get('clarification_question', '')}")

# ---------------- MAIN EXECUTION ---------------- #

if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════╗
║        🧠 GANGU - Intent & Extraction Agent                  ║
║        ─────────────────────────────────────────             ║
║        Converting speech to structured intent                ║
║        Supports: Hindi | English | Hinglish                  ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    # Test examples
    # test_inputs = [
    #     "White chane khatam ho gaye",
    #     "Gangu, doodh le aao",
    #     "Ghar pe cheeni nahi bachi",
    #     "Order atta",
    #     "Sar dard ki goli chahiye",
    #     "Daal bas thodi si bachi hai"
    # ]
    
    # print("📋 Running test examples first...\n")
    # print("-" * 50)
    
    # for test_input in test_inputs[:2]:  # Run 2 tests
    #     print(f"\n🗣️ User: \"{test_input}\"")
    #     result = extract_intent(test_input)
    #     pretty_print_result(result)
    #     print()
    
    # print("\n" + "=" * 50)
    # print("🚀 Interactive Mode - Enter your queries")
    # print("=" * 50)
    # print("(Type 'quit' or 'exit' to stop)\n")
    
    # Interactive loop
    while True:
        try:
            user_input = input("🗣️ You: ").strip()
            
            if not user_input:
                continue
                
            if user_input.lower() in ['quit', 'exit', 'q', 'bye']:
                print("\n👋 Namaste! GANGU Intent Agent signing off.")
                break
            
            result = extract_intent(user_input)
            pretty_print_result(result)
            
            # Show the raw JSON that would go to Task Planner
            print(f"\n📨 Output for Task Planner Agent:")
            print(json.dumps(result, ensure_ascii=False))
            
        except KeyboardInterrupt:
            print("\n\n👋 Namaste! GANGU Intent Agent signing off.")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
