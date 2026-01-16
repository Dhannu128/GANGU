"""
Quick test of GANGU with automated input
"""
import sys
import os
from pathlib import Path

# Add GANGU root to path
gangu_root = Path(__file__).parent
sys.path.insert(0, str(gangu_root))

# Load environment - must happen BEFORE any agent imports
from dotenv import load_dotenv, dotenv_values

# Load env variables from .env file
env_file = gangu_root / ".env"
if env_file.exists():
    # Load into environment
    env_vars = dotenv_values(env_file)
    for key, value in env_vars.items():
        if value:  # Only set non-empty values
            os.environ[key] = value
    print(f"[OK] Loaded {len(env_vars)} environment variables from .env")
else:
    print(f"[WARNING] .env file not found at {env_file}")

# Verify API key is loaded
if not os.environ.get('GEMINI_API_KEY'):
    print("[ERROR] GEMINI_API_KEY not loaded!")
    sys.exit(1)
else:
    print(f"[OK] GEMINI_API_KEY loaded (length: {len(os.environ['GEMINI_API_KEY'])})")

# Import after loading env
from orchestration.gangu_graph import create_gangu_graph

def test_input(user_input: str):
    """Test GANGU with a specific input"""
    print("\n" + "=" * 80)
    print(f"🧪 TESTING GANGU WITH INPUT: \"{user_input}\"")
    print("=" * 80)
    
    # Create graph
    print("\n📊 Creating GANGU graph...")
    gangu_graph = create_gangu_graph(checkpointer=None)
    print("✅ Graph created\n")
    
    # Prepare state
    initial_state = {
        "user_input": user_input,
        "user_preferences": {}
    }
    
    print("=" * 80)
    print("🔄 Processing through pipeline...")
    print("=" * 80 + "\n")
    
    try:
        # Run the pipeline
        result = gangu_graph.invoke(initial_state)
        
        # Display results
        print("\n" + "=" * 80)
        print("📊 RESULTS")
        print("=" * 80)
        
        print(f"\n🧠 Intent: {result.get('detected_intent')}")
        print(f"📦 Item: {result.get('item_name')} ({result.get('item_original')})")
        print(f"📊 Quantity: {result.get('quantity')}")
        print(f"⚡ Urgency: {result.get('urgency')}")
        
        print(f"\n🎯 Decision: {result.get('decision_type')}")
        print(f"✅ Confidence: {result.get('confidence_level')}")
        
        selected = result.get('selected_option')
        if selected:
            platform = selected.get('platform', 'N/A')
            price = selected.get('unit_price_label', selected.get('price', 'N/A'))
            print(f"🏆 Selected: {platform} at {price}")
        
        print("\n" + "=" * 80)
        print("🤖 FINAL RESPONSE TO USER:")
        print("=" * 80)
        print(result.get('ai_response', 'No response'))
        print("=" * 80)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # Test cases
    test_cases = [
        "doodh khatam ho gaya",
        "White chane khatam ho gaye",
        "Atta le aao"
    ]
    
    print("\n" + "=" * 80)
    print(" " * 25 + "GANGU AUTOMATED TEST")
    print("=" * 80)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n\n{'='*80}")
        print(f"TEST {i}/{len(test_cases)}")
        print(f"{'='*80}")
        
        success = test_input(test_case)
        
        if success:
            print(f"\n[PASS] TEST {i} PASSED")
        else:
            print(f"\n[FAIL] TEST {i} FAILED")
        
        if i < len(test_cases):
            print("\n" + "-"*80)
            input("Press Enter to continue to next test...")
    
    print("\n\n" + "="*80)
    print("ALL TESTS COMPLETED!")
    print("="*80)
