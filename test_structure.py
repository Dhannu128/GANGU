"""
Quick test to verify GANGU folder structure
"""
import os
import sys

def test_structure():
    """Test that all folders and key files exist"""
    
    gangu_root = r"d:\personal\AI-ML\python\GANGU"
    
    print("=" * 60)
    print("Testing GANGU Folder Structure")
    print("=" * 60)
    
    # Test folders
    folders = [
        "agents",
        "orchestration",
        "mcp_clients",
        "config",
        "docs",
        "scripts"
    ]
    
    print("\n📁 Checking folders...")
    for folder in folders:
        path = os.path.join(gangu_root, folder)
        status = "✅" if os.path.exists(path) else "❌"
        print(f"{status} {folder}/")
    
    # Test key files
    files = {
        "agents/intent_extraction_agent.py": "Intent Extraction Agent",
        "agents/task_planner_agent.py": "Task Planner Agent",
        "agents/search_agent.py": "Search Agent (MCP-enabled)",
        "orchestration/gangu_graph.py": "LangGraph Orchestration",
        "orchestration/gangu_main.py": "Main Application",
        "mcp_clients/zepto_mcp_client.py": "Zepto MCP Client",
        "config/requirements.txt": "Dependencies",
        "config/docker-compose.yml": "MongoDB Config",
        "docs/README.md": "Main Documentation",
        "scripts/setup_zepto_mcp.ps1": "Setup Script"
    }
    
    print("\n📄 Checking key files...")
    for file_path, description in files.items():
        path = os.path.join(gangu_root, file_path)
        status = "✅" if os.path.exists(path) else "❌"
        print(f"{status} {description:30} [{file_path}]")
    
    # Test imports
    print("\n🐍 Testing imports...")
    sys.path.insert(0, gangu_root)
    
    try:
        from agents import intent_extraction_agent
        print("✅ agents.intent_extraction_agent")
    except Exception as e:
        print(f"❌ agents.intent_extraction_agent: {e}")
    
    try:
        from agents import search_agent
        print("✅ agents.search_agent")
    except Exception as e:
        print(f"❌ agents.search_agent: {e}")
    
    try:
        from mcp_clients import zepto_mcp_client
        print("✅ mcp_clients.zepto_mcp_client")
    except Exception as e:
        print(f"❌ mcp_clients.zepto_mcp_client: {e}")
    
    try:
        from orchestration import gangu_graph
        print("✅ orchestration.gangu_graph")
    except Exception as e:
        print(f"❌ orchestration.gangu_graph: {e}")
    
    # Summary
    print("\n" + "=" * 60)
    print("✅ GANGU Structure Test Complete!")
    print("=" * 60)
    print("\n📋 Next Steps:")
    print("1. Test Search Agent: python agents/search_agent.py")
    print("2. Test MCP Client: python mcp_clients/zepto_mcp_client.py")
    print("3. Run GANGU: python orchestration/gangu_main.py")
    print("")

if __name__ == "__main__":
    test_structure()
