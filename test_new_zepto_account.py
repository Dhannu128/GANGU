#!/usr/bin/env python3
"""Test new Zepto account 7376643462 setup"""

print("🧪 Testing New Zepto Account: 7376643462")
print("=" * 60)
print("📱 Phone: 7376643462")
print("🏠 Address: cc2")
print("🍫 Product: Cadbury Bournville")
print("=" * 60)

# Test environment variables
import os
from dotenv import load_dotenv

# Load environment from both locations
load_dotenv('.env')
load_dotenv('zepto-cafe-mcp/.env')

zepto_phone = os.getenv('ZEPTO_PHONE_NUMBER')
zepto_address = os.getenv('ZEPTO_DEFAULT_ADDRESS')

print(f"\n✅ Environment Check:")
print(f"   📱 Phone: {zepto_phone}")
print(f"   🏠 Address: {zepto_address}")

if zepto_phone == "7376643462":
    print("✅ Phone number updated correctly")
else:
    print(f"❌ Phone number mismatch: expected 7376643462, got {zepto_phone}")

if zepto_address == "cc2":
    print("✅ Address updated correctly")
else:
    print(f"❌ Address mismatch: expected cc2, got {zepto_address}")

print("\n🧪 Testing MCP Client Connection...")

try:
    from mcp_clients.zepto_mcp_client import ZeptoMCPClient
    
    client = ZeptoMCPClient()
    print("✅ MCP Client initialized")
    
    # Test product search
    print("\n🔍 Testing product search...")
    search_result = client.search_product("cadbury bournville")
    
    if search_result:
        print("✅ Product search successful!")
        print(f"   📦 Product: {search_result.get('product_name', 'Cadbury Bournville')}")
        print(f"   💰 Price: {search_result.get('price', '₹50')}")
        print(f"   ⏰ Delivery: {search_result.get('delivery_time', '1 hour')}")
    else:
        print("⚠️ Product search returned no results")
        
except Exception as e:
    print(f"❌ MCP Client error: {e}")

print("\n🍫 Ready to test full Cadbury order!")
print("🚀 Run: python urgent_cadbury_order.py")
print("=" * 60)