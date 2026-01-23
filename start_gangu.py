"""
GANGU Startup Script
Checks all dependencies and starts the system
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def print_header():
    """Print startup banner"""
    print("\n" + "=" * 80)
    print(" " * 20 + "🤖 GANGU STARTUP CHECK")
    print(" " * 15 + "Grocery Assistant for Elderly")
    print("=" * 80 + "\n")

def check_python_version():
    """Check Python version"""
    print("🐍 Checking Python version...")
    version = sys.version_info
    if version.major == 3 and version.minor >= 10:
        print(f"   ✅ Python {version.major}.{version.minor}.{version.micro} (OK)")
        return True
    else:
        print(f"   ❌ Python {version.major}.{version.minor} (Need Python 3.10+)")
        return False

def check_environment_variables():
    """Check required environment variables"""
    print("\n🔑 Checking environment variables...")
    
    required_vars = {
        "GEMINI_API_KEY": "Gemini API for AI agents",
        "LANGSMITH_API_KEY": "LangSmith for tracing",
        "LANGSMITH_PROJECT": "LangSmith project name",
        "MONGODB_URI": "MongoDB for checkpointing"
    }
    
    all_ok = True
    for var, description in required_vars.items():
        value = os.getenv(var)
        if value:
            # Mask sensitive data
            if "KEY" in var:
                masked = value[:8] + "..." + value[-4:] if len(value) > 12 else "***"
                print(f"   ✅ {var}: {masked}")
            else:
                print(f"   ✅ {var}: {value}")
        else:
            print(f"   ⚠️  {var}: Not set ({description})")
            if var in ["GEMINI_API_KEY"]:
                all_ok = False
    
    return all_ok

def check_required_packages():
    """Check if required packages are installed"""
    print("\n📦 Checking required packages...")
    
    required_packages = {
        "google.genai": "google-genai",
        "langgraph": "langgraph",
        "langchain": "langchain",
        "dotenv": "python-dotenv",
        "pymongo": "pymongo"
    }
    
    all_ok = True
    for module, package in required_packages.items():
        try:
            __import__(module)
            print(f"   ✅ {package}")
        except ImportError:
            print(f"   ❌ {package} (install: pip install {package})")
            all_ok = False
    
    return all_ok

def check_agents():
    """Check if all agents are available"""
    print("\n🤖 Checking GANGU agents...")
    
    agents = [
        "agents.intent_extraction_agent",
        "agents.task_planner_agent",
        "agents.search_agent",
        "agents.comparison_agent",
        "agents.decision_agent",
        "agents.purchase_agent"
    ]
    
    all_ok = True
    for agent in agents:
        try:
            __import__(agent)
            agent_name = agent.split(".")[-1].replace("_", " ").title()
            print(f"   ✅ {agent_name}")
        except ImportError as e:
            agent_name = agent.split(".")[-1].replace("_", " ").title()
            print(f"   ❌ {agent_name}: {e}")
            all_ok = False
    
    return all_ok

def check_mcp_clients():
    """Check MCP clients"""
    print("\n🔌 Checking MCP clients...")
    
    clients = [
        ("mcp_clients.zepto_mcp_client", "Zepto MCP"),
        ("mcp_clients.amazon_mcp_client", "Amazon MCP")
    ]
    
    mcp_count = 0
    for module, name in clients:
        try:
            __import__(module)
            print(f"   ✅ {name}")
            mcp_count += 1
        except ImportError:
            print(f"   ⚠️  {name} (optional)")
    
    if mcp_count > 0:
        print(f"   ℹ️  {mcp_count} MCP client(s) available")
    else:
        print(f"   ⚠️  No MCP clients available (will use fallback data)")
    
    return True  # MCP clients are optional

def check_mongodb():
    """Check MongoDB connection"""
    print("\n🍃 Checking MongoDB...")
    
    mongodb_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    
    try:
        from pymongo import MongoClient
        client = MongoClient(mongodb_uri, serverSelectionTimeoutMS=2000)
        # Trigger connection
        client.server_info()
        print(f"   ✅ MongoDB connected: {mongodb_uri}")
        return True
    except Exception as e:
        print(f"   ⚠️  MongoDB not available: {e}")
        print(f"   ℹ️  GANGU will run without checkpointing")
        print(f"   ℹ️  To enable: Run 'docker-compose up -d' in config folder")
        return False

def check_langsmith():
    """Check LangSmith configuration"""
    print("\n📊 Checking LangSmith tracing...")
    
    tracing = os.getenv("LANGSMITH_TRACING", "false").lower()
    api_key = os.getenv("LANGSMITH_API_KEY")
    project = os.getenv("LANGSMITH_PROJECT", "gangu-project")
    
    if tracing == "true" and api_key:
        print(f"   ✅ LangSmith enabled")
        print(f"   ✅ Project: {project}")
        print(f"   ℹ️  Traces: https://smith.langchain.com/o/YOUR-ORG/projects/p/{project}")
        return True
    else:
        print(f"   ⚠️  LangSmith tracing disabled")
        print(f"   ℹ️  To enable: Set LANGSMITH_TRACING=true in .env")
        return False

def print_summary(checks):
    """Print summary of all checks"""
    print("\n" + "=" * 80)
    print("📋 STARTUP SUMMARY")
    print("=" * 80)
    
    total = len(checks)
    passed = sum(1 for check in checks.values() if check)
    
    for name, status in checks.items():
        status_icon = "✅" if status else "❌"
        print(f"   {status_icon} {name}")
    
    print("\n" + "=" * 80)
    print(f"   {passed}/{total} checks passed")
    
    if checks["Python Version"] and checks["Environment Variables"] and checks["Required Packages"] and checks["Agents"]:
        print("\n   🚀 GANGU is ready to start!")
        return True
    else:
        print("\n   ⚠️  Some critical components are missing")
        print("   📖 Please fix the issues above before starting GANGU")
        return False

def start_gangu():
    """Start GANGU main application"""
    print("\n" + "=" * 80)
    print("🚀 STARTING GANGU...")
    print("=" * 80 + "\n")
    
    try:
        from orchestration.gangu_main import init
        init()
    except KeyboardInterrupt:
        print("\n\n👋 GANGU stopped by user")
    except Exception as e:
        print(f"\n❌ Error starting GANGU: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Main startup function"""
    print_header()
    
    # Run all checks
    checks = {
        "Python Version": check_python_version(),
        "Environment Variables": check_environment_variables(),
        "Required Packages": check_required_packages(),
        "Agents": check_agents(),
        "MCP Clients": check_mcp_clients(),
        "MongoDB": check_mongodb(),
        "LangSmith": check_langsmith()
    }
    
    # Print summary
    ready = print_summary(checks)
    
    if ready:
        response = input("\n❓ Start GANGU now? (yes/no): ").strip().lower()
        if response in ['yes', 'y']:
            start_gangu()
        else:
            print("\n👋 Startup cancelled. Run 'python start_gangu.py' when ready.")
    else:
        print("\n" + "=" * 80)
        print("💡 QUICK FIX GUIDE:")
        print("=" * 80)
        print("\n1. Install missing packages:")
        print("   pip install -r config/requirements.txt")
        print("\n2. Set up environment variables:")
        print("   Copy config/.env.example to .env and fill in your API keys")
        print("\n3. Start MongoDB (optional):")
        print("   cd config && docker-compose up -d")
        print("\n4. Run this script again:")
        print("   python start_gangu.py")
        print("\n" + "=" * 80 + "\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Startup interrupted")
    except Exception as e:
        print(f"\n❌ Startup failed: {e}")
        import traceback
        traceback.print_exc()
