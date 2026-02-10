"""
Test script for Zepto Purchase Agent
Tests complete order flow with cash on delivery
"""
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from agents.purchase_agent import execute_purchase
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_zepto_order():
    """Test Zepto order with cash on delivery"""
    
    print("=" * 80)
    print("🧪 TESTING ZEPTO PURCHASE AGENT - CASH ON DELIVERY")
    print("=" * 80)
    
    # Check if environment variables are set
    phone = os.environ.get('ZEPTO_PHONE_NUMBER')
    address = os.environ.get('ZEPTO_DEFAULT_ADDRESS')
    
    if not phone:
        print("\n❌ Error: ZEPTO_PHONE_NUMBER not set in .env file")
        print("Please add: ZEPTO_PHONE_NUMBER=your_phone_number")
        return
    
    if not address:
        print("\n⚠️ Warning: ZEPTO_DEFAULT_ADDRESS not set, using default 'Home'")
        address = "Home"
    
    print(f"\n✅ Phone Number: {phone}")
    print(f"✅ Address: {address}")
    
    # Sample product URL for Zepto - Coca Cola (Cold Drink)
    test_product_url = "https://www.zepto.com/pn/coca-cola-soft-drink-can-carbonated-beverage/pvid/e630c9c4-a67f-4349-a884-0a17553450ab"
    
    # Backup products if main one is out of stock
    backup_products = [
        {
            "url": "https://www.zepto.com/pn/pepsi-black-cola-diet-soft-drink/pvid/c6ddb7ce-ffe7-495d-bcbd-5e8697db0e78",
            "name": "Pepsi Black",
            "price": 40.00
        },
        {
            "url": "https://www.zepto.com/pn/strawberry-lemonade/pvid/0adbb1a8-79df-4c2b-af11-6442999138f2",
            "name": "Strawberry Lemonade",
            "price": 50.00
        },
        {
            "url": "https://www.zepto.com/pn/fresh-onion/pvid/5b5c1960-d2d1-4528-8a74-bc7280174071",
            "name": "Fresh Onion",
            "price": 30.00
        }
    ]
    
    # Create test decision input
    test_decision = {
        "final_decision": {
            "selected_platform": "Zepto",
            "product": {
                "name": "Coca Cola Regular",
                "brand": "Coca Cola",
                "product_id": "zepto_coke_regular",
                "product_url": test_product_url,
                "url": test_product_url,
                "quantity": 1,
                "price": 40.00,
                "currency": "INR"
            },
            "delivery": {
                "eta_hours": 0.25,  # 15 minutes
                "delivery_date": "2026-01-30",
                "slot": "immediate"
            },
            "confidence_score": 0.95,
            "fallback_options": []
        },
        "user_context": {
            "urgency": "high",
            "budget_limit": 200.00
        }
    }
    
    print("\n📦 Test Product: Coca Cola Regular (Cold Drink)")
    print(f"🔗 Product URL: {test_product_url}")
    print(f"💰 Expected Price: ₹40.00")
    print(f"\n📋 Backup Products Available:")
    for idx, backup in enumerate(backup_products, 1):
        print(f"   {idx}. {backup['name']} - ₹{backup['price']}")
    
    # Ask for user confirmation
    print("\n" + "=" * 80)
    print("⚠️  USER CONFIRMATION REQUIRED")
    print("=" * 80)
    print("\nThis will place a REAL order on Zepto with Cash on Delivery!")
    print("You will need to:")
    print("  1. Enter OTP when prompted")
    print("  2. Pay cash when the delivery arrives")
    print("  3. If out of stock, will try backup products automatically")
    
    confirm = input("\n🤔 Do you want to proceed? (yes/no): ").strip().lower()
    
    if confirm not in ['yes', 'y']:
        print("\n❌ Order cancelled by user")
        return
    
    print("\n" + "=" * 80)
    print("🚀 STARTING ORDER EXECUTION")
    print("=" * 80)
    
    # Execute purchase with retry for out of stock
    result = None
    current_product = test_decision["final_decision"]["product"].copy()
    
    for attempt in range(len(backup_products) + 1):
        if attempt == 0:
            print("\n🛒 Attempting to order: Coca Cola Regular")
        else:
            backup = backup_products[attempt - 1]
            print(f"\n🔄 Previous product was out of stock, trying: {backup['name']}")
            test_decision["final_decision"]["product"] = {
                "name": backup["name"],
                "brand": "Zepto",
                "product_id": f"zepto_backup_{attempt}",
                "product_url": backup["url"],
                "url": backup["url"],
                "quantity": 1,
                "price": backup["price"],
                "currency": "INR"
            }
        
        result = execute_purchase(test_decision)
        
        # Check if order was successful or product was out of stock
        if result.get("purchase_status") == "success":
            print("\n✅ Order placed successfully!")
            break
        elif "out of stock" in result.get("user_message", "").lower() or "out_of_stock" in str(result.get("failures_encountered", [])):
            if attempt < len(backup_products):
                print(f"⚠️ Product out of stock, trying next option...")
                continue
            else:
                print(f"❌ All products are out of stock!")
                break
        else:
            # Some other error occurred
            break
    
    # Display result
    print("\n" + "=" * 80)
    print("📊 FINAL ORDER RESULT")
    print("=" * 80)
    
    import json
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    if result.get("purchase_status") == "success":
        print("\n🎉 ORDER PLACED SUCCESSFULLY!")
        print(f"✅ Order ID: {result.get('execution_details', {}).get('order_id')}")
        print(f"✅ Platform: {result.get('execution_details', {}).get('platform_used')}")
        print(f"💳 Payment: Cash on Delivery")
        print(f"\n{result.get('user_message', '')}")
    else:
        print(f"\n❌ ORDER FAILED: {result.get('user_message', 'Unknown error')}")
    
    print("\n" + "=" * 80)


if __name__ == "__main__":
    test_zepto_order()
