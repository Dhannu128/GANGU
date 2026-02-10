# 🛒 Zepto Order Guide - Cash on Delivery

Complete guide for placing orders on Zepto with Cash on Delivery through GANGU Purchase Agent.

## ✨ Features

- ✅ **Complete Order Automation**: From product selection to order placement
- ✅ **Cash on Delivery**: No need for online payment
- ✅ **User Confirmation**: OTP-based verification for secure ordering
- ✅ **Real-time Updates**: See each step of the order process
- ✅ **Stock Check**: Automatic out-of-stock detection
- ✅ **Address Selection**: Uses your saved address from environment

## 📋 Prerequisites

### 1. Environment Setup

Make sure you have these in your `.env` file:

```env
ZEPTO_PHONE_NUMBER=your_phone_number_here
ZEPTO_DEFAULT_ADDRESS=HSR Home
GEMINI_API_KEY=your_api_key_here
```

### 2. Dependencies Installed

```bash
pip install playwright mcp python-dotenv google-genai
python -m playwright install firefox
```

### 3. Zepto Account

- Have a Zepto account with the phone number specified above
- Have at least one saved address in your Zepto account

## 🚀 How to Place an Order

### Method 1: Using Test Script (Recommended for Testing)

```bash
python test_purchase_zepto.py
```

This will:
1. Load your environment variables
2. Show you the test product (Fresh Onion)
3. Ask for confirmation before placing order
4. Guide you through OTP entry
5. Complete the order with Cash on Delivery

### Method 2: Using Purchase Agent Directly

```python
from agents.purchase_agent import execute_purchase

# Create order decision
decision = {
    "final_decision": {
        "selected_platform": "Zepto",
        "product": {
            "name": "Product Name",
            "product_url": "https://www.zepto.com/pn/...",
            "quantity": 1,
            "price": 100.00
        },
        "delivery": {
            "eta_hours": 0.25,
            "delivery_date": "2026-01-30"
        }
    },
    "user_context": {
        "urgency": "normal",
        "budget_limit": 500.00
    }
}

# Execute purchase
result = execute_purchase(decision)
print(result)
```

## 📱 Order Flow

### Step-by-Step Process

1. **🔌 Connection**
   - Purchase Agent connects to Zepto MCP Server
   - Loads your phone number and address from environment

2. **🛒 Order Initialization**
   - Navigates to product page
   - Checks product availability
   - Adds product to cart

3. **📍 Address Selection**
   - Automatically selects your default address
   - Confirms delivery location

4. **📱 OTP Request**
   - System sends OTP to your phone
   - You'll see: "OTP sent to your_number"

5. **🔑 OTP Entry**
   ```
   🔑 Enter the OTP received on your phone: ______
   ```
   - Enter the 4-6 digit OTP
   - Press Enter

6. **💳 Payment Selection**
   - Automatically selects "Cash on Delivery"
   - No online payment required

7. **✅ Order Confirmation**
   - Order is placed successfully
   - You'll receive order confirmation
   - Pay cash when delivery arrives

## 💡 Example Products

Here are some product URLs you can use for testing:

```python
# Vegetables
onion = "https://www.zepto.com/pn/fresh-onion/pvid/5b5c1960-d2d1-4528-8a74-bc7280174071"
potato = "https://www.zepto.com/pn/potato/pvid/f72c0479-1ae2-44fd-a65f-ca569d4f8c72"
tomato = "https://www.zepto.com/pn/tomato/pvid/d34f8cf4-5876-40ef-8ea5-cd2a31b4db39"

# Dairy
milk = "https://www.zepto.com/pn/plain-curd/pvid/a1a7b157-d40b-41c0-92be-e119a8c77e9a"
paneer = "https://www.zepto.com/pn/paneer-tandoori-tikka/pvid/7eb6a978-fd60-4288-a37e-7627312cd8ea"

# Staples
dal = "https://www.zepto.com/pn/popular-essentials-toor-dal/pvid/870056e6-aad4-43e6-8e38-e757dc2b028c"
rice = "https://www.zepto.com/pn/steamed-rice/pvid/6b744fa4-f7e0-4cb9-8b3e-3befcf1ecb2d"
```

## 🛡️ Safety Features

### Pre-Order Validation
- ✅ Price verification (alerts if price changed)
- ✅ Availability check
- ✅ Duplicate order prevention
- ✅ Risk assessment

### During Order
- ✅ Stock verification before adding to cart
- ✅ Cart contents verification
- ✅ Address confirmation
- ✅ Payment method selection

### Post-Order
- ✅ Order ID generation
- ✅ Audit logging
- ✅ Confirmation message
- ✅ Delivery tracking info

## ⚠️ Important Notes

### 1. Real Money Transaction
- This places **REAL orders** on Zepto
- You will need to **pay cash** when delivery arrives
- Make sure you actually want the product before confirming

### 2. OTP Required
- You must have access to the phone number in `.env`
- OTP is required for every order
- OTP typically expires in 5 minutes

### 3. Address Must Exist
- The address must be saved in your Zepto account
- Default options: "HSR Home", "Office New Cafe", "Hyd Home"
- You can add custom addresses in Zepto app first

### 4. Out of Stock Handling
- If product is out of stock, order will not be placed
- You'll get a clear error message
- Try a different product or wait for restock

## 🐛 Troubleshooting

### Issue: "ZEPTO_PHONE_NUMBER not set"
**Solution**: Add your phone number to `.env` file:
```env
ZEPTO_PHONE_NUMBER=9876543210
```

### Issue: "Address modal not found"
**Solution**: 
1. Check that you have saved addresses in Zepto app
2. Try logging into Zepto website manually once
3. Make sure address name matches one in your account

### Issue: "OTP timeout"
**Solution**:
1. Check your phone for OTP SMS
2. Enter OTP within 5 minutes
3. If expired, restart the order process

### Issue: "Product out of stock"
**Solution**:
1. Try a different product
2. Check Zepto app manually to verify stock
3. Try again later when restocked

### Issue: "Order placed but not showing"
**Solution**:
1. Check Zepto app - orders section
2. Look for order confirmation SMS
3. Check audit log: `logs/purchase_audit.jsonl`

## 📊 Order Result Format

Successful order returns:

```json
{
  "purchase_status": "success",
  "execution_details": {
    "timestamp": "2026-01-30T...",
    "platform_used": "Zepto",
    "order_id": "ZEPTO_1738234567",
    "transaction_id": "ZEPTO_1738234567"
  },
  "order_confirmation": {
    "product_name": "Fresh Onion",
    "quantity": 1,
    "final_price": 50.00,
    "currency": "INR",
    "delivery_date": "2026-01-30"
  },
  "user_message": "✅ Order placed successfully! Fresh Onion will arrive on 2026-01-30."
}
```

## 📝 Audit Log

All orders are logged in `logs/purchase_audit.jsonl`:

```json
{
  "audit_id": "audit_202601301430_abc123",
  "timestamp": "2026-01-30T14:30:00Z",
  "agent": "purchase_agent",
  "action": "purchase_success",
  "platform": "Zepto",
  "product": "Fresh Onion",
  "price": 50.00,
  "result": "success"
}
```

## 🎯 Best Practices

1. **Start Small**: Test with a cheap product first (like onion)
2. **Verify Address**: Make sure correct delivery address is selected
3. **Check Stock**: Products may go out of stock quickly
4. **Keep Phone Ready**: Have your phone handy for OTP
5. **Morning Orders**: Best time is 8 AM - 11 AM for fresh items
6. **Cash Ready**: Keep exact change ready for delivery

## 🔄 Integration with GANGU

This purchase agent is part of the GANGU pipeline:

```
User Request → Intent Agent → Search Agent → Comparison Agent 
→ Decision Agent → Purchase Agent (YOU ARE HERE) → Notification
```

The Purchase Agent receives structured decisions and executes them safely with:
- Pre-purchase validation
- Risk assessment  
- Retry logic
- Fallback options
- Audit logging

## 📞 Support

If you encounter issues:

1. Check logs in `logs/` directory
2. Verify environment variables in `.env`
3. Test Zepto website manually
4. Check network connection
5. Restart the server and try again

---

**Made with ❤️ by GANGU Team**

*Helping elderly users shop online safely and easily*
