"""
Debug Amazon MCP Response
"""
import asyncio
from mcp_clients.amazon_mcp_client import AmazonMCPClient

async def debug():
    client = AmazonMCPClient()
    
    try:
        await client.connect()
        
        # Call tool directly to see raw response
        result = await client.session.call_tool(
            "amazon_search",
            {"q": "rice", "domain": "amazon.in"}
        )
        
        print("Raw MCP Response:")
        print(f"Type: {type(result)}")
        print(f"Content length: {len(result.content)}")
        
        for i, content in enumerate(result.content):
            print(f"\nContent {i}:")
            print(f"  Type: {type(content)}")
            if hasattr(content, 'text'):
                print(f"  Text: {content.text[:500]}")
            else:
                print(f"  Value: {str(content)[:500]}")
                
    finally:
        await client.disconnect()

if __name__ == "__main__":
    asyncio.run(debug())
