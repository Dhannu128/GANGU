# 💳 Purchase Agent Architecture

## Overview
```
┌─────────────────────────────────────────────────────────────┐
│                    GANGU PURCHASE AGENT                      │
│         Safe, Reliable Transaction Execution                 │
└─────────────────────────────────────────────────────────────┘
```

## Full Pipeline Flow

```
┌──────────────┐
│     User     │  "Toor dal khatam ho gayi"
└──────┬───────┘
       │
       ▼
┌──────────────────────┐
│  Intent Extraction   │  Extract: buy_grocery, toor dal, 1kg
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│   Task Planner       │  Plan: search → compare → decide → buy
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│   Search Agent       │  Find products on Zepto, Amazon
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│  Comparison Agent    │  Rank by price, delivery, quality
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│  Decision Agent      │  Select: Zepto, ₹150, 10hrs
└──────┬───────────────┘
       │
       ▼
┌─────────────────────────────────────────────────────────────┐
│                   PURCHASE AGENT ✅                          │
│                                                              │
│  Phase 1: PRE-VALIDATION                                     │
│    ├─ Check product still available                          │
│    ├─ Verify price unchanged (±10%)                          │
│    ├─ Confirm delivery slot valid                            │
│    └─ Test platform API health                               │
│                                                              │
│  Phase 2: RISK ASSESSMENT                                    │
│    ├─ Calculate risk score (0-100)                           │
│    ├─ Check price spike (>50% = suspicious)                  │
│    ├─ Detect duplicate orders                                │
│    └─ Assign risk level: LOW/MEDIUM/HIGH/CRITICAL            │
│                                                              │
│  Phase 3: EXECUTION                                          │
│    ├─ Step 1: Add to cart                                    │
│    ├─ Step 2: Verify cart contents                           │
│    ├─ Step 3: Proceed to checkout                            │
│    ├─ Step 4: Confirm payment                                │
│    └─ Step 5: Get order ID                                   │
│                                                              │
│  Phase 4: FAILURE RECOVERY (if needed)                       │
│    ├─ Retry (max 3 attempts)                                 │
│    ├─ Try fallback platform                                  │
│    └─ Report failure transparently                           │
│                                                              │
│  Phase 5: AUDIT                                              │
│    └─ Log to purchase_audit.jsonl                            │
│                                                              │
│  OUTPUT:                                                     │
│    ✅ Status: success                                        │
│    📦 Order ID: ZEPTO-12345                                  │
│    🛡️ Risk: LOW (15/100)                                    │
└─────────────────────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────┐
│  Notification Agent  │  "✅ Order placed! Arriving tomorrow."
└──────┬───────────────┘
       │
       ▼
┌──────────────┐
│     User     │  Gets confirmation message
└──────────────┘
```

## Risk Assessment Matrix

```
┌─────────────────────────────────────────────────────────────┐
│                    RISK SCORING                              │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Score Range    │  Risk Level  │  Action                     │
│  ─────────────  │  ──────────  │  ──────                     │
│  0 - 30         │  🟢 LOW      │  Auto-proceed               │
│  31 - 60        │  🟡 MEDIUM   │  Extra validation           │
│  61 - 80        │  🟠 HIGH     │  User confirmation required │
│  81 - 100       │  🔴 CRITICAL │  Block purchase             │
│                                                              │
├─────────────────────────────────────────────────────────────┤
│                   RISK FACTORS                               │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Factor              │  Points  │  Example                   │
│  ──────              │  ──────  │  ───────                   │
│  Price spike >50%    │  +40     │  ₹100 → ₹180               │
│  Out of stock        │  +20     │  Not available             │
│  Platform down       │  +20     │  API failure rate >50%     │
│  Large order >₹5000  │  +20     │  Bulk purchase             │
│  Duplicate order     │  +30     │  Same order in 5 mins      │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Execution States

```
┌─────────────────────────────────────────────────────────────┐
│                  PURCHASE STATES                             │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ✅ SUCCESS                                                  │
│      → Order placed successfully                             │
│      → Order ID received                                     │
│      → Payment confirmed                                     │
│                                                              │
│  ⏳ PENDING                                                  │
│      → Requires user confirmation                            │
│      → High-risk order                                       │
│      → Price changed significantly                           │
│                                                              │
│  🚫 BLOCKED                                                  │
│      → Critical risk detected                                │
│      → Manual review required                                │
│      → Suspicious activity                                   │
│                                                              │
│  ❌ FAILED                                                   │
│      → Primary platform failed                               │
│      → All fallbacks exhausted                               │
│      → Payment gateway error                                 │
│                                                              │
│  🔄 FALLBACK                                                 │
│      → Primary failed, trying alternate                      │
│      → Blinkit → Zepto                                       │
│      → Transparent to user                                   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Failure Recovery Flow

```
Primary Platform (Zepto)
     │
     ├─ Attempt 1 ──❌─→ Failed
     │
     ├─ Wait 2s
     │
     ├─ Attempt 2 ──❌─→ Failed
     │
     ├─ Wait 2s
     │
     ├─ Attempt 3 ──❌─→ Failed
     │
     └─ Primary Exhausted
          │
          ▼
     Fallback Platform (Amazon)
          │
          ├─ Attempt 1 ──❌─→ Failed
          │
          ├─ Wait 2s
          │
          ├─ Attempt 2 ──✅─→ Success!
          │
          ▼
     Order Placed via Amazon
     Message: "✅ Ordered via Amazon (Zepto unavailable)"
```

## Idempotency Check

```
New Order Request
     │
     ▼
Generate Order Hash
     │
     ├─ hash = MD5(platform + product_id + user_id + date)
     │
     ▼
Check Order History
     │
     ├─ Hash exists in last 5 mins?
     │
     ├─ YES ──→ Return existing order_id
     │           "Already placed: ZEPTO-12345"
     │
     └─ NO ──→ Proceed with purchase
                 Create new order
```

## Audit Trail Example

```jsonl
{"audit_id": "audit_001", "action": "validation_started", "timestamp": "10:30:00"}
{"audit_id": "audit_002", "action": "risk_assessed", "risk_score": 15, "timestamp": "10:30:01"}
{"audit_id": "audit_003", "action": "add_to_cart", "status": "success", "timestamp": "10:30:02"}
{"audit_id": "audit_004", "action": "checkout", "status": "success", "timestamp": "10:30:03"}
{"audit_id": "audit_005", "action": "payment_confirmed", "order_id": "ZEPTO-12345", "timestamp": "10:30:04"}
{"audit_id": "audit_006", "action": "purchase_success", "platform": "Zepto", "price": 150.0, "timestamp": "10:30:05"}
```

## Integration Points

```
┌─────────────────────────────────────────────────────────────┐
│              OTHER AGENTS → PURCHASE AGENT                   │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Decision Agent Output:                                      │
│  {                                                           │
│    "selected_platform": "Zepto",                             │
│    "product": {...},                                         │
│    "fallback_options": [...]                                 │
│  }                                                           │
│                                                              │
│         ↓ ↓ ↓                                                │
│                                                              │
│  Purchase Agent Input:                                       │
│  {                                                           │
│    "final_decision": {...},                                  │
│    "user_context": {...}                                     │
│  }                                                           │
│                                                              │
│         ↓ ↓ ↓                                                │
│                                                              │
│  Purchase Agent Output:                                      │
│  {                                                           │
│    "purchase_status": "success",                             │
│    "order_id": "ZEPTO-12345",                                │
│    "execution_details": {...},                               │
│    "validation_results": {...}                               │
│  }                                                           │
│                                                              │
│         ↓ ↓ ↓                                                │
│                                                              │
│  Notification Agent Input:                                   │
│  Uses purchase_result to generate user message               │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Safety Layers

```
┌─────────────────────────────────────────────────────────────┐
│                    SAFETY LAYERS                             │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Layer 1: PRE-VALIDATION                                     │
│    │ Re-check everything before spending money               │
│    └─ Price, availability, delivery, platform health         │
│                                                              │
│  Layer 2: RISK ASSESSMENT                                    │
│    │ Evaluate risk before proceeding                         │
│    └─ Price spikes, duplicates, platform reliability         │
│                                                              │
│  Layer 3: IDEMPOTENCY                                        │
│    │ Prevent accidental duplicate orders                     │
│    └─ Hash-based order tracking                              │
│                                                              │
│  Layer 4: RETRY LOGIC                                        │
│    │ Handle transient failures gracefully                    │
│    └─ Max 3 attempts with exponential backoff                │
│                                                              │
│  Layer 5: FALLBACK MECHANISM                                 │
│    │ Don't fail, try alternate platform                      │
│    └─ Zepto fails → Try Amazon                               │
│                                                              │
│  Layer 6: AUDIT TRAIL                                        │
│    │ Every action logged for accountability                  │
│    └─ Complete replay capability                             │
│                                                              │
│  Layer 7: DRY-RUN MODE                                       │
│    │ Test without real money                                 │
│    └─ Simulation mode for development                        │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Why This Design Is Strong

```
Traditional Chatbot              GANGU Purchase Agent
─────────────────                ────────────────────
"Here are options"        vs     "Order placed!"
No validation             vs     Multi-layer validation
No risk assessment        vs     Risk scoring (0-100)
No failure recovery       vs     Retry + Fallback
No audit                  vs     Complete audit trail
Test = production         vs     Dry-run mode
Fails silently            vs     Transparent errors
Single point of failure   vs     Platform redundancy
```

---

**This Purchase Agent is production-ready, enterprise-grade, and elderly-safe! 🎉**
