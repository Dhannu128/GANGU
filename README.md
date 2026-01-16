# 🤖 GANGU - Grocery Assistant for Elderly Users

**GANGU** (Grocery Assistant for eNderly users Going Universal) is an intelligent agentic AI system designed to help elderly Indian users order groceries through natural language conversations in Hindi, English, or Hinglish.

## 📂 Project Structure

```
GANGU/
├── agents/                          # Core AI Agents
│   ├── intent_extraction_agent.py   # ✅ Agent 1: Extract intent from user input
│   ├── task_planner_agent.py        # ✅ Agent 2: Create execution plan
│   ├── search_agent.py              # ✅ Agent 3: Search across platforms (MCP)
│   ├── comparison_agent.py          # 🔨 TODO: Compare & rank results
│   ├── decision_agent.py            # 🔨 TODO: Select best option
│   ├── purchase_agent.py            # 🔨 TODO: Execute order
│   └── notification_agent.py        # 🔨 TODO: Send response
│
├── mcp_clients/                     # MCP Server Clients
│   ├── zepto_mcp_client.py          # ✅ Zepto platform integration
│   └── amazon_mcp_client.py         # ✅ Amazon platform integration
│
├── orchestration/                   # LangGraph Workflow
│   ├── gangu_graph.py               # ✅ Main agent orchestration
│   ├── gangu_main.py                # ✅ Interactive interface
│   └── gangu_support.py             # ✅ Admin/support interface
│
├── config/                          # Configuration
│   ├── docker-compose.yml           # MongoDB for checkpointing
│   └── requirements.txt             # Python dependencies
│
└── docs/                            # Documentation
    ├── MCP_SETUP_GUIDE.md           # Amazon & Zepto MCP setup
    ├── DATA_FLOW.md                 # Data flow documentation
    ├── README.md                    # Documentation index
    └── TESTING_GUIDE.md             # Testing instructions
```

## 🔄 Agent Pipeline (Data Flow)

### Complete Flow:
```
User Input: "White chane khatam ho gaye"
    ↓
[Agent 1] Intent & Extraction Agent
    Output: {
        intent: "buy_grocery",
        item: "white chickpeas",
        quantity: "1 kg",
        urgency: "normal"
    }
    ↓
[Agent 2] Task Planner Agent
    Input: Intent data from Agent 1
    Output: {
        steps: [
            {step: 1, agent: "search_agent", action: "search_platforms"},
            {step: 2, agent: "compare_agent", action: "compare_results"},
            {step: 3, agent: "decision_agent", action: "select_best"},
            {step: 4, agent: "purchase_agent", action: "execute_order"},
            {step: 5, agent: "notification_agent", action: "notify_user"}
        ]
    }
    ↓
[Agent 3] Search Agent (MCP Integrated)
    Input: Task plan + item details
    Output: {
        platforms_searched: ["Zepto", "Amazon"],
        results: [
            {platform: "Zepto", price: 45, delivery: "10-15 min", source: "mcp_server"},
            {platform: "Amazon", price: 120, delivery: "1-2 days", source: "mcp_server"}
        ]
    }
    ↓
[Agent 4] Comparison Agent 🔨 TODO
    Input: Search results
    Output: {scored_results, best_option}
    ↓
[Agent 5] Decision Agent 🔨 TODO
    Input: Comparison scores
    Output: {selected_platform, selected_product}
    ↓
[Agent 6] Purchase Agent 🔨 TODO
    Input: Selected product
    Output: {order_id, delivery_time}
    ↓
[Agent 7] Notification Agent 🔨 TODO
    Input: Order details
    Output: "Aapke chane 15 min mein aa jayenge ✅"
```

## 🚀 Quick Start

### 1. Install Dependencies
```powershell
cd d:\personal\AI-ML\python\GANGU
pip install -r config/requirements.txt
python -m playwright install firefox
```

### 2. Setup Environment Variables
Create `.env` in GANGU root:
```env
GEMINI_API_KEY=your_google_gemini_api_key
LANGSMITH_API_KEY=your_langsmith_api_key
ZEPTO_PHONE_NUMBER=your_phone_number
ZEPTO_DEFAULT_ADDRESS=Home
```

### 3. Setup Zepto MCP Server
```powershell
.\setup_zepto_mcp.ps1
```

### 4. Start MongoDB (for checkpointing)
```powershell
cd config
docker-compose up -d
```

### 5. Run GANGU
```powershell
python orchestration/gangu_main.py
```

## 💬 Example Usage

```
User: "White chane khatam ho gaye"

GANGU:
  🧠 [Agent 1] Intent Extraction: buy_grocery, item=white chickpeas
  📋 [Agent 2] Task Planning: Created 5-step execution plan
  🔍 [Agent 3] Search: Found on Zepto (₹45, 10-15 min)
  ⚖️  [Agent 4] Comparison: Zepto best (fast + reliable)
  ✅ [Agent 5] Decision: Selected Zepto
  🛒 [Agent 6] Purchase: Order placed #12345
  📱 [Agent 7] Response: "Aapke chane 15 minutes mein aa jayenge!"
```

## 🔧 Agent Function Signatures

### Agent 1: Intent Extraction
```python
def extract_intent(user_input: str) -> dict
Input:  "White chane khatam ho gaye"
Output: {intent, item, quantity, urgency, confidence}
```

### Agent 2: Task Planner
```python
def create_action_plan(intent_output: dict) -> dict
Input:  Intent data from Agent 1
Output: {steps: [{agent, action, params}]}
```

### Agent 3: Search
```python
def search_platforms(search_input: dict) -> dict
Input:  {action, item, quantity, urgency}
Output: {platforms_searched, results}
```

## 🧪 Testing

```powershell
# Test individual agents
python agents/intent_extraction_agent.py
python agents/task_planner_agent.py
python agents/search_agent.py

# Test MCP integration
python mcp_clients/zepto_mcp_client.py

# Test full pipeline
python orchestration/gangu_main.py
```

## 🔌 MCP Integration

**Currently Integrated:**
- ✅ Zepto (10-15 min delivery, 100+ products)

**Coming Soon:**
- 🔨 Blinkit
- 🔨 Swiggy Instamart
- 🔨 Amazon Fresh

## 📊 Status

### ✅ Completed
- Intent extraction (Hindi/English/Hinglish)
- Task planning
- Multi-platform search with Zepto MCP
- LangGraph orchestration
- MongoDB checkpointing

### 🔨 In Progress
- Comparison & ranking
- Decision engine
- Purchase execution
- Response generation

## 🤝 Contributing

Build the remaining agents following the template in existing agents!

## 📚 Documentation

- [Zepto Integration Guide](docs/ZEPTO_INTEGRATION_GUIDE.md)
- [Testing Guide](docs/TESTING_GUIDE.md)

---

Made with ❤️ for elderly users
