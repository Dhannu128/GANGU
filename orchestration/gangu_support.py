"""
GANGU Support Script
View and resume interrupted workflows
"""
from gangu_graph import create_gangu_graph
from dotenv import load_dotenv
from langgraph.checkpoint.mongodb import MongoDBSaver
from langgraph.types import Command
import os

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")

def init():
    """Support interface for GANGU"""
    
    print("=" * 60)
    print("🔧 GANGU SUPPORT - Admin Panel")
    print("=" * 60)
    
    with MongoDBSaver.from_conn_string(MONGODB_URI) as checkpointer:
        gangu_graph = create_gangu_graph(checkpointer=checkpointer)
        
        # Check state for user
        config = {"configurable": {"thread_id": "user_001"}}
        
        state = gangu_graph.get_state(config=config)
        
        print("\n📊 Current State:")
        print(f"   User Input: {state.values.get('user_input', 'N/A')}")
        print(f"   Intent: {state.values.get('detected_intent', 'N/A')}")
        print(f"   Item: {state.values.get('item_name', 'N/A')}")
        print(f"   Status: {state.next if state.next else 'Completed'}")
        
        if state.next:
            print(f"\n⚠️  Workflow paused at: {state.next}")
            
            action = input("\nResume workflow? (yes/no): ").strip().lower()
            
            if action == 'yes':
                print("\n🔄 Resuming workflow...")
                
                # Resume with empty command
                resume_command = Command(resume={})
                
                for event in gangu_graph.stream(resume_command, config, stream_mode="values"):
                    pass
                
                final_state = gangu_graph.get_state(config)
                response = final_state.values.get("ai_response", "Completed")
                
                print("\n✅ Workflow completed:")
                print(response)
        else:
            print("\n✅ No pending workflows")
            
            # Show last response
            last_response = state.values.get("ai_response", "N/A")
            if last_response != "N/A":
                print("\n📝 Last Response:")
                print(last_response)


if __name__ == "__main__":
    init()
