"""
GANGU FastAPI Backend
Exposes GANGU agents as REST API with WebSocket support for real-time updates
"""
import logging
from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI, WebSocket, WebSocketDisconnect, HTTPException, File, UploadFile, Query
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Literal
import asyncio
import json
import os
import sys
import secrets
from pathlib import Path
from datetime import datetime

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

# --- LangSmith: disable cleanly when key is missing/placeholder so we don't
# spam the console with 403s and slow each request down. ---
def _is_real_key(value: Optional[str]) -> bool:
    if not value:
        return False
    v = value.strip().lower()
    return len(v) >= 20 and not any(token in v for token in ("your", "placeholder", "here", "xxxx", "replace"))

if not _is_real_key(os.getenv("LANGSMITH_API_KEY")):
    os.environ["LANGSMITH_TRACING"] = "false"
    os.environ["LANGCHAIN_TRACING_V2"] = "false"
    logging.getLogger("langsmith").setLevel(logging.CRITICAL)

from orchestration.gangu_graph import create_gangu_graph
from api.security import AuthenticatedUser, authenticate_websocket, get_current_user, ws_tickets
from api.session_store import session_store
from api.swiggy_oauth import create_authorization_url, exchange_callback
from api.zepto_runtime import ZeptoOrderRuntime

zepto_runtime = ZeptoOrderRuntime(Path(__file__).parent.parent / "zepto-cafe-mcp" / "zepto_mcp_server.py")

@asynccontextmanager
async def lifespan(app: FastAPI):
    global gangu_graph
    try:
        gangu_graph = create_gangu_graph()
        print("✅ GANGU Graph initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize GANGU: {e}")
        raise
    yield
    await zepto_runtime.close_all()

app = FastAPI(
    title="GANGU API",
    description="Grocery Assistant for Elderly Users - Voice-First Agentic AI",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS Configuration - Allow frontend to connect
# Add prod URLs via FRONTEND_URLS env var (comma-separated), e.g.
# FRONTEND_URLS=https://gangu.vercel.app,https://gangu-staging.vercel.app
_default_origins = ["http://localhost:3000", "http://localhost:3001"]
_extra_origins = [o.strip() for o in os.getenv("FRONTEND_URLS", "").split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_default_origins + _extra_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Active WebSocket connections, isolated by authenticated user and session.
active_connections: Dict[tuple[str, str], set[WebSocket]] = {}

# Active sessions and cancellation tracking
active_sessions: Dict[str, bool] = {}  # session_id -> is_cancelled
session_tasks: Dict[str, asyncio.Task] = {}  # session_id -> task for instant cancellation

# Request/Response Models
class VoiceTranscriptionRequest(BaseModel):
    """Request from Whisper API transcription"""
    text: str = Field(min_length=1, max_length=10_000)
    language: Optional[str] = "hi"  # Hindi default
    confidence: Optional[float] = 0.0

class ChatRequest(BaseModel):
    """Text-based chat request"""
    message: str = Field(min_length=1, max_length=2_000)
    session_id: Optional[str] = Field(default=None, min_length=8, max_length=128, pattern=r"^[A-Za-z0-9_-]+$")

class OrderConfirmationRequest(BaseModel):
    """User confirms purchase"""
    session_id: str = Field(min_length=8, max_length=128, pattern=r"^[A-Za-z0-9_-]+$")
    quote_id: str = Field(min_length=16, max_length=128)
    selected_product_index: int = Field(ge=0, le=100)
    delivery_address: str = Field(min_length=5, max_length=500)
    payment_method: Literal["upi", "cod", "card"]


class ZeptoOtpRequest(BaseModel):
    session_id: str = Field(min_length=8, max_length=128, pattern=r"^[A-Za-z0-9_-]+$")
    otp: str = Field(pattern=r"^\d{4,8}$")
    otp_type: Literal["login", "payment"] = "login"

class CancelRequest(BaseModel):
    """Cancel processing request"""
    session_id: str = Field(min_length=8, max_length=128, pattern=r"^[A-Za-z0-9_-]+$")

class AgentStatusUpdate(BaseModel):
    """Real-time agent status update"""
    step: str
    status: str  # "processing", "complete", "error"
    message: str
    data: Optional[Dict[str, Any]] = None

# Initialize GANGU Graph
gangu_graph = None


# ============================================================================
# WEBSOCKET ENDPOINT - Real-time Agent Updates
# ============================================================================

@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """
    WebSocket connection for real-time agent pipeline updates
    Frontend connects here to receive live status
    """
    user = await authenticate_websocket(websocket)
    if user is None:
        await websocket.close(code=4401, reason="Authentication required")
        return
    try:
        session_store.claim_session(session_id, user.uid)
    except PermissionError:
        await websocket.close(code=4403, reason="Session access denied")
        return

    key = (user.uid, session_id)
    await websocket.accept()
    active_connections.setdefault(key, set()).add(websocket)
    
    try:
        await websocket.send_json({
            "type": "connection",
            "status": "connected",
            "session_id": session_id,
            "message": "Connected to GANGU"
        })
        
        # Keep connection alive
        while True:
            data = await websocket.receive_text()
            # Echo back for heartbeat
            await websocket.send_json({"type": "heartbeat", "status": "alive"})
            
    except WebSocketDisconnect:
        connections = active_connections.get(key)
        if connections:
            connections.discard(websocket)
            if not connections:
                active_connections.pop(key, None)
        print(f"Client {session_id} disconnected")

async def broadcast_agent_status(session_id: str, update: AgentStatusUpdate):
    """Send an agent update only to the owning user's session sockets."""
    message = {
        "type": "agent_update",
        "session_id": session_id,
        "timestamp": datetime.now().isoformat(),
        **update.model_dump()
    }
    
    user_id = session_store.owner_of(session_id)
    if user_id is None:
        return
    dead_connections: list[WebSocket] = []
    for connection in list(active_connections.get((user_id, session_id), set())):
        try:
            await connection.send_json(message)
        except Exception:
            dead_connections.append(connection)
    for connection in dead_connections:
        active_connections.get((user_id, session_id), set()).discard(connection)


@app.post("/api/auth/ws-ticket")
async def create_websocket_ticket(user: AuthenticatedUser = Depends(get_current_user)):
    ticket, expires_in = ws_tickets.issue(user)
    return {"ticket": ticket, "expires_in": expires_in}


@app.post("/api/auth/swiggy/start")
async def start_swiggy_oauth(user: AuthenticatedUser = Depends(get_current_user)):
    return {"authorization_url": create_authorization_url(user.uid)}


@app.get("/api/auth/callback/swiggy", response_class=HTMLResponse)
async def swiggy_oauth_callback(
    code: str = Query(min_length=4, max_length=4096),
    state: str = Query(min_length=16, max_length=512),
):
    await exchange_callback(code, state)
    return HTMLResponse(
        "<html><body><h1>Swiggy connected successfully</h1>"
        "<p>You can close this window and return to GANGU.</p></body></html>"
    )

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


@app.get("/api/integrations/zepto/status")
async def zepto_integration_status():
    """Report capability readiness without exposing phone/address secrets."""
    server_path = Path(__file__).parent.parent / "zepto-cafe-mcp" / "zepto_mcp_server.py"
    phone_configured = bool(os.getenv("ZEPTO_PHONE_NUMBER", "").strip())
    address_configured = bool(os.getenv("ZEPTO_DEFAULT_ADDRESS", "").strip())
    dry_run = os.getenv("GANGU_DRY_RUN", "true").strip().lower() == "true"
    enabled = os.getenv("ENABLE_REAL_PURCHASES", "false").strip().lower() == "true"
    return {
        "provider": "zepto",
        "mcp_server_available": server_path.exists(),
        "catalog_search_ready": server_path.exists(),
        "cod_only": os.getenv("ZEPTO_PAYMENT_METHOD", "cod").strip().lower() == "cod",
        "phone_configured": phone_configured,
        "address_configured": address_configured,
        "dry_run": dry_run,
        "real_purchase_enabled": enabled,
        "order_flow_ready": server_path.exists() and phone_configured and address_configured and enabled and not dry_run,
    }

@app.post("/api/voice/transcribe")
async def transcribe_voice(
    request: VoiceTranscriptionRequest,
    user: AuthenticatedUser = Depends(get_current_user),
):
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
async def whisper_transcribe(
    file: UploadFile = File(...),
    user: AuthenticatedUser = Depends(get_current_user),
):
    """
    OpenAI Whisper API endpoint for voice transcription
    Uses premium API key - ONLY for voice transcription
    """
    temp_audio_path = None
    try:
        from openai import OpenAI
        import tempfile

        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            raise HTTPException(status_code=503, detail="Voice transcription is not configured")

        audio_data = await file.read()
        if len(audio_data) > 25 * 1024 * 1024:
            raise HTTPException(status_code=413, detail="Audio file exceeds the 25 MB limit")

        with tempfile.NamedTemporaryFile(suffix=".webm", delete=False) as temp_audio:
            temp_audio.write(audio_data)
            temp_audio_path = temp_audio.name

        client = OpenAI(api_key=openai_api_key)
        with open(temp_audio_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language="hi",
            )

        return {"success": True, "text": transcript.text, "language": "hi-IN"}
    except HTTPException:
        raise
    except Exception as exc:
        print(f"Whisper error: {exc}")
        raise HTTPException(status_code=502, detail="Voice transcription failed") from exc
    finally:
        if temp_audio_path and os.path.exists(temp_audio_path):
            os.unlink(temp_audio_path)


@app.post("/api/chat/process")
async def process_chat(
    request: ChatRequest,
    user: AuthenticatedUser = Depends(get_current_user),
):
    """
    Main endpoint: Process user input through GANGU pipeline
    Returns: Intent extraction + Task plan + Search results + Comparison
    
    This is the CORE endpoint that runs the entire agent pipeline
    """
    try:
        session_id = request.session_id or f"session_{secrets.token_urlsafe(18)}"
        try:
            session_store.claim_session(session_id, user.uid)
        except PermissionError as exc:
            raise HTTPException(status_code=403, detail=str(exc)) from exc
        existing_task = session_tasks.get(session_id)
        if existing_task is not None and not existing_task.done():
            raise HTTPException(status_code=409, detail="This session is already processing a request")
        
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
            "messages": []
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
        
        # Stream through the graph as a CHILD TASK so /api/cancel can
        # interrupt it instantly via asyncio.Task.cancel(). Without this, the
        # cancel flag is only checked between agent boundaries — and slow
        # agents (e.g. Zepto MCP retries) keep the user waiting up to 15s.
        result_state: Optional[Dict[str, Any]] = None
        merged_state: Dict[str, Any] = {}
        cancelled = False

        async def _run_stream():
            nonlocal result_state
            async for event in gangu_graph.astream(initial_state, config):
                if isinstance(event, dict):
                    for node_state in event.values():
                        if isinstance(node_state, dict):
                            merged_state.update(node_state)
                # Cooperative cancel — kept for safety in case .cancel() isn't called.
                if active_sessions.get(session_id, False):
                    print(f"⏹️ Session {session_id} cancelled (cooperative)")
                    raise asyncio.CancelledError()
                
                # Broadcast each agent's progress based on node names
                # LangGraph returns events with node names as keys
                
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
                    await broadcast_agent_status(
                        session_id,
                        AgentStatusUpdate(
                            step="task_planning",
                            status="complete",
                            message=f"Plan created with {len(steps)} steps",
                            data={"steps": len(steps)}
                        )
                    )
                    # Start next step
                    await broadcast_agent_status(
                        session_id,
                        AgentStatusUpdate(
                            step="search",
                            status="processing",
                            message="Searching across platforms...",
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
                    
                if "purchase_result" in event or (result_state and "purchase" in result_state):
                    purchase_data = event.get("purchase_result") or result_state.get("purchase", {})
                    is_success = purchase_data.get("success", False)
                    
                    await broadcast_agent_status(
                        session_id,
                        AgentStatusUpdate(
                            step="purchase",
                            status="complete" if is_success else "error",
                            message="Order processed successfully" if is_success else "Order processing failed",
                            data=purchase_data
                        )
                    )
                    
                    # Send notification update
                    await broadcast_agent_status(
                        session_id,
                        AgentStatusUpdate(
                            step="notification",
                            status="complete",
                            message="Notification sent",
                            data={}
                        )
                    )
                
                result_state = event
        # END of _run_stream

        pipeline_task = asyncio.create_task(_run_stream())
        session_tasks[session_id] = pipeline_task

        try:
            await pipeline_task
        except (GeneratorExit, asyncio.CancelledError, StopAsyncIteration) as e:
            print(f"⏹️ Graph stream interrupted for session {session_id}: {type(e).__name__}")
            cancelled = True
            try:
                await broadcast_agent_status(
                    session_id,
                    AgentStatusUpdate(
                        step="cancelled",
                        status="error",
                        message="Processing stopped",
                        data={}
                    )
                )
            except Exception:
                pass
        finally:
            session_tasks.pop(session_id, None)
            active_sessions.pop(session_id, None)

        if cancelled:
            return {
                "success": False,
                "session_id": session_id,
                "message": "Operation cancelled by user",
                "cancelled": True,
            }
        
        # After graph completes, ensure purchase and notification are marked complete.
        if merged_state.get("decision_results") or merged_state.get("selected_option"):
            await broadcast_agent_status(
                session_id,
                AgentStatusUpdate(
                    step="purchase",
                    status="complete",
                    message="Order prepared (awaiting confirmation)",
                    data={}
                )
            )
            await broadcast_agent_status(
                session_id,
                AgentStatusUpdate(
                    step="notification",
                    status="complete",
                    message="Ready to confirm",
                    data={}
                )
            )

        # Extract final state from the accumulator (event payloads only carry the
        # latest node's output, so we must merge across the full stream).
        intent_block = merged_state.get("intent_data", {})
        comparison_block = merged_state.get("comparison_results", {})
        ranked_products = merged_state.get("ranked_products", [])
        decision_block = merged_state.get("decision_results", {})
        selected_option = merged_state.get("selected_option")
        ai_response = merged_state.get("ai_response", "")
        decision_type = merged_state.get("decision_type", "unknown")

        # Preserve provenance from search results. LLM ranking output is not
        # trusted to invent or relabel whether a product came from live data.
        raw_results = merged_state.get("search_results", {}).get("results", [])
        provenance_by_id = {
            str(product.get("product_id")): product
            for product in raw_results
            if product.get("product_id") is not None
        }
        enriched_products = []
        for product in ranked_products:
            enriched = dict(product)
            raw = provenance_by_id.get(str(product.get("product_id")), {})
            enriched["source"] = raw.get("source", "unknown")
            enriched["url"] = raw.get("url") or raw.get("product_url")
            enriched_products.append(enriched)
        ranked_products = enriched_products

        recommendation = {
            **decision_block,
            "selected_option": selected_option,
            "decision_type": decision_type,
        }
        quote = None
        if ranked_products:
            quote = session_store.create_quote(
                session_id=session_id,
                user_id=user.uid,
                products=ranked_products,
                recommendation=recommendation,
            )

        # Clean up session from active sessions
        if session_id in active_sessions:
            del active_sessions[session_id]

        return {
            "success": True,
            "session_id": session_id,
            "intent": intent_block,
            "comparison": {
                **comparison_block,
                "ranked_products": ranked_products,
            },
            "recommendation": recommendation,
            "ai_response": ai_response,
            "requires_confirmation": quote is not None,
            "quote_id": quote.quote_id if quote else None,
            "quote_expires_at": datetime.fromtimestamp(quote.expires_at).isoformat() if quote else None,
        }
        
    except HTTPException:
        raise
    except Exception as e:
        await broadcast_agent_status(
            session_id,
            AgentStatusUpdate(
                step="error",
                status="error",
                message=f"Error: {str(e)}"
            )
        )
        raise HTTPException(status_code=500, detail="Unable to process this request") from e

@app.post("/api/order/confirm")
async def confirm_order(
    request: OrderConfirmationRequest,
    user: AuthenticatedUser = Depends(get_current_user),
):
    """Consume an exact server-side quote and execute only that selection."""
    try:
        session_id = request.session_id
        try:
            session_store.assert_owner(session_id, user.uid)
            quote, product = session_store.consume_quote(
                quote_id=request.quote_id,
                session_id=session_id,
                user_id=user.uid,
                selected_index=request.selected_product_index,
            )
        except PermissionError as exc:
            raise HTTPException(status_code=404, detail="Quote not found") from exc
        except TimeoutError as exc:
            raise HTTPException(status_code=410, detail=str(exc)) from exc
        except (ValueError, IndexError) as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc

        # Broadcast: Purchase starting
        await broadcast_agent_status(
            session_id,
            AgentStatusUpdate(
                step="purchase",
                status="processing",
                message="Validating confirmed quote...",
                data={"product_index": request.selected_product_index, "quote_id": request.quote_id}
            )
        )

        dry_run = os.getenv("GANGU_DRY_RUN", "true").strip().lower() == "true"
        real_purchases_enabled = os.getenv("ENABLE_REAL_PURCHASES", "false").strip().lower() == "true"
        source = str(product.get("source", "unknown"))
        platform = str(product.get("platform", "Unknown"))

        if dry_run:
            order_id = f"DRY-RUN-{secrets.token_hex(6).upper()}"
            result = {
                "success": True,
                "order_id": order_id,
                "message": "Dry-run completed; no real order was placed",
                "estimated_delivery": product.get("delivery_time_label") or product.get("delivery_time"),
                "simulated": True,
                "product": product,
            }
        elif not real_purchases_enabled:
            raise HTTPException(status_code=503, detail="Real purchases are disabled by server policy")
        elif source != "live_zepto_mcp":
            raise HTTPException(
                status_code=409,
                detail="This product source does not support verified real checkout",
            )
        elif not os.getenv("ZEPTO_PHONE_NUMBER", "").strip():
            raise HTTPException(status_code=503, detail="Zepto phone number is not configured")
        elif not os.getenv("ZEPTO_DEFAULT_ADDRESS") or (
            os.getenv("ZEPTO_DEFAULT_ADDRESS", "").strip().casefold()
            != request.delivery_address.strip().casefold()
        ):
            raise HTTPException(
                status_code=409,
                detail="Confirmed delivery address does not match the verified Zepto address",
            )
        elif request.payment_method != "cod":
            raise HTTPException(status_code=409, detail="Verified Zepto checkout currently supports COD only")
        else:
            upstream = await zepto_runtime.start(
                user_id=user.uid,
                session_id=session_id,
                product_name=product.get("item_name") or product.get("name") or "product",
                item_url=product.get("url"),
                phone_number=os.environ["ZEPTO_PHONE_NUMBER"],
                address=request.delivery_address,
            )
            if upstream.get("requires_otp"):
                result = {
                    "success": False,
                    "status": upstream.get("status"),
                    "requires_otp": True,
                    "otp_type": "payment" if upstream.get("status") == "payment_otp_required" else "login",
                    "message": "Enter the OTP sent by Zepto to continue this confirmed COD order.",
                    "simulated": False,
                    "product": product,
                }
            elif not upstream.get("success") or upstream.get("status") != "completed":
                raise HTTPException(
                    status_code=502,
                    detail=upstream.get("error") or upstream.get("message") or "Zepto did not confirm the order",
                )
            else:
                result = {
                    "success": True,
                    "status": "completed",
                    "order_id": f"ZEPTO-COD-{secrets.token_hex(6).upper()}",
                    "message": "Zepto confirmed the Cash on Delivery order.",
                    "estimated_delivery": product.get("delivery_time_label") or product.get("delivery_time"),
                    "simulated": False,
                    "product": product,
                }

        await broadcast_agent_status(
            session_id,
            AgentStatusUpdate(
                step="purchase",
                status="processing" if result.get("requires_otp") else "complete",
                message=result["message"],
                data=result,
            )
        )
        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Unable to process the confirmed quote") from e


@app.post("/api/order/zepto/otp")
async def submit_zepto_order_otp(
    request: ZeptoOtpRequest,
    user: AuthenticatedUser = Depends(get_current_user),
):
    """Continue the already-confirmed Zepto order without logging the OTP."""
    try:
        session_store.assert_owner(request.session_id, user.uid)
    except PermissionError as exc:
        raise HTTPException(status_code=404, detail="Session not found") from exc

    try:
        upstream = await zepto_runtime.submit_otp(
            user.uid, request.session_id, request.otp, request.otp_type
        )
    except LookupError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail="Zepto could not continue the OTP flow") from exc

    if upstream.get("requires_otp"):
        return {
            "success": False,
            "status": upstream.get("status"),
            "requires_otp": True,
            "otp_type": "payment" if upstream.get("status") == "payment_otp_required" else "login",
            "message": "Enter the next OTP requested by Zepto.",
            "simulated": False,
        }
    if not upstream.get("success") or upstream.get("status") != "completed":
        raise HTTPException(
            status_code=502,
            detail=upstream.get("error") or upstream.get("message") or "Zepto did not confirm the order",
        )
    return {
        "success": True,
        "status": "completed",
        "order_id": f"ZEPTO-COD-{secrets.token_hex(6).upper()}",
        "message": "Zepto confirmed the Cash on Delivery order.",
        "simulated": False,
    }


@app.get("/api/session/{session_id}")
async def get_session_data(
    session_id: str,
    user: AuthenticatedUser = Depends(get_current_user),
):
    """Retrieve session data for continuing conversation"""
    try:
        session_store.assert_owner(session_id, user.uid)
        # TODO: Retrieve from MongoDB checkpointer
        return {
            "success": True,
            "session_id": session_id,
            "message": "Session data retrieved"
        }
    except PermissionError as exc:
        raise HTTPException(status_code=404, detail="Session not found") from exc

@app.get("/api/history")
async def get_order_history(user: AuthenticatedUser = Depends(get_current_user)):
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
async def cancel_processing(
    request: CancelRequest,
    user: AuthenticatedUser = Depends(get_current_user),
):
    """
    Cancel ongoing agent processing.
    Calls .cancel() on the running pipeline task so the long-running agents
    (Zepto MCP, Amazon scrape, etc.) are interrupted instantly rather than
    waiting up to 15s for the next agent boundary.
    """
    try:
        session_id = request.session_id
        try:
            session_store.assert_owner(session_id, user.uid)
        except PermissionError as exc:
            raise HTTPException(status_code=404, detail="Session not found") from exc

        # Cooperative flag (defence-in-depth in case the task hook is missed)
        active_sessions[session_id] = True

        # Hard-cancel the running pipeline task
        task = session_tasks.get(session_id)
        if task is not None and not task.done():
            task.cancel()
            print(f"⏹️ Cancelled pipeline task for session {session_id}")

        await zepto_runtime.cancel(user.uid, session_id)

        # Broadcast cancellation immediately so the WS client updates UI
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
        port=int(os.getenv("PORT", "8000")),
        log_level="info"
    )
