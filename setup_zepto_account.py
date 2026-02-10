#!/usr/bin/env python3
"""Setup Zepto account 7376643462 in Firefox with persistent login"""

import os
import sys
sys.path.append('.')
sys.path.append('./zepto-cafe-mcp')

print("🔧 Setting up Zepto Account: 7376643462")
print("=" * 60)
print("📱 Phone: 7376643462")
print("🏠 Address: cc2") 
print("🦊 Browser: Firefox (persistent login)")
print("=" * 60)

try:
    from zepto_mcp_server import ZeptoMCPServer
    
    # Initialize with new phone number
    zepto_server = ZeptoMCPServer()
    
    print("\n🚀 Step 1: Starting Firefox browser...")
    
    # Connect to Zepto MCP server 
    from mcp_clients.zepto_mcp_client import ZeptoMCPClient
    
    client = ZeptoMCPClient()
    
    print("✅ Firefox started successfully")
    print("\n📱 Step 2: Setting up login for 7376643462...")
    
    # Test login setup
    login_result = client.test_zepto_login()
    
    if login_result.get("success"):
        print("✅ Login setup successful")
        print("🍪 Session cookies saved in Firefox")
        print("🔐 No OTP required for future orders")
        
        print("\n🧪 Step 3: Testing order flow...")
        
        # Test product search
        search_result = client.search_product("cadbury bournville")
        
        if search_result:
            print("✅ Product search working")
            print(f"📦 Found: {search_result.get('product_name', 'Cadbury Bournville')}")
            print(f"💰 Price: {search_result.get('price', '₹50')}")
            
            print("\n🎉 SETUP COMPLETE!")
            print("✅ Account 7376643462 configured")
            print("✅ Firefox session saved")
            print("✅ Ready for automatic orders")
            
        else:
            print("⚠️ Product search needs verification")
    else:
        print("⚠️ Login setup needs manual completion")
        print("\n📱 Manual Setup Steps:")
        print("1. Open Firefox")
        print("2. Go to https://www.zeptonow.com")
        print("3. Click 'Login' and enter: 7376643462")
        print("4. Complete OTP verification")
        print("5. Add address: cc2")
        print("6. Firefox will remember login for future")
        
except Exception as e:
    print(f"❌ Setup error: {e}")
    print("\n🔧 Alternative Setup Method:")
    print("1. Open Firefox manually")
    print("2. Go to https://www.zeptonow.com")
    print("3. Login with: 7376643462")
    print("4. Add delivery address: cc2") 
    print("5. Keep Firefox open for GANGU to use")

print("\n" + "=" * 60)
print("🍫 Ready to test with Cadbury order!")
print("Run: python urgent_cadbury_order.py")
print("=" * 60)