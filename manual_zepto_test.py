"""
Manual Zepto Order Test
Run this to see what's happening in browser and manually complete if needed
"""
import asyncio
import sys
import os
from pathlib import Path

# Add zepto-cafe-mcp to path
zepto_path = Path(__file__).parent / "zepto-cafe-mcp"
sys.path.insert(0, str(zepto_path))

async def test_manual_order():
    """Test order with manual browser interaction"""
    from playwright.async_api import async_playwright
    
    print("=" * 80)
    print("🧪 MANUAL ZEPTO ORDER TEST")
    print("=" * 80)
    
    phone = os.getenv("ZEPTO_PHONE_NUMBER", "7023988261")
    product_url = "https://www.zepto.com/pn/coca-cola-soft-drink-can-carbonated-beverage/pvid/e630c9c4-a67f-4349-a884-0a17553450ab"
    
    print(f"\n📱 Phone: {phone}")
    print(f"🔗 Product: Coca Cola Regular")
    print(f"🌐 URL: {product_url}")
    
    async with async_playwright() as p:
        print("\n🚀 Launching browser (you can see and interact)...")
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        # Step 1: Go to product page
        print(f"\n📦 Step 1: Opening product page...")
        await page.goto(product_url)
        await asyncio.sleep(3)
        
        print("\n👀 BROWSER WINDOW OPENED!")
        print("=" * 80)
        print("NOW DO MANUALLY:")
        print("1. Click on address at top")
        print("2. Select your address (look for 'Hostel' or 'BH3' or 'IIIT')")
        print("3. Click 'Add to Cart'")
        print("4. Go to cart")
        print("5. Click 'Proceed to Checkout'")
        print("6. Select 'Cash on Delivery'")
        print("7. Enter OTP when asked")
        print("8. Complete order")
        print("=" * 80)
        
        input("\n⏸️  Press ENTER when you've completed the order (or want to stop)...")
        
        print("\n✅ Test complete!")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_manual_order())
