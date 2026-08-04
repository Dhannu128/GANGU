from mcp.server.fastmcp import FastMCP
import random
import time

# Create a Swiggy Mock Server
mcp = FastMCP("Swiggy_Instamart_Mock")

# Local Mock Database
CATALOG = {
    "milk": ("Amul Taaza Toned Milk 1 L", 48.0, 4.4, "10 minutes", "https://www.swiggy.com/instamart/search?query=amul+milk"),
    "bread": ("Britannia 100% Whole Wheat Bread", 40.0, 4.3, "12 minutes", "https://www.swiggy.com/instamart/search?query=bread"),
    "atta": ("Aashirvaad Whole Wheat Atta 5 kg", 285.0, 4.6, "15 minutes", "https://www.swiggy.com/instamart/search?query=atta"),
    "paneer": ("Amul Fresh Paneer 200 g", 90.0, 4.6, "12 minutes", "https://www.swiggy.com/instamart/search?query=paneer"),
    "chocolate": ("Cadbury Dairy Milk 150 g", 95.0, 4.7, "10 minutes", "https://www.swiggy.com/instamart/search?query=dairy+milk"),
    "tea": ("Tata Tea Premium 500 g", 240.0, 4.5, "12 minutes", "https://www.swiggy.com/instamart/search?query=tata+tea"),
    "chai": ("Tata Tea Premium 500 g", 240.0, 4.5, "12 minutes", "https://www.swiggy.com/instamart/search?query=tata+tea"),
}

mock_cart = []

@mcp.tool("search_products")
def search_products(query: str, max_results: int = 5) -> dict:
    """Search for a product on Swiggy Instamart"""
    key = query.lower().strip()
    
    products = []
    
    # Exact match or fuzzy match
    for cat_key, entry in CATALOG.items():
        if key in cat_key or cat_key in key:
            products.append({
                "product_name": entry[0],
                "price": entry[1],
                "rating": str(entry[2]),
                "url": entry[4],
                "platform": "Swiggy",
                "availability": "Available on Instamart",
                "delivery_time": entry[3]
            })
            
    if not products:
        # Fallback for demo
        price = round((len(query) % 7 + 2) * 25 + 50, 0)
        products.append({
            "product_name": f"Swiggy Instamart {query.strip().title()}",
            "price": price,
            "rating": "4.3",
            "url": f"https://www.swiggy.com/instamart/search?query={query.replace(' ', '+')}",
            "platform": "Swiggy",
            "availability": "Available on Instamart",
            "delivery_time": "10 minutes"
        })
        
    return {
        "found": len(products) > 0,
        "query": query,
        "platform": "Swiggy",
        "products": products[:max_results]
    }

@mcp.tool("get_food_cart")
def get_food_cart() -> dict:
    """Get the current cart"""
    total = sum([item["price"] * item["quantity"] for item in mock_cart])
    return {
        "cart_id": "cart_12345",
        "items": mock_cart,
        "total_amount": total,
        "delivery_fee": 15.0 if total > 0 else 0.0,
        "status": "active"
    }

@mcp.tool("update_food_cart")
def update_food_cart(product_name: str, price: float, quantity: int = 1) -> dict:
    """Update cart by adding or modifying an item"""
    global mock_cart
    
    found = False
    for item in mock_cart:
        if item["product_name"] == product_name:
            item["quantity"] += quantity
            found = True
            break
            
    if not found:
        mock_cart.append({
            "product_name": product_name,
            "price": price,
            "quantity": quantity
        })
        
    return get_food_cart()

@mcp.tool("place_food_order")
def place_food_order(address: str) -> dict:
    """Place an order with the current cart"""
    global mock_cart
    
    if not mock_cart:
        return {"success": False, "error": "Cart is empty"}
        
    order_id = f"SWIGGY_{random.randint(10000, 99999)}"
    total = sum([item["price"] * item["quantity"] for item in mock_cart]) + 15.0
    
    # Empty cart after order
    mock_cart = []
    
    return {
        "success": True,
        "order_id": order_id,
        "total_paid": total,
        "status": "placed",
        "estimated_delivery": "10-15 minutes",
        "address": address
    }

if __name__ == "__main__":
    print("Starting Swiggy Mock MCP Server over SSE at http://localhost:8001/sse")
    # Using port 8001 to avoid conflict with GANGU API on port 8000
    mcp.settings.port = 8001
    mcp.run("sse")
