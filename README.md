# GANGU 🛒

> **Voice-first grocery assistance designed for older Indian adults and their families.**
> Speak or type in Hindi, English, or Hinglish, compare the available results, and explicitly review an option before confirming it. Development and estimated data are labelled in the interface.

```
"doodh khatam ho gaya, le aao"
        ↓
   intent → plan → search → compare → decide → purchase → notify
        ↓
   "Zepto · Amul Milk 1 L · ₹64 · 10 min" ✓
```

---

## What is GANGU?

GANGU is a multi-agent AI system built on **LangGraph**, powered by **Google Gemini 2.5 Flash**. It is designed for elderly Indian users who may find apps difficult — instead of navigating menus, they just speak naturally and GANGU handles everything.

**The full flow:**
1. User speaks or types in Hindi / English / Hinglish
2. 6 AI agents work in a sequential pipeline, each with one job
3. Products are found on **Zepto** and **Swiggy Instamart** (via MCP clients)
4. The best option is selected using a weighted scoring model + safety checks
5. The user reviews the option, address, price source and transaction mode
6. Confirmation remains a safe simulation unless every production purchase safeguard is deliberately enabled

---

## Project Structure

```
GANGU/
├── agents/                        # 6 core AI agents + shared LLM client
│   ├── llm.py                     # Gemini 2.5 Flash client with 6-key pool
│   ├── intent_extraction_agent.py # Agent 1: parse user input → structured intent
│   ├── task_planner_agent.py      # Agent 2: build execution plan
│   ├── search_agent.py            # Agent 3: search Zepto + Swiggy via MCP
│   ├── comparison_agent.py        # Agent 4: score & rank products
│   ├── decision_agent.py          # Agent 5: apply safety policies, pick winner
│   └── purchase_agent.py          # Agent 6: place real Zepto COD order
│
├── orchestration/                 # LangGraph wiring
│   ├── gangu_graph.py             # StateGraph: 8 nodes + conditional routing + MongoDB checkpoint
│   ├── gangu_main.py              # CLI entry point
│   └── gangu_support.py           # Utility helpers
│
├── api/                           # FastAPI backend
│   ├── main.py                    # REST + WebSocket endpoints
│   └── requirements.txt
│
├── mcp_clients/                   # Platform connectors (MCP protocol)
│   ├── zepto_mcp_client.py        # Zepto: search + cart + checkout via Playwright
│   ├── swiggy_mcp_client.py       # Swiggy Instamart: search via SSE
│   ├── swiggy_auth.py             # Swiggy auth helper
│   ├── amazon_mcp_client.py       # Amazon (⚠️ stub — not yet implemented)
│   └── enhanced_amazon_client.py  # Amazon (⚠️ stub — not yet implemented)
│
├── frontend/                      # Next.js 14 app
│   ├── app/
│   │   ├── page.tsx               # Public landing page
│   │   ├── layout.tsx             # Root layout
│   │   ├── signin/page.tsx        # Redirects to the shared Firebase sign-in flow
│   │   ├── signup/page.tsx        # Firebase phone OTP + Google sign-in
│   │   └── (authenticated)/       # Protected routes — auto-redirects to /signin
│   │       └── app/
│   │           ├── page.tsx       # Main workspace (voice/text + agent timeline)
│   │           ├── orders/        # Past orders
│   │           ├── lists/         # Saved shopping lists
│   │           ├── family/        # Family member management
│   │           └── settings/      # Preferences, address, payment, accessibility
│   ├── components/
│   │   ├── auth/                  # Global Firebase session synchronisation
│   │   ├── app/                   # AppShell, LeftRail, MobileNav, TodayPanel, etc.
│   │   └── *.tsx                  # VoiceInput, AgentTimeline, ProductComparison, Toast
│   ├── lib/
│   │   ├── store.ts               # Zustand global state (with localStorage persist)
│   │   └── api.ts                 # API call helpers
│   └── styles/globals.css         # Design tokens
│
├── config/                        # Docker Compose (MongoDB) + Python requirements
├── scripts/                       # PowerShell setup & dev launchers
├── docs/                          # Detailed architecture documents
├── logs/                          # Runtime logs
├── .env.example                   # Environment variable template — copy to .env
├── start_gangu.py                 # One-command startup script
└── render.yaml                    # Render.com deployment config
```

---

## Agent Pipeline — How It Works

The full pipeline is a **LangGraph StateGraph** defined in `orchestration/gangu_graph.py`. It has 8 nodes and one conditional routing branch.

```
START
  │
  ▼
[1] intent_extraction    — Parses Hindi/Hinglish/English → structured intent JSON
  │
  ▼
[2] task_planner         — Builds an ordered execution plan from intent
  │
  ├─ intent is "buy" or "reorder" ─────────────────────────────────┐
  │                                                                 ▼
  │                                                          [3] search
  │                                                     Zepto + Swiggy Instamart
  │                                                                 │
  │                                                                 ▼
  │                                                         [4] comparison
  │                                                    Normalise, score & rank
  │                                                                 │
  │                                                                 ▼
  │                                                          [5] decision
  │                                                     Apply 6 safety policies
  │                                                                 │
  │                                                                 ▼
  │                                                          [6] purchase
  │                                                   Zepto COD / simulate others
  │                                                                 │
  │                                                                 ▼
  │                                                        [7] notification ──► END
  │
  └─ all other intents ──► [8] query_info_only ────────────────────────────────► END
```

### Agent Descriptions

| # | Node | File | What it does |
|---|---|---|---|
| 1 | `intent_extraction` | `agents/intent_extraction_agent.py` | Parses user input → JSON with `item`, `quantity`, `urgency`, `language`, `confidence`, `needs_clarification` |
| 2 | `task_planner` | `agents/task_planner_agent.py` | Creates an ordered step-by-step plan based on the detected intent |
| 3 | `search` | `agents/search_agent.py` | Queries **Zepto** (stdio/Playwright MCP) and **Swiggy Instamart** (SSE MCP) in parallel; returns raw product list |
| 4 | `comparison` | `agents/comparison_agent.py` | Normalises data across platforms; scores by **price 40% · speed 25% · quality 15% · platform reputation 20%** |
| 5 | `decision` | `agents/decision_agent.py` | Applies 6 safety policies (confidence, stock, price sanity, elderly safeguards, etc.); outputs one of: `auto_buy`, `confirm_with_user`, `clarify_needed`, `no_good_option` |
| 6 | `purchase` | `agents/purchase_agent.py` | Executes real Zepto COD order via MCP (simulates for other platforms); full audit logging; respects `GANGU_DRY_RUN` |
| 7 | `notification` | `orchestration/gangu_graph.py` | Generates a friendly Hindi/Hinglish response based on the final outcome |
| 8 | `query_info_only` | `orchestration/gangu_graph.py` | Handles informational queries — RAG placeholder (not yet built) |

---

## LLM — Google Gemini 2.5 Flash

All agents share one LLM client defined in `agents/llm.py`.

- **Model:** `gemini-2.5-flash` (default; override via `LLM_MODEL` in `.env`)
- **SDK:** `google-generativeai` (`google.genai`)
- **Key pool:** 6 Gemini API keys are stored in `llm.py`; one is **randomly chosen per call** to distribute load and avoid per-key rate limits
- **No code changes needed** to switch models — just change `LLM_MODEL`

```python
# agents/llm.py (simplified)
DEFAULT_MODEL = "gemini-2.5-flash"
GEMINI_KEYS = ["key1", "key2", ..., "key6"]   # pool of 6 keys

def Client():
    api_key = random.choice(GEMINI_KEYS)       # random key each call
    return genai.Client(api_key=api_key)
```

> **Note for production:** Move the keys from source code into `.env` and load them with `os.getenv()`.

---

## MCP Clients (Platform Connectors)

GANGU uses the **Model Context Protocol (MCP)** to talk to shopping platforms:

| Client | File | Transport | Status |
|---|---|---|---|
| **Zepto** | `mcp_clients/zepto_mcp_client.py` | `stdio` (Playwright/Firefox) | Catalog/demo connector; not a verified production API |
| **Swiggy Instamart** | `mcp_clients/swiggy_mcp_client.py` | `SSE` over HTTP | Client scaffold; live access pending Swiggy approval |
| Amazon | `mcp_clients/amazon_mcp_client.py` | — | Stub — not implemented |

The **Zepto connector** includes a built-in product URL catalog. Prices and availability are estimates unless a verified live connector supplies them, so the API defaults to dry-run and refuses to convert estimated results into real orders.

---

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- Docker (for MongoDB)
- Playwright Firefox (`python -m playwright install firefox`)

### 1 — Backend Setup

```powershell
# Install Python dependencies
pip install -r config/requirements.txt
pip install -r api/requirements.txt

# Install Playwright Firefox (needed for Zepto MCP)
python -m playwright install firefox

# Start MongoDB via Docker
cd config && docker-compose up -d && cd ..

# Copy and fill in env vars
copy .env.example .env
# Edit .env with your values (see "Environment Variables" below)
```

### 2 — Frontend Setup

```powershell
cd frontend
npm install
copy .env.local.example .env.local
# Edit frontend/.env.local if your backend URL is different
cd ..
```

### 3 — Run (two terminals)

```powershell
# Terminal 1 — Backend
cd api && python main.py          # → http://localhost:8000

# Terminal 2 — Frontend
cd frontend && npm run dev        # → http://localhost:3000
```

Open **http://localhost:3000** → **Sign in**. Phone OTP and Google use Firebase Authentication; there is no development OTP or mock social login. Enable the providers and authorize the domain in Firebase Console before testing.

### One-command start (optional)

```powershell
python start_gangu.py
```

---

## Environment Variables

### Backend `.env` (project root) — copy from `.env.example`

```env
# LLM — default model is set in agents/llm.py; override here if needed
GEMINI_API_KEY=your_gemini_api_key
LLM_MODEL=gemini-2.5-flash

# LangSmith tracing (optional — set false to disable)
LANGSMITH_TRACING=true
LANGSMITH_ENDPOINT=https://api.smith.langchain.com
LANGSMITH_API_KEY=your_langsmith_api_key
LANGSMITH_PROJECT=GANGU

# Zepto MCP (your Zepto-registered phone number)
ZEPTO_PHONE_NUMBER=your_10_digit_phone
ZEPTO_DEFAULT_ADDRESS=Home

# OpenAI Whisper (voice transcription only)
OPENAI_API_KEY=your_openai_api_key

# MongoDB (LangGraph checkpointing)
MONGODB_URI=mongodb://localhost:27017

# Firebase tokens are verified by the backend (fail-closed by default)
GANGU_AUTH_REQUIRED=true
FIREBASE_PROJECT_ID=gangu-adffd

# Safety — both switches are required before any real transaction is possible
GANGU_DRY_RUN=true
ENABLE_REAL_PURCHASES=false
```

### Frontend `frontend/.env.local`

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
NEXT_PUBLIC_FIREBASE_API_KEY=your_firebase_web_api_key
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
NEXT_PUBLIC_FIREBASE_PROJECT_ID=your-project-id
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=your-project.firebasestorage.app
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=your_sender_id
NEXT_PUBLIC_FIREBASE_APP_ID=your_web_app_id
```

In Firebase Console, enable **Google** and **Phone** under Authentication > Sign-in method. Add `localhost` for local development and the exact Vercel production hostname under Authentication > Settings > Authorized domains. The backend `FIREBASE_PROJECT_ID` must identify the same Firebase project. Firebase web configuration is public app metadata; never place an Admin SDK private key or service-account JSON in `NEXT_PUBLIC_*` variables.

---

## Frontend Routes

| Route | Description |
|---|---|
| `/` | Public, consumer-facing product explanation with honest live/demo boundaries |
| `/signin` | Redirect to the real Firebase authentication screen |
| `/signup` | Firebase phone OTP and Google authentication |
| `/app` | Voice/text request, transparent progress, comparison and explicit final review |
| `/app/orders` | Browser-local order records; provider history is not yet synchronized |
| `/app/lists` | Browser-local saved lists that prepare a new request for review |
| `/app/family` | Browser-local household contacts; no invitation or access grant is sent |
| `/app/settings` | Browser-local language, address, payment and accessibility preferences |

All `/app/*` routes are inside the `(authenticated)` route group and auto-redirect to `/signin` if the user is not logged in.

---

## Backend API Endpoints

| Method | Path | Purpose |
|---|---|---|
| `POST` | `/api/chat/process` | Run the full agent pipeline on a user message |
| `POST` | `/api/order/confirm` | Consume a one-time server quote and confirm the selected product |
| `POST` | `/api/auth/ws-ticket` | Issue an authenticated, single-use WebSocket ticket |
| `POST` | `/api/auth/swiggy/start` | Start authenticated Swiggy OAuth with PKCE |
| `GET` | `/api/auth/callback/swiggy` | Exact public Swiggy OAuth redirect path |
| `POST` | `/api/cancel` | Cancel an in-flight pipeline run |
| `POST` | `/api/voice/whisper` | Transcribe voice audio via OpenAI Whisper |
| `GET` | `/api/session/{id}` | Fetch current session state |
| `GET` | `/api/history` | Fetch order history |
| `WS` | `/ws/{session_id}` | Session-scoped agent updates; requires a short-lived ticket |

For local development and the current single-worker Render setup, `GANGU_STATE_BACKEND=memory` keeps session and OAuth state in-process. A multi-worker production deployment should use `GANGU_STATE_BACKEND=mongodb`; this makes session ownership and one-time quotes safe across workers and stores Swiggy OAuth tokens encrypted with `SWIGGY_TOKEN_ENCRYPTION_KEY`.

The exact redirect URI to send Swiggy is your deployed API origin plus `/api/auth/callback/swiggy`, for example `https://api.example.com/api/auth/callback/swiggy`. The same full value must be configured in `SWIGGY_REDIRECT_URI`.

---

## Tech Stack

### Backend
| Technology | Purpose |
|---|---|
| Python 3.11+ | Runtime |
| **LangGraph** | Agent orchestration (StateGraph + conditional routing) |
| **Google Gemini 2.5 Flash** | LLM powering all 6 agents |
| **FastAPI** | REST + WebSocket API server |
| **Playwright (Firefox)** | Browser automation for Zepto MCP |
| **MCP (Model Context Protocol)** | Platform integrations (Zepto, Swiggy) |
| MongoDB | LangGraph checkpointing — session memory and resumability |
| OpenAI Whisper | Voice transcription |
| LangSmith | Agent tracing and observability |

### Frontend
| Technology | Purpose |
|---|---|
| Next.js 14 (App Router) | Framework |
| TypeScript 5 | Type safety |
| Tailwind CSS 3 | Styling |
| Zustand 4 + persist | Global state with localStorage persistence |
| lucide-react | Icons |
| axios | HTTP API calls |
| Plus Jakarta Sans + Inter | Typography |

### Infrastructure
| Technology | Purpose |
|---|---|
| Docker Compose | MongoDB container |
| Render.com | Backend deployment (`render.yaml`) |
| PowerShell scripts | Local dev setup (`scripts/`) |

---

## Key Design Decisions

**Why LangGraph?**
LangGraph gives fine-grained control over the pipeline. Each agent is a named **graph node** and routing between them uses **conditional edges** (buy-intent → full search pipeline; info-intent → query handler). MongoDB-backed production persistence is still planned; the current quote/session store is single-process.

**Why a random key pool in `llm.py`?**
Gemini free-tier keys have per-minute rate limits. By randomly selecting from a pool of 6 keys, GANGU handles more concurrent requests without throttling.

**Why Playwright for Zepto?**
Zepto has no public API. The Zepto MCP client uses Playwright to automate Firefox — navigate the site, search, add to cart, checkout — exactly like a human. This is wrapped as an MCP server so agents call it as a tool.

**Why `GANGU_DRY_RUN`?**
The confirmation endpoint checks this flag before any platform call. When `true`, it returns an explicitly labelled dry-run result. A real transaction additionally requires `ENABLE_REAL_PURCHASES=true`, a verified live-data source, authentication, and a valid one-time quote.

---

## Dev Tips

- **Local auth bypass:** only set `GANGU_AUTH_REQUIRED=false` explicitly for isolated development/testing
- **TypeScript check:** `cd frontend && npx tsc --noEmit`
- **Backend safety tests:** `python -m pytest -q`
- **Reset auth state:** Clear the `gangu-store` key in browser localStorage
- **Cancel a pipeline:** The agent timeline has a **Cancel** button while running
- **Add a new platform:** Copy `mcp_clients/zepto_mcp_client.py` as a template; register it in `agents/search_agent.py`
- **Windows UTF-8:** `api/main.py` reconfigures stdout to UTF-8 so emoji don't crash on Windows cp1252 consoles
- **Disable LangSmith:** Set `LANGSMITH_TRACING=false` in `.env`

---

## Status

### ✅ Shipped
- All 6 agents + notification + query_info graph nodes
- LangGraph orchestration with conditional routing
- FastAPI backend (REST + WebSocket)
- Backend Firebase token verification and session-scoped WebSockets
- One-time quote → explicit confirmation transaction boundary
- Next.js frontend: landing · auth · workspace · 4 sub-routes
- Calm, accessible consumer landing and authenticated workspace
- Firebase Google and phone authentication in the active sign-in route
- Settings draft/save UX with toasts
- Real Firebase session synchronization, token refresh and global toast system

### ⚠️ Not Yet / Stubs
- Durable production persistence for orders, lists, contacts, preferences and idempotency
- Swiggy live MCP credentials and OAuth redirect flow (awaiting Swiggy approval)
- Zepto live MCP checkout; current catalog data is labelled as estimated
- Backend persistence for family members + saved lists (localStorage only)
- Amazon MCP client (`amazon_mcp_client.py` is an empty stub)
- BigBasket / JioMart / Dunzo MCP clients
- RAG-based `query_info_only` agent (placeholder message only)
- Complete authenticated end-to-end production verification using a real Firebase user

---

## Documentation

| File | Contents |
|---|---|
| [`ARCHITECTURE.md`](ARCHITECTURE.md) | Full system design + data flow |
| [`DEPLOYMENT_GUIDE.md`](DEPLOYMENT_GUIDE.md) | Production setup on Render.com |
| [`MCP_SETUP_GUIDE.md`](MCP_SETUP_GUIDE.md) | How to add new platform MCP clients |
| [`QUICKSTART.md`](QUICKSTART.md) | Minimal setup guide |
| [`FRONTEND_QUICKSTART.md`](FRONTEND_QUICKSTART.md) | Frontend-only setup |
| [`PROJECT_NAVIGATION.md`](PROJECT_NAVIGATION.md) | How to navigate the codebase |
| [`IMPLEMENTATION_SUMMARY.md`](IMPLEMENTATION_SUMMARY.md) | What was built and when |

Detailed docs also live in [`docs/`](docs/).

---

Built with ♥ in India · for the people tech often forgets.
