# GANGU

Voice-first grocery assistant for elderly Indian users. Speak naturally in Hindi, English, or Hinglish — six AI agents search Zepto and Amazon, compare options, apply safety policies, and place the order.

```
"doodh khatam ho gaya, le aao"
        ↓
   intent → plan → search → compare → decide → purchase
        ↓
   "Zepto · Amul Milk 1 L · ₹64 · 10 min" ✓
```

---

## What's in here

**Backend** — `api/` + `agents/` + `orchestration/` + `mcp_clients/`
- 6 Gemini-powered agents orchestrated with **LangGraph**
- **Zepto** MCP server (Playwright/Firefox automation) and **Amazon** MCP integration
- **FastAPI** REST + WebSocket server for live agent updates
- **MongoDB** checkpointing, **LangSmith** tracing
- **OpenAI Whisper** for voice transcription

**Frontend** — `frontend/` (Next.js 14 · TypeScript · Tailwind)
- Public landing with hero, live demo, platforms marquee, how-it-works, testimonials, pricing, FAQ
- Phone + OTP authentication (Truecaller/Zepto pattern)
- Authenticated workspace with voice + text input, live agent timeline, today panel, quick re-order
- Sub-pages for past orders, saved lists, family management, settings
- Dark glass design with warm saffron accents · persisted state · WCAG-friendly

---

## Quick start

```powershell
# 1) One-time backend setup
pip install -r config/requirements.txt
pip install -r api/requirements.txt
python -m playwright install firefox
cd config && docker-compose up -d && cd ..    # MongoDB

# 2) One-time frontend setup
cd frontend
npm install
cp .env.local.example .env.local
cd ..

# 3) Configure secrets — see "Environment" below
#    Edit .env (backend) and frontend/.env.local

# 4) Run (two terminals)
cd api && python main.py                       # → http://localhost:8000
cd frontend && npm run dev                     # → http://localhost:3000
```

Open **http://localhost:3000** → click **Get started** → use OTP `123456` in dev mode.

---

## Frontend routes

| Route | Description |
|---|---|
| `/` | Public landing page |
| `/signin` · `/signup` | Phone-OTP auth (split-screen) |
| `/app` | Workspace — voice + text input, agent timeline, today, quick re-order |
| `/app/orders` | Past orders with platform filter and pipeline replay |
| `/app/lists` | Saved shopping lists, dispatch whole list in one tap |
| `/app/family` | Invite & manage family members with permissions |
| `/app/settings` | Language · address · payment · accessibility · privacy |

`/app/*` is protected by an `(authenticated)` route group that redirects unauthenticated users to `/signin`.

---

## Backend endpoints

| Method | Path | Purpose |
|---|---|---|
| `POST` | `/api/chat/process` | Run the agent pipeline on a user message |
| `POST` | `/api/order/confirm` | Confirm a pending order from the comparison |
| `POST` | `/api/cancel` | Cancel an in-flight pipeline |
| `POST` | `/api/voice/whisper` | Transcribe voice via OpenAI Whisper |
| `GET` | `/api/session/{id}` | Fetch session state |
| `GET` | `/api/history` | Fetch order history |
| `WS` | `/ws/{session_id}` | Live agent step updates |

Auth endpoints (`/api/auth/otp/{request,verify}`) are stubs in `api/main.py`. The frontend mocks them locally with `123456` until the backend ships.

---

## Agent pipeline

| # | Agent | What it does |
|---|---|---|
| 1 | `intent_extraction_agent` | Parses Hindi/English/Hinglish into structured intent |
| 2 | `task_planner_agent` | Builds an ordered execution plan |
| 3 | `search_agent` | Queries Zepto + Amazon MCPs in parallel |
| 4 | `comparison_agent` | Scores by price (40%) · speed (25%) · quality (15%) · platform reputation |
| 5 | `decision_agent` | Applies 6 safety policies (confidence, stock, price sanity, elderly safeguards, etc.) |
| 6 | `purchase_agent` | Executes the order with audit logging |

---

## Folder structure

```
GANGU/
├── agents/                        # 6 Gemini-backed agents
├── api/                           # FastAPI server (main.py + requirements.txt)
├── config/                        # docker-compose.yml + Python requirements
├── docs/                          # Architecture & design docs
├── frontend/                      # Next.js 14 frontend
│   ├── app/
│   │   ├── page.tsx               # Public landing
│   │   ├── layout.tsx             # Root layout
│   │   ├── (auth)/{signin,signup}/page.tsx
│   │   └── (authenticated)/
│   │       ├── layout.tsx         # AppShell + auth guard
│   │       └── app/
│   │           ├── page.tsx       # Workspace
│   │           ├── orders/page.tsx
│   │           ├── lists/page.tsx
│   │           ├── family/page.tsx
│   │           └── settings/page.tsx
│   ├── components/
│   │   ├── auth/                  # AuthShell, PhoneOtpForm
│   │   ├── app/                   # AppShell, LeftRail, MobileNav, Greeting,
│   │   │                          # TodayPanel, QuickReorder, EmptyState
│   │   ├── landing/               # DemoStrip, Testimonials, Pricing, FAQ
│   │   └── *.tsx                  # VoiceInput, TextInput, AgentTimeline,
│   │                              # ProductComparison, OrderConfirmation,
│   │                              # SuccessScreen, Logo
│   ├── lib/                       # store.ts (Zustand + persist) · api.ts
│   ├── styles/globals.css         # Design system
│   └── tailwind.config.js
├── mcp_clients/                   # zepto_mcp_client.py · amazon_mcp_client.py
├── orchestration/
│   ├── gangu_graph.py             # LangGraph StateGraph + MongoDB checkpoint
│   └── gangu_main.py              # CLI entry point
├── scripts/                       # PowerShell setup + dev launchers
├── zepto-cafe-mcp/                # Standalone Zepto MCP server
└── README.md
```

---

## Environment

### Backend `.env` (project root)

```env
# Gemini (multiple keys for rate-limit rotation)
GEMINI_API_KEY=...
GEMINI_API_KEY_2=...
# ... up to 8

LANGSMITH_API_KEY=...
LANGSMITH_PROJECT=GANGU

ZEPTO_PHONE_NUMBER=98xxxxxxxx
ZEPTO_DEFAULT_ADDRESS=Home

OPENAI_API_KEY=...                  # for Whisper voice transcription
MONGODB_URI=mongodb://localhost:27017
```

### Frontend `frontend/.env.local`

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
```

---

## Tech stack

**Backend:** Python 3.11+ · LangGraph · Google GenAI (Gemini 2.5 Flash) · FastAPI · WebSockets · MongoDB · Playwright · OpenAI · LangSmith

**Frontend:** Next.js 14 (App Router) · TypeScript 5 · Tailwind CSS 3 · Zustand 4 (with persist) · lucide-react · Plus Jakarta Sans + Inter · axios

**Infrastructure:** Docker Compose for MongoDB · PowerShell setup scripts

---

## Dev tips

- **Dev OTP:** `123456` works for any phone number (frontend mock fallback).
- **TypeScript check:** `cd frontend && npx tsc --noEmit`.
- **Reset state:** clear the `gangu-store` key in browser localStorage to wipe persisted auth.
- **Cancel an order:** the agent timeline has a Cancel button while a pipeline is running.
- **Windows console:** `api/main.py` reconfigures stdout to UTF-8 so emoji prints don't crash on cp1252 consoles.
- **Adding a platform:** copy `mcp_clients/zepto_mcp_client.py` as a template; register the new client in `agents/search_agent.py`.

---

## Status

**Shipped:** all 6 agents · Zepto + Amazon MCP · LangGraph orchestration · MongoDB checkpointing · FastAPI backend · Next.js frontend (landing + auth + workspace + 4 sub-routes)

**Not yet:** real `/api/auth/*` endpoints (frontend mocks them) · backend persistence for family members + saved lists (frontend uses localStorage) · Blinkit/BigBasket/JioMart/Swiggy/Dunzo MCP clients

---

## Documentation

Detailed docs live in [`docs/`](docs/):

- `ARCHITECTURE.md` — full system design
- `PURCHASE_AGENT_ARCHITECTURE.md` — purchase flow & safety policies
- `FRONTEND_ARCHITECTURE.md` — frontend ↔ backend ↔ agent flow
- `DEPLOYMENT_GUIDE.md` — production setup
- `MCP_SETUP_GUIDE.md` — adding new platform MCPs

Top-level setup helpers: `QUICKSTART.md`, `FRONTEND_QUICKSTART.md`, `PROJECT_NAVIGATION.md`.

---

Built with ♥ in India · for the people tech often forgets.
