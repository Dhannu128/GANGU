"""
GANGU Main Application with Full Pipeline
Connects all 5 agents: Intent → Task Planner → Search → Comparison → Decision
"""
from pathlib import Path
from dotenv import load_dotenv
from langgraph.checkpoint.mongodb import MongoDBSaver
import os
import sys

# Load .env from GANGU root directory (parent of orchestration)
gangu_root = Path(__file__).parent.parent
env_path = gangu_root / ".env"
load_dotenv(dotenv_path=env_path)

# Also try current directory
load_dotenv()

# Import after loading env
from gangu_graph import create_gangu_graph

# MongoDB connection
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")

def print_banner():
    """Print GANGU banner"""
    print("\n" + "=" * 70)
    print("🤖 GANGU - Grocery Assistant for Elderly")
    print("   Complete AI Pipeline: Intent → Plan → Search → Compare → Decide")
    print("=" * 70)

def print_help():
    """Print usage examples"""
    print("\n💡 Try these commands:")
    print("   - 'White chane khatam ho gaye' (Buy grocery)")
    print("   - 'Doodh le aao' (Buy milk)")
    print("   - 'Atta khatam ho gaya' (Buy flour)")
    print("   - 'help' for this message")
    print("   - 'exit' to quit\n")

def init():
    """Initialize GANGU with MongoDB checkpointing and full pipeline"""
    
    print_banner()
    
    # Check MongoDB connection
    try:
        with MongoDBSaver.from_conn_string(MONGODB_URI) as test_checkpointer:
            print("\n✅ MongoDB connected successfully")
    except Exception as e:
        print(f"\n⚠️  MongoDB connection failed: {e}")
        print("   Running without checkpointing (states won't be saved)")
        print("   To fix: Start MongoDB with 'docker-compose up -d' in config folder")
        
        user_choice = input("\n   Continue without MongoDB? (yes/no): ").strip().lower()
        if user_choice not in ['yes', 'y']:
            print("\n👋 Exiting. Please start MongoDB and try again.")
            return
    
    print_help()
    
    # For now, run without checkpointing for simplicity
    # MongoDB checkpointing can be added later after proper testing
    print("\n📊 Initializing GANGU pipeline...")
    gangu_graph = create_gangu_graph(checkpointer=None)
    print("✅ GANGU pipeline initialized (running without checkpointing)")
    print("   Note: To enable MongoDB checkpointing, see INTEGRATION_COMPLETE.md")
    
    # Config for tracking (even without checkpointing)
    config = {"configurable": {"thread_id": "user_001"}}
    
    print("\n🚀 GANGU is ready! Start talking...\n")
    
    while True:
        try:
            user_input = input("👤 You: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['exit', 'quit', 'bye']:
                print("\n👋 Goodbye! Stay healthy!")
                break
            
            if user_input.lower() in ['help', 'h', '?']:
                print_help()
                continue
            
            # Prepare state
            initial_state = {
                "user_input": user_input,
                "user_preferences": {}  # Can load from DB in future
            }
            
            print("\n" + "=" * 70)
            print("🔄 Processing your request through GANGU pipeline...")
            print("=" * 70)
            
            # Stream events to show progress
            try:
                # Use invoke for simpler execution
                result = gangu_graph.invoke(initial_state)
                
                # Check if confirmation is needed
                decision_type = result.get("decision_type", "")
                purchase_status = result.get("purchase_status", "")
                
                if decision_type == "confirm_with_user" and purchase_status == "pending_confirmation":
                    # Handle confirmation flow with automatic COD execution
                    result = handle_user_confirmation_with_cod(gangu_graph, result)
                
                # Display response
                response = result.get("ai_response", "⚠️ Processing incomplete. Please try again.")
                
                print("\n" + "=" * 70)
                print("🤖 GANGU Response:")
                print("=" * 70)
                print(response)
                print("=" * 70)
                
            except Exception as e:
                print(f"\n❌ Error during processing: {e}")
                print("   Please try again with a different query.")
                import traceback
                traceback.print_exc()
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye! Stay healthy!")
            break
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")
            print("   Please try again.")


def handle_user_confirmation_with_cod(gangu_graph, result):
    """Handle user confirmation with automatic COD order execution"""
    selected_option = result.get("selected_option", {})
    platform = selected_option.get("platform", "Unknown")
    item_name = result.get("item_name", "Item")
    price = selected_option.get("unit_price_label", selected_option.get("price", "N/A"))
    delivery = selected_option.get("delivery_time_label", "Delivery time not available")
    
    # Display confirmation prompt in Hindi/English mix (as user prefers)
    print("\n" + "=" * 70)
    print("🤖 GANGU Order Confirmation:")
    print("=" * 70)
    
    # Display recommendation summary
    print(f"📦 Best Option Found:")
    print(f"   Platform: {platform}")
    print(f"   Product: {item_name}")
    print(f"   Price: {price}")
    print(f"   Delivery: {delivery}")
    print(f"   Payment: Cash on Delivery (COD)")
    print()
    
    # Show urgency justification
    urgency = result.get("urgency", "normal")
    if urgency == "urgent":
        print("⚡ **Urgent order detected** - Fastest option selected!")
    elif urgency == "high":
        print("🏃 **High priority** - Speed prioritized!")
    
    # Ask for confirmation
    print("**Kya main yeh order place kar doon?** (COD payment)")
    print()
    print("Options:")
    print("  ✅ **Yes** - Order place karo (place order)")
    print("  ❌ **No**  - Order cancel karo (cancel order)")
    print()
    
    while True:
        try:
            user_choice = input("👤 Your Choice (Yes/No): ").strip().lower()
            
            if user_choice in ['yes', 'y', 'haan', 'ha', 'kar do', 'place karo', 'ok']:
                print("\n✅ Order confirmation received! Placing COD order...")
                print("\n" + "=" * 70)
                print("💳 Processing Zepto COD Order...")
                print("=" * 70)
                
                # Update state to proceed with purchase
                result["decision_type"] = "auto_buy"
                result["purchase_status"] = "processing"
                result["user_confirmed"] = True
                
                # Execute purchase using the purchase agent immediately
                try:
                    from agents.purchase_agent import execute_purchase
                    
                    # Prepare proper input for purchase agent
                    purchase_input = {
                        "final_decision": {
                            "selected_platform": platform,
                            "product": {
                                "name": item_name,
                                "price": selected_option.get("price", 77),
                                "quantity": result.get("quantity", "1"),
                                "product_id": item_name.lower().replace(" ", "_").replace(",", "_")
                            },
                            "delivery": {
                                "delivery_date": "today",
                                "slot": "within 1 hour"
                            }
                        },
                        "user_context": {
                            "payment_preference": "cash_on_delivery",
                            "platform_preference": "zepto",
                            "confirmed_by_user": True,
                            "urgency_level": urgency
                        }
                    }
                    
                    print("   🚀 Executing real Zepto COD order...")
                    purchase_result = execute_purchase(purchase_input)
                    
                    # Process the purchase result
                    if purchase_result.get("purchase_status") == "success":
                        order_id = purchase_result.get("execution_details", {}).get("order_id", "Unknown")
                        platform_used = purchase_result.get("execution_details", {}).get("platform_used", platform)
                        product_name = purchase_result.get("order_confirmation", {}).get("product_name", item_name)
                        final_price = purchase_result.get("order_confirmation", {}).get("final_price", "N/A")
                        
                        result["purchase_status"] = "success"
                        result["order_id"] = order_id
                        result["ai_response"] = f"""✅ Order Successfully Placed!

📦 Order Details:
   Platform: {platform_used}
   Product: {product_name}
   Price: ₹{final_price}
   Payment: Cash on Delivery (COD)
   Order ID: {order_id}
   Delivery: Within 1 hour

🎉 Aapka order place ho gaya! Delivery person aayega aur aap cash mein payment kar denge.

Thank you for using GANGU! 🙏"""
                        
                    elif purchase_result.get("purchase_status") == "failed":
                        result["purchase_status"] = "failed"
                        error_msg = purchase_result.get("user_message", "Order placement failed")
                        result["ai_response"] = f"""❌ Order Failed

{error_msg}

😔 Kshama karein, order place nahi ho paaya. Kya aap dusra option try karna chahenge ya phir se koshish karein?

Available alternatives:
- Try Amazon (slower but available)
- Search for different products
- Try again later"""
                        
                    else:
                        result["purchase_status"] = "pending"
                        result["ai_response"] = f"""⏳ Order Processing...

Aapka order process ho raha hai. Thoda intezaar kariye...

Status: {purchase_result.get('purchase_status', 'processing')}
Platform: {platform}
Product: {item_name}"""
                    
                except Exception as e:
                    print(f"❌ Purchase execution failed: {e}")
                    result["ai_response"] = f"""❌ माफ़ करें, ऑर्डर प्लेस करते समय समस्या आई।

Error: {str(e)}

कृपया बाद में कोशिश करें या customer support से संपर्क करें।

Available options:
- Try again: 'retry order'
- Check status: 'order status'
- Help: 'help'"""
                    result["purchase_status"] = "failed"
                
                break
                
            elif user_choice in ['no', 'n', 'nahi', 'cancel', 'cancel karo', 'mat karo']:
                print("\n❌ Order cancelled by user.")
                result["decision_type"] = "cancelled_by_user"
                result["purchase_status"] = "cancelled"
                result["user_confirmed"] = False
                result["ai_response"] = f"""❌ ऑर्डर cancel कर दिया गया।

📋 Summary:
   Item: {item_name}
   Platform: {platform}
   Price: {price}
   Status: Cancelled by user

कोई और चीज़ चाहिए तो बताइए! 😊

Try these:
- "दूसरा option dikhao"
- "कुछ और order karna hai"
- "help"
"""
                break
                
            else:
                print(f"⚠️  Please answer with 'Yes' or 'No' (you entered: '{user_choice}')")
                print("   Valid responses: Yes, Y, No, N, Haan, Nahi, OK, Kar Do")
                continue
                
        except KeyboardInterrupt:
            print("\n\n❌ Order cancelled by user (Ctrl+C)")
            result["decision_type"] = "cancelled_by_user"
            result["purchase_status"] = "cancelled"
            result["user_confirmed"] = False
            result["ai_response"] = "❌ ऑर्डर cancel कर दिया गया। कोई और चीज़ चाहिए तो बताइए!"
            break
            
        except Exception as e:
            print(f"❌ Error during confirmation: {e}")
            continue
    
    return result


def handle_user_confirmation(gangu_graph, result):
    """Handle user confirmation for order placement"""
    selected_option = result.get("selected_option", {})
    platform = selected_option.get("platform", "Unknown")
    item_name = result.get("item_name", "Item")
    price = selected_option.get("normalized_attributes", {}).get("unit_price_label", "Price not available")
    delivery = selected_option.get("normalized_attributes", {}).get("delivery_time_label", "Delivery time not available")
    
    # Display confirmation prompt in Hindi/English mix (as user prefers)
    print("\n" + "=" * 70)
    print("🤖 GANGU Order Confirmation:")
    print("=" * 70)
    
    # Display recommendation summary
    print(f"📦 Recommended Option:")
    print(f"   Platform: {platform}")
    print(f"   Product: {item_name}")
    print(f"   Price: {price}")
    print(f"   Delivery: {delivery}")
    print()
    
    # Risk information for Zepto
    if platform.lower() == "zepto":
        print("⚠️  Note: Zepto orders might face stock availability issues.")
        print("   However, it's the cheapest and fastest option.")
        print()
    
    # Ask for confirmation
    print("**Kya main yeh order place kar doon?**")
    print()
    print("Options:")
    print("  📋 **Yes** - Order place karo (proceed with purchase)")
    print("  ❌ **No**  - Order cancel karo (cancel purchase)")
    print()
    
    while True:
        try:
            user_choice = input("👤 Your Choice (Yes/No): ").strip().lower()
            
            if user_choice in ['yes', 'y', 'haan', 'ha', 'kar do', 'place karo']:
                print("\n✅ Order confirmation received! Processing purchase...")
                print("\n" + "=" * 70)
                print("💳 Processing Order...")
                print("=" * 70)
                
                # Update state to proceed with purchase
                result["decision_type"] = "auto_buy"
                result["purchase_status"] = "processing"
                result["user_confirmed"] = True
                
                # Create new state for purchase execution
                purchase_state = {
                    "user_input": result.get("user_input", ""),
                    "selected_option": selected_option,
                    "decision_type": "auto_buy",
                    "item_name": item_name,
                    "quantity": result.get("quantity", "1"),
                    "purchase_status": "processing",
                    "user_confirmed": True
                }
                
                # Execute purchase using the actual purchase agent
                try:
                    from agents.purchase_agent import execute_purchase
                    
                    # Prepare proper input for purchase agent as per its expected format
                    purchase_input = {
                        "final_decision": {
                            "selected_platform": selected_option.get("platform", "zepto"),
                            "product": {
                                "name": item_name,
                                "price": selected_option.get("normalized_attributes", {}).get("price", 30),
                                "quantity": result.get("quantity", "1kg"),
                                "product_id": item_name.lower().replace(" ", "_").replace("-", "_")
                            },
                            "delivery": {
                                "delivery_date": "today",
                                "slot": "within 1 hour"
                            }
                        },
                        "user_context": {
                            "payment_preference": "cash_on_delivery",
                            "platform_preference": "zepto",
                            "confirmed_by_user": True
                        }
                    }
                    
                    print("   🚀 Executing Zepto Cash on Delivery order...")
                    purchase_result = execute_purchase(purchase_input)
                    
                    # Process the purchase result
                    if purchase_result.get("purchase_status") == "success":
                        order_id = purchase_result.get("execution_details", {}).get("order_id", "Unknown")
                        platform_used = purchase_result.get("execution_details", {}).get("platform_used", "Zepto")
                        product_name = purchase_result.get("order_confirmation", {}).get("product_name", item_name)
                        final_price = purchase_result.get("order_confirmation", {}).get("final_price", "N/A")
                        
                        result["purchase_status"] = "success"
                        result["order_id"] = order_id
                        result["ai_response"] = f"""✅ Order Successfully Placed!

📦 Order Details:
   Platform: {platform_used}
   Product: {product_name}
   Price: ₹{final_price}
   Payment: Cash on Delivery (COD)
   Order ID: {order_id}
   Delivery: Within 1 hour

🎉 Aapka order place ho gaya! Delivery person aayega aur aap cash mein payment kar denge.

Thank you for using GANGU! 🙏"""
                        
                    elif purchase_result.get("purchase_status") == "failed":
                        result["purchase_status"] = "failed"
                        error_msg = purchase_result.get("user_message", "Order placement failed")
                        result["ai_response"] = f"""❌ Order Failed

{error_msg}

😔 Kshama karein, order place nahi ho paaya. Kya aap dusra option try karna chahenge ya phir se koshish karein?"""
                    else:
                        result["purchase_status"] = "pending"
                        result["ai_response"] = f"""⏳ Order Processing...

Aapka order process ho raha hai. Thoda intezaar kariye...

Status: {purchase_result.get('purchase_status', 'unknown')}"""
                    
                except Exception as e:
                    print(f"❌ Purchase execution failed: {e}")
                    result["ai_response"] = f"❌ माफ़ करें, ऑर्डर प्लेस करते समय समस्या आई। कृपया बाद में कोशिश करें।\nError: {str(e)}"
                    result["purchase_status"] = "failed"
                
                break
                
            elif user_choice in ['no', 'n', 'nahi', 'cancel', 'cancel karo', 'mat karo']:
                print("\n❌ Order cancelled by user.")
                result["decision_type"] = "cancelled_by_user"
                result["purchase_status"] = "cancelled"
                result["user_confirmed"] = False
                result["ai_response"] = f"❌ ऑर्डर cancel कर दिया गया।\n\n📋 Summary:\n   Item: {item_name}\n   Platform: {platform}\n   Status: Cancelled by user\n\nकोई और चीज़ चाहिए तो बताइए! 😊"
                break
                
            else:
                print(f"⚠️  Please answer with 'Yes' or 'No' (you entered: '{user_choice}')")
                print("   Valid responses: Yes, Y, No, N, Haan, Nahi")
                continue
                
        except KeyboardInterrupt:
            print("\n\n❌ Order cancelled by user (Ctrl+C)")
            result["decision_type"] = "cancelled_by_user"
            result["purchase_status"] = "cancelled"
            result["user_confirmed"] = False
            result["ai_response"] = "❌ ऑर्डर cancel कर दिया गया। कोई और चीज़ चाहिए तो बताइए!"
            break
            
        except Exception as e:
            print(f"❌ Error during confirmation: {e}")
            continue
    
    return result


if __name__ == "__main__":
    try:
        init()
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        print("   Please check your setup and try again.")
        sys.exit(1)
