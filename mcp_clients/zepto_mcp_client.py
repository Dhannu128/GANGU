"""
Zepto MCP Client - Interface for GANGU Search Agent
Connects to the Zepto MCP server to search products and get pricing info
"""
import asyncio
import json
from contextlib import AsyncExitStack
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import os
import re
import sys


def _configure_utf8_console() -> None:
    """Keep MCP diagnostics from crashing on Windows' legacy console encoding."""
    if sys.platform != "win32":
        return
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure:
            try:
                reconfigure(encoding="utf-8", errors="replace")
            except (AttributeError, ValueError):
                pass


_configure_utf8_console()


def classify_order_message(message: str) -> dict:
    """Convert the text-only upstream MCP response into a safe state.

    A tool call completing is not the same as an order completing. In
    particular, OTP prompts and an already-running workflow must never be
    reported as successful purchases.
    """
    normalized = (message or "").strip().lower()
    if not normalized:
        return {"success": False, "status": "failed", "error": "Empty MCP response"}
    if "waiting for login otp" in normalized or "provide the login otp" in normalized:
        return {"success": False, "status": "login_otp_required", "requires_otp": True}
    if "waiting for payment otp" in normalized or "provide the payment otp" in normalized:
        return {"success": False, "status": "payment_otp_required", "requires_otp": True}
    if "order already in progress" in normalized:
        return {"success": False, "status": "in_progress"}
    if normalized.startswith("error:") or normalized.startswith("failed") or "could not" in normalized:
        return {"success": False, "status": "failed", "error": message}
    placed = bool(re.search(r"\border (?:has been )?placed\b|\border placed\b", normalized))
    if placed:
        return {"success": True, "status": "completed"}
    return {"success": False, "status": "pending"}

# Product catalog from Zepto MCP Server
ZEPTO_PRODUCT_CATALOG = {
    "onion": "https://www.zepto.com/pn/fresh-onion/pvid/5b5c1960-d2d1-4528-8a74-bc7280174071",
    "potato": "https://www.zepto.com/pn/potato/pvid/f72c0479-1ae2-44fd-a65f-ca569d4f8c72",
    "tomato": "https://www.zepto.com/pn/tomato/pvid/d34f8cf4-5876-40ef-8ea5-cd2a31b4db39",
    "dal": "https://www.zepto.com/pn/popular-essentials-toor-dal/pvid/870056e6-aad4-43e6-8e38-e757dc2b028c",
    "rice": "https://www.zepto.com/pn/steamed-rice/pvid/6b744fa4-f7e0-4cb9-8b3e-3befcf1ecb2d",
    "milk": "https://www.zepto.com/pn/amul-taaza-toned-fresh-milk-pouch/pvid/faabc8db-cb19-4021-9a0f-77e1011baa4c",
    "doodh": "https://www.zepto.com/pn/amul-taaza-toned-fresh-milk-pouch/pvid/faabc8db-cb19-4021-9a0f-77e1011baa4c",
    "amul milk": "https://www.zepto.com/pn/amul-taaza-toned-fresh-milk-pouch/pvid/faabc8db-cb19-4021-9a0f-77e1011baa4c",
    "bread": "https://www.zepto.com/pn/brano-asli-makhan-malai-bread/pvid/dbcf5163-4f13-4f7e-85d0-33563cd03a2b",
    "paneer": "https://www.zepto.com/pn/paneer-tandoori-tikka/pvid/7eb6a978-fd60-4288-a37e-7627312cd8ea",
    "chai": "https://www.zepto.com/pn/adrak-chai/pvid/959a5253-e580-4f44-8236-07ac7ba96bbf",
    "tea": "https://www.zepto.com/pn/adrak-chai/pvid/959a5253-e580-4f44-8236-07ac7ba96bbf",  # Same as chai
    "coffee": "https://www.zepto.com/pn/iced-americano/pvid/1f0d5ca8-8cb2-4499-b326-27654a68b6c7",
    "eggs": "https://www.zepto.com/pn/bulls-eye-egg-2pcs/pvid/4b4962cb-3ba0-4ff8-8764-7d628d2fd09e",
    "chicken": "https://www.zepto.com/pn/butter-chicken/pvid/695e7401-a412-4698-be8a-c3cfb33521c9",
    "ghee": "https://www.zepto.com/pn/desi-ghee-aloo-paratha-with-dahi/pvid/f58ccd8c-e532-4e4e-b261-79b6290017e5",
    "oil": "https://www.zepto.com/pn/popular-essentials-saunffennel-seeds/pvid/870056e6-aad4-43e6-8e38-e757dc2b028c",
    "sugar": "https://www.zepto.com/pn/masala-chai-no-sugar-500-ml/pvid/3556a247-d92c-47b1-a280-e0eb953de97e",
    "salt": "https://www.zepto.com/pn/popular-essentials-saunffennel-seeds/pvid/870056e6-aad4-43e6-8e38-e757dc2b028c",
    "atta": "https://www.zepto.com/pn/wheat-chapati-pack-of-5/pvid/4b9364e7-fe2f-4f60-a050-66e8716887e9",
    "flour": "https://www.zepto.com/pn/wheat-chapati-pack-of-5/pvid/4b9364e7-fe2f-4f60-a050-66e8716887e9",  # Same as atta
    "besan": "https://www.zepto.com/pn/bhelpuri/pvid/a42c13b4-10d8-4c33-8e11-bbbb3a8f682f",
    "gram flour": "https://www.zepto.com/pn/bhelpuri/pvid/a42c13b4-10d8-4c33-8e11-bbbb3a8f682f",  # Same as besan
    "chana": "https://www.zepto.com/pn/channa-jor-chaat/pvid/a0ee7d1a-fde7-4f27-898c-a1e0eb9bb19a",
    "rajma": "https://www.zepto.com/pn/rajma-masala-rice/pvid/08abb94e-438d-4d42-b914-2130c3a9fcd8",
    "curd": "https://www.zepto.com/pn/plain-curd/pvid/a1a7b157-d40b-41c0-92be-e119a8c77e9a",
    "dahi": "https://www.zepto.com/pn/plain-curd/pvid/a1a7b157-d40b-41c0-92be-e119a8c77e9a",  # Same as curd
    "butter": "https://www.zepto.com/pn/butter-croissant/pvid/37732d9c-b578-461e-9bd2-54bdd92b74d9",
    "cheese": "https://www.zepto.com/pn/garlic-bread-with-cheese-dip/pvid/5b265566-61a3-4660-9e76-5e40643fe81f",
    "papaya": "https://www.zepto.com/pn/papaya/pvid/105c48cc-d5cb-4279-ac58-fe36cc92d51d",
    "banana": "https://www.zepto.com/pn/papaya/pvid/105c48cc-d5cb-4279-ac58-fe36cc92d51d",
    "apple": "https://www.zepto.com/pn/papaya/pvid/105c48cc-d5cb-4279-ac58-fe36cc92d51d",
    "orange": "https://www.zepto.com/pn/papaya/pvid/105c48cc-d5cb-4279-ac58-fe36cc92d51d",
    "mango": "https://www.zepto.com/pn/papaya/pvid/105c48cc-d5cb-4279-ac58-fe36cc92d51d",
    "pomegranate": "https://www.zepto.com/pn/pomegranate-small/pvid/99dd9fd0-1b06-4649-b53f-cf756f60b8ea",
    "strawberry": "https://www.zepto.com/pn/strawberry/pvid/cf8e41c6-8b18-461f-95b4-02876a22edce",
    "grapes": "https://www.zepto.com/pn/papaya/pvid/105c48cc-d5cb-4279-ac58-fe36cc92d51d",
    "cucumber": "https://www.zepto.com/pn/ash-gourd/pvid/aa891942-3ce5-437e-bb11-0120ae085874",
    "carrot": "https://www.zepto.com/pn/beetroot-500-g-combo/pvid/20b3e088-7254-4355-8955-e25ebd552f9e",
    "capsicum": "https://www.zepto.com/pn/ash-gourd/pvid/aa891942-3ce5-437e-bb11-0120ae085874",
    "chocolate": "https://www.zepto.com/pn/cadbury-bournville-rich-cocoa-50-dark-chocolate-bar/pvid/db6c4a25-24fe-49e9-8828-9bea53557aa2",
    # Snacks / chips
    "kurkure": "https://www.zepto.com/pn/kurkure-masala-munch-combo/pvid/bf401859-bcff-42ce-aa90-089679e05d55",
    "masala munch": "https://www.zepto.com/pn/kurkure-masala-munch-combo/pvid/bf401859-bcff-42ce-aa90-089679e05d55",
    "balaji": "https://www.zepto.com/pn/balaji-tomato-wafers/pvid/91fae44c-865d-4bc8-8ac1-bda71ac51292",
    "wafers": "https://www.zepto.com/pn/balaji-tomato-wafers/pvid/91fae44c-865d-4bc8-8ac1-bda71ac51292",
    "tomato wafers": "https://www.zepto.com/pn/balaji-tomato-wafers/pvid/91fae44c-865d-4bc8-8ac1-bda71ac51292",
    "chips": "https://www.zepto.com/pn/balaji-tomato-wafers/pvid/91fae44c-865d-4bc8-8ac1-bda71ac51292",
    # Ice cream
    "ice-cream": "https://www.zepto.com/pn/kwality-walls-vanilla-ice-cream-tub/pvid/02e2974d-901a-42fb-a907-a625aca61029",
    "ice cream": "https://www.zepto.com/pn/kwality-walls-vanilla-ice-cream-tub/pvid/02e2974d-901a-42fb-a907-a625aca61029",
    "icecream": "https://www.zepto.com/pn/kwality-walls-vanilla-ice-cream-tub/pvid/02e2974d-901a-42fb-a907-a625aca61029",
    # Biscuits / cookies
    "biscuit": "https://www.zepto.com/pn/original-choco-fills-by-sunfeast-dark-fantasy-perfect-snack/pvid/b9606e95-79a6-4814-827d-104b680ca81f",
    "biscuits": "https://www.zepto.com/pn/original-choco-fills-by-sunfeast-dark-fantasy-perfect-snack/pvid/b9606e95-79a6-4814-827d-104b680ca81f",
    "cookies": "https://www.zepto.com/pn/original-choco-fills-by-sunfeast-dark-fantasy-perfect-snack/pvid/b9606e95-79a6-4814-827d-104b680ca81f",
    "dark fantasy": "https://www.zepto.com/pn/original-choco-fills-by-sunfeast-dark-fantasy-perfect-snack/pvid/b9606e95-79a6-4814-827d-104b680ca81f",
    # Stationery
    "pen": "https://www.zepto.com/pn/reynolds-vista-retractable-ball-pen-set-5-blue-pens/pvid/39116aa7-1eb6-42fe-9eb8-b45295f0288f",
    "ball pen": "https://www.zepto.com/pn/reynolds-vista-retractable-ball-pen-set-5-blue-pens/pvid/39116aa7-1eb6-42fe-9eb8-b45295f0288f",
    "copy": "https://www.zepto.com/pn/classmate-single-line-spiral-notebook-160-pages-27-x-20-cm-assorted-designs/pvid/83161c72-c063-4dbe-a69d-107abc5b6f25",
    "notebook": "https://www.zepto.com/pn/classmate-single-line-spiral-notebook-160-pages-27-x-20-cm-assorted-designs/pvid/83161c72-c063-4dbe-a69d-107abc5b6f25",
    "spiral notebook": "https://www.zepto.com/pn/classmate-single-line-spiral-notebook-160-pages-27-x-20-cm-assorted-designs/pvid/83161c72-c063-4dbe-a69d-107abc5b6f25",
    "classmate": "https://www.zepto.com/pn/classmate-single-line-spiral-notebook-160-pages-27-x-20-cm-assorted-designs/pvid/83161c72-c063-4dbe-a69d-107abc5b6f25",
    # Soft drinks
    "soft drinks": "https://www.zepto.com/pn/sprite-lemon-soft-drink-carbonated-beverage/pvid/d3159067-a3e8-44aa-a215-ff937c6da7da",
    "soft drink": "https://www.zepto.com/pn/sprite-lemon-soft-drink-carbonated-beverage/pvid/d3159067-a3e8-44aa-a215-ff937c6da7da",
    "cold drink": "https://www.zepto.com/pn/sprite-lemon-soft-drink-carbonated-beverage/pvid/d3159067-a3e8-44aa-a215-ff937c6da7da",
    "cold drinks": "https://www.zepto.com/pn/sprite-lemon-soft-drink-carbonated-beverage/pvid/d3159067-a3e8-44aa-a215-ff937c6da7da",
    "sprite": "https://www.zepto.com/pn/sprite-lemon-soft-drink-carbonated-beverage/pvid/d3159067-a3e8-44aa-a215-ff937c6da7da",
    # Watermelon
    "water melon": "https://www.zepto.com/pn/watermelon-saraswati/pvid/7bbe801b-d489-49dd-9368-ab4e039eb3a9",
    "watermelon": "https://www.zepto.com/pn/watermelon-saraswati/pvid/7bbe801b-d489-49dd-9368-ab4e039eb3a9",
    "tarbooj": "https://www.zepto.com/pn/watermelon-saraswati/pvid/7bbe801b-d489-49dd-9368-ab4e039eb3a9",
}


class ZeptoMCPClient:
    """Client to connect to Zepto MCP Server"""
    
    def __init__(self, server_script_path: str):
        """
        Initialize Zepto MCP Client
        
        Args:
            server_script_path: Path to zepto_mcp_server.py
        """
        self.server_script_path = server_script_path
        self.session = None
        self.exit_stack = None
        
    async def connect(self):
        """Connect to the Zepto MCP server"""
        if self.session:
            return  # Already connected
            
        self.exit_stack = AsyncExitStack()
        
        # Get Python executable from virtual environment if available
        python_exe = sys.executable
        
        # Server parameters
        server_params = StdioServerParameters(
            command=python_exe,
            args=[self.server_script_path],
            env={
                **os.environ,
                "ZEPTO_PHONE_NUMBER": os.getenv("ZEPTO_PHONE_NUMBER", ""),
                "ZEPTO_DEFAULT_ADDRESS": os.getenv("ZEPTO_DEFAULT_ADDRESS", "")
            }
        )
        
        # Start client
        stdio_transport = await self.exit_stack.enter_async_context(
            stdio_client(server_params)
        )
        
        stdio, write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(
            ClientSession(stdio, write)
        )
        
        # Initialize session
        await self.session.initialize()
        
        print("✅ Connected to Zepto MCP Server")
        
        # List available tools
        tools_result = await self.session.list_tools()
        print(f"📋 Available tools: {[tool.name for tool in tools_result.tools]}")
        
    async def disconnect(self):
        """Disconnect from the Zepto MCP server"""
        if self.exit_stack:
            await self.exit_stack.aclose()
            self.session = None
            self.exit_stack = None
            print("✅ Disconnected from Zepto MCP Server")
    
    async def search_product(self, product_name: str) -> dict:
        """
        Search for a product in Zepto catalog
        
        Args:
            product_name: Name of the product to search
            
        Returns:
            dict with product info: {
                "found": bool,
                "product_name": str,
                "url": str,
                "platform": "Zepto",
                "estimated_price": str (placeholder),
                "availability": "Available"
            }
        """
        if not self.session:
            await self.connect()
        
        # Normalize product name
        product_key = product_name.lower().strip()
        
        # Check if product exists in catalog
        if product_key in ZEPTO_PRODUCT_CATALOG:
            print(f"✅ Found '{product_name}' in Zepto catalog")
            return {
                "found": True,
                "product_name": product_name,
                "url": ZEPTO_PRODUCT_CATALOG[product_key],
                "platform": "Zepto",
                "price": "REAL_PRICE_FROM_WEBSITE",  # Will be fetched by order automation
                "availability": "CHECK_AT_ORDER_TIME",
                "delivery_time": "10-15 minutes"
            }
        else:
            # Fuzzy search - check if any catalog item contains the search term
            for catalog_item, url in ZEPTO_PRODUCT_CATALOG.items():
                if product_key in catalog_item or catalog_item in product_key:
                    print(f"✅ Fuzzy matched '{product_name}' -> '{catalog_item}' in Zepto")
                    return {
                        "found": True,
                        "product_name": catalog_item,
                        "url": url,
                        "platform": "Zepto",
                        "price": "REAL_PRICE_FROM_WEBSITE",
                        "availability": "CHECK_AT_ORDER_TIME",
                        "delivery_time": "10-15 minutes",
                        "matched_term": catalog_item
                    }
            
            print(f"❌ '{product_name}' NOT in Zepto catalog (searched: {product_key})")
            return {
                "found": False,
                "product_name": product_name,
                "platform": "Zepto",
                "error": f"REAL_DATA_ONLY: Product '{product_name}' not in catalog. Add to ZEPTO_PRODUCT_CATALOG to enable.",
                "searched_key": product_key
            }
    
    async def search_multiple_products(self, product_names: list[str]) -> dict:
        """
        Search for multiple products
        
        Args:
            product_names: List of product names to search
            
        Returns:
            dict with results for each product
        """
        results = []
        for product_name in product_names:
            result = await self.search_product(product_name)
            results.append(result)
        
        return {
            "platform": "Zepto",
            "total_products": len(product_names),
            "found_count": sum(1 for r in results if r.get("found")),
            "results": results
        }

    async def _call_text_tool(self, name: str, arguments: dict) -> dict:
        if not self.session:
            await self.connect()
        result = await self.session.call_tool(name, arguments)
        if not result.content:
            return {"success": False, "status": "failed", "error": "No content in response"}
        content = result.content[0]
        message = content.text if hasattr(content, "text") else str(content)
        return {"message": message, "raw_result": str(result), **classify_order_message(message)}

    async def start_zepto_order(
        self,
        product_name: str,
        item_url: str | None = None,
        phone_number: str | None = None,
        address: str | None = None,
    ) -> dict:
        """
        Start a Zepto order using the MCP server tool.

        If `item_url` is provided, the MCP server bypasses its built-in
        cafe catalog and orders directly from that URL — required for
        grocery items not in the cafe catalog (e.g. chocolate).
        """
        if not self.session:
            await self.connect()

        try:
            args: dict = {"product_name": product_name}
            if item_url:
                args["item_url"] = item_url
            if phone_number:
                args["phone_number"] = phone_number
            if address:
                args["address"] = address
            return await self._call_text_tool("start_zepto_order", args)
                
        except Exception as e:
            return {"success": False, "status": "failed", "error": str(e)}

    async def submit_login_otp(self, otp: str) -> dict:
        """Continue an order in the same MCP session after login OTP."""
        return await self._call_text_tool("submit_login_otp", {"otp": otp})

    async def submit_payment_otp(self, otp: str) -> dict:
        """Continue an order in the same MCP session after payment OTP."""
        return await self._call_text_tool("submit_payment_otp", {"otp": otp})

    async def stop_order(self) -> dict:
        """Cancel the active upstream workflow in this MCP session."""
        return await self._call_text_tool("stop_order", {})
    
    async def get_server_status(self) -> dict:
        """Get the status of the MCP server"""
        if not self.session:
            return {"connected": False, "message": "Not connected to server"}
        
        try:
            # Call get_order_status tool
            result = await self.session.call_tool("get_order_status", {})
            return {
                "connected": True,
                "server_status": result.content[0].text if result.content else "Unknown"
            }
        except Exception as e:
            return {
                "connected": True,
                "error": str(e)
            }


async def test_zepto_mcp_client():
    """Test the Zepto MCP client"""
    print("=" * 60)
    print("Testing Zepto MCP Client for GANGU")
    print("=" * 60)
    
    # Get script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Path to zepto MCP server (you need to clone the repo first)
    server_path = os.path.join(script_dir, "zepto-cafe-mcp", "zepto_mcp_server.py")
    
    if not os.path.exists(server_path):
        print(f"❌ Zepto MCP server not found at: {server_path}")
        print("\n📋 Setup Instructions:")
        print("1. Clone the repo:")
        print("   cd", script_dir)
        print("   git clone https://github.com/proddnav/zepto-cafe-mcp.git")
        print("\n2. Install dependencies:")
        print("   pip install playwright mcp python-dotenv")
        print("   python -m playwright install firefox")
        print("\n3. Set environment variables:")
        print("   set ZEPTO_PHONE_NUMBER=your_phone_number")
        print("   set ZEPTO_DEFAULT_ADDRESS=your_address")
        print("\n4. Run this test again")
        return
    
    # Create client
    client = ZeptoMCPClient(server_path)
    
    try:
        # Test 1: Connect to server
        print("\n📡 Test 1: Connecting to Zepto MCP Server...")
        await client.connect()
        
        # Test 2: Search single product
        print("\n🔍 Test 2: Search for 'onion'...")
        result = await client.search_product("onion")
        print(json.dumps(result, indent=2))
        
        # Test 3: Search multiple products
        print("\n🔍 Test 3: Search for multiple products...")
        products = ["chana", "dal", "rice", "milk"]
        results = await client.search_multiple_products(products)
        print(json.dumps(results, indent=2))
        
        # Test 4: Search product not in catalog
        print("\n🔍 Test 4: Search for product not in catalog...")
        result = await client.search_product("xyz123notfound")
        print(json.dumps(result, indent=2))
        
        # Test 5: Get server status
        print("\n📊 Test 5: Get server status...")
        status = await client.get_server_status()
        print(json.dumps(status, indent=2))
        
        print("\n✅ All tests completed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Disconnect
        await client.disconnect()


if __name__ == "__main__":
    asyncio.run(test_zepto_mcp_client())
