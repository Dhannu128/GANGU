"""
GANGU Agentic System with LangGraph
Complete orchestration with checkpointing
Integrates your existing agents: Intent & Extraction, Task Planner, Search
"""
from typing import TypedDict, Annotated, Literal
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.mongodb import MongoDBSaver
import json
import os
from dotenv import load_dotenv
from datetime import datetime
import sys
from pathlib import Path

# Add GANGU directory to path to import your agents
gangu_dir = Path(__file__).parent
sys.path.insert(0, str(gangu_dir))

# Import your existing agents
from importlib import import_module

load_dotenv()

# Configure LangSmith tracing
os.environ["LANGSMITH_TRACING"] = os.getenv("LANGSMITH_TRACING", "true")
os.environ["LANGSMITH_ENDPOINT"] = os.getenv("LANGSMITH_ENDPOINT", "https://api.smith.langchain.com")
os.environ["LANGSMITH_API_KEY"] = os.getenv("LANGSMITH_API_KEY", "")
os.environ["LANGSMITH_PROJECT"] = os.getenv("LANGSMITH_PROJECT", "gangu-project")

# ==================== STATE DEFINITION ====================
class GANGUState(TypedDict):
    """Complete state for GANGU workflow"""
    # Input
    user_input: str
    
    # Intent & Extraction Output (from your agent)
    intent_data: dict  # Full output from your Intent Agent
    detected_intent: str
    item_name: str
    item_original: str
    quantity: str
    urgency: str
    confidence: str
    needs_clarification: bool
    language_detected: str
    
    # Task Planning Output (from your agent)
    task_plan: dict  # Full output from your Task Planner Agent
    execution_steps: list[dict]
    
    # Search Results (from your agent)
    search_results: dict  # Full output from your Search Agent
    platforms_searched: list[str]
    
    # Comparison Output (from Comparison Agent)
    comparison_results: dict  # Full output from Comparison Agent
    ranked_products: list[dict]
    comparison_insights: dict
    
    # Decision Output (from Decision Agent)
    decision_results: dict  # Full output from Decision Agent
    final_decision: dict
    selected_option: dict
    decision_type: str
    confidence_level: str
    risk_level: str
    
    # Purchase & Notification (TODO)
    order_id: str
    purchase_status: str
    
    # Final Response
    ai_response: str
    
    # RAG metadata (Query Info Agent)
    rag_metadata: dict
    
    # Metadata
    timestamp: str
    user_preferences: dict


# ==================== AGENT 1: INTENT & EXTRACTION (YOUR AGENT) ====================
def intent_extraction_agent(state: GANGUState) -> GANGUState:
    """
    YOUR Intent & Extraction Agent
    Wrapped for LangGraph integration
    """
    print("\n🧠 [Agent 1] Intent & Extraction Agent (Your Implementation)")
    
    user_input = state.get("user_input", "")
    
    # Import and use your agent
    try:
        import sys
        import os
        parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if parent_dir not in sys.path:
            sys.path.insert(0, parent_dir)
        
        intent_module = import_module("agents.intent_extraction_agent")
        
        # Call your agent's extract_intent function
        intent_result = intent_module.extract_intent(user_input)
        
        # Store full result
        state["intent_data"] = intent_result
        
        # Extract key fields for easy access
        state["detected_intent"] = intent_result.get("intent", "")
        state["item_name"] = intent_result.get("item", "")
        state["item_original"] = intent_result.get("item_original", "")
        state["quantity"] = intent_result.get("quantity", "1 unit")
        state["urgency"] = intent_result.get("urgency", "normal")
        state["confidence"] = intent_result.get("confidence", "medium")
        state["needs_clarification"] = intent_result.get("needs_clarification", False)
        state["language_detected"] = intent_result.get("language_detected", "unknown")
        state["timestamp"] = datetime.now().isoformat()
        
        print(f"   ✓ Intent: {state['detected_intent']}")
        print(f"   ✓ Item: {state['item_name']} ({state['item_original']})")
        print(f"   ✓ Quantity: {state['quantity']}")
        print(f"   ✓ Urgency: {state['urgency']}")
        print(f"   ✓ Confidence: {state['confidence']}")
        
    except Exception as e:
        print(f"   ❌ Error loading your agent: {e}")
        print(f"   ℹ️  Falling back to basic extraction")
        
        # Fallback: Basic extraction
        state["detected_intent"] = "buy_grocery"
        state["item_name"] = user_input
        state["quantity"] = "1 unit"
        state["urgency"] = "normal"
        state["confidence"] = "low"
        state["timestamp"] = datetime.now().isoformat()
    
    return state


# ==================== AGENT 2: TASK PLANNER (YOUR AGENT) ====================
def task_planner_agent(state: GANGUState) -> GANGUState:
    """
    YOUR Task Planner Agent
    Wrapped for LangGraph integration
    """
    print("\n📋 [Agent 2] Task Planner Agent (Your Implementation)")
    
    intent_data = state.get("intent_data", {})
    
    # Import and use your agent
    try:
        import sys
        import os
        parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if parent_dir not in sys.path:
            sys.path.insert(0, parent_dir)
        
        planner_module = import_module("agents.task_planner_agent")
        
        # Call your agent's create_action_plan function (correct name)
        task_result = planner_module.create_action_plan(intent_data)
        
        # Store full result
        state["task_plan"] = task_result
        
        # Extract execution steps for easy access
        state["execution_steps"] = task_result.get("steps", [])
        
        print(f"   ✓ Created plan with {len(state['execution_steps'])} steps")
        for step in state["execution_steps"]:
            print(f"      {step.get('step_number', '?')}. {step.get('agent', 'unknown')}: {step.get('action', 'N/A')}")
        
    except Exception as e:
        print(f"   ❌ Error loading your agent: {e}")
        print(f"   ℹ️  Falling back to basic planning")
        
        # Fallback: Basic plan
        intent = state.get("detected_intent")
        if "buy" in intent or "reorder" in intent:
            state["execution_steps"] = [
                {"step_number": 1, "agent": "search_agent", "action": "search_platforms"},
                {"step_number": 2, "agent": "compare_agent", "action": "compare_results"},
                {"step_number": 3, "agent": "decision_agent", "action": "select_best"},
                {"step_number": 4, "agent": "purchase_agent", "action": "execute_order"},
                {"step_number": 5, "agent": "notification_agent", "action": "notify_user"}
            ]
        else:
            state["execution_steps"] = [
                {"step_number": 1, "agent": "rag_agent", "action": "retrieve_info"},
                {"step_number": 2, "agent": "notification_agent", "action": "respond_user"}
            ]
    
    return state


# ==================== ROUTING LOGIC ====================
def route_after_planning(state: GANGUState) -> Literal["search", "query_info_only"]:
    """Routes based on intent — purchase flow vs RAG info query"""
    intent = state.get("detected_intent", "")
    needs_clarification = state.get("needs_clarification", False)
    
    # Route to search agent for buy/reorder intents (unless clarification needed)
    if any(keyword in intent for keyword in ["buy", "reorder"]) and not needs_clarification:
        return "search"
    
    # Everything else goes to RAG-based query info agent
    # This includes: inquiry, unclear, general questions, product info requests
    return "query_info_only"


# ==================== AGENT 3: SEARCH (YOUR AGENT) ====================
def search_agent(state: GANGUState) -> GANGUState:
    """
    YOUR Search Agent
    Wrapped for LangGraph integration
    """
    print("\n🔍 [Agent 3] Search Agent (Your Implementation)")
    
    # Get task plan output from previous agent
    task_plan = state.get("task_plan", {})
    
    # Build search input from task plan
    search_params = {
        "action": "search_all_platforms",
        "item": state.get("item_name"),
        "quantity": state.get("quantity"),
        "urgency": state.get("urgency"),
        "intent": state.get("detected_intent")
    }
    
    # Import and use your agent
    try:
        import sys
        import os
        parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if parent_dir not in sys.path:
            sys.path.insert(0, parent_dir)
        
        search_module = import_module("agents.search_agent")
        
        # Call your agent's search_platforms function
        search_result = search_module.search_platforms(search_params)
        
        # Store full result
        state["search_results"] = search_result
        
        # Extract platform list
        state["platforms_searched"] = search_result.get("platforms_searched", [])
        
        results_count = search_result.get("total_results_found", 0)
        print(f"   ✓ Searched {len(state['platforms_searched'])} platforms")
        print(f"   ✓ Found {results_count} total results")
        
        # Show summary
        for result in search_result.get("results", [])[:3]:
            platform = result.get("platform", "Unknown")
            price = result.get("price", "N/A")
            available = result.get("available", False)
            status = "✓" if available else "✗"
            print(f"      {status} {platform}: ₹{price}")
        
    except Exception as e:
        print(f"   ❌ Error loading your agent: {e}")
        print(f"   ℹ️  Falling back to basic search")
        
        # Get item name from state for fallback
        item_name = state.get("item_name", "item")
        
        # Fallback: Mock search results
        state["search_results"] = {
            "platforms_searched": ["Blinkit", "Amazon", "Flipkart"],
            "total_results_found": 3,
            "results": [
                {
                    "platform": "Blinkit",
                    "item_name": item_name,
                    "price": 110,
                    "delivery_time": "15 minutes",
                    "rating": 4.4,
                    "available": True
                },
                {
                    "platform": "Amazon",
                    "item_name": item_name,
                    "price": 95,
                    "delivery_time": "Tomorrow",
                    "rating": 4.6,
                    "available": True
                }
            ]
        }
        state["platforms_searched"] = ["Blinkit", "Amazon", "Flipkart"]
    
    return state


# ==================== AGENT 4: COMPARISON & RANKING (YOUR AGENT) ====================
def comparison_agent(state: GANGUState) -> GANGUState:
    """
    YOUR Comparison Agent
    Wrapped for LangGraph integration
    """
    print("\n⚖️  [Agent 4] Comparison & Ranking Agent (Your Implementation)")
    
    # Get search results and intent from state
    search_results = state.get("search_results", {})
    intent_data = state.get("intent_data", {})
    
    # CRITICAL FIX: Add urgency to comparison inputs
    urgency_level = state.get("urgency", "normal")
    
    # Enhance search results with urgency context for comparison agent
    enhanced_search_results = dict(search_results)
    enhanced_search_results["urgency_level"] = urgency_level
    enhanced_search_results["context"] = {
        "urgency": urgency_level,
        "intent": state.get("detected_intent", ""),
        "item_name": state.get("item_name", ""),
        "quantity": state.get("quantity", "")
    }
    
    # Import and use your agent
    try:
        import sys
        import os
        parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if parent_dir not in sys.path:
            sys.path.insert(0, parent_dir)
        
        comparison_module = import_module("agents.comparison_agent")
        
        # Call your agent's compare_products function with enhanced data
        comparison_result = comparison_module.compare_products(enhanced_search_results)

        # If comparison failed or returned no ranked products, force fallback
        ranked_products = comparison_result.get("ranked_products", []) if isinstance(comparison_result, dict) else []
        if not ranked_products:
            status = comparison_result.get("status") if isinstance(comparison_result, dict) else None
            if status == "failed" or enhanced_search_results.get("results"):
                print("   ⚠️ Comparison agent returned no rankings. Using fallback comparison.")
                comparison_result = comparison_module.create_fallback_comparison(enhanced_search_results)
        
        # Store full result
        state["comparison_results"] = comparison_result
        
        # Extract key fields for easy access
        state["ranked_products"] = comparison_result.get("ranked_products", [])
        state["comparison_insights"] = comparison_result.get("comparison_insights", {})
        
        print(f"   ✓ Analyzed {comparison_result.get('comparison_summary', {}).get('total_products_received', 0)} products")
        print(f"   ✓ Ranked {len(state['ranked_products'])} options")
        
        # Show top 3
        for i, product in enumerate(state["ranked_products"][:3], 1):
            platform = product.get("platform", "Unknown")
            score = product.get("scores", {}).get("final_score", 0)
            price = product.get("normalized_attributes", {}).get("unit_price_label", "N/A")
            delivery = product.get("normalized_attributes", {}).get("delivery_time_label", "N/A")
            print(f"      #{i} {platform}: Score {score}/100 | {price} | {delivery}")
        
    except Exception as e:
        print(f"   ❌ Error loading your agent: {e}")
        import traceback
        traceback.print_exc()
        print(f"   ℹ️  Using fallback comparison")
        
        # Fallback: Basic comparison
        results = search_results.get("results", [])
        state["ranked_products"] = results[:3] if results else []
        state["comparison_insights"] = {"confidence": "low", "fallback": True}
    
    return state


# ==================== AGENT 5: DECISION MAKING (YOUR AGENT) ====================
def decision_agent(state: GANGUState) -> GANGUState:
    """
    YOUR Decision Agent
    Wrapped for LangGraph integration
    """
    print("\n🎯 [Agent 5] Decision Making Agent (Your Implementation)")
    
    # Get comparison results from state
    comparison_results = state.get("comparison_results", {})
    
    # CRITICAL FIX: Add urgency context to decision agent
    urgency_level = state.get("urgency", "normal")
    
    # Enhance comparison results with urgency context for decision agent
    enhanced_comparison_results = dict(comparison_results)
    enhanced_comparison_results["urgency_context"] = {
        "urgency_level": urgency_level,
        "original_intent": state.get("detected_intent", ""),
        "item_name": state.get("item_name", ""),
        "user_said_urgent": urgency_level in ["urgent", "high"]
    }
    
    # Import and use your agent
    try:
        import sys
        import os
        parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if parent_dir not in sys.path:
            sys.path.insert(0, parent_dir)
        
        decision_module = import_module("agents.decision_agent")
        
        # Call your agent's make_decision function with enhanced context
        decision_result = decision_module.make_decision(enhanced_comparison_results)
        
        # Store full result
        state["decision_results"] = decision_result
        
        # Extract key fields for easy access
        state["final_decision"] = decision_result.get("decision_summary", {})
        state["selected_option"] = decision_result.get("selected_option")
        state["decision_type"] = decision_result.get("decision_summary", {}).get("decision_type", "unknown")
        state["confidence_level"] = decision_result.get("decision_summary", {}).get("confidence_level", "low")
        state["risk_level"] = decision_result.get("decision_summary", {}).get("risk_level", "high")
        
        decision_made = decision_result.get("decision_summary", {}).get("decision_made", False)
        decision_type = state["decision_type"]
        
        print(f"   ✓ Decision Made: {'Yes' if decision_made else 'No'}")
        print(f"   ✓ Decision Type: {decision_type}")
        print(f"   ✓ Confidence: {state['confidence_level']}")
        print(f"   ✓ Risk Level: {state['risk_level']}")
        
        if state["selected_option"]:
            platform = state["selected_option"].get("platform", "N/A")
            price = state["selected_option"].get("unit_price_label", state["selected_option"].get("price", "N/A"))
            print(f"   ✓ Selected: {platform} at {price}")
        
    except Exception as e:
        print(f"   ❌ Error loading your agent: {e}")
        import traceback
        traceback.print_exc()
        print(f"   ℹ️  Using fallback decision")
        
        # Fallback: Select first ranked product
        ranked = state.get("ranked_products", [])
        if ranked:
            state["selected_option"] = ranked[0]
            state["decision_type"] = "confirm_with_user"
            state["confidence_level"] = "low"
            state["risk_level"] = "medium"
        else:
            state["selected_option"] = None
            state["decision_type"] = "no_good_option"
            state["confidence_level"] = "low"
            state["risk_level"] = "high"
    
    return state


# ==================== AGENT 6: PURCHASE EXECUTION (SIMULATED) ====================
def purchase_agent(state: GANGUState) -> GANGUState:
    """
    Purchase Execution Agent - Now integrated with real purchase agent for Zepto COD
    """
    print("\n💳 [Agent 6] Purchase Execution Agent (Real Implementation)")
    
    decision_type = state.get("decision_type", "unknown")
    selected_option = state.get("selected_option")
    
    # Check if we should actually purchase
    if decision_type == "auto_buy":
        print("   ✓ Auto-buy approved, proceeding with purchase...")
    elif decision_type == "confirm_with_user":
        print("   ⚠️  Confirmation required from user")
        state["purchase_status"] = "pending_confirmation"
        return state
    elif decision_type == "clarify_needed":
        print("   ⚠️  Clarification needed, skipping purchase")
        state["purchase_status"] = "needs_clarification"
        return state
    elif decision_type == "no_good_option":
        print("   ✗ No good option available, skipping purchase")
        state["purchase_status"] = "no_option"
        return state
    
    if not selected_option:
        print("   ✗ No option selected, cannot purchase")
        state["purchase_status"] = "failed"
        return state
    
    platform = selected_option.get("platform", "Unknown")
    item_name = state.get("item_name", "Item")
    
    # For Zepto orders, use the real purchase agent
    if platform.lower() == "zepto":
        print("   🛒 Using real Zepto purchase agent for Cash on Delivery...")
        
        try:
            # Import and use the actual purchase agent
            from agents.purchase_agent import execute_purchase
            
            # Prepare input for purchase agent
            purchase_input = {
                "final_decision": {
                    "selected_platform": platform,
                    "product": {
                        "name": item_name,
                        "price": selected_option.get("price", 30),
                        "quantity": state.get("quantity", 1),
                        "product_id": item_name.lower().replace(" ", "_")
                    },
                    "delivery": {
                        "delivery_date": "today",
                        "slot": "within 1 hour"
                    }
                },
                "user_context": {
                    "payment_preference": "cash_on_delivery",
                    "platform_preference": "zepto"
                }
            }
            
            # Execute purchase
            purchase_result = execute_purchase(purchase_input)
            
            # Process result
            if purchase_result.get("purchase_status") == "success":
                order_id = purchase_result.get("execution_details", {}).get("order_id")
                state["order_id"] = order_id
                state["purchase_status"] = "confirmed"
                state["purchase_details"] = purchase_result
                
                print(f"   ✅ Zepto COD order successful!")
                print(f"   🆔 Order ID: {order_id}")
                print(f"   💳 Payment: Cash on Delivery")
                
            else:
                state["purchase_status"] = "failed"
                state["purchase_error"] = purchase_result.get("user_message", "Order failed")
                print(f"   ❌ Zepto order failed: {purchase_result.get('user_message')}")
                
        except Exception as e:
            print(f"   ❌ Error in purchase execution: {str(e)}")
            state["purchase_status"] = "failed"
            state["purchase_error"] = f"Purchase agent error: {str(e)}"
    
    else:
        # For other platforms, simulate (as before)
        print(f"   🛒 Simulating order placement on {platform}...")
        order_id = f"ORD{datetime.now().strftime('%Y%m%d%H%M%S')}"
        state["order_id"] = order_id
        state["purchase_status"] = "confirmed"
        print(f"   ✓ Simulated order confirmed: {order_id}")
    
    return state


# ==================== AGENT 7: NOTIFICATION ====================
def notification_agent(state: GANGUState) -> GANGUState:
    """
    Notification Agent
    Generates user-friendly response based on decision
    """
    print("\n🔔 [Agent 7] Notification Agent")
    
    decision_results = state.get("decision_results", {})
    decision_type = state.get("decision_type", "unknown")
    purchase_status = state.get("purchase_status", "unknown")
    
    # Get user explanation from decision agent
    explanation = decision_results.get("explanation_for_user", {})
    simple_message = explanation.get("simple_message", "")
    why_option = explanation.get("why_this_option", "")
    
    # Build response based on decision type
    if decision_type == "auto_buy" and purchase_status == "confirmed":
        selected = state.get("selected_option", {})
        platform = selected.get("platform", "Unknown")
        price = selected.get("unit_price_label", selected.get("price", "N/A"))
        delivery = selected.get("delivery_time_label", "Soon")
        order_id = state.get("order_id", "N/A")
        
        response = f"""✅ Order Successful!

{simple_message}

📦 Details:
   Platform: {platform}
   Price: {price}
   Delivery: {delivery}
   Order ID: {order_id}

{why_option}

Thank you for using GANGU! 🙏
"""
    
    elif decision_type == "confirm_with_user":
        selected = state.get("selected_option", {})
        platform = selected.get("platform", "Unknown")
        price = selected.get("unit_price_label", selected.get("price", "N/A"))
        delivery = selected.get("delivery_time_label", "Soon")
        
        # Get fallback options
        fallback = decision_results.get("fallback_strategy", {})
        
        response = f"""🤔 Confirmation Needed

{simple_message}

📦 Recommended Option:
   Platform: {platform}
   Price: {price}
   Delivery: {delivery}

{why_option}

Kya main yeh order kar doon? (Yes/No)
"""
    
    elif decision_type == "clarify_needed":
        response = f"""❓ Clarification Needed

{simple_message if simple_message else 'Kuch aur jaankari chahiye.'}

{why_option}

Kya aap thoda aur bata sakte hain?
"""
    
    elif decision_type == "no_good_option":
        response = f"""😔 No Good Option Found

{simple_message if simple_message else 'Abhi koi accha option nahi mila.'}

Kya main baad mein phir se try karoon?
"""
    
    else:
        response = f"""⚠️ Processing...

Decision Type: {decision_type}
Status: {purchase_status}

{simple_message}
"""
    
    state["ai_response"] = response
    
    print("   ✓ User notification prepared")
    print(f"   ✓ Decision Type: {decision_type}")
    
    return state


# ==================== AGENT 8: INFO QUERY (RAG-Based) ====================
def query_info_agent(state: GANGUState) -> GANGUState:
    """
    RAG-based Query Info Agent
    Uses knowledge base + Gemini embeddings to answer information queries.
    Handles: product info, GANGU features, Hindi/English translations, and more.
    """
    print("\n📚 [Agent 8] Query Info Agent (RAG-Based Implementation)")

    user_input = state.get("user_input", "")
    item = state.get("item_name", "")
    language = state.get("language_detected", "hinglish")

    # Build a rich query from available context
    query = user_input
    if item and item.lower() not in user_input.lower():
        query = f"{user_input} — item: {item}"

    try:
        import sys, os
        parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if parent_dir not in sys.path:
            sys.path.insert(0, parent_dir)

        from agents.query_info_agent import query_info

        rag_result = query_info(query, language_hint=language)

        response_text = rag_result.get("response", "")
        sources_used = rag_result.get("sources_used", 0)
        retrieval_time = rag_result.get("retrieval_time_ms", 0)

        state["ai_response"] = response_text

        # Store RAG metadata in state for observability
        state["rag_metadata"] = {
            "sources_used": sources_used,
            "retrieval_time_ms": retrieval_time,
            "sources": rag_result.get("sources", []),
            "method": "rag",
        }

        print(f"   ✅ RAG response generated ({sources_used} sources, {retrieval_time}ms)")
        print(f"   📝 Response preview: {response_text[:120]}...")

    except Exception as e:
        print(f"   ❌ RAG agent error: {e}")
        import traceback
        traceback.print_exc()

        # Fallback: Basic response
        if item:
            state["ai_response"] = (
                f"'{item}' ke baare mein abhi detailed jaankari available nahi hai. "
                f"Agar aap yeh item kharidna chahte hain toh bol dijiye — 'order karo' ya '{item} mangao'. 🙏"
            )
        else:
            state["ai_response"] = (
                "Maaf kijiye, aapki baat samajh nahi aayi. "
                "Kya aap thoda aur detail mein bata sakte hain? 🙏"
            )

    return state


# ==================== BUILD GRAPH ====================
def create_gangu_graph(checkpointer=None):
    """Creates the complete GANGU graph with all agents"""
    
    graph_builder = StateGraph(GANGUState)
    
    # Add all agent nodes (your agents + placeholders)
    graph_builder.add_node("intent_extraction", intent_extraction_agent)  # YOUR AGENT
    graph_builder.add_node("task_planner", task_planner_agent)  # YOUR AGENT
    graph_builder.add_node("search", search_agent)  # YOUR AGENT
    graph_builder.add_node("comparison", comparison_agent)
    graph_builder.add_node("decision", decision_agent)
    graph_builder.add_node("purchase", purchase_agent)
    graph_builder.add_node("notification", notification_agent)
    graph_builder.add_node("query_info_only", query_info_agent)
    
    # Define flow
    graph_builder.add_edge(START, "intent_extraction")  # YOUR AGENT
    graph_builder.add_edge("intent_extraction", "task_planner")  # YOUR AGENT
    
    # Conditional routing after task planner
    graph_builder.add_conditional_edges(
        "task_planner",
        route_after_planning
    )
    
    # Grocery ordering flow (your agents + placeholders)
    graph_builder.add_edge("search", "comparison")  # YOUR AGENT → placeholder
    graph_builder.add_edge("comparison", "decision")
    graph_builder.add_edge("decision", "purchase")
    graph_builder.add_edge("purchase", "notification")
    graph_builder.add_edge("notification", END)
    
    # Info query flow
    graph_builder.add_edge("query_info_only", END)
    
    # Compile with checkpointer
    if checkpointer:
        return graph_builder.compile(checkpointer=checkpointer)
    else:
        return graph_builder.compile()


# ==================== EXPORT ====================
graph = create_gangu_graph()

if __name__ == "__main__":
    # Test the graph
    test_state = {
        "user_input": "White chane khatam ho gaye",
        "user_preferences": {}
    }
    
    print("=" * 60)
    print("GANGU AGENTIC SYSTEM - STARTING")
    print("=" * 60)
    
    result = graph.invoke(test_state)
    
    print("\n" + "=" * 60)
    print("FINAL RESULT")
    print("=" * 60)
    print(result.get("ai_response", ""))
