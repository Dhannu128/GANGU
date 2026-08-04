"""
Swiggy Instamart MCP Client - Interface for GANGU Search Agent
Connects to Swiggy Instamart MCP Server over HTTP/SSE.
"""
import asyncio
import json
from contextlib import AsyncExitStack
from mcp import ClientSession
from mcp.client.sse import sse_client

class SwiggyMCPClient:
    """Client to search Swiggy Instamart products for GANGU using MCP over SSE."""

    def __init__(self, server_url: str = "http://localhost:8001/sse"):
        self.server_url = server_url
        self.session = None
        self.exit_stack = None

    async def connect(self):
        """Connect to the Swiggy MCP server over SSE"""
        if self.session:
            return
            
        self.exit_stack = AsyncExitStack()
        try:
            # Connect to SSE endpoint
            sse_transport = await self.exit_stack.enter_async_context(
                sse_client(self.server_url)
            )
            self.session = await self.exit_stack.enter_async_context(
                ClientSession(sse_transport[0], sse_transport[1])
            )
            await self.session.initialize()
            print(f"✅ Connected to Swiggy MCP Server at {self.server_url}")
        except Exception as e:
            print(f"⚠️ Failed to connect to Swiggy MCP Server: {e}")
            await self.disconnect()
            raise

    async def disconnect(self):
        """Disconnect from the server"""
        if self.exit_stack:
            try:
                await self.exit_stack.aclose()
            except Exception:
                pass
            self.session = None
            self.exit_stack = None
            print("✅ Disconnected from Swiggy MCP Server")

    async def search_product(self, product_name: str, max_results: int = 5) -> dict:
        """Search for a product using Swiggy MCP tool"""
        if not self.session:
            await self.connect()
            
        try:
            print(f"🔍 Calling Swiggy MCP search for: {product_name}")
            result = await self.session.call_tool(
                "search_products",
                arguments={"query": product_name, "max_results": max_results}
            )
            
            content = result.content[0].text
            return json.loads(content)
        except Exception as e:
            print(f"⚠️ Swiggy MCP search failed: {e}")
            return {"found": False, "error": str(e)}

    # Additional tools for end-to-end checkout flow demo
    async def get_food_cart(self) -> dict:
        if not self.session:
            await self.connect()
        try:
            result = await self.session.call_tool("get_food_cart", arguments={})
            return json.loads(result.content[0].text)
        except Exception as e:
            return {"error": str(e)}

    async def update_food_cart(self, product_name: str, price: float, quantity: int = 1) -> dict:
        if not self.session:
            await self.connect()
        try:
            result = await self.session.call_tool(
                "update_food_cart", 
                arguments={"product_name": product_name, "price": price, "quantity": quantity}
            )
            return json.loads(result.content[0].text)
        except Exception as e:
            return {"error": str(e)}
            
    async def place_food_order(self, address: str) -> dict:
        if not self.session:
            await self.connect()
        try:
            result = await self.session.call_tool(
                "place_food_order", 
                arguments={"address": address}
            )
            return json.loads(result.content[0].text)
        except Exception as e:
            return {"error": str(e)}

async def _test():
    client = SwiggyMCPClient()
    try:
        await client.connect()
        print("\n--- Searching for Paneer ---")
        res = await client.search_product("paneer")
        print(json.dumps(res, indent=2))
        
        if res.get("found"):
            prod = res["products"][0]
            print("\n--- Adding to Cart ---")
            cart_res = await client.update_food_cart(prod["product_name"], prod["price"], 2)
            print(json.dumps(cart_res, indent=2))
            
            print("\n--- Placing Order ---")
            order_res = await client.place_food_order("123 GANGU St, Senior Living")
            print(json.dumps(order_res, indent=2))
            
    finally:
        await client.disconnect()

if __name__ == "__main__":
    asyncio.run(_test())
