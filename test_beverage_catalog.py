#!/usr/bin/env python3
"""
Test Zepto Beverage Catalog
Check what beverages are available in Zepto
"""
import asyncio
import sys
from pathlib import Path

# Add GANGU root to path
gangu_root = Path(__file__).parent
sys.path.append(str(gangu_root))

from mcp_clients.zepto_mcp_client import ZeptoMCPClient

async def check_beverage_catalog():
    """Check what beverages are available in Zepto catalog"""
    
    # Get server script path
    server_script_path = gangu_root / "zepto-cafe-mcp" / "zepto_mcp_server.py"
    zepto_client = ZeptoMCPClient(str(server_script_path))
    
    try:
        print("🔗 Connecting to Zepto MCP server...")
        await zepto_client.connect()
        
        # Test common beverage items
        beverages_to_test = [
            # Hot beverages
            "tea", "chai", "adrak chai", "coffee", "latte", "cappuccino", 
            "espresso", "hot chocolate", "green tea",
            
            # Cold beverages  
            "cold coffee", "iced tea", "lemonade", "juice", "orange juice",
            "apple juice", "mango juice", "coconut water",
            
            # Dairy
            "milk", "lassi", "buttermilk", "milkshake",
            
            # Soft drinks
            "cola", "pepsi", "coke", "sprite", "fanta", "soda", "energy drink",
            
            # Water
            "water", "mineral water", "drinking water"
        ]
        
        available_beverages = []
        unavailable_beverages = []
        
        print(f"\n🧪 Testing {len(beverages_to_test)} beverage items...\n")
        
        for i, beverage in enumerate(beverages_to_test, 1):
            print(f"   [{i:2d}/{len(beverages_to_test)}] Testing: {beverage:<20}", end="")
            
            try:
                result = await zepto_client.start_zepto_order(beverage)
                
                if isinstance(result, dict):
                    message = result.get('message', '').lower()
                    success = result.get('success', False)
                else:
                    message = str(result).lower()
                    success = True
                
                if "not found in catalog" in message:
                    unavailable_beverages.append(beverage)
                    print("❌ Not available")
                elif "available products:" in message:
                    unavailable_beverages.append(beverage)
                    print("❌ Not in catalog")
                else:
                    available_beverages.append(beverage)
                    print("✅ Available")
                    
            except Exception as e:
                unavailable_beverages.append(beverage)
                print(f"❌ Error: {str(e)[:30]}...")
        
        print("\n" + "="*70)
        print("📊 ZEPTO BEVERAGE CATALOG RESULTS")
        print("="*70)
        
        if available_beverages:
            print(f"\n✅ AVAILABLE BEVERAGES ({len(available_beverages)}):")
            for i, beverage in enumerate(available_beverages, 1):
                print(f"   {i:2d}. {beverage}")
        else:
            print("\n❌ NO BEVERAGES FOUND IN CATALOG")
        
        print(f"\n📊 Summary:")
        print(f"   • Available: {len(available_beverages)}")
        print(f"   • Not Available: {len(unavailable_beverages)}")
        print(f"   • Total Tested: {len(beverages_to_test)}")
        
        return available_beverages, unavailable_beverages
        
    except Exception as e:
        print(f"❌ Error connecting to Zepto: {e}")
        return [], []
    finally:
        try:
            await zepto_client.disconnect()
            print("\n🔌 Disconnected from Zepto")
        except:
            pass

async def get_full_catalog():
    """Get the full available product catalog from server response"""
    
    server_script_path = gangu_root / "zepto-cafe-mcp" / "zepto_mcp_server.py"
    zepto_client = ZeptoMCPClient(str(server_script_path))
    
    try:
        print("\n🔍 Getting full catalog from server...")
        await zepto_client.connect()
        
        # Query a non-existent item to get full catalog list
        result = await zepto_client.start_zepto_order("nonexistent_item_xyz")
        
        if isinstance(result, dict):
            message = result.get('message', '')
            
            if "Available products:" in message:
                # Extract product list
                products_section = message.split("Available products:")[1].strip()
                products = [p.strip() for p in products_section.split(",")]
                
                # Filter for beverages (rough categorization)
                beverages = []
                beverage_keywords = [
                    'tea', 'chai', 'coffee', 'latte', 'cappuccino', 'espresso',
                    'juice', 'lemon', 'milk', 'shake', 'cold', 'hot', 'iced',
                    'coca', 'cola', 'pepsi', 'drink', 'water', 'chaas'
                ]
                
                for product in products:
                    for keyword in beverage_keywords:
                        if keyword.lower() in product.lower():
                            beverages.append(product)
                            break
                
                print(f"\n🥤 BEVERAGES FROM FULL CATALOG ({len(beverages)}):")
                for i, beverage in enumerate(beverages, 1):
                    print(f"   {i:2d}. {beverage}")
                
                print(f"\n📋 TOTAL PRODUCTS IN CATALOG: {len(products)}")
                
                return beverages, products
        
    except Exception as e:
        print(f"❌ Error getting catalog: {e}")
        return [], []
    finally:
        await zepto_client.disconnect()

if __name__ == "__main__":
    print("🥤 Checking Zepto Beverage Catalog...")
    print("="*50)
    
    # Method 1: Test specific beverages
    available_beverages, unavailable = asyncio.run(check_beverage_catalog())
    
    # Method 2: Get beverages from full catalog
    catalog_beverages, all_products = asyncio.run(get_full_catalog())
    
    if catalog_beverages:
        print(f"\n🎯 FINAL BEVERAGE LIST:")
        print("="*30)
        for i, beverage in enumerate(sorted(set(catalog_beverages)), 1):
            print(f"   {i:2d}. {beverage}")
    
    print(f"\n✅ Beverage catalog check complete!")