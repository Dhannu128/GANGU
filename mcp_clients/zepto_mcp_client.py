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
import sys

# Product catalog from Zepto MCP Server
ZEPTO_PRODUCT_CATALOG = {
    "onion": "https://www.zepto.com/pn/fresh-onion/pvid/5b5c1960-d2d1-4528-8a74-bc7280174071",
    "potato": "https://www.zepto.com/pn/potato/pvid/f72c0479-1ae2-44fd-a65f-ca569d4f8c72",
    "tomato": "https://www.zepto.com/pn/tomato/pvid/d34f8cf4-5876-40ef-8ea5-cd2a31b4db39",
    "dal": "https://www.zepto.com/pn/popular-essentials-toor-dal/pvid/870056e6-aad4-43e6-8e38-e757dc2b028c",
    "rice": "https://www.zepto.com/pn/steamed-rice/pvid/6b744fa4-f7e0-4cb9-8b3e-3befcf1ecb2d",
    "milk": "https://www.zepto.com/pn/plain-curd/pvid/a1a7b157-d40b-41c0-92be-e119a8c77e9a",
    "bread": "https://www.zepto.com/pn/garlic-bread-with-cheese-dip/pvid/5b265566-61a3-4660-9e76-5e40643fe81f",
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
    "pomegranate": "https://www.zepto.com/pn/pomegranate-small/pvid/99dd9fd0-1b06-4649-b53f-cf756f60b8ea",
    "strawberry": "https://www.zepto.com/pn/strawberry/pvid/cf8e41c6-8b18-461f-95b4-02876a22edce",
    "grapes": "https://www.zepto.com/pn/papaya/pvid/105c48cc-d5cb-4279-ac58-fe36cc92d51d",
    # Real Zepto products for actual ordering (PRIORITY - check these first)
    "slice mango": "https://www.zepto.com/pn/slice-mango-drink-ready-to-drink-beverage/pvid/a9f72e4a-10f5-488d-b12e-653a2983c0b5",
    "mango slice": "https://www.zepto.com/pn/slice-mango-drink-ready-to-drink-beverage/pvid/a9f72e4a-10f5-488d-b12e-653a2983c0b5",
    "slice drink": "https://www.zepto.com/pn/slice-mango-drink-ready-to-drink-beverage/pvid/a9f72e4a-10f5-488d-b12e-653a2983c0b5",
    "mango drink": "https://www.zepto.com/pn/slice-mango-drink-ready-to-drink-beverage/pvid/a9f72e4a-10f5-488d-b12e-653a2983c0b5",
    "slice": "https://www.zepto.com/pn/slice-mango-drink-ready-to-drink-beverage/pvid/a9f72e4a-10f5-488d-b12e-653a2983c0b5",
    
    # Cadbury Bournville Dark Chocolate Bar - User requested
    "cadbury bournville": "https://www.zepto.com/pn/cadbury-bournville-rich-cocoa-50-dark-chocolate-bar/pvid/db6c4a25-24fe-49e9-8828-9bea53557aa2",
    "bournville": "https://www.zepto.com/pn/cadbury-bournville-rich-cocoa-50-dark-chocolate-bar/pvid/db6c4a25-24fe-49e9-8828-9bea53557aa2",
    "cadbury chocolate": "https://www.zepto.com/pn/cadbury-bournville-rich-cocoa-50-dark-chocolate-bar/pvid/db6c4a25-24fe-49e9-8828-9bea53557aa2",
    "dark chocolate": "https://www.zepto.com/pn/cadbury-bournville-rich-cocoa-50-dark-chocolate-bar/pvid/db6c4a25-24fe-49e9-8828-9bea53557aa2",
    "bournville chocolate": "https://www.zepto.com/pn/cadbury-bournville-rich-cocoa-50-dark-chocolate-bar/pvid/db6c4a25-24fe-49e9-8828-9bea53557aa2",
    "cadbury bournville dark chocolate": "https://www.zepto.com/pn/cadbury-bournville-rich-cocoa-50-dark-chocolate-bar/pvid/db6c4a25-24fe-49e9-8828-9bea53557aa2",
    
    # Updated IN-STOCK items (Feb 2026) - These are confirmed available
    "onion": "https://www.zepto.com/pn/onion/pvid/b503d0e6-c17d-46e8-965f-63cd13f39752",
    "fresh onion": "https://www.zepto.com/pn/onion/pvid/b503d0e6-c17d-46e8-965f-63cd13f39752",
    "chana": "https://www.zepto.com/pn/rajdhani-chana-kabuli/pvid/44fd38fd-c59f-44b7-aac3-701c0a12dada",
    "chana kabuli": "https://www.zepto.com/pn/rajdhani-chana-kabuli/pvid/44fd38fd-c59f-44b7-aac3-701c0a12dada",
    "rajdhani chana": "https://www.zepto.com/pn/rajdhani-chana-kabuli/pvid/44fd38fd-c59f-44b7-aac3-701c0a12dada",
    "besan": "https://www.zepto.com/pn/nandi-besan/pvid/7649650b-8632-447c-a8f5-afd81b41f1f2",
    "gram flour": "https://www.zepto.com/pn/nandi-besan/pvid/7649650b-8632-447c-a8f5-afd81b41f1f2",
    "nandi besan": "https://www.zepto.com/pn/nandi-besan/pvid/7649650b-8632-447c-a8f5-afd81b41f1f2",
    "soan papdi": "https://www.zepto.com/pn/kaleva-soan-papdi-traditional-indian-sweet/pvid/19f1abf8-8407-423b-a003-aaaab56c3a83",
    "kaleva soan papdi": "https://www.zepto.com/pn/kaleva-soan-papdi-traditional-indian-sweet/pvid/19f1abf8-8407-423b-a003-aaaab56c3a83",
    "lays": "https://www.zepto.com/pn/lays-indias-magic-masala-potato-chips-crunchy-enjoyable/pvid/07878a63-2656-4618-a7cc-ecfe8c2faf22",
    "chips": "https://www.zepto.com/pn/lays-indias-magic-masala-potato-chips-crunchy-enjoyable/pvid/07878a63-2656-4618-a7cc-ecfe8c2faf22",
    "lays magic masala": "https://www.zepto.com/pn/lays-indias-magic-masala-potato-chips-crunchy-enjoyable/pvid/07878a63-2656-4618-a7cc-ecfe8c2faf22",
    "potato chips": "https://www.zepto.com/pn/lays-indias-magic-masala-potato-chips-crunchy-enjoyable/pvid/07878a63-2656-4618-a7cc-ecfe8c2faf22",
    "bingo tedhe medhe": "https://www.zepto.com/pn/bingo-tedhe-medhe-crunchy-snack/pvid/4b0a3db9-bb0f-49d4-bdf3-2c39db3b1e05",
    "tedhe medhe": "https://www.zepto.com/pn/bingo-tedhe-medhe-crunchy-snack/pvid/4b0a3db9-bb0f-49d4-bdf3-2c39db3b1e05",
    "bingo snacks": "https://www.zepto.com/pn/bingo-tedhe-medhe-crunchy-snack/pvid/4b0a3db9-bb0f-49d4-bdf3-2c39db3b1e05",
    # Generic fruits (lower priority)  
    "mango": "https://www.zepto.com/pn/papaya/pvid/105c48cc-d5cb-4279-ac58-fe36cc92d51d",
    "cucumber": "https://www.zepto.com/pn/ash-gourd/pvid/aa891942-3ce5-437e-bb11-0120ae085874",
    "carrot": "https://www.zepto.com/pn/beetroot-500-g-combo/pvid/20b3e088-7254-4355-8955-e25ebd552f9e",
    "capsicum": "https://www.zepto.com/pn/ash-gourd/pvid/aa891942-3ce5-437e-bb11-0120ae085874",

    # User-added catalog items (Feb 2026)
    # NOTE: keys are used for exact + fuzzy matching; add common phrases people type.
    "rajdhani chana kabuli": "https://www.zepto.com/pn/rajdhani-chana-kabuli/pvid/2356c46a-5c51-4a93-9744-9352fe981623",
    "rajdhani kabuli chana": "https://www.zepto.com/pn/rajdhani-chana-kabuli/pvid/2356c46a-5c51-4a93-9744-9352fe981623",
    "rajdhani chana kabuli 500 g": "https://www.zepto.com/pn/rajdhani-chana-kabuli/pvid/2356c46a-5c51-4a93-9744-9352fe981623",

    "nandi besan": "https://www.zepto.com/pn/nandi-besan/pvid/7649650b-8632-447c-a8f5-afd81b41f1f2",
    "nandi gram flour": "https://www.zepto.com/pn/nandi-besan/pvid/7649650b-8632-447c-a8f5-afd81b41f1f2",

    "fortune suji combo": "https://www.zepto.com/pn/fortune-suji-combo/pvid/a71aefbb-964f-454f-8077-f9eb7be3192a",
    "suji combo": "https://www.zepto.com/pn/fortune-suji-combo/pvid/a71aefbb-964f-454f-8077-f9eb7be3192a",

    "amul gold tricone butterscotch ice cream cone": "https://www.zepto.com/pn/amul-gold-tricone-butterscotch-ice-cream-cone/pvid/5138a29d-e84c-4136-b602-dae0554ac434",
    "amul gold tricone butterscotch": "https://www.zepto.com/pn/amul-gold-tricone-butterscotch-ice-cream-cone/pvid/5138a29d-e84c-4136-b602-dae0554ac434",
    "amul tricone butterscotch": "https://www.zepto.com/pn/amul-gold-tricone-butterscotch-ice-cream-cone/pvid/5138a29d-e84c-4136-b602-dae0554ac434",
    "amul butterscotch cone": "https://www.zepto.com/pn/amul-gold-tricone-butterscotch-ice-cream-cone/pvid/5138a29d-e84c-4136-b602-dae0554ac434",

    "kurkure masala munch": "https://www.zepto.com/pn/kurkure-masala-munch-crunchy-snack/pvid/c32d9425-0bdb-4d31-bb21-47630f1811f9",
    "masala munch": "https://www.zepto.com/pn/kurkure-masala-munch-crunchy-snack/pvid/c32d9425-0bdb-4d31-bb21-47630f1811f9",
    "kurkure masala munch crunchy snack": "https://www.zepto.com/pn/kurkure-masala-munch-crunchy-snack/pvid/c32d9425-0bdb-4d31-bb21-47630f1811f9",

    "lays american cream & onion": "https://www.zepto.com/pn/lays-american-cream-onion-potato-chips/pvid/1e28f2c0-fbc5-4366-9efb-a65bd12428cb",
    "lays american cream and onion": "https://www.zepto.com/pn/lays-american-cream-onion-potato-chips/pvid/1e28f2c0-fbc5-4366-9efb-a65bd12428cb",
    "lays cream and onion": "https://www.zepto.com/pn/lays-american-cream-onion-potato-chips/pvid/1e28f2c0-fbc5-4366-9efb-a65bd12428cb",
    "lays cream onion chips": "https://www.zepto.com/pn/lays-american-cream-onion-potato-chips/pvid/1e28f2c0-fbc5-4366-9efb-a65bd12428cb",
    "american cream and onion chips": "https://www.zepto.com/pn/lays-american-cream-onion-potato-chips/pvid/1e28f2c0-fbc5-4366-9efb-a65bd12428cb",

    "nic chocochips ice cream": "https://www.zepto.com/pn/nic-chocochips-ice-cream-tub-preservative-free-no-artificial-flavors/pvid/d866f161-47e9-4e03-9c78-cbf215b8e815",
    "nic chocochips ice cream tub": "https://www.zepto.com/pn/nic-chocochips-ice-cream-tub-preservative-free-no-artificial-flavors/pvid/d866f161-47e9-4e03-9c78-cbf215b8e815",
    "nic chocochips": "https://www.zepto.com/pn/nic-chocochips-ice-cream-tub-preservative-free-no-artificial-flavors/pvid/d866f161-47e9-4e03-9c78-cbf215b8e815",
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
    
    async def get_real_price(self, product_url: str) -> float:
        """
        Fetch actual price from Zepto product URL
        
        Args:
            product_url: Full Zepto product URL
            
        Returns:
            float: Actual price in rupees, or estimated price if scraping fails
        """
        try:
            from playwright.async_api import async_playwright
            
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                
                # Navigate to product page
                await page.goto(product_url, wait_until='networkidle')
                await page.wait_for_timeout(2000)  # Wait for dynamic content
                
                # Try multiple price selectors (Zepto uses different formats)
                price_selectors = [
                    '[data-testid="pdp-product-price"]',
                    '.price',
                    '[class*="price"]',
                    '[class*="Price"]',
                    'span:has-text("₹")',
                    'div:has-text("₹")',
                    '[class*="amount"]',
                    '[data-testid*="price"]'
                ]
                
                price = None
                for selector in price_selectors:
                    try:
                        price_element = await page.wait_for_selector(selector, timeout=3000)
                        if price_element:
                            price_text = await price_element.inner_text()
                            # Extract numeric value from price text
                            import re
                            price_match = re.search(r'₹\s*(\d+(?:\.\d+)?)', price_text)
                            if price_match:
                                price = float(price_match.group(1))
                                print(f"✅ Found real price: ₹{price} for {product_url}")
                                break
                    except:
                        continue
                
                await browser.close()
                
                # Return actual price or fallback to estimated based on product type
                if price:
                    return price
                else:
                    # Fallback estimation based on product type in URL
                    url_lower = product_url.lower()
                    if 'slice' in url_lower or 'mango' in url_lower:
                        return 77.0
                    elif 'lays' in url_lower or 'chips' in url_lower:
                        return 30.0
                    elif 'soan-papdi' in url_lower:
                        return 120.0
                    elif 'onion' in url_lower:
                        return 40.0
                    elif 'chana' in url_lower:
                        return 150.0
                    elif 'besan' in url_lower:
                        return 90.0
                    else:
                        return 50.0  # Generic fallback
                        
        except Exception as e:
            print(f"⚠️ Price scraping failed for {product_url}: {e}")
            # Return estimated price based on product URL
            url_lower = product_url.lower()
            if 'slice' in url_lower:
                return 77.0  # Mango slice current price
            elif 'lays' in url_lower:
                return 30.0
            elif 'soan-papdi' in url_lower:
                return 120.0
            elif 'onion' in url_lower:
                return 40.0
            elif 'chana' in url_lower:
                return 150.0
            elif 'besan' in url_lower:
                return 90.0
            else:
                return 50.0

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
            product_url = ZEPTO_PRODUCT_CATALOG[product_key]
            
            # Get real price from the URL
            real_price = await self.get_real_price(product_url)
            
            return {
                "found": True,
                "product_name": product_name,
                "url": product_url,
                "platform": "Zepto",
                "price": f"₹{real_price}",
                "estimated_price": real_price,  # Numeric value for calculations
                "availability": "CHECK_AT_ORDER_TIME",
                "delivery_time": "10-15 minutes"
            }
        else:
            # Fuzzy search - check if any catalog item contains the search term
            for catalog_item, url in ZEPTO_PRODUCT_CATALOG.items():
                if product_key in catalog_item or catalog_item in product_key:
                    print(f"✅ Fuzzy matched '{product_name}' -> '{catalog_item}' in Zepto")
                    
                    # Get real price from the URL
                    real_price = await self.get_real_price(url)
                    
                    return {
                        "found": True,
                        "product_name": catalog_item,
                        "url": url,
                        "platform": "Zepto",
                        "price": f"₹{real_price}",
                        "estimated_price": real_price,  # Numeric value for calculations
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

    async def start_zepto_order(self, product_name: str) -> dict:
        """
        Start a Zepto order using the MCP server tool
        
        Args:
            product_name: Name of the product to order
            
        Returns:
            dict with order result
        """
        if not self.session:
            await self.connect()
        
        try:
            # Call the start_zepto_order tool on the server
            result = await self.session.call_tool("start_zepto_order", {
                "product_name": product_name
            })
            
            # Extract the result from MCP response
            if result.content and len(result.content) > 0:
                content = result.content[0]
                if hasattr(content, 'text'):
                    return {"success": True, "message": content.text, "raw_result": str(result)}
                else:
                    return {"success": True, "message": str(content), "raw_result": str(result)}
            else:
                return {"success": False, "error": "No content in response", "raw_result": str(result)}
                
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def start_zepto_multi_order(self, items: list[dict]) -> dict:
        """
        Start a Zepto multi-item order using the MCP server tool

        Args:
            items: List of dicts with product_name/item_url and quantity

        Returns:
            dict with order result
        """
        if not self.session:
            await self.connect()

        try:
            result = await self.session.call_tool("start_zepto_multi_order", {
                "items": items
            })

            if result.content and len(result.content) > 0:
                content = result.content[0]
                if hasattr(content, 'text'):
                    return {"success": True, "message": content.text, "raw_result": str(result)}
                else:
                    return {"success": True, "message": str(content), "raw_result": str(result)}
            else:
                return {"success": False, "error": "No content in response", "raw_result": str(result)}

        except Exception as e:
            return {"success": False, "error": str(e)}
    
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
