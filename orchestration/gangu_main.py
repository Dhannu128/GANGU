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


if __name__ == "__main__":
    try:
        init()
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        print("   Please check your setup and try again.")
        sys.exit(1)
