"""
Test Amazon MCP Client
"""
import asyncio
from mcp_clients.amazon_mcp_client import AmazonMCPClient

async def test():
    print("🧪 Testing Amazon MCP Client\n")
    
    client = AmazonMCPClient()
    
    try:
        print("1️⃣ Connecting to Amazon MCP...")
        await client.connect()
        
        print("\n2️⃣ Searching for 'rice'...")
        result = await client.search_product("rice", domain="amazon.in")
        
        print(f"\n📊 Result:")
        print(f"   Found: {result.get('found')}")
        print(f"   Products: {len(result.get('products', []))}")
        
        if result.get('found'):
            for i, p in enumerate(result['products'][:3], 1):
                print(f"\n   Product {i}:")
                print(f"      Name: {p['product_name']}")
                print(f"      Price: {p['price']}")
                print(f"      URL: {p['url'][:60]}...")
        else:
            print(f"   Error: {result.get('error')}")
            if 'raw_response' in result:
                print(f"   Raw: {result['raw_response']}")
                
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await client.disconnect()

if __name__ == "__main__":
    asyncio.run(test())
