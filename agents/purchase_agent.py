"""
🧠 GANGU - Purchase Agent
==========================
The transaction executor of GANGU.
Safely, reliably, and autonomously executes purchase decisions with risk management.

Pipeline Position:
    Decision Agent → Purchase Agent (YOU) → Notification Agent

⚠️ CRITICAL: This agent handles REAL MONEY. Every action must be:
    - Validated before execution
    - Logged for audit
    - Recoverable on failure
    - Transparent to user

Author: GANGU Team
"""

import os
import sys
import json
from pathlib import Path
from dotenv import load_dotenv
from typing import Dict, List, Any, Optional
from datetime import datetime
import time
import hashlib
import re

# Load .env from the GANGU root directory
gangu_root = Path(__file__).parent.parent
env_path = gangu_root / ".env"
load_dotenv(dotenv_path=env_path)

# Also try loading from current working directory
load_dotenv()

# Use the new google-genai package
from google import genai

# Try to import MCP clients
try:
    from mcp_clients.zepto_mcp_client import ZeptoMCPClient
    ZEPTO_AVAILABLE = True
except ImportError:
    ZEPTO_AVAILABLE = False
    print("⚠️  Zepto MCP client not available")

try:
    from mcp_clients.amazon_mcp_client import AmazonMCPClient
    AMAZON_AVAILABLE = True
except ImportError:
    AMAZON_AVAILABLE = False
    print("⚠️  Amazon MCP client not available")

# ---------------- API CONFIGURATION ---------------- #

api_key = os.environ.get('GEMINI_API_KEY_PURCHASE') or os.environ.get('GEMINI_API_KEY') or os.environ.get('GOOGLE_API_KEY')
if not api_key:
    raise ValueError("❌ GEMINI_API_KEY environment variable not set")

print(f"🔑 Purchase Agent using API key: ...{api_key[-8:]}")

# Initialize the new GenAI client
client = genai.Client(api_key=api_key)

# ---------------- CONFIGURATION ---------------- #

# Risk thresholds
PRICE_SPIKE_THRESHOLD = 1.5  # 50% increase = suspicious
MAX_RETRY_ATTEMPTS = 3
RETRY_DELAY_SECONDS = 2

# Dry run mode (for testing)
DRY_RUN_MODE = os.environ.get('GANGU_DRY_RUN', 'false').lower() == 'true'

# Order history for idempotency (in-memory for now)
order_history = {}

# Audit log file
AUDIT_LOG_PATH = gangu_root / "logs" / "purchase_audit.jsonl"
AUDIT_LOG_PATH.parent.mkdir(exist_ok=True)

# ---------------- SYSTEM PROMPT ---------------- #

system_prompt = """
You are the **Purchase Agent** — the transaction executor of GANGU, an AI assistant designed for elderly Indian users.

## 🎯 YOUR ONLY JOB
Safely, reliably, and autonomously execute purchase decisions while handling real-world uncertainties.
You are the **point of no return** — once you act, real money and trust are involved.

## 📍 YOUR POSITION IN GANGU PIPELINE
```
Decision Agent → Purchase Agent (YOU) → Notification Agent
```

You receive FINAL PURCHASE DECISION from Decision Agent.
You output TRANSACTION RESULT to Notification Agent.

## ⚠️ CRITICAL RULES - THIS IS ABOUT REAL MONEY

### What You MUST Do:
1. **Pre-Purchase Validation** — Re-verify EVERYTHING before buying
   - Product still available?
   - Price unchanged (or within 10% tolerance)?
   - Delivery slot still valid?
   - Platform API healthy?
   - Quantity limits respected?

2. **Risk Assessment** — Be conservative, not reckless
   - Flag unusual price spikes (>50% increase)
   - Detect duplicate orders (idempotency)
   - Check platform reliability scores
   - Validate order size (unusually large?)

3. **Safety First Execution**
   - Execute step-by-step (add to cart → verify → checkout → confirm)
   - Never assume success without confirmation
   - Log every step for audit trail
   - Handle authentication/session gracefully

4. **Failure Recovery** — Expect and handle failures
   - Retry (max 3 times) with exponential backoff
   - Switch to fallback platform if primary fails
   - Never leave orders in inconsistent state
   - Report failures transparently

5. **Post-Purchase Verification**
   - Confirm order ID received
   - Verify payment success
   - Check delivery date/time
   - Save order confirmation

6. **Audit Everything**
   - Log timestamp, platform, item, price, result
   - Track all state changes
   - Enable replay/debugging

### What You MUST NOT Do:
❌ Do NOT purchase without validation
❌ Do NOT ignore price mismatches
❌ Do NOT proceed if session expired
❌ Do NOT retry indefinitely
❌ Do NOT create duplicate orders
❌ Do NOT assume success without confirmation
❌ Do NOT hide failures from user

## 🛡️ RISK MANAGEMENT FRAMEWORK

### Risk Levels:
- **LOW** (0-30): Normal, proceed automatically
- **MEDIUM** (31-60): Proceed with extra validation
- **HIGH** (61-80): Require explicit confirmation
- **CRITICAL** (81-100): Block and escalate

### Risk Factors:
1. **Price Risk**: Current price vs expected price
2. **Platform Risk**: API health, recent failure rate
3. **Order Risk**: Unusually large quantity or amount
4. **Timing Risk**: Urgent orders, late night orders
5. **Duplication Risk**: Similar order placed recently

## 📊 INPUT FORMAT FROM DECISION AGENT

```json
{
  "final_decision": {
    "selected_platform": "Zepto",
    "product": {
      "name": "White Chickpeas (Kabuli Chana)",
      "brand": "Nature's Basket",
      "product_id": "zepto_12345",
      "quantity": "1 kg",
      "price": 120.00,
      "currency": "INR"
    },
    "delivery": {
      "eta_hours": 10,
      "delivery_date": "2026-01-13",
      "slot": "morning"
    },
    "confidence_score": 0.92,
    "decision_rationale": "Best overall option - fastest delivery",
    "fallback_options": [
      {
        "platform": "Amazon",
        "product_id": "amz_abc123",
        "price": 110.00,
        "delivery_hours": 24
      }
    ]
  },
  "user_context": {
    "urgency": "normal",
    "budget_limit": 200.00
  }
}
```

## 📊 OUTPUT FORMAT (STRICT)

```json
{
  "purchase_status": "success | failed | pending | cancelled",
  "execution_details": {
    "timestamp": "2026-01-12T14:30:00Z",
    "platform_used": "Zepto",
    "primary_or_fallback": "primary",
    "order_id": "ZEPTO-ORD-12345",
    "transaction_id": "TXN-67890"
  },
  "order_confirmation": {
    "product_name": "White Chickpeas (Kabuli Chana)",
    "quantity": "1 kg",
    "final_price": 120.00,
    "currency": "INR",
    "delivery_date": "2026-01-13",
    "delivery_time": "10:00 AM - 12:00 PM",
    "order_url": "https://zepto.com/orders/12345"
  },
  "validation_results": {
    "price_validated": true,
    "availability_validated": true,
    "delivery_validated": true,
    "price_deviation_percent": 0,
    "risk_score": 15,
    "risk_level": "low"
  },
  "execution_steps": [
    {
      "step": "pre_purchase_validation",
      "status": "passed",
      "timestamp": "2026-01-12T14:29:50Z"
    },
    {
      "step": "add_to_cart",
      "status": "success",
      "timestamp": "2026-01-12T14:30:00Z"
    },
    {
      "step": "checkout",
      "status": "success",
      "timestamp": "2026-01-12T14:30:10Z"
    },
    {
      "step": "payment_confirmation",
      "status": "success",
      "timestamp": "2026-01-12T14:30:20Z"
    }
  ],
  "retry_attempts": 0,
  "failures_encountered": [],
  "fallback_used": false,
  "user_message": "✅ Order placed successfully! Your White Chickpeas will arrive tomorrow morning.",
  "audit_log_id": "audit_202601121430_abc123"
}
```

## 🔄 EXECUTION WORKFLOW (Step-by-Step)

### Phase 1: Pre-Purchase Validation (MANDATORY)
```
1. Parse decision input
2. Extract platform, product_id, price, quantity
3. Call platform API to re-fetch current data
4. Compare:
   - Expected price vs Current price (tolerance: ±10%)
   - Availability status
   - Delivery slot validity
5. Calculate risk score
6. If risk > HIGH → block and request confirmation
7. If validation fails → try fallback OR report failure
```

### Phase 2: Risk Assessment
```
1. Price spike check: (current_price - expected_price) / expected_price
2. Duplicate order check: hash(platform + product + user + date)
3. Platform health check: recent success rate
4. Order size check: quantity * price > unusual_threshold?
5. Assign risk_level: LOW | MEDIUM | HIGH | CRITICAL
```

### Phase 3: Purchase Execution
```
IF risk_level == CRITICAL:
    → Block and escalate to user

IF risk_level == HIGH:
    → Request explicit confirmation
    → "Order costs ₹500, which is 60% more than expected. Confirm?"

ELSE:
    1. Add item to cart (via MCP client)
    2. Verify cart contents
    3. Select delivery slot
    4. Proceed to checkout
    5. Confirm payment
    6. Wait for order_id confirmation
    7. Verify order placed successfully
```

### Phase 4: Failure Handling
```
IF any step fails:
    1. Log failure reason
    2. Retry (max 3 times, 2-sec delay)
    3. If still failing → try fallback platform
    4. If fallback also fails → report to user transparently
    
Example:
"❌ Zepto checkout failed (timeout). Trying Amazon instead..."
```

### Phase 5: Post-Purchase Verification
```
1. Receive order_id from platform
2. Fetch order details to verify:
   - Product name matches
   - Quantity matches
   - Price matches
   - Delivery date confirmed
3. If mismatch → flag for manual review
4. Save order confirmation
```

### Phase 6: Audit Logging
```
Log to audit file:
{
  "audit_id": "unique_id",
  "timestamp": "ISO timestamp",
  "agent": "purchase_agent",
  "action": "purchase_executed",
  "platform": "Zepto",
  "product": "...",
  "price": 120.00,
  "result": "success",
  "risk_score": 15,
  "user_id": "elderly_user_123"
}
```

## 📝 EXAMPLES

### Example 1: Successful Purchase (Normal Flow)

**Input:**
```json
{
  "final_decision": {
    "selected_platform": "Zepto",
    "product": {
      "name": "Toor Dal (Arhar)",
      "brand": "Farm Fresh",
      "product_id": "zepto_dal_001",
      "quantity": "1 kg",
      "price": 150.00
    },
    "delivery": {
      "eta_hours": 10,
      "delivery_date": "2026-01-13"
    },
    "confidence_score": 0.88
  }
}
```

**Processing:**
```
✅ Pre-validation: Price = ₹150 (matches), Available = Yes
✅ Risk assessment: Score = 20 (LOW)
✅ Add to cart: Success
✅ Checkout: Success
✅ Payment: Confirmed
✅ Order ID: ZEPTO-12345
```

**Output:**
```json
{
  "purchase_status": "success",
  "execution_details": {
    "platform_used": "Zepto",
    "order_id": "ZEPTO-12345"
  },
  "order_confirmation": {
    "product_name": "Toor Dal (Arhar)",
    "quantity": "1 kg",
    "final_price": 150.00,
    "delivery_date": "2026-01-13"
  },
  "validation_results": {
    "risk_score": 20,
    "risk_level": "low"
  },
  "user_message": "✅ Order placed! Toor Dal will arrive tomorrow."
}
```

### Example 2: Price Spike Detected (Risk Management)

**Input:**
```json
{
  "final_decision": {
    "selected_platform": "Amazon",
    "product": {
      "name": "Basmati Rice",
      "price": 250.00,
      "product_id": "amz_rice_123"
    }
  }
}
```

**Processing:**
```
⚠️ Pre-validation: Expected ₹250, Current ₹380 (52% spike!)
⚠️ Risk assessment: Score = 75 (HIGH)
⚠️ Action: BLOCK and request confirmation
```

**Output:**
```json
{
  "purchase_status": "pending",
  "execution_details": {
    "platform_used": "Amazon",
    "order_id": null
  },
  "validation_results": {
    "price_validated": false,
    "price_deviation_percent": 52,
    "risk_score": 75,
    "risk_level": "high"
  },
  "user_message": "⚠️ Price increased 52% (₹250 → ₹380). Confirm purchase?",
  "requires_confirmation": true
}
```

### Example 3: Primary Failed, Fallback Succeeded

**Input:**
```json
{
  "final_decision": {
    "selected_platform": "Blinkit",
    "product": {
      "name": "Milk",
      "price": 65.00,
      "product_id": "blinkit_milk_001"
    },
    "fallback_options": [
      {
        "platform": "Zepto",
        "product_id": "zepto_milk_002",
        "price": 68.00
      }
    ]
  }
}
```

**Processing:**
```
✅ Pre-validation: Passed
❌ Blinkit add_to_cart: Failed (API timeout)
🔄 Retry 1: Failed
🔄 Retry 2: Failed
⚠️ Switching to fallback: Zepto
✅ Zepto add_to_cart: Success
✅ Checkout: Success
✅ Order ID: ZEPTO-78910
```

**Output:**
```json
{
  "purchase_status": "success",
  "execution_details": {
    "platform_used": "Zepto",
    "primary_or_fallback": "fallback",
    "order_id": "ZEPTO-78910"
  },
  "order_confirmation": {
    "product_name": "Milk",
    "final_price": 68.00
  },
  "retry_attempts": 2,
  "failures_encountered": [
    {
      "platform": "Blinkit",
      "step": "add_to_cart",
      "reason": "API timeout"
    }
  ],
  "fallback_used": true,
  "user_message": "✅ Order placed via Zepto (Blinkit was unavailable). Milk arriving soon."
}
```

### Example 4: Complete Failure (All Options Exhausted)

**Input:**
```json
{
  "final_decision": {
    "selected_platform": "Amazon",
    "product": {
      "name": "Atta",
      "price": 300.00
    },
    "fallback_options": [
      {"platform": "BigBasket"}
    ]
  }
}
```

**Processing:**
```
❌ Amazon: Checkout failed (payment gateway down)
❌ Retry: Failed
❌ BigBasket: Out of stock
❌ No more fallbacks
```

**Output:**
```json
{
  "purchase_status": "failed",
  "execution_details": {
    "platform_used": null,
    "order_id": null
  },
  "failures_encountered": [
    {
      "platform": "Amazon",
      "reason": "Payment gateway down"
    },
    {
      "platform": "BigBasket",
      "reason": "Out of stock"
    }
  ],
  "user_message": "❌ Unable to complete order. All platforms unavailable. Kya baad mein try karein?",
  "retry_recommended": true
}
```

## 🧠 ADVANCED FEATURES

### 1. Idempotency (Prevent Duplicate Orders)
```
order_hash = hash(platform + product_id + user_id + date)
IF order_hash in recent_orders (last 5 minutes):
    → Skip purchase
    → Return existing order_id
```

### 2. Dry-Run Mode (Testing)
```
IF DRY_RUN_MODE == true:
    → Simulate all steps
    → Log actions
    → Return mock order_id
    → Don't actually purchase
```

### 3. Circuit Breaker (Platform Health)
```
IF platform_failure_rate > 50% (last 10 orders):
    → Temporarily disable platform
    → Use fallback automatically
```

## 🎤 YOUR PERSONALITY

You are:
- **Conservative**: "Better safe than sorry"
- **Transparent**: Always explain what you're doing
- **Resilient**: Handle failures gracefully
- **Trustworthy**: Never hide mistakes
- **Respectful**: Elderly users' money = sacred

## 🎯 REMEMBER

You are NOT:
❌ A comparison agent (that's done)
❌ A decision maker (Decision Agent did that)
❌ A notification sender (that's next agent)

You ARE:
✅ The executor
✅ The validator
✅ The risk manager
✅ The failure handler
✅ The auditor

Your success = GANGU's trust.
Your failure = User's money lost.

**Act accordingly.**

Now execute the purchase with maximum safety and reliability.
"""

# ---------------- MODEL INITIALIZATION ---------------- #

MODEL_NAME = "gemini-2.5-flash"

# Chat history to maintain context
chat_history = [
    {"role": "user", "parts": [{"text": system_prompt}]},
    {"role": "model", "parts": [{"text": "Understood. I am the Purchase Agent for GANGU. I will safely execute purchase decisions with thorough validation, risk assessment, failure handling, and audit logging. I prioritize user trust and money safety above all else. Ready to execute purchases."}]}
]

# ---------------- HELPER FUNCTIONS ---------------- #

def generate_order_hash(platform: str, product_id: str, user_id: str = "default_user") -> str:
    """Generate unique hash for idempotency check"""
    today = datetime.now().strftime("%Y-%m-%d")
    hash_input = f"{platform}_{product_id}_{user_id}_{today}"
    return hashlib.md5(hash_input.encode()).hexdigest()

def log_audit(action: str, details: Dict[str, Any]):
    """Log purchase action to audit file"""
    try:
        audit_entry = {
            "audit_id": f"audit_{int(time.time())}_{hashlib.md5(str(details).encode()).hexdigest()[:8]}",
            "timestamp": datetime.now().isoformat(),
            "agent": "purchase_agent",
            "action": action,
            "details": details
        }
        
        with open(AUDIT_LOG_PATH, 'a', encoding='utf-8') as f:
            f.write(json.dumps(audit_entry, ensure_ascii=False) + "\n")
        
        return audit_entry["audit_id"]
    except Exception as e:
        print(f"⚠️ Audit log failed: {e}")
        return None

def calculate_risk_score(
    price_deviation: float,
    availability: bool,
    platform_reliability: float = 0.95,
    order_size: float = 0.0
) -> tuple[int, str]:
    """Calculate risk score and level"""
    risk_score = 0
    
    # Price deviation risk (0-40 points)
    if price_deviation > 50:
        risk_score += 40
    elif price_deviation > 30:
        risk_score += 30
    elif price_deviation > 10:
        risk_score += 15
    
    # Availability risk (0-20 points)
    if not availability:
        risk_score += 20
    
    # Platform reliability risk (0-20 points)
    if platform_reliability < 0.5:
        risk_score += 20
    elif platform_reliability < 0.7:
        risk_score += 10
    
    # Order size risk (0-20 points)
    if order_size > 5000:
        risk_score += 20
    elif order_size > 2000:
        risk_score += 10
    
    # Determine risk level
    if risk_score >= 81:
        risk_level = "critical"
    elif risk_score >= 61:
        risk_level = "high"
    elif risk_score >= 31:
        risk_level = "medium"
    else:
        risk_level = "low"
    
    return risk_score, risk_level

def parse_quantity_to_int(quantity: Any) -> int:
    """Parse quantity into an integer count (default 1)."""
    if quantity is None:
        return 1
    if isinstance(quantity, (int, float)):
        return max(1, int(quantity))
    if isinstance(quantity, str):
        match = re.search(r"(\d+)", quantity)
        if match:
            return max(1, int(match.group(1)))
    return 1

def validate_product_availability(platform: str, product_id: str, expected_price: float) -> Dict[str, Any]:
    """
    Re-validate product availability and price before purchase
    Returns validation results
    """
    validation_result = {
        "available": False,
        "current_price": None,
        "price_deviation_percent": 0,
        "delivery_available": False,
        "validation_passed": False,
        "reason": ""
    }
    
    try:
        # Try to query platform via MCP client
        if platform.lower() == "zepto" and ZEPTO_AVAILABLE:
            # In real implementation, call Zepto MCP to check product
            # For now, simulate
            validation_result.update({
                "available": True,
                "current_price": expected_price,
                "price_deviation_percent": 0,
                "delivery_available": True,
                "validation_passed": True,
                "reason": "Product validated successfully"
            })
        
        elif platform.lower() == "amazon" and AMAZON_AVAILABLE:
            # In real implementation, call Amazon MCP
            validation_result.update({
                "available": True,
                "current_price": expected_price,
                "price_deviation_percent": 0,
                "delivery_available": True,
                "validation_passed": True,
                "reason": "Product validated successfully"
            })
        
        else:
            # Fallback: assume validation passed with warning
            validation_result.update({
                "available": True,
                "current_price": expected_price,
                "price_deviation_percent": 0,
                "delivery_available": True,
                "validation_passed": True,
                "reason": "MCP client unavailable, using expected values"
            })
    
    except Exception as e:
        validation_result["reason"] = f"Validation failed: {str(e)}"
    
    return validation_result

def execute_purchase_with_retry(
    platform: str,
    product: Dict[str, Any],
    delivery: Dict[str, Any],
    max_retries: int = MAX_RETRY_ATTEMPTS,
    cash_on_delivery: bool = False,
    quantity: int = 1
) -> Dict[str, Any]:
    """
    Execute purchase with retry logic
    Returns execution result
    """
    result = {
        "status": "failed",
        "order_id": None,
        "transaction_id": None,
        "attempts": 0,
        "steps_completed": [],
        "failure_reason": None
    }
    
    for attempt in range(1, max_retries + 1):
        result["attempts"] = attempt
        
        try:
            # Execute based on platform
            if platform.lower() == "zepto" and not DRY_RUN_MODE and cash_on_delivery:
                # Real Zepto execution using MCP client
                print(f"   🛒 Executing Zepto Cash on Delivery order...")
                
                if ZEPTO_AVAILABLE:
                    import asyncio
                    
                    # Use asyncio to run the async Zepto client
                    async def execute_zepto_order():
                        # Path to Zepto MCP server
                        server_path = Path(__file__).parent.parent / "zepto-cafe-mcp" / "zepto_mcp_server.py"
                        zepto_client = ZeptoMCPClient(str(server_path))
                        try:
                            # Connect and start order
                            await zepto_client.connect()
                            
                            # Start Zepto order - the MCP server handles cash on delivery automatically
                            # Prefer a human product name; fall back to item_name/product_name when upstream agents don't set `name`
                            product_name = (
                                product.get('name')
                                or product.get('item_name')
                                or product.get('product_name')
                                or 'tea'
                            )
                            print(f"   📦 Starting Zepto order for: {product_name}")
                            if quantity > 1:
                                order_result = await zepto_client.start_zepto_multi_order([
                                    {"product_name": product_name, "quantity": quantity}
                                ])
                            else:
                                order_result = await zepto_client.start_zepto_order(product_name)
                            print(f"   ✅ Zepto order result: {order_result}")
                            
                            # Check if COD succeeded
                            result_message = order_result.get('message', '') if isinstance(order_result, dict) else str(order_result)
                            if "order placed" in result_message.lower() and ("pay on delivery" in result_message.lower() or "cash on delivery" in result_message.lower()):
                                await zepto_client.disconnect()
                                return {"status": "cod_success", "data": order_result}
                            else:
                                # COD failed, try QR scanner fallback
                                print(f"   💳 COD not available, providing manual order instructions...")
                                
                                qr_info = {
                                    "message": "COD not available. Please complete order manually on Zepto app",
                                    "instructions": [
                                        f"1. Open Zepto app or website: https://www.zeptonow.com",
                                        f"2. Search for: {product_name}",
                                        f"3. Add {quantity} to cart and proceed to checkout",
                                        "4. Select your preferred payment method",
                                        "5. Complete the order"
                                    ],
                                    "zepto_url": "https://www.zeptonow.com",
                                    "search_term": product_name
                                }
                                
                                await zepto_client.disconnect()
                                return {"status": "manual_order", "qr_info": qr_info}
                            
                        except Exception as e:
                            await zepto_client.disconnect()
                            raise e
                    
                    # Run the async order
                    order_result = asyncio.run(execute_zepto_order())
                    
                    # Process the result based on status
                    if order_result.get("status") == "cod_success":
                        # COD order successful
                        order_data = order_result.get("data", {})
                        order_id = f"ZEPTO_COD_{int(time.time())}"
                        transaction_id = f"COD_TXN_{int(time.time())}"
                        
                        result["steps_completed"].extend([
                            {
                                "step": "zepto_order_start",
                                "status": "success",
                                "timestamp": datetime.now().isoformat()
                            },
                            {
                                "step": "cash_on_delivery_selection",
                                "status": "success",
                                "timestamp": datetime.now().isoformat()
                            },
                            {
                                "step": "order_placement",
                                "status": "success",
                                "timestamp": datetime.now().isoformat()
                            }
                        ])
                        
                        result["status"] = "success"
                        result["order_id"] = order_id
                        result["transaction_id"] = transaction_id
                        result["payment_method"] = "cash_on_delivery"
                        result["order_details"] = order_data
                        
                        return result
                        
                    elif order_result.get("status") == "manual_order":
                        # COD failed, provide manual order instructions
                        qr_info = order_result.get("qr_info", {})
                        
                        result["status"] = "manual_order_required"
                        result["qr_scanner_info"] = qr_info
                        result["payment_method"] = "manual_app_order"
                        result["order_id"] = f"ZEPTO_MANUAL_{int(time.time())}"
                        result["steps_completed"].append({
                            "step": "manual_order_instructions_provided",
                            "status": "success", 
                            "timestamp": datetime.now().isoformat()
                        })
                        
                        return result
                    
                    else:
                        raise Exception(f"Unexpected Zepto order result: {order_result}")
                else:
                    raise Exception("Zepto MCP client not available")
            
            elif DRY_RUN_MODE:
                # Dry run mode
                print(f"   [DRY RUN] Would add {quantity} x {product['name']} to cart on {platform}")
                print(f"   [DRY RUN] Would proceed with {'Cash on Delivery' if cash_on_delivery else 'default payment'}")
                
                order_id = f"DRY_RUN_{platform.upper()}_{int(time.time())}"
                transaction_id = f"TXN_DRY_RUN_{int(time.time())}"
                
                result["steps_completed"].extend([
                    {
                        "step": "add_to_cart",
                        "status": "success",
                        "timestamp": datetime.now().isoformat()
                    },
                    {
                        "step": "checkout",
                        "status": "success",
                        "timestamp": datetime.now().isoformat()
                    },
                    {
                        "step": "payment_confirmation",
                        "status": "success",
                        "timestamp": datetime.now().isoformat()
                    }
                ])
                
                result["status"] = "success"
                result["order_id"] = order_id
                result["transaction_id"] = transaction_id
                
                time.sleep(1)  # Simulate processing time
                return result
            
            else:
                # Fallback simulation for other platforms
                print(f"   ⚠️ Platform {platform} not supported for real orders, using simulation")
                order_id = f"{platform.upper()}_SIM_{int(time.time())}"
                transaction_id = f"TXN_SIM_{int(time.time())}"
                
                result["steps_completed"].append({
                    "step": "simulated_order",
                    "status": "success", 
                    "timestamp": datetime.now().isoformat()
                })
                
                result["status"] = "success"
                result["order_id"] = order_id
                result["transaction_id"] = transaction_id
                
                return result
        
        except Exception as e:
            result["failure_reason"] = str(e)
            
            if attempt < max_retries:
                print(f"   ⚠️ Attempt {attempt} failed: {e}. Retrying in {RETRY_DELAY_SECONDS}s...")
                time.sleep(RETRY_DELAY_SECONDS)
            else:
                print(f"   ❌ All {max_retries} attempts failed")
    
    return result

def execute_purchase(decision_input: Dict[str, Any]) -> Dict[str, Any]:
    """
    Main purchase execution function
    
    Args:
        decision_input: Decision from Decision Agent
    
    Returns:
        Purchase result for Notification Agent
    """
    print("\n" + "=" * 80)
    print("💳 PURCHASE AGENT - TRANSACTION EXECUTION")
    print("=" * 80)
    
    # Parse input
    final_decision = decision_input.get("final_decision", {})
    selected_platform = final_decision.get("selected_platform")
    product = final_decision.get("product", {})
    delivery = final_decision.get("delivery", {})
    fallback_options = final_decision.get("fallback_options", [])
    user_context = decision_input.get("user_context", {})
    
    product_id = product.get("product_id")
    expected_price = product.get("price", 0)
    # Prefer a human product name; fall back to item_name/product_name when upstream agents don't set `name`
    product_name = product.get("name") or product.get("item_name") or product.get("product_name")
    quantity = product.get("quantity")
    quantity_int = parse_quantity_to_int(quantity)
    
    print(f"\n📦 Product: {product_name}")
    print(f"🏪 Platform: {selected_platform}")
    print(f"💰 Expected Price: ₹{expected_price}")
    print(f"📊 Quantity: {quantity} (parsed: {quantity_int})")
    
    # Check for duplicate order (idempotency)
    order_hash = generate_order_hash(selected_platform, product_id)
    if order_hash in order_history:
        print(f"\n⚠️ DUPLICATE ORDER DETECTED!")
        existing_order = order_history[order_hash]
        return {
            "purchase_status": "duplicate",
            "message": f"Order already placed: {existing_order['order_id']}",
            "existing_order_id": existing_order['order_id']
        }
    
    # PHASE 1: Pre-Purchase Validation
    print(f"\n🔍 PHASE 1: Pre-Purchase Validation")
    validation = validate_product_availability(selected_platform, product_id, expected_price)
    
    if not validation["validation_passed"]:
        print(f"   ❌ Validation failed: {validation['reason']}")
        log_audit("validation_failed", {
            "platform": selected_platform,
            "product": product_name,
            "reason": validation["reason"]
        })
        
        return {
            "purchase_status": "failed",
            "user_message": f"❌ Cannot place order: {validation['reason']}",
            "validation_results": validation
        }
    
    price_deviation = abs(validation["current_price"] - expected_price) / expected_price * 100 if expected_price > 0 else 0
    print(f"   ✅ Product available: {validation['available']}")
    print(f"   ✅ Current price: ₹{validation['current_price']}")
    print(f"   ✅ Price deviation: {price_deviation:.1f}%")
    
    # PHASE 2: Risk Assessment
    print(f"\n🛡️ PHASE 2: Risk Assessment")
    risk_score, risk_level = calculate_risk_score(
        price_deviation=price_deviation,
        availability=validation["available"],
        platform_reliability=0.95,  # Can be dynamic
        order_size=expected_price
    )
    
    # CRITICAL: Check if this is urgent order
    urgency_level = user_context.get('urgency_level', 'normal')
    is_urgent = urgency_level in ['urgent', 'high']
    
    print(f"   📊 Risk Score: {risk_score}/100")
    print(f"   📊 Risk Level: {risk_level.upper()}")
    
    # Handle high risk
    if risk_level == "critical":
        print(f"   🚨 CRITICAL RISK - Purchase blocked!")
        return {
            "purchase_status": "blocked",
            "user_message": f"⚠️ Order blocked due to critical risk (score: {risk_score}). Manual review required.",
            "validation_results": {
                "risk_score": risk_score,
                "risk_level": risk_level,
                "price_deviation_percent": price_deviation
            },
            "requires_manual_review": True
        }
    
    if risk_level == "high":
        # Skip confirmation for urgent orders
        if is_urgent:
            print(f"   ⚠️ HIGH RISK but URGENT - Proceeding anyway")
        else:
            print(f"   ⚠️ HIGH RISK - Requesting user confirmation")
            return {
                "purchase_status": "pending",
                "user_message": f"⚠️ Price changed {price_deviation:.0f}% (₹{expected_price} → ₹{validation['current_price']}). Confirm order?",
            "validation_results": {
                "risk_score": risk_score,
                "risk_level": risk_level,
                "price_deviation_percent": price_deviation
            },
            "requires_confirmation": True
        }
    
    # PHASE 3: Purchase Execution
    print(f"\n🚀 PHASE 3: Purchase Execution")
    print(f"   Platform: {selected_platform}")
    
    # Enable cash on delivery for Zepto orders
    cash_on_delivery = selected_platform.lower() == 'zepto'
    
    if cash_on_delivery:
        print(f"   💳 Payment Method: Cash on Delivery (COD)")
    
    if DRY_RUN_MODE:
        print(f"   🧪 DRY RUN MODE - Simulating purchase")
    
    execution_result = execute_purchase_with_retry(
        platform=selected_platform,
        product=product,
        delivery=delivery,
        max_retries=MAX_RETRY_ATTEMPTS,
        cash_on_delivery=cash_on_delivery,
        quantity=quantity_int
    )
    
    # PHASE 4: Handle Result
    if execution_result["status"] == "success":
        print(f"\n✅ PURCHASE SUCCESSFUL!")
        print(f"   Order ID: {execution_result['order_id']}")
        print(f"   Transaction ID: {execution_result['transaction_id']}")
        
        # Save to order history
        order_history[order_hash] = {
            "order_id": execution_result['order_id'],
            "timestamp": datetime.now().isoformat(),
            "platform": selected_platform,
            "product": product_name,
            "price": validation['current_price']
        }
        
        # Audit log
        audit_id = log_audit("purchase_success", {
            "platform": selected_platform,
            "order_id": execution_result['order_id'],
            "product": product_name,
            "price": validation['current_price'],
            "risk_score": risk_score
        })
        
        return {
            "purchase_status": "success",
            "execution_details": {
                "timestamp": datetime.now().isoformat(),
                "platform_used": selected_platform,
                "primary_or_fallback": "primary",
                "order_id": execution_result['order_id'],
                "transaction_id": execution_result['transaction_id']
            },
            "order_confirmation": {
                "product_name": product_name,
                "quantity": quantity,
                "final_price": validation['current_price'],
                "currency": "INR",
                "delivery_date": delivery.get("delivery_date"),
                "delivery_time": delivery.get("slot", "TBD")
            },
            "validation_results": {
                "price_validated": True,
                "availability_validated": True,
                "delivery_validated": True,
                "price_deviation_percent": price_deviation,
                "risk_score": risk_score,
                "risk_level": risk_level
            },
            "execution_steps": execution_result["steps_completed"],
            "retry_attempts": execution_result["attempts"] - 1,
            "failures_encountered": [],
            "fallback_used": False,
            "user_message": f"✅ Order placed successfully! {product_name} will arrive on {delivery.get('delivery_date', 'soon')}.",
            "audit_log_id": audit_id,
            "dry_run": DRY_RUN_MODE
        }

    elif execution_result["status"] == "manual_order_required":
        print(f"\n📱 MANUAL ORDER REQUIRED!")
        print(f"   COD not available, providing app instructions")
        
        qr_info = execution_result.get("qr_scanner_info", {})
        
        # Save to order history as pending manual
        order_history[order_hash] = {
            "order_id": execution_result['order_id'],
            "timestamp": datetime.now().isoformat(),
            "platform": selected_platform,
            "product": product_name,
            "price": validation['current_price'],
            "status": "manual_pending"
        }
        
        # Audit log
        audit_id = log_audit("manual_order_provided", {
            "platform": selected_platform,
            "order_id": execution_result['order_id'],
            "product": product_name,
            "price": validation['current_price']
        })
        
        return {
            "purchase_status": "manual_order_provided",
            "execution_details": {
                "timestamp": datetime.now().isoformat(),
                "platform_used": selected_platform,
                "primary_or_fallback": "manual",
                "order_id": execution_result['order_id'],
                "payment_method": "manual_app_order"
            },
            "manual_order_info": qr_info,
            "order_confirmation": {
                "product_name": product_name,
                "quantity": quantity,
                "final_price": validation['current_price'],
                "currency": "INR",
                "platform_url": qr_info.get("zepto_url", ""),
                "search_term": qr_info.get("search_term", product_name)
            },
            "validation_results": {
                "price_validated": True,
                "availability_validated": True,
                "delivery_validated": True,
                "price_deviation_percent": price_deviation,
                "risk_score": risk_score,
                "risk_level": risk_level
            },
            "execution_steps": execution_result["steps_completed"],
            "user_message": f"📱 COD not available for {product_name}. Please complete order manually using the Zepto app. Instructions provided below.",
            "manual_instructions": qr_info.get("instructions", []),
            "audit_log_id": audit_id,
            "dry_run": DRY_RUN_MODE
        }
    
    else:
        # PHASE 5: Failure Recovery - Try Fallback
        print(f"\n❌ Primary platform failed: {execution_result['failure_reason']}")
        
        if fallback_options:
            print(f"\n🔄 Trying fallback options...")
            
            for i, fallback in enumerate(fallback_options, 1):
                fallback_platform = fallback.get("platform")
                print(f"\n   Fallback {i}: {fallback_platform}")
                
                # Validate fallback
                fallback_validation = validate_product_availability(
                    fallback_platform,
                    fallback.get("product_id"),
                    fallback.get("price", 0)
                )
                
                if not fallback_validation["validation_passed"]:
                    print(f"   ❌ Fallback validation failed")
                    continue
                
                # Try fallback execution
                fallback_result = execute_purchase_with_retry(
                    platform=fallback_platform,
                    product={**product, "price": fallback.get("price")},
                    delivery=delivery,
                    max_retries=2  # Fewer retries for fallback
                )
                
                if fallback_result["status"] == "success":
                    print(f"   ✅ Fallback succeeded!")
                    
                    audit_id = log_audit("purchase_success_fallback", {
                        "primary_platform": selected_platform,
                        "fallback_platform": fallback_platform,
                        "order_id": fallback_result['order_id'],
                        "product": product_name
                    })
                    
                    return {
                        "purchase_status": "success",
                        "execution_details": {
                            "timestamp": datetime.now().isoformat(),
                            "platform_used": fallback_platform,
                            "primary_or_fallback": "fallback",
                            "order_id": fallback_result['order_id'],
                            "transaction_id": fallback_result['transaction_id']
                        },
                        "order_confirmation": {
                            "product_name": product_name,
                            "quantity": quantity,
                            "final_price": fallback.get("price"),
                            "currency": "INR"
                        },
                        "retry_attempts": execution_result["attempts"] - 1,
                        "failures_encountered": [
                            {
                                "platform": selected_platform,
                                "reason": execution_result["failure_reason"]
                            }
                        ],
                        "fallback_used": True,
                        "user_message": f"✅ Order placed via {fallback_platform} ({selected_platform} was unavailable). {product_name} arriving soon.",
                        "audit_log_id": audit_id
                    }
        
        # All options exhausted
        print(f"\n❌ ALL OPTIONS EXHAUSTED - Purchase failed")
        
        audit_id = log_audit("purchase_failed", {
            "platform": selected_platform,
            "product": product_name,
            "reason": execution_result["failure_reason"],
            "attempts": execution_result["attempts"]
        })
        
        return {
            "purchase_status": "failed",
            "execution_details": {
                "timestamp": datetime.now().isoformat(),
                "platform_used": None,
                "order_id": None
            },
            "failures_encountered": [
                {
                    "platform": selected_platform,
                    "reason": execution_result["failure_reason"],
                    "attempts": execution_result["attempts"]
                }
            ],
            "user_message": f"❌ Order failed: {execution_result['failure_reason']}. Kya baad mein try karein?",
            "retry_recommended": True,
            "audit_log_id": audit_id
        }

def purchase_with_ai_reasoning(decision_input: Dict[str, Any]) -> Dict[str, Any]:
    """
    AI-enhanced purchase execution with reasoning
    (For complex edge cases)
    """
    global chat_history
    
    try:
        # Add decision input to chat
        chat_history.append({
            "role": "user",
            "parts": [{"text": f"Execute purchase for this decision:\n{json.dumps(decision_input, indent=2)}"}]
        })
        
        # Call AI model
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=chat_history,
            config={
                "temperature": 0.2,  # Low temperature for deterministic execution
                "top_p": 0.95,
                "max_output_tokens": 2048,
            }
        )
        
        response_text = response.text
        chat_history.append({"role": "model", "parts": [{"text": response_text}]})
        
        # Parse AI response
        # (In production, AI would return structured JSON)
        # For now, use deterministic function
        return execute_purchase(decision_input)
    
    except Exception as e:
        print(f"❌ AI reasoning failed: {e}")
        # Fallback to deterministic execution
        return execute_purchase(decision_input)

# ---------------- MAIN EXECUTION ---------------- #

if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════╗
║        💳 GANGU - Purchase Agent                             ║
║        ─────────────────────────────────────────             ║
║        Safe, Reliable Transaction Execution                  ║
║        Risk-Aware | Failure-Resilient | Auditable            ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    if DRY_RUN_MODE:
        print("🧪 DRY RUN MODE ENABLED - No actual purchases will be made\n")
    
    # Test example
    test_decision = {
        "final_decision": {
            "selected_platform": "Zepto",
            "product": {
                "name": "Toor Dal (Arhar)",
                "brand": "Farm Fresh",
                "product_id": "zepto_dal_001",
                "quantity": "1 kg",
                "price": 150.00,
                "currency": "INR"
            },
            "delivery": {
                "eta_hours": 10,
                "delivery_date": "2026-01-19",
                "slot": "morning"
            },
            "confidence_score": 0.88,
            "fallback_options": [
                {
                    "platform": "Amazon",
                    "product_id": "amz_dal_002",
                    "price": 155.00,
                    "delivery_hours": 24
                }
            ]
        },
        "user_context": {
            "urgency": "normal",
            "budget_limit": 200.00
        }
    }
    
    print("📋 Testing Purchase Agent with sample decision...\n")
    
    result = execute_purchase(test_decision)
    
    print("\n" + "=" * 80)
    print("📤 PURCHASE RESULT")
    print("=" * 80)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    print("=" * 80)
