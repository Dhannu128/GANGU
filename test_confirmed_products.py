#!/usr/bin/env python3
"""
Test direct order with confirmed in-stock products
"""
import asyncio
import sys
from pathlib import Path

gangu_root = Path(__file__).parent
sys.path.append(str(gangu_root))

from mcp_clients.zepto_mcp_client import ZeptoMCPClient

async def test_confirmed_products():
    """Test with products that were confirmed to be in stock"""
    
    # Products from our beverage catalog that showed as available
    confirmed_products = [
        "potato",  # Confirmed available from earlier test
        "onion",   # Confirmed available from earlier test
    ]
    
    server_script_path = gangu_root / "zepto-cafe-mcp" / "zepto_mcp_server.py"
    zepto_client = ZeptoMCPClient(str(server_script_path))
    
    try:
        await zepto_client.connect()
        print("🔗 Connected to Zepto MCP server")
        
        for product in confirmed_products:
            print(f"\n📦 Testing confirmed product: {product}")
            
            try:
                result = await zepto_client.start_zepto_order(product)
                
                if isinstance(result, dict):
                    message = result.get('message', '')
                    success = result.get('success', False)
                    
                    print(f"   Success: {success}")
                    print(f"   Message: {message[:100]}...")
                    
                    if "out of stock" in message.lower():
                        print(f"   ❌ {product} is out of stock")
                    elif "not found" in message.lower():
                        print(f"   ❌ {product} not found in catalog")
                    elif success:
                        print(f"   ✅ {product} is available for ordering!")
                    else:
                        print(f"   ⚠️ Unknown status for {product}")
                        
            except Exception as e:
                print(f"   ❌ Error testing {product}: {e}")
                
    except Exception as e:
        print(f"❌ Connection error: {e}")
    finally:
        await zepto_client.disconnect()

if __name__ == "__main__":
    print("🧪 Testing confirmed available products...")
    asyncio.run(test_confirmed_products())