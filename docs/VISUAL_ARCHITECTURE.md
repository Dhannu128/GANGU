# 🎨 GANGU - Complete Visual Architecture

## 🌐 Complete System Overview

```
┌──────────────────────────────────────────────────────────────────────────┐
│                              USER INTERFACE                              │
│                         http://localhost:3000                            │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │                     1. INPUT LAYER                                 │ │
│  │                                                                    │ │
│  │   ╔══════════╗                                                    │ │
│  │   ║   🎤    ║  ←── Voice Input (Primary)                        │ │
│  │   ║  Speak  ║      Web Speech API (Hindi/English/Hinglish)       │ │
│  │   ╚══════════╝                                                    │ │
│  │                                                                    │ │
│  │   ┌──────────────────────────────────┐                           │ │
│  │   │ Type your message...        📤 │  ←── Text Input (Fallback)  │ │
│  │   └──────────────────────────────────┘                           │ │
│  └────────────────────────────────────────────────────────────────────┘ │
│                          ↓                                             │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │                     2. AGENT TIMELINE                              │ │
│  │                   (Real-time Updates via WebSocket)                │ │
│  │                                                                    │ │
│  │   ✓ 🎯 Understanding request                                     │ │
│  │   ✓ 🧠 Identifying: White Chickpeas (1 kg)                       │ │
│  │   ⏳ 🔍 Searching platforms [Blinkit] [Amazon] [Flipkart]        │ │
│  │   ⏳ ⚖️ Comparing prices & reviews                               │ │
│  │   ⏳ ✨ Selecting best option                                     │ │
│  └────────────────────────────────────────────────────────────────────┘ │
│                          ↓                                             │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │                     3. PRODUCT COMPARISON                          │ │
│  │                                                                    │ │
│  │  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐        │ │
│  │  │✨ Recommended │  │               │  │               │        │ │
│  │  │  BLINKIT      │  │  AMAZON       │  │  FLIPKART     │        │ │
│  │  │  ₹89          │  │  ₹104         │  │  ₹95          │        │ │
│  │  │  ⭐ 4.5      │  │  ⭐ 4.3      │  │  ⭐ 4.1      │        │ │
│  │  │  🚚 Today 6PM │  │  🚚 Tomorrow  │  │  🚚 2 days    │        │ │
│  │  │               │  │               │  │               │        │ │
│  │  │  💡 Best price+│  │               │  │               │        │ │
│  │  │  fastest       │  │               │  │               │        │ │
│  │  └───────────────┘  └───────────────┘  └───────────────┘        │ │
│  └────────────────────────────────────────────────────────────────────┘ │
│                          ↓ (User clicks)                               │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │                     4. CONFIRMATION MODAL                          │ │
│  │                                                                    │ │
│  │   🛒 Confirm Your Order                                           │ │
│  │                                                                    │ │
│  │   White Chickpeas (1 kg)                                          │ │
│  │   ₹89 • Blinkit • Today 6 PM                                     │ │
│  │                                                                    │ │
│  │   💡 Best price + fastest delivery                                │ │
│  │                                                                    │ │
│  │   I'll place this order on Blinkit. Should I proceed?             │ │
│  │                                                                    │ │
│  │   [✅ Confirm Purchase] [🔁 Change] [❌ Cancel]                  │ │
│  └────────────────────────────────────────────────────────────────────┘ │
│                          ↓ (User confirms)                             │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │                     5. SUCCESS SCREEN                              │ │
│  │                                                                    │ │
│  │                    ╔═════════╗                                     │ │
│  │                    ║    ✓    ║                                     │ │
│  │                    ╚═════════╝                                     │ │
│  │                                                                    │ │
│  │                🎉 Order Placed!                                    │ │
│  │                                                                    │ │
│  │   Order ID: ORD-1234567890                                        │ │
│  │   Delivery: Today by 6:00 PM                                      │ │
│  │                                                                    │ │
│  │   [Order Something Else] [📦 Track Order]                        │ │
│  └────────────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────────────┘
                          ↑ ↓ REST API + WebSocket
┌──────────────────────────────────────────────────────────────────────────┐
│                          BACKEND API SERVER                              │
│                        http://localhost:8000                             │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  REST Endpoints:                     WebSocket:                         │
│  ├─ GET  /                          ├─ WS /ws/{session_id}             │
│  ├─ POST /api/chat/process          │   • Real-time updates            │
│  ├─ POST /api/order/confirm         │   • Agent status                 │
│  ├─ GET  /api/session/{id}          │   • Progress tracking            │
│  └─ GET  /api/history                                                   │
└──────────────────────────────────────────────────────────────────────────┘
                          ↓ Invokes GANGU Pipeline
┌──────────────────────────────────────────────────────────────────────────┐
│                        GANGU AGENT PIPELINE                              │
│                         (LangGraph + Gemini)                             │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  [1] Intent Agent → [2] Task Planner → [3] Search Agent                │
│                            ↓                       ↓                     │
│           [4] Comparison Agent ← [5] Decision Agent                     │
│                            ↓                                             │
│                   [6] Purchase Agent (Future)                            │
└──────────────────────────────────────────────────────────────────────────┘
                          ↓ Calls MCP Servers
┌──────────────────────────────────────────────────────────────────────────┐
│                         MCP INTEGRATIONS                                 │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌─────────────────────┐           ┌─────────────────────┐             │
│  │   Zepto MCP         │           │   Amazon MCP        │             │
│  │   (Playwright)      │           │   (Apify API)       │             │
│  │   Firefox Automation│           │   Product Search    │             │
│  └─────────────────────┘           └─────────────────────┘             │
│            ↓                                    ↓                        │
│    [Real Products]                      [Real Products]                 │
└──────────────────────────────────────────────────────────────────────────┘
                          ↓ Stored in
┌──────────────────────────────────────────────────────────────────────────┐
│                           MONGODB DATABASE                               │
│                      mongodb://localhost:27017                           │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  Collections:                                                            │
│  ├─ sessions (conversation history)                                     │
│  ├─ checkpoints (LangGraph state)                                       │
│  └─ orders (future)                                                      │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## 📊 Data Flow Diagram

```
USER SPEAKS
    ↓
"White chane khatam ho gaye"
    ↓
┌─────────────────────────────────────┐
│ VoiceInput Component                │
│ Web Speech API                      │
│ Transcribes: "White chane le aao"   │
└────────────┬────────────────────────┘
             ↓
┌─────────────────────────────────────┐
│ Frontend Store (Zustand)            │
│ setTranscription(text)              │
└────────────┬────────────────────────┘
             ↓
┌─────────────────────────────────────┐
│ API Client (lib/api.ts)             │
│ POST /api/chat/process              │
│ { message, session_id }             │
└────────────┬────────────────────────┘
             ↓ HTTP Request
┌─────────────────────────────────────┐
│ FastAPI Backend                     │
│ Receives request                    │
└────────────┬────────────────────────┘
             ↓
┌─────────────────────────────────────┐
│ GANGU Graph (LangGraph)             │
│ create_gangu_graph()                │
└────────────┬────────────────────────┘
             ↓
┌─────────────────────────────────────┐
│ Agent 1: Intent Extraction          │
│ Input: "White chane le aao"         │
│ Output: {                           │
│   intent: "buy_grocery",            │
│   item: "white chickpeas",          │
│   quantity: "1 kg"                  │
│ }                                   │
└────────────┬────────────────────────┘
             ↓ WebSocket Update
             [Frontend shows: "🎯 Understanding request"]
             ↓
┌─────────────────────────────────────┐
│ Agent 2: Task Planner               │
│ Creates execution plan              │
│ Output: {                           │
│   steps: [search, compare, decide]  │
│ }                                   │
└────────────┬────────────────────────┘
             ↓ WebSocket Update
             [Frontend shows: "📋 Creating plan"]
             ↓
┌─────────────────────────────────────┐
│ Agent 3: Search Agent               │
│ Parallel MCP calls                  │
│   ├─> Zepto MCP                     │
│   └─> Amazon MCP                    │
│ Output: {                           │
│   platforms: 3,                     │
│   products: 6                       │
│ }                                   │
└────────────┬────────────────────────┘
             ↓ WebSocket Update
             [Frontend shows: "🔍 Searching platforms"]
             ↓
┌─────────────────────────────────────┐
│ Agent 4: Comparison Agent           │
│ Ranks products by:                  │
│   • Price                           │
│   • Delivery time                   │
│   • Rating                          │
│   • Stock availability              │
│ Output: { ranked_products: [...] }  │
└────────────┬────────────────────────┘
             ↓ WebSocket Update
             [Frontend shows: "⚖️ Comparing products"]
             ↓
┌─────────────────────────────────────┐
│ Agent 5: Decision Agent             │
│ Selects best option                 │
│ Output: {                           │
│   selected_index: 0,                │
│   reasoning: "Best price + fastest" │
│ }                                   │
└────────────┬────────────────────────┘
             ↓ WebSocket Update
             [Frontend shows: "✨ Selecting best option"]
             ↓ Final Response
┌─────────────────────────────────────┐
│ Backend Returns:                    │
│ {                                   │
│   success: true,                    │
│   intent: {...},                    │
│   comparison: {                     │
│     products: [                     │
│       {                             │
│         platform: "Blinkit",        │
│         price: 89,                  │
│         rating: 4.5,                │
│         delivery_time: "Today 6PM"  │
│       },                            │
│       ...                           │
│     ]                               │
│   },                                │
│   recommendation: {                 │
│     selected_index: 0,              │
│     reasoning: "..."                │
│   }                                 │
│ }                                   │
└────────────┬────────────────────────┘
             ↓
┌─────────────────────────────────────┐
│ Frontend Receives Response          │
│ Updates Store                       │
│ setComparison(data)                 │
│ setRecommendation(data)             │
└────────────┬────────────────────────┘
             ↓
┌─────────────────────────────────────┐
│ ProductComparison Component         │
│ Renders 3 cards                     │
│ Highlights recommended              │
└────────────┬────────────────────────┘
             ↓ User Clicks
┌─────────────────────────────────────┐
│ OrderConfirmation Modal             │
│ Shows product details               │
│ User clicks "Confirm"               │
└────────────┬────────────────────────┘
             ↓
┌─────────────────────────────────────┐
│ API Client                          │
│ POST /api/order/confirm             │
│ { session_id, product_index }       │
└────────────┬────────────────────────┘
             ↓
┌─────────────────────────────────────┐
│ Backend Processes Order             │
│ (Purchase Agent - Future)           │
│ Returns: { order_id, delivery_eta } │
└────────────┬────────────────────────┘
             ↓
┌─────────────────────────────────────┐
│ Frontend Shows Success              │
│ SuccessScreen Component             │
│ 🎉 Order placed!                    │
└─────────────────────────────────────┘
```

---

## 🎨 Component Hierarchy

```
App (page.tsx)
│
├─ VoiceInput
│  ├─ Mic Button
│  ├─ Transcription Display
│  └─ Status Text
│
├─ TextInput
│  ├─ Input Field
│  ├─ Send Button
│  └─ Suggestion Chips
│
├─ AgentTimeline
│  └─ AgentStep (repeated)
│     ├─ Status Icon
│     ├─ Step Name
│     ├─ Message
│     └─ Data Preview
│
├─ ProductComparison
│  └─ ProductCard (repeated)
│     ├─ Platform Badge
│     ├─ Product Image
│     ├─ Product Name
│     ├─ Price
│     ├─ Rating
│     ├─ Delivery Time
│     ├─ Recommended Badge (conditional)
│     └─ Reasoning (conditional)
│
├─ OrderConfirmation (Modal)
│  ├─ Product Summary
│  ├─ Reasoning Display
│  ├─ Confirm Button
│  ├─ Change Button
│  └─ Cancel Button
│
└─ SuccessScreen (Overlay)
   ├─ Success Icon
   ├─ Order Details
   ├─ Order Again Button
   └─ Track Order Button
```

---

## 🔄 State Management Flow

```
┌────────────────────────────────────┐
│      Zustand Store (lib/store.ts)  │
├────────────────────────────────────┤
│                                    │
│  Connection State:                 │
│  ├─ connected: boolean             │
│  └─ sessionId: string              │
│                                    │
│  UI State:                         │
│  ├─ isListening: boolean           │
│  ├─ isProcessing: boolean          │
│  └─ transcription: string          │
│                                    │
│  Agent Pipeline:                   │
│  ├─ agentSteps: Step[]             │
│  └─ currentStep: string            │
│                                    │
│  Results:                          │
│  ├─ intent: object                 │
│  ├─ comparison: object             │
│  └─ recommendation: object         │
│                                    │
│  Order:                            │
│  ├─ orderPlaced: boolean           │
│  └─ orderId: string                │
└────────────────────────────────────┘
        ↑           ↓
┌────────────────────────────────────┐
│         React Components           │
│  useGANGUStore() hook              │
└────────────────────────────────────┘
```

---

## 🔌 API Communication Patterns

### REST API (Request-Response)
```
Frontend                Backend
   │                       │
   ├──POST /api/chat──────>│
   │  (user message)        │
   │                       │
   │<──Response────────────┤
   │  (intent, comparison, │
   │   recommendation)      │
   │                       │
```

### WebSocket (Real-time Push)
```
Frontend                Backend
   │                       │
   ├──Connect WS──────────>│
   │                       │
   │<──agent_update────────┤
   │  (intent complete)     │
   │                       │
   │<──agent_update────────┤
   │  (search in progress)  │
   │                       │
   │<──agent_update────────┤
   │  (comparison done)     │
   │                       │
```

---

## 📱 Responsive Layout Breakpoints

```
Mobile (< 640px)
┌────────────┐
│   Header   │
├────────────┤
│  Voice In  │
│  ┌──────┐  │
│  │  🎤 │  │
│  └──────┘  │
├────────────┤
│ Timeline   │
│ (Scroll)   │
├────────────┤
│  Product   │
│  ┌──────┐  │
│  │Card 1│  │
│  └──────┘  │
│  ┌──────┐  │
│  │Card 2│  │
│  └──────┘  │
└────────────┘

Tablet (640-1024px)
┌──────────────────────┐
│      Header          │
├──────────────────────┤
│   Voice Input        │
│    ┌────────┐        │
│    │   🎤  │        │
│    └────────┘        │
├──────────────────────┤
│  Agent Timeline      │
├──────────────────────┤
│  ┌────────┐┌────────┐│
│  │ Card 1 ││ Card 2 ││
│  └────────┘└────────┘│
│  ┌────────┐          │
│  │ Card 3 │          │
│  └────────┘          │
└──────────────────────┘

Desktop (> 1024px)
┌──────────────────────────────────┐
│            Header                │
├──────────────────────────────────┤
│         Voice Input              │
│          ┌──────────┐            │
│          │    🎤   │            │
│          └──────────┘            │
├──────────────────────────────────┤
│       Agent Timeline             │
├──────────────────────────────────┤
│  ┌────────┐┌────────┐┌────────┐ │
│  │ Card 1 ││ Card 2 ││ Card 3 │ │
│  └────────┘└────────┘└────────┘ │
└──────────────────────────────────┘
```

---

**This visual architecture shows the complete GANGU system from UI to database! 🎨**
