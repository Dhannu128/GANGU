"""
Amazon MCP Client - Interface for GANGU Search Agent
Connects to Amazon MCP Server via uvx (Fewsats Amazon MCP)
"""
import asyncio
import json
from contextlib import AsyncExitStack
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import os
import sys

class AmazonMCPClient:
    """Client to connect to Amazon MCP Server (Fewsats)"""
    
    def __init__(self):
        """Initialize Amazon MCP Client"""
        self.session = None
        self.exit_stack = None
        
    async def connect(self):
        """Connect to the Amazon MCP server via uvx"""
        if self.session:
            return  # Already connected
            
        self.exit_stack = AsyncExitStack()
        
        # Server parameters - using uvx to run amazon-mcp
        server_params = StdioServerParameters(
            command="uvx",
            args=["amazon-mcp"],
            env={
                **os.environ,
            }
        )
        
        # Start client
        try:
            stdio_transport = await self.exit_stack.enter_async_context(
                stdio_client(server_params)
            )
            
            stdio, write = stdio_transport
            self.session = await self.exit_stack.enter_async_context(
                ClientSession(stdio, write)
            )
            
            # Initialize session
            await self.session.initialize()
            
            print("✅ Connected to Amazon MCP Server")
            
            # List available tools
            tools_result = await self.session.list_tools()
            print(f"📋 Available tools: {[tool.name for tool in tools_result.tools]}")
        except Exception as e:
            print(f"⚠️ Failed to connect to Amazon MCP Server: {e}")
            print(f"💡 Make sure 'uvx' is installed and 'amazon-mcp' package is available")
            raise
        
    async def disconnect(self):
        """Disconnect from the Amazon MCP server"""
        if self.exit_stack:
            try:
                await self.exit_stack.aclose()
            except Exception as e:
                # Ignore cleanup errors
                pass
            finally:
                self.session = None
                self.exit_stack = None
                print("✅ Disconnected from Amazon MCP Server")
    
    async def search_product(self, product_name: str, domain: str = "amazon.in", max_results: int = 5) -> dict:
        """
        Search for a product on Amazon
        
        Args:
            product_name: Name of the product to search
            domain: Amazon domain (default: amazon.in for India)
            max_results: Maximum number of results to return
            
        Returns:
            dict with product info
        """
        if not self.session:
            await self.connect()
        
        try:
            print(f"🔍 Calling Amazon MCP search for: {product_name} on {domain}")
            
            # Call amazon_search tool
            result = await self.session.call_tool(
                "amazon_search",
                {
                    "q": product_name,
                    "domain": domain
                }
            )
            
            # Amazon MCP returns: [status_code, product1_json, product2_json, ...]
            if result and len(result.content) > 1:
                # First content is status code (200)
                # Rest are product JSONs
                products = []
                
                for i, content in enumerate(result.content[1:max_results+1]):  # Skip status code, limit results
                    try:
                        product_text = content.text if hasattr(content, 'text') else str(content)
                        product_data = json.loads(product_text)
                        
                        products.append({
                            "product_name": product_data.get("title", "Unknown Product"),
                            "price": "Check on Amazon",  # Price not in response
                            "url": product_data.get("link", ""),
                            "rating": "N/A",
                            "asin": product_data.get("asin", ""),
                            "image": "",
                            "availability": "Available on Amazon"
                        })
                    except json.JSONDecodeError as e:
                        print(f"⚠️ Could not parse product {i+1}: {e}")
                        continue
                
                if products:
                    print(f"✅ Found {len(products)} products on Amazon")
                    return {
                        "found": True,
                        "products": products,
                        "platform": "Amazon",
                        "domain": domain,
                        "query": product_name
                    }
                else:
                    return {
                        "found": False,
                        "products": [],
                        "platform": "Amazon",
                        "error": "Could not parse products"
                    }
            else:
                return {
                    "found": False,
                    "products": [],
                    "platform": "Amazon",
                    "error": "No products returned"
                }
                
        except Exception as e:
            print(f"❌ Error searching Amazon: {e}")
            import traceback
            traceback.print_exc()
            return {
                "found": False,
                "products": [],
                "platform": "Amazon",
                "error": str(e)
            }


# Test function
async def test_amazon_client():
    """Test the Amazon MCP Client"""
    client = AmazonMCPClient()
    
    try:
        # Test search
        print("\n🔍 Testing Amazon search...")
        result = await client.search_product("white chickpeas", domain="amazon.in")
        print(f"\n📦 Search Result:")
        print(json.dumps(result, indent=2))
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
    finally:
        await client.disconnect()


if __name__ == "__main__":
    print("🚀 Amazon MCP Client Test")
    print("=" * 60)
    asyncio.run(test_amazon_client())
