"""
Walmart MCP Client - Interface for GANGU Search Agent
Connects to Walmart MCP Server via Apify (walmart-mcp)
"""
import asyncio
import json
from contextlib import AsyncExitStack
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import os
import sys

class WalmartMCPClient:
    """Client to connect to Walmart MCP Server (Apify walmart-savings)"""
    
    def __init__(self, apify_token: str = None):
        """
        Initialize Walmart MCP Client
        
        Args:
            apify_token: Apify API token (if None, will look in environment)
        """
        self.session = None
        self.exit_stack = None
        self.apify_token = apify_token or os.environ.get('APIFY_TOKEN')
        
        if not self.apify_token:
            print("⚠️ Warning: APIFY_TOKEN not set. Walmart MCP may not work properly.")
        
    async def connect(self):
        """Connect to the Walmart MCP server via npx"""
        if self.session:
            return  # Already connected
            
        self.exit_stack = AsyncExitStack()
        
        # Validate APIFY_TOKEN
        if not self.apify_token:
            raise ValueError("APIFY_TOKEN is required but not set. Please add it to your .env file.")
        
        # Server parameters - using npx to run walmart-mcp
        server_params = StdioServerParameters(
            command="npx",
            args=["-y", "walmart-mcp"],
            env={
                **os.environ,
                "APIFY_TOKEN": self.apify_token
            }
        )
        
        # Start client
        try:
            print("🔄 Connecting to Walmart MCP Server...")
            stdio_transport = await self.exit_stack.enter_async_context(
                stdio_client(server_params)
            )
            
            stdio, write = stdio_transport
            self.session = await self.exit_stack.enter_async_context(
                ClientSession(stdio, write)
            )
            
            # Initialize session with timeout
            await asyncio.wait_for(self.session.initialize(), timeout=30.0)
            
            print("✅ Connected to Walmart MCP Server")
            
            # List available tools
            tools_result = await self.session.list_tools()
            print(f"📋 Available tools: {[tool.name for tool in tools_result.tools]}")
        except asyncio.TimeoutError:
            print(f"❌ Timeout connecting to Walmart MCP Server")
            print(f"💡 This may indicate an issue with your APIFY_TOKEN or network connectivity")
            await self.disconnect()
            raise
        except Exception as e:
            print(f"❌ Failed to connect to Walmart MCP Server: {e}")
            print(f"💡 Possible issues:")
            print(f"   - Invalid APIFY_TOKEN (verify at apify.com)")
            print(f"   - Network connectivity issues")
            print(f"   - npx or Node.js not properly installed")
            await self.disconnect()
            raise
        
    async def disconnect(self):
        """Disconnect from the Walmart MCP server"""
        if self.exit_stack:
            try:
                await self.exit_stack.aclose()
            except Exception as e:
                # Ignore cleanup errors
                pass
            finally:
                self.session = None
                self.exit_stack = None
                print("✅ Disconnected from Walmart MCP Server")
    
    async def search_product(self, product_name: str, max_results: int = 5) -> dict:
        """
        Search for a product on Walmart
        
        Args:
            product_name: Name of the product to search
            max_results: Maximum number of results to return
            
        Returns:
            dict with product info
        """
        if not self.session:
            await self.connect()
        
        try:
            print(f"🔍 Calling Walmart MCP search for: {product_name}")
            
            # Call walmart_search tool (based on typical Apify MCP naming)
            result = await self.session.call_tool(
                "walmart_search",
                {
                    "query": product_name,
                    "maxResults": max_results
                }
            )
            
            # Parse Walmart MCP response
            if result and result.content:
                products = []
                
                for i, content in enumerate(result.content[:max_results]):
                    try:
                        product_text = content.text if hasattr(content, 'text') else str(content)
                        
                        # Try to parse as JSON if possible
                        try:
                            product_data = json.loads(product_text)
                        except:
                            # If not JSON, treat as plain text
                            product_data = {"raw": product_text}
                        
                        # Normalize Walmart data to GANGU format
                        products.append({
                            "product_name": product_data.get("name") or product_data.get("title", "Unknown Product"),
                            "price": self._format_price(product_data.get("price")),
                            "url": product_data.get("url") or product_data.get("productUrl", ""),
                            "rating": self._format_rating(product_data.get("rating")),
                            "id": product_data.get("id") or product_data.get("productId", ""),
                            "image": product_data.get("image") or product_data.get("imageUrl", ""),
                            "availability": self._format_availability(product_data.get("availability")),
                            "brand": product_data.get("brand", ""),
                            "savings": product_data.get("savings", "")
                        })
                    except Exception as e:
                        print(f"⚠️ Could not parse product {i+1}: {e}")
                        continue
                
                if products:
                    print(f"✅ Found {len(products)} products on Walmart")
                    return {
                        "found": True,
                        "products": products,
                        "platform": "Walmart",
                        "query": product_name
                    }
                else:
                    return {
                        "found": False,
                        "products": [],
                        "platform": "Walmart",
                        "error": "Could not parse products"
                    }
            else:
                return {
                    "found": False,
                    "products": [],
                    "platform": "Walmart",
                    "error": "No products returned"
                }
                
        except Exception as e:
            print(f"❌ Error searching Walmart: {e}")
            import traceback
            traceback.print_exc()
            return {
                "found": False,
                "products": [],
                "platform": "Walmart",
                "error": str(e)
            }
    
    def _format_price(self, price) -> str:
        """Format price to standard string"""
        if price is None:
            return "Check on Walmart"
        
        if isinstance(price, (int, float)):
            return f"${price:.2f}"
        
        return str(price)
    
    def _format_rating(self, rating) -> str:
        """Format rating to standard string"""
        if rating is None:
            return "N/A"
        
        if isinstance(rating, (int, float)):
            return f"{rating:.1f}/5"
        
        return str(rating)
    
    def _format_availability(self, availability) -> str:
        """Format availability to standard string"""
        if availability is None:
            return "Check availability"
        
        if isinstance(availability, bool):
            return "In Stock" if availability else "Out of Stock"
        
        return str(availability)


# Test function
async def test_walmart_client():
    """Test the Walmart MCP Client"""
    client = WalmartMCPClient()
    
    try:
        # Test search
        print("\n🔍 Testing Walmart search...")
        result = await client.search_product("chickpeas")
        print(f"\n📦 Search Result:")
        print(json.dumps(result, indent=2))
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
    finally:
        await client.disconnect()


if __name__ == "__main__":
    print("🚀 Walmart MCP Client Test")
    print("=" * 60)
    asyncio.run(test_walmart_client())
