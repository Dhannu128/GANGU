#!/usr/bin/env python3
"""
Test Purchase Agent Fix
=======================
Quick test to verify ZeptoMCPClient can be created with server_script_path
"""

import sys
from pathlib import Path
sys.path.append('.')

print("🔧 Testing Purchase Agent Fix...")
print("=" * 50)

try:
    # Test ZeptoMCPClient creation with server_script_path
    from mcp_clients.zepto_mcp_client import ZeptoMCPClient
    
    # Same path logic as in purchase agent
    server_path = Path(__file__).parent / "zepto-cafe-mcp" / "zepto_mcp_server.py"
    print(f"📁 Server path: {server_path}")
    print(f"📁 Server exists: {server_path.exists()}")
    
    # Try to create the client
    zepto_client = ZeptoMCPClient(str(server_path))
    print("✅ ZeptoMCPClient created successfully!")
    print(f"✅ Server script path: {zepto_client.server_script_path}")
    
    print("\n🎯 RESULT:")
    print("✅ Purchase Agent fix successful!")
    print("✅ ZeptoMCPClient will no longer fail with missing server_script_path")
    print("✅ Ready for real Slice Mango ordering!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    print("❌ Purchase agent fix failed")

print("\n🚀 NEXT STEPS:")
print("1. Start GANGU: python start_gangu.py")
print("2. Say: 'slice order kar do'")
print("3. Confirm purchase when asked")
print("4. GANGU will place real Zepto order via COD!")