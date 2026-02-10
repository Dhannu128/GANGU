# 🔄 GANGU Agent Pipeline - Complete Data Flow

## Overview
This document shows exactly how data flows through the GANGU system from user input to final response.

## Agent Chain Visualization

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER INPUT                              │
│             "White chane khatam ho gaye"                       │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  AGENT 1: Intent & Extraction Agent                            │
│  File: agents/intent_extraction_agent.py                       │
│  Function: extract_intent(user_input: str) -> dict            │
└─────────────────────────────────────────────────────────────────┘
                              ↓
                    OUTPUT (intent_data):
                    {
                      "intent": "buy_grocery",
                      "item": "white chickpeas",
                      "item_original": "white chane",
                      "quantity": "1 kg",
                      "urgency": "normal",
                      "confidence": "high",
                      "language_detected": "hinglish"
                    }
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  AGENT 2: Task Planner Agent                                   │
│  File: agents/task_planner_agent.py                            │
│  Function: create_action_plan(intent_data: dict) -> dict       │
└─────────────────────────────────────────────────────────────────┘
                              ↓
                    OUTPUT (task_plan):
                    {
                      "steps": [
                        {
                          "step_number": 1,
                          "agent": "search_agent",
                          "action": "search_platforms",
                          "params": {...}
                        },
                        {
                          "step_number": 2,
                          "agent": "compare_agent",
                          "action": "compare_results"
                        },
                        ...
                      ]
                    }
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  ROUTING LOGIC                                                  │
│  Function: route_after_planning(state)                         │
│  Decision: intent="buy_grocery" → Route to SEARCH              │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  AGENT 3: Search Agent (MCP INTEGRATED)                        │
│  File: agents/search_agent.py                                  │
│  Function: search_platforms(search_input: dict) -> dict        │
│                                                                 │
│  ┌──────────────────────────────────────────────────────┐     │
│  │  MCP CONNECTION                                       │     │
│  │                                                       │     │
│  │  Search Agent                                        │     │
│  │       ↓                                              │     │
│  │  zepto_mcp_client.py                                 │     │
│  │       ↓                                              │     │
│  │  Zepto MCP Server (proddnav/zepto-cafe-mcp)         │     │
│  │       ↓                                              │     │
│  │  Playwright → Zepto Website                          │     │
│  │       ↓                                              │     │
│  │  Real Product Data ✅                                 │     │
│  └──────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────────┘
                              ↓
                    OUTPUT (search_results):
                    {
                      "platforms_searched": ["Zepto", "Blinkit", "Amazon"],
                      "total_results_found": 3,
                      "results": [
                        {
                          "platform": "Zepto",
                          "item_name": "white chickpeas",
                          "price": 45,
                          "currency": "INR",
                          "delivery_time": "10-15 min",
                          "rating": 4.5,
                          "url": "https://zepto.com/...",
                          "source": "mcp_server"  ← REAL DATA
                        },
                        {
                          "platform": "Blinkit",
                          "price": 50,
                          "delivery_time": "20 min"
                        },
                        ...
                      ]
                    }
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  AGENT 4: Comparison Agent (TODO - You will build)             │
│  File: agents/comparison_agent.py                              │
│  Function: compare_and_score(search_results: dict) -> dict     │
│                                                                 │
│  Logic: Score based on:                                        │
│    - Fast delivery (priority for elderly)                      │
│    - Reliability/rating                                        │
│    - Price                                                     │
└─────────────────────────────────────────────────────────────────┘
                              ↓
                    OUTPUT (comparison_scores):
                    {
                      "scored_results": [
                        {
                          "platform": "Zepto",
                          "score": 9.5,
                          "reasons": ["Fastest delivery", "Good rating"]
                        },
                        ...
                      ],
                      "best_option": {
                        "platform": "Zepto",
                        "score": 9.5
                      }
                    }
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  AGENT 5: Decision Agent (TODO - You will build)               │
│  File: agents/decision_agent.py                                │
│  Function: make_decision(comparison_scores: dict) -> dict      │
│                                                                 │
│  Logic: Select best option, handle edge cases                  │
└─────────────────────────────────────────────────────────────────┘
                              ↓
                    OUTPUT (decision):
                    {
                      "selected_platform": "Zepto",
                      "selected_product": {...},
                      "reasoning": "Fastest delivery + reliable"
                    }
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  AGENT 6: Purchase Agent (TODO - You will build)               │
│  File: agents/purchase_agent.py                                │
│  Function: execute_order(decision: dict) -> dict               │
│                                                                 │
│  Actions: Place order via MCP server                           │
└─────────────────────────────────────────────────────────────────┘
                              ↓
                    OUTPUT (order_confirmation):
                    {
                      "order_id": "ZEPTO-12345",
                      "delivery_time": "10-15 minutes",
                      "total_amount": 45,
                      "status": "confirmed"
                    }
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  AGENT 7: Notification Agent (TODO - You will build)           │
│  File: agents/notification_agent.py                            │
│  Function: generate_response(order_confirmation: dict) -> str  │
│                                                                 │
│  Logic: Generate elderly-friendly response in Hindi/Hinglish   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
                    FINAL OUTPUT (ai_response):
                    "✅ Aapke white chane Zepto se 
                     15 minutes mein aa jayenge!
                     Price: ₹45
                     Order #ZEPTO-12345"
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                        USER RECEIVES                            │
│                    "Chane aa jayenge 15 min mein!"              │
└─────────────────────────────────────────────────────────────────┘
```

## State Management (LangGraph)

### GANGUState Structure
```python
class GANGUState(TypedDict):
    # Input
    user_input: str
    
    # Agent 1 Output
    intent_data: dict
    detected_intent: str
    item_name: str
    quantity: str
    urgency: str
    confidence: str
    
    # Agent 2 Output
    task_plan: dict
    execution_steps: list[dict]
    
    # Agent 3 Output
    search_results: dict
    platforms_searched: list[str]
    
    # Agent 4 Output (TODO)
    comparison_scores: list[dict]
    best_option: dict
    
    # Agent 5 Output (TODO)
    selected_platform: str
    selected_product: dict
    
    # Agent 6 Output (TODO)
    order_id: str
    delivery_time: str
    
    # Agent 7 Output (TODO)
    ai_response: str
```

## Data Transformations

### 1. Intent Extraction Transform
```
Input:  "White chane khatam ho gaye" (string)
        ↓ [NLP Processing]
Output: {intent, item, quantity, urgency, confidence} (structured dict)
```

### 2. Task Planning Transform
```
Input:  {intent: "buy_grocery", item: "white chickpeas"}
        ↓ [Strategy Generation]
Output: {steps: [search, compare, decide, purchase, notify]}
```

### 3. Search Transform
```
Input:  {item: "white chickpeas", quantity: "1 kg"}
        ↓ [MCP Call to Zepto + other platforms]
Output: {platforms: [...], results: [{platform, price, delivery}]}
```

### 4. Comparison Transform (TODO)
```
Input:  {results: [{platform, price, delivery}]}
        ↓ [Scoring Algorithm]
Output: {scored_results: [...], best_option: {...}}
```

### 5. Decision Transform (TODO)
```
Input:  {scored_results, best_option}
        ↓ [Selection Logic]
Output: {selected_platform, selected_product}
```

### 6. Purchase Transform (TODO)
```
Input:  {selected_platform, selected_product}
        ↓ [MCP Order Execution]
Output: {order_id, delivery_time, status}
```

### 7. Notification Transform (TODO)
```
Input:  {order_id, delivery_time, platform}
        ↓ [Response Generation]
Output: "Aapke chane 15 min mein aa jayenge!" (string)
```

## Key Integration Points

### 1. Agent → Agent Integration
- **How:** LangGraph state management
- **Pattern:** Each agent reads from state, writes to state
- **Example:**
  ```python
  # Agent 1 writes
  state["intent_data"] = extract_intent(user_input)
  
  # Agent 2 reads
  intent_data = state.get("intent_data")
  task_plan = create_action_plan(intent_data)
  ```

### 2. Agent → MCP Integration
- **How:** MCP client wrappers
- **Pattern:** Agent calls async MCP client, waits for response
- **Example:**
  ```python
  # In Search Agent
  zepto_result = await zepto_mcp_client.search_product(item)
  state["search_results"] = zepto_result
  ```

### 3. Error Handling
- **Strategy:** Graceful fallback at each agent
- **Pattern:**
  ```python
  try:
      result = agent_function(input)
  except Exception as e:
      print(f"Error: {e}, using fallback")
      result = fallback_function(input)
  ```

## Testing the Flow

### End-to-End Test
```powershell
cd d:\personal\AI-ML\python\GANGU
python orchestration/gangu_main.py
```

Input: `White chane khatam ho gaye`

Expected Flow:
```
[Agent 1] ✅ Extracted: buy_grocery, white chickpeas
[Agent 2] ✅ Planned: 5 steps
[Agent 3] ✅ Searched: Zepto (MCP), Blinkit, Amazon
[Agent 4] 🔨 TODO: Compare results
[Agent 5] 🔨 TODO: Select best
[Agent 6] 🔨 TODO: Place order
[Agent 7] 🔨 TODO: Generate response
```

### Individual Agent Test
```powershell
# Test Agent 1
python agents/intent_extraction_agent.py

# Test Agent 2
python agents/task_planner_agent.py

# Test Agent 3
python agents/search_agent.py
```

## Checkpointing (MongoDB)

### How it Works:
1. After each agent completes, state is saved to MongoDB
2. If system crashes, can resume from last checkpoint
3. Enables "pause and resume" conversations

### Usage:
```python
# Start MongoDB
docker-compose up -d

# Checkpoints saved automatically
# Resume with:
python orchestration/gangu_support.py
```

## Summary

| Agent | Input | Output | Status | MCP |
|-------|-------|--------|--------|-----|
| Intent Extraction | User text | Structured intent | ✅ Done | No |
| Task Planner | Intent data | Execution steps | ✅ Done | No |
| Search | Task plan | Platform results | ✅ Done | ✅ Zepto |
| Comparison | Search results | Scored options | 🔨 TODO | No |
| Decision | Scores | Selected option | 🔨 TODO | No |
| Purchase | Selected option | Order confirmation | 🔨 TODO | ✅ Zepto |
| Notification | Order confirmation | User response | 🔨 TODO | No |

---

**Next Step:** Build Agents 4-7 following the same pattern as Agents 1-3!
