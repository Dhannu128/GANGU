# 🎨 GANGU Frontend & Backend Architecture

## 🏗️ System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         GANGU System                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────────┐         ┌──────────────────┐             │
│  │   FRONTEND       │ ◄────── │    BACKEND API   │             │
│  │   (Next.js)      │  HTTP   │    (FastAPI)     │             │
│  │   Port 3000      │  REST   │    Port 8000     │             │
│  │                  │ ◄────── │                  │             │
│  │                  │ WebSocket│                  │             │
│  └──────────────────┘         └──────────────────┘             │
│         │                              │                        │
│         │                              │                        │
│         ▼                              ▼                        │
│  ┌──────────────────┐         ┌──────────────────┐             │
│  │   Web Speech     │         │  GANGU Agents    │             │
│  │   API (Browser)  │         │  (LangGraph)     │             │
│  └──────────────────┘         └──────────────────┘             │
│                                        │                        │
│                                        ▼                        │
│                               ┌──────────────────┐             │
│                               │  MCP Servers     │             │
│                               │  (Zepto/Amazon)  │             │
│                               └──────────────────┘             │
└─────────────────────────────────────────────────────────────────┘
```

## 📂 Complete Project Structure

```
GANGU/
├── api/                        # NEW: FastAPI Backend
│   ├── main.py                # API server with WebSocket
│   └── requirements.txt       # FastAPI, uvicorn, websockets
│
├── frontend/                   # NEW: Next.js Frontend
│   ├── app/
│   │   ├── layout.tsx         # Root layout
│   │   └── page.tsx           # Main page
│   ├── components/
│   │   ├── VoiceInput.tsx     # 🎙️ Voice input component
│   │   ├── TextInput.tsx      # ⌨️ Text fallback
│   │   ├── AgentTimeline.tsx  # 🤖 Live agent status
│   │   ├── ProductComparison.tsx  # 🛒 Product cards
│   │   ├── OrderConfirmation.tsx  # ✅ Confirm before buy
│   │   └── SuccessScreen.tsx  # 🎉 Order success
│   ├── lib/
│   │   ├── store.ts           # Zustand state management
│   │   └── api.ts             # API + WebSocket client
│   ├── styles/
│   │   └── globals.css        # Tailwind + custom styles
│   ├── package.json
│   ├── tsconfig.json
│   ├── tailwind.config.js
│   └── README.md
│
├── agents/                     # Existing: AI Agents
│   ├── intent_extraction_agent.py
│   ├── task_planner_agent.py
│   ├── search_agent.py
│   ├── comparison_agent.py
│   ├── decision_agent.py
│   └── purchase_agent.py
│
├── orchestration/              # Existing: LangGraph
│   ├── gangu_graph.py
│   └── gangu_main.py
│
├── mcp_clients/                # Existing: MCP Integrations
│   ├── zepto_mcp_client.py
│   └── amazon_mcp_client.py
│
└── scripts/                    # NEW: Setup scripts
    ├── setup_frontend.ps1     # One-time setup
    └── start_dev_servers.ps1  # Start both servers
```

## 🔄 Data Flow (Complete Pipeline)

### 1️⃣ User Input → Frontend

```
User speaks: "White chane khatam ho gaye"
         ↓
[VoiceInput.tsx]
- Web Speech API captures audio
- Transcribes to text
- Shows live transcription
         ↓
[TextInput.tsx]
- User can edit text
- Sends to backend
```

### 2️⃣ Frontend → Backend API

```
POST /api/chat/process
{
  "message": "White chane khatam ho gaye",
  "session_id": "session_123"
}
         ↓
[FastAPI Backend]
- Receives request
- Creates GANGU graph instance
- Streams through agents
```

### 3️⃣ Backend → GANGU Agents

```
[FastAPI] → [GANGU Graph] → [Agents Pipeline]
         ↓
[Intent Agent]
Output: { intent: "buy_grocery", item: "white chickpeas" }
         ↓
[Task Planner]
Output: { steps: ["search", "compare", "decide"] }
         ↓
[Search Agent]
- Calls Zepto MCP
- Calls Amazon MCP
Output: { products: [...] }
         ↓
[Comparison Agent]
Output: { ranked_products: [...] }
         ↓
[Decision Agent]
Output: { selected_product: {...}, reasoning: "..." }
```

### 4️⃣ Backend → Frontend (Real-time Updates)

```
[Backend] → WebSocket → [Frontend]

Timeline updates sent as agents work:
{
  "type": "agent_update",
  "step": "search",
  "status": "complete",
  "message": "Found 6 products",
  "data": { platforms: ["Blinkit", "Amazon"] }
}
         ↓
[AgentTimeline.tsx]
- Displays each step with checkmark
- Shows live progress
```

### 5️⃣ Frontend → Product Comparison

```
[ProductComparison.tsx]
- Receives comparison data
- Renders product cards
- Highlights recommended product
- Shows reasoning
         ↓
User clicks product
         ↓
[OrderConfirmation.tsx]
- Shows modal with details
- User confirms
```

### 6️⃣ Frontend → Backend (Purchase)

```
POST /api/order/confirm
{
  "session_id": "session_123",
  "selected_product_index": 0
}
         ↓
[Backend]
- Calls Purchase Agent
- Places order
- Sends status updates via WebSocket
         ↓
[SuccessScreen.tsx]
- Shows order ID
- Shows delivery time
```

## 🔌 API Endpoints

### REST API (Backend)

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/` | GET | Health check |
| `/api/voice/transcribe` | POST | Receive voice transcription |
| `/api/chat/process` | POST | **Main pipeline** - Process user input |
| `/api/order/confirm` | POST | Confirm and place order |
| `/api/session/{id}` | GET | Retrieve session data |
| `/api/history` | GET | Get order history |

### WebSocket (Backend)

| Endpoint | Purpose |
|----------|---------|
| `/ws/{session_id}` | Real-time agent status updates |

## 🎨 Frontend Components

### Input Layer

```typescript
<VoiceInput />
- Web Speech API integration
- Hindi language support ('hi-IN')
- Live transcription display
- Animated mic button

<TextInput />
- Fallback for voice
- Quick suggestions
- Chat-style interface
```

### Timeline Layer

```typescript
<AgentTimeline />
- Real-time agent progress
- Checkmarks for completed steps
- Loading spinners for in-progress
- Clear step descriptions
```

### Comparison Layer

```typescript
<ProductComparison />
- Card-based product display
- Platform logos
- Price, rating, delivery time
- Recommended badge
- Click to select
```

### Confirmation Layer

```typescript
<OrderConfirmation />
- Modal overlay
- Product summary
- Reasoning explanation
- Confirm/Change/Cancel buttons
```

### Success Layer

```typescript
<SuccessScreen />
- Full-screen success message
- Order ID and details
- Delivery ETA
- "Order again" button
```

## 🔐 State Management (Zustand)

```typescript
// Global state store
interface GANGUStore {
  // Connection
  connected: boolean
  sessionId: string | null
  
  // UI State
  isListening: boolean
  isProcessing: boolean
  transcription: string
  
  // Agent Pipeline
  agentSteps: AgentStep[]
  currentStep: string | null
  
  // Results
  intent: any
  comparison: Comparison | null
  recommendation: any
  
  // Order
  orderPlaced: boolean
  orderId: string | null
}
```

## 🚀 Deployment Architecture

### Development

```
Frontend: http://localhost:3000
Backend:  http://localhost:8000
MongoDB:  localhost:27017
```

### Production

```
┌─────────────────┐
│   Vercel/CDN    │ ← Next.js Frontend
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Cloud Server  │ ← FastAPI Backend
│   (EC2/Azure)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   MongoDB Atlas │ ← Database
└─────────────────┘
```

## 🧪 Testing Flow

### Manual Testing

1. **Voice Input Test**
   ```
   1. Click mic button
   2. Say: "White chane le aao"
   3. Verify transcription
   4. Check agent timeline starts
   ```

2. **Agent Pipeline Test**
   ```
   1. Watch timeline populate
   2. Verify each step completes
   3. Check products appear
   4. Confirm recommendation badge
   ```

3. **Purchase Flow Test**
   ```
   1. Click recommended product
   2. Verify modal shows correct details
   3. Click "Confirm Purchase"
   4. Watch real-time status
   5. See success screen
   ```

### Automated Testing (Future)

```bash
# Frontend tests
npm run test

# Backend tests
pytest api/tests/

# E2E tests
playwright test
```

## 📊 Performance Metrics

### Frontend
- **First Load**: < 3 seconds
- **Voice Recognition**: < 1 second latency
- **WebSocket Connection**: < 500ms

### Backend
- **Intent Extraction**: ~1-2 seconds
- **Search**: ~3-5 seconds (parallel MCP calls)
- **Comparison**: ~1 second
- **Total Pipeline**: ~5-8 seconds

## 🔮 Future Enhancements

### Phase 2
- [ ] User authentication (Firebase/Auth0)
- [ ] Order history page
- [ ] Repeat last order
- [ ] Scheduled orders
- [ ] Multi-language UI

### Phase 3
- [ ] Mobile app (React Native)
- [ ] WhatsApp bot integration
- [ ] Voice responses (TTS)
- [ ] AR product preview
- [ ] Smart notifications

## 📚 Tech Stack Summary

| Layer | Technology | Purpose |
|-------|------------|---------|
| Frontend | Next.js 14 | React framework |
| Frontend | Tailwind CSS | Styling |
| Frontend | Zustand | State management |
| Frontend | Web Speech API | Voice input |
| Backend | FastAPI | REST API |
| Backend | WebSockets | Real-time updates |
| Backend | LangGraph | Agent orchestration |
| Backend | Google Gemini | LLM for agents |
| Database | MongoDB | Session storage |
| MCP | Playwright | Zepto automation |
| MCP | Apify | Amazon scraping |

---

**This is the complete GANGU architecture - Voice-first, AI-powered, trustworthy grocery assistant! 🚀**
