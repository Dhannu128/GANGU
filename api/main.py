"""GANGU FastAPI Backend

Exposes GANGU agents as REST API with WebSocket support for real-time updates.

This server also hosts a lightweight static web UI at /app.
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import asyncio
import json
import os
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from orchestration.gangu_graph import create_gangu_graph
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="GANGU API",
    description="Grocery Assistant for Elderly Users - Voice-First Agentic AI",
    version="1.0.0"
)

# CORS for local frontend usage (Vite/Next) and any embedded UI.
# NOTE: In production, tighten this list.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ConnectionManager:
    """Tracks WebSocket connections per session."""

    def __init__(self) -> None:
        self._connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, session_id: str, websocket: WebSocket) -> None:
        await websocket.accept()
        self._connections.setdefault(session_id, []).append(websocket)

    def disconnect(self, session_id: str, websocket: WebSocket) -> None:
        conns = self._connections.get(session_id)
        if not conns:
            return
        try:
            conns.remove(websocket)
        except ValueError:
            pass
        if not conns:
            self._connections.pop(session_id, None)

    async def send_json(self, session_id: str, payload: Dict[str, Any]) -> None:
        conns = list(self._connections.get(session_id, []))
        for ws in conns:
            try:
                await ws.send_json(payload)
            except Exception:
                # Drop dead sockets
                self.disconnect(session_id, ws)


ws_manager = ConnectionManager()

# Active sessions and cancellation tracking
active_sessions: Dict[str, bool] = {}  # session_id -> is_cancelled
session_tasks: Dict[str, asyncio.Task] = {}  # session_id -> task for instant cancellation

# Cache last pipeline state for confirmation step (in-memory; good for dev)
session_cache: Dict[str, Dict[str, Any]] = {}  # session_id -> {final_state, ranked_products, selected_option, ...}

# Request/Response Models
class VoiceTranscriptionRequest(BaseModel):
    """Request from Whisper API transcription"""
    text: str
    language: Optional[str] = "hi"  # Hindi default
    confidence: Optional[float] = 0.0

class ChatRequest(BaseModel):
    """Text-based chat request"""
    message: str
    session_id: Optional[str] = None

class OrderConfirmationRequest(BaseModel):
    """User confirms purchase"""
    session_id: str
    selected_product_index: int  # Which product from comparison

class CancelRequest(BaseModel):
    """Cancel processing request"""
    session_id: str

class AgentStatusUpdate(BaseModel):
    """Real-time agent status update"""
    step: str
    status: str  # "processing", "complete", "error"
    message: str
    data: Optional[Dict[str, Any]] = None

# Initialize GANGU Graph
gangu_graph = None

def init_gangu():
    """Initialize GANGU graph"""
    global gangu_graph
    try:
        gangu_graph = create_gangu_graph()
        print("✅ GANGU Graph initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize GANGU: {e}")
        raise

@app.on_event("startup")
async def startup_event():
    """Initialize GANGU on startup"""
    init_gangu()

    # Mount static web UI at /app (if present)
    web_dir = Path(__file__).parent.parent / "web"
    if web_dir.exists():
        app.mount("/app", StaticFiles(directory=str(web_dir), html=True), name="app")
        print(f"✅ Mounted web UI at /app from: {web_dir}")

# ============================================================================
# WEBSOCKET ENDPOINT - Real-time Agent Updates
# ============================================================================

@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """
    WebSocket connection for real-time agent pipeline updates
    Frontend connects here to receive live status
    """
    await ws_manager.connect(session_id, websocket)
    
    try:
        await websocket.send_json({
            "type": "connection",
            "status": "connected",
            "session_id": session_id,
            "message": "Connected to GANGU"
        })
        
        # Keep connection alive. Client may optionally send heartbeats.
        while True:
            _ = await websocket.receive_text()
            await websocket.send_json({"type": "heartbeat", "status": "alive"})
            
    except WebSocketDisconnect:
        ws_manager.disconnect(session_id, websocket)
        print(f"Client {session_id} disconnected")

async def broadcast_agent_status(session_id: str, update: AgentStatusUpdate):
    """Broadcast agent status to WebSocket clients for this session."""
    message = {
        "type": "agent_update",
        "session_id": session_id,
        "timestamp": datetime.now().isoformat(),
        **update.dict()
    }

    await ws_manager.send_json(session_id, message)
    # Small delay to improve perceived ordering in UI
    await asyncio.sleep(0.05)

# ============================================================================
# REST API ENDPOINTS
# ============================================================================

@app.get("/")
async def root():
    """Health check"""
    return {
        "status": "healthy",
        "service": "GANGU API",
        "version": "1.0.0"
    }


@app.get("/api/project/index")
async def project_index():
    """Lightweight project index for the frontend (agent list + UX hints)."""
    return {
        "name": "GANGU",
        "ui": {"path": "/app"},
        "agents": [
            {"id": "intent_extraction", "label": "Intent Extraction", "order": 1},
            {"id": "task_planning", "label": "Task Planning", "order": 2},
            {"id": "search", "label": "Search", "order": 3},
            {"id": "comparison", "label": "Comparison", "order": 4},
            {"id": "decision", "label": "Decision", "order": 5},
            {"id": "purchase", "label": "Purchase", "order": 6},
            {"id": "notification", "label": "Notification", "order": 7},
            {"id": "query_info", "label": "Knowledge (RAG)", "order": 8},
        ],
        "capabilities": {
            "chat": True,
            "voice": True,
            "realtime_agent_updates": True,
            "rag_query": True,
        },
    }

@app.post("/api/voice/transcribe")
async def transcribe_voice(request: VoiceTranscriptionRequest):
    """
    Receive transcribed voice input from frontend (Whisper API)
    Returns processed intent
    """
    try:
        # Store transcription
        return {
            "success": True,
            "transcription": request.text,
            "language": request.language,
            "confidence": request.confidence,
            "message": "Transcription received"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/voice/whisper")
async def whisper_transcribe(file: UploadFile = File(...)):
    """
    OpenAI Whisper API endpoint for voice transcription
    Uses premium API key - ONLY for voice transcription
    """
    try:
        from openai import OpenAI
        import tempfile
        
        # Get API key from environment
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            raise HTTPException(status_code=500, detail="OpenAI API key not configured")
        
        # Initialize OpenAI client
        client = OpenAI(api_key=openai_api_key)
        
        # Read audio file from request
        audio_data = await file.read()
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(suffix=".webm", delete=False) as temp_audio:
            temp_audio.write(audio_data)
            temp_audio_path = temp_audio.name
        
        # Transcribe using Whisper
        with open(temp_audio_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language="hi"  # Hindi + English mix
            )
        
        # Cleanup temp file
        os.unlink(temp_audio_path)
        
        return {
            "success": True,
            "text": transcript.text,
            "language": "hi-IN"
        }
        
    except Exception as e:
        print(f"❌ Whisper error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/chat/process")
async def process_chat(request: ChatRequest):
    """
    Main endpoint: Process user input through GANGU pipeline
    Returns: Intent extraction + Task plan + Search results + Comparison
    
    This is the CORE endpoint that runs the entire agent pipeline
    """
    try:
        session_id = request.session_id or f"session_{datetime.now().timestamp()}"
        
        # Initialize session as not cancelled
        active_sessions[session_id] = False
        
        # Broadcast: Starting pipeline
        await broadcast_agent_status(
            session_id,
            AgentStatusUpdate(
                step="init",
                status="processing",
                message="Understanding your request...",
                data={"input": request.message}
            )
        )
        
        # Run GANGU pipeline
        config = {"configurable": {"thread_id": session_id}}
        initial_state = {
            "user_input": request.message,
            "messages": [],
            "user_preferences": {},
        }
        
        # Initial status
        await broadcast_agent_status(
            session_id,
            AgentStatusUpdate(
                step="intent_extraction",
                status="processing",
                message="Understanding your request...",
                data={}
            )
        )
        
        # Stream through the graph with proper exception handling
        # LangGraph stream yields events like: {"node_name": full_state_at_that_node}
        last_state: Optional[Dict[str, Any]] = None
        cancelled = False
        
        try:
            async for event in gangu_graph.astream(initial_state, config):
                # Check for cancellation before processing each event
                if active_sessions.get(session_id, False):
                    print(f"⏹️ Session {session_id} cancelled by user")
                    await broadcast_agent_status(
                        session_id,
                        AgentStatusUpdate(
                            step="cancelled",
                            status="error",
                            message="Operation cancelled by user",
                            data={}
                        )
                    )
                    # Cleanup
                    active_sessions.pop(session_id, None)
                    cancelled = True
                    break  # Exit the loop immediately
                
                # Broadcast each agent's progress based on node names
                # LangGraph returns events with node names as keys

                # Track final state for API response
                try:
                    if isinstance(event, dict) and len(event) == 1:
                        _node, _state = next(iter(event.items()))
                        if isinstance(_state, dict):
                            last_state = _state
                except Exception:
                    pass
                
                if "intent_extraction" in event:
                    node_state = event["intent_extraction"]
                    item = node_state.get("item_name", "processing...")
                    await broadcast_agent_status(
                        session_id,
                        AgentStatusUpdate(
                            step="intent_extraction",
                            status="complete",
                            message=f"Understood: {item}",
                            data={"item": item, "intent": node_state.get("detected_intent")}
                        )
                    )
                    # Start next step
                    await broadcast_agent_status(
                        session_id,
                        AgentStatusUpdate(
                            step="task_planning",
                            status="processing",
                            message="Creating execution plan...",
                            data={}
                        )
                    )
                
                if "task_planner" in event:
                    node_state = event["task_planner"]
                    steps = node_state.get("execution_steps", [])
                    intent = node_state.get("detected_intent", "")
                    needs_clarification = node_state.get("needs_clarification", False)

                    await broadcast_agent_status(
                        session_id,
                        AgentStatusUpdate(
                            step="task_planning",
                            status="complete",
                            message=f"Plan created with {len(steps)} steps",
                            data={"steps": len(steps)}
                        )
                    )

                    # Predict route to broadcast the correct next-step
                    is_purchase = any(kw in intent for kw in ["buy", "reorder"]) and not needs_clarification
                    if is_purchase:
                        await broadcast_agent_status(
                            session_id,
                            AgentStatusUpdate(
                                step="search",
                                status="processing",
                                message="Searching across platforms...",
                                data={}
                            )
                        )
                    else:
                        await broadcast_agent_status(
                            session_id,
                            AgentStatusUpdate(
                                step="query_info",
                                status="processing",
                                message="Searching knowledge base...",
                                data={}
                            )
                        )
                
                if "search" in event:
                    node_state = event["search"]
                    platforms = node_state.get("platforms_searched", [])
                    await broadcast_agent_status(
                        session_id,
                        AgentStatusUpdate(
                            step="search",
                            status="complete",
                            message=f"Found products from {len(platforms)} platforms",
                            data={"platforms": platforms}
                        )
                    )
                    # Start next step
                    await broadcast_agent_status(
                        session_id,
                        AgentStatusUpdate(
                            step="comparison",
                            status="processing",
                            message="Comparing products...",
                            data={}
                        )
                    )
                
                if "comparison" in event:
                    node_state = event["comparison"]
                    ranked = node_state.get("ranked_products", [])
                    await broadcast_agent_status(
                        session_id,
                        AgentStatusUpdate(
                            step="comparison",
                            status="complete",
                            message=f"Compared {len(ranked)} products successfully",
                            data={"count": len(ranked)}
                        )
                    )
                    # Start next step
                    await broadcast_agent_status(
                        session_id,
                        AgentStatusUpdate(
                            step="decision",
                            status="processing",
                            message="Selecting best option...",
                            data={}
                        )
                    )
                
                if "decision" in event:
                    node_state = event["decision"]
                    selected = node_state.get("selected_option", {})
                    await broadcast_agent_status(
                        session_id,
                        AgentStatusUpdate(
                            step="decision",
                            status="complete",
                            message="Best option selected",
                            data={"platform": selected.get("platform")}
                        )
                    )
                    # Start purchase step
                    await broadcast_agent_status(
                        session_id,
                        AgentStatusUpdate(
                            step="purchase",
                            status="processing",
                            message="Processing order...",
                            data={}
                        )
                    )
                
                if "purchase" in event:
                    await broadcast_agent_status(
                        session_id,
                        AgentStatusUpdate(
                            step="purchase",
                            status="processing",
                            message="Processing order...",
                            data={}
                        )
                    )
                
                if "query_info_only" in event:
                    node_state = event["query_info_only"]
                    rag_meta = node_state.get("rag_metadata", {})
                    sources_used = rag_meta.get("sources_used", 0) if isinstance(rag_meta, dict) else 0
                    await broadcast_agent_status(
                        session_id,
                        AgentStatusUpdate(
                            step="query_info",
                            status="complete",
                            message=f"Found answer from {sources_used} knowledge sources",
                            data={"sources_used": sources_used, "method": "rag"}
                        )
                    )
                    
                # Note: purchase + notification are already nodes in the graph.
        
        except (GeneratorExit, asyncio.CancelledError, StopAsyncIteration) as e:
            # Handle graceful shutdown of async generator
            print(f"⏹️ Graph stream interrupted for session {session_id}: {type(e).__name__}")
            cancelled = True
            await broadcast_agent_status(
                session_id,
                AgentStatusUpdate(
                    step="cancelled",
                    status="error",
                    message="Processing stopped",
                    data={}
                )
            )
        
        # If cancelled, return cancellation response
        if cancelled:
            # Cleanup session
            active_sessions.pop(session_id, None)
            return {
                "success": False,
                "session_id": session_id,
                "message": "Operation cancelled by user",
                "cancelled": True
            }

        # Ensure we have a final state
        if not last_state:
            raise RuntimeError("Pipeline finished without a final state")

        # Cache for later confirmation step
        session_cache[session_id] = {
            "final_state": last_state,
            "ranked_products": last_state.get("ranked_products", []) or [],
            "selected_option": last_state.get("selected_option"),
            "comparison_results": last_state.get("comparison_results", {}) or {},
            "decision_results": last_state.get("decision_results", {}) or {},
        }
        
        # Clean up session from active sessions
        if session_id in active_sessions:
            del active_sessions[session_id]

        decision_type = last_state.get("decision_type", "")
        purchase_status = last_state.get("purchase_status", "")
        requires_confirmation = decision_type == "confirm_with_user" or purchase_status == "pending_confirmation"

        return {
            "success": True,
            "session_id": session_id,
            "ai_response": last_state.get("ai_response", ""),
            "intent": last_state.get("intent_data", {}),
            "ranked_products": last_state.get("ranked_products", []),
            "selected_option": last_state.get("selected_option"),
            "comparison_results": last_state.get("comparison_results", {}),
            "decision_results": last_state.get("decision_results", {}),
            "decision_type": decision_type,
            "purchase_status": purchase_status,
            "requires_confirmation": requires_confirmation,
            "rag_metadata": last_state.get("rag_metadata"),
        }
        
    except Exception as e:
        await broadcast_agent_status(
            session_id,
            AgentStatusUpdate(
                step="error",
                status="error",
                message=f"Error: {str(e)}"
            )
        )
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# RAG QUERY ENDPOINT — Standalone knowledge query
# ============================================================================

class RAGQueryRequest(BaseModel):
    """Direct RAG knowledge query (bypasses full pipeline)"""
    query: str
    language: Optional[str] = "hinglish"

@app.post("/api/query/info")
async def query_info_endpoint(request: RAGQueryRequest):
    """
    Standalone RAG query endpoint.
    Directly queries the knowledge base without running the full agent pipeline.
    Useful for quick product info, feature questions, translations, etc.
    """
    try:
        from agents.query_info_agent import query_info
        result = query_info(request.query, language_hint=request.language or "hinglish")
        return {
            "success": True,
            **result,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"RAG query failed: {str(e)}")

@app.get("/api/query/search")
async def rag_search(q: str, top_k: int = 5):
    """
    Search the knowledge base (no generation, just retrieval).
    Useful for debugging and seeing what the RAG system finds.
    """
    try:
        from agents.query_info_agent import get_agent
        agent = get_agent()
        results = agent.search_only(q, top_k=top_k)
        return {
            "success": True,
            "query": q,
            "results": results,
            "count": len(results),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"RAG search failed: {str(e)}")

@app.post("/api/order/confirm")
async def confirm_order(request: OrderConfirmationRequest):
    """
    User confirms purchase - triggers Purchase Agent
    """
    try:
        session_id = request.session_id

        cached = session_cache.get(session_id, {})
        ranked_products = cached.get("ranked_products", []) or []
        if not ranked_products:
            raise HTTPException(status_code=400, detail="No ranked products found for this session. Run /api/chat/process first.")

        if request.selected_product_index < 0 or request.selected_product_index >= len(ranked_products):
            raise HTTPException(status_code=400, detail=f"selected_product_index out of range (0..{len(ranked_products)-1})")

        chosen = ranked_products[request.selected_product_index]
        
        # Broadcast: Purchase starting
        await broadcast_agent_status(
            session_id,
            AgentStatusUpdate(
                step="purchase",
                status="processing",
                message="Adding to cart...",
                data={"product_index": request.selected_product_index, "platform": chosen.get("platform")}
            )
        )

        # Execute real purchase via purchase_agent
        await broadcast_agent_status(
            session_id,
            AgentStatusUpdate(
                step="purchase",
                status="processing",
                message="Checking out...",
                data={"platform": chosen.get("platform")}
            )
        )

        try:
            from agents.purchase_agent import execute_purchase

            final_state = cached.get("final_state", {}) or {}
            urgency = final_state.get("urgency", "normal")
            item_name = final_state.get("item_name") or chosen.get("item_name") or chosen.get("name") or "item"
            quantity = final_state.get("quantity", "1")

            purchase_input = {
                "final_decision": {
                    "selected_platform": chosen.get("platform", "zepto"),
                    "product": {
                        "name": item_name,
                        "price": chosen.get("price") or chosen.get("normalized_attributes", {}).get("price") or 0,
                        "quantity": quantity,
                        "product_id": (item_name or "item").lower().replace(" ", "_").replace(",", "_")
                    },
                    "delivery": {"delivery_date": "today", "slot": "within 1 hour"},
                },
                "user_context": {
                    "payment_preference": "cash_on_delivery",
                    "platform_preference": chosen.get("platform", "zepto"),
                    "confirmed_by_user": True,
                    "urgency_level": urgency,
                },
            }

            purchase_result = execute_purchase(purchase_input)

        except Exception as e:
            await broadcast_agent_status(
                session_id,
                AgentStatusUpdate(
                    step="purchase",
                    status="error",
                    message=f"Purchase failed: {str(e)}",
                    data={}
                )
            )
            raise HTTPException(status_code=500, detail=str(e))

        is_success = purchase_result.get("purchase_status") == "success" or purchase_result.get("success") is True
        order_id = (
            purchase_result.get("execution_details", {}).get("order_id")
            or purchase_result.get("order_id")
            or f"ORD-{datetime.now().timestamp()}"
        )

        await broadcast_agent_status(
            session_id,
            AgentStatusUpdate(
                step="purchase",
                status="complete" if is_success else "error",
                message="Order placed successfully" if is_success else "Order placement failed",
                data={"order_id": order_id, **(purchase_result if isinstance(purchase_result, dict) else {})}
            )
        )

        await broadcast_agent_status(
            session_id,
            AgentStatusUpdate(
                step="notification",
                status="complete" if is_success else "error",
                message="Done" if is_success else "Order failed",
                data={"order_id": order_id}
            )
        )

        return {
            "success": bool(is_success),
            "order_id": order_id,
            "message": "Order placed successfully" if is_success else "Order placement failed",
            "purchase_result": purchase_result,
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/session/{session_id}")
async def get_session_data(session_id: str):
    """Retrieve session data for continuing conversation"""
    try:
        # TODO: Retrieve from MongoDB checkpointer
        return {
            "success": True,
            "session_id": session_id,
            "message": "Session data retrieved"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/history")
async def get_order_history():
    """Get user's order history (for personalization UI)"""
    try:
        # TODO: Retrieve from database
        return {
            "success": True,
            "orders": [],
            "frequent_items": []
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/cancel")
async def cancel_processing(request: CancelRequest):
    """
    Cancel ongoing agent processing
    """
    try:
        session_id = request.session_id
        
        # Mark session as cancelled
        active_sessions[session_id] = True  # True = cancelled
        
        # Broadcast cancellation
        await broadcast_agent_status(
            session_id,
            AgentStatusUpdate(
                step="cancelled",
                status="error",
                message="Processing cancelled by user",
                data={"cancelled": True}
            )
        )
        
        return {
            "success": True,
            "session_id": session_id,
            "message": "Processing cancelled successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
