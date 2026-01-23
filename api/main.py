"""
GANGU FastAPI Backend
Exposes GANGU agents as REST API with WebSocket support for real-time updates
"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
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

# CORS Configuration - Allow frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],  # Next.js default ports
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Active WebSocket connections
active_connections: List[WebSocket] = []

# Active sessions and cancellation tracking
active_sessions: Dict[str, bool] = {}  # session_id -> is_cancelled
session_tasks: Dict[str, asyncio.Task] = {}  # session_id -> task for instant cancellation

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

# ============================================================================
# WEBSOCKET ENDPOINT - Real-time Agent Updates
# ============================================================================

@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """
    WebSocket connection for real-time agent pipeline updates
    Frontend connects here to receive live status
    """
    await websocket.accept()
    active_connections.append(websocket)
    
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
        active_connections.remove(websocket)
        print(f"Client {session_id} disconnected")

async def broadcast_agent_status(session_id: str, update: AgentStatusUpdate):
    """Broadcast agent status to all connected clients"""
    message = {
        "type": "agent_update",
        "session_id": session_id,
        "timestamp": datetime.now().isoformat(),
        **update.dict()
    }
    
    for connection in active_connections:
        try:
            await connection.send_json(message)
            # Small delay to ensure message is sent before next update
            await asyncio.sleep(0.1)
        except:
            pass

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
        
        # Stream through the graph with proper exception handling
        result_state = None
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
        
        # After graph completes, ensure purchase and notification are marked complete
        # (These agents run but graph may complete before we catch their events)
        if result_state:
            # Mark purchase complete if decision was made
            if result_state.get("decision"):
                await broadcast_agent_status(
                    session_id,
                    AgentStatusUpdate(
                        step="purchase",
                        status="complete",
                        message="Order prepared (awaiting confirmation)",
                        data={}
                    )
                )
                
                # Mark notification complete
                await broadcast_agent_status(
                    session_id,
                    AgentStatusUpdate(
                        step="notification",
                        status="complete",
                        message="Ready to confirm",
                        data={}
                    )
                )
        
        # Extract final state
        final_decision = result_state.get("decision", {})
        comparison = result_state.get("comparison", {})
        
        # Clean up session from active sessions
        if session_id in active_sessions:
            del active_sessions[session_id]
        
        return {
            "success": True,
            "session_id": session_id,
            "intent": result_state.get("intent", {}),
            "comparison": comparison,
            "recommendation": final_decision,
            "requires_confirmation": True
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

@app.post("/api/order/confirm")
async def confirm_order(request: OrderConfirmationRequest):
    """
    User confirms purchase - triggers Purchase Agent
    """
    try:
        session_id = request.session_id
        
        # Broadcast: Purchase starting
        await broadcast_agent_status(
            session_id,
            AgentStatusUpdate(
                step="purchase",
                status="processing",
                message="Adding to cart...",
                data={"product_index": request.selected_product_index}
            )
        )
        
        # TODO: Call Purchase Agent here
        # For now, simulate purchase
        await asyncio.sleep(2)  # Simulate cart add
        
        await broadcast_agent_status(
            session_id,
            AgentStatusUpdate(
                step="purchase",
                status="processing",
                message="Checking out..."
            )
        )
        
        await asyncio.sleep(2)  # Simulate checkout
        
        await broadcast_agent_status(
            session_id,
            AgentStatusUpdate(
                step="purchase",
                status="complete",
                message="Order placed successfully! 🎉",
                data={
                    "order_id": f"ORD-{datetime.now().timestamp()}",
                    "estimated_delivery": "Today by 7:00 PM"
                }
            )
        )
        
        return {
            "success": True,
            "order_id": f"ORD-{datetime.now().timestamp()}",
            "message": "Order placed successfully",
            "estimated_delivery": "Today by 7:00 PM"
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
