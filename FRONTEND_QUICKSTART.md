# GANGU Frontend (Static UI)

This repo now includes a **professional static web UI** served directly by the FastAPI backend.

## What you get

- Chat UI to run the **full agent pipeline**
- **Voice input** (browser speech recognition)
- **Live agent workflow** timeline (Intent → Plan → Search → Compare → Decide → Purchase)
- Product options + **Confirm** to place order

## Run

1) Install backend deps (if you haven’t already)

- Use your existing Python setup (`config/requirements.txt` or `api/requirements.txt`).

2) Start the API

- Run `uvicorn api.main:app --reload --port 8000`

3) Open the UI

- Visit: `http://localhost:8000/app`

## Notes

- Voice input uses the browser’s Web Speech API (best on Chrome/Edge).
- The UI uses Tailwind **CDN** (no Node/Vite build required).
- WebSocket endpoint: `/ws/{session_id}`
- Chat pipeline endpoint: `POST /api/chat/process`
- Purchase confirm endpoint: `POST /api/order/confirm`
