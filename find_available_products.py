#!/usr/bin/env python3
"""
Find products that are actually available in stock on Zepto
"""
import asyncio
import sys
from pathlib import Path

gangu_root = Path(__file__).parent
sys.path.append(str(gangu_root))

from mcp_clients.zepto_mcp_client import ZeptoMCPClient

async def find_available_products():
    """Test various product categories to find what's actually in stock"""
    
    # Test common products across different categories
    test_products = [
        # Vegetables & Fruits
        "potato", "onion", "tomato", "apple", "banana", "orange",
        # Dairy & Eggs
        "milk", "eggs", "paneer", "butter", "curd",
        # Grains & Staples
        "rice", "wheat flour", "sugar", "salt", "oil",
        # Snacks & Packaged
        "biscuits", "chips", "namkeen", "bread", "maggi",
        # Personal Care
        "toothpaste", "soap", "shampoo", "detergent",
        # Beverages (simpler ones)
        "water bottle", "soft drink", "juice", "tea", "coffee"
    ]
    
    server_script_path = gangu_root / "zepto-cafe-mcp" / "zepto_mcp_server.py"
    zepto_client = ZeptoMCPClient(str(server_script_path))
    
    available_products = []
    
    try:
        await zepto_client.connect()
        print("🔗 Connected to Zepto MCP server")
        print("🔍 Scanning for available products...\n")
        
        for product in test_products:
            try:
                result = await zepto_client.start_zepto_order(product)
                
                if isinstance(result, dict):
                    message = result.get('message', '')
                    success = result.get('success', False)
                    
                    # Check if product is actually available for ordering
                    if ("add to cart" in message.lower() or 
                        "added to cart" in message.lower() or
                        "proceed" in message.lower() or
                        success):
                        
                        available_products.append(product)
                        print(f"✅ {product} - AVAILABLE")
                        
                    elif "out of stock" in message.lower():
                        print(f"❌ {product} - OUT OF STOCK")
                    elif "not found" in message.lower():
                        print(f"❓ {product} - NOT FOUND")
                    else:
                        # Check message for availability indicators
                        if any(keyword in message.lower() for keyword in 
                              ["available", "in stock", "order", "cart"]):
                            available_products.append(product)
                            print(f"✅ {product} - LIKELY AVAILABLE")
                        else:
                            print(f"⚠️ {product} - UNCLEAR STATUS")
                            
                # Small delay to avoid overwhelming server
                await asyncio.sleep(0.5)
                        
            except Exception as e:
                print(f"❌ Error testing {product}: {e}")
                
    except Exception as e:
        print(f"❌ Connection error: {e}")
    finally:
        await zepto_client.disconnect()
    
    print(f"\n🎯 SUMMARY: Found {len(available_products)} available products:")
    for product in available_products:
        print(f"   • {product}")
        
    return available_products

if __name__ == "__main__":
    print("🛒 Finding products that are actually available on Zepto...")
    available = asyncio.run(find_available_products())
    
    # Save results for use in other scripts
    with open("available_products.txt", "w") as f:
        for product in available:
            f.write(f"{product}\n")
    
    print(f"\n💾 Saved {len(available)} available products to available_products.txt")