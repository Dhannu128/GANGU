# 🚀 Quick Start - Zepto Order with Cash on Delivery

**Complete a Zepto order in under 2 minutes!**

## ⚡ Fastest Way to Order

### Step 1: Check Your `.env` File (30 seconds)

```bash
# Open .env and make sure these are filled:
ZEPTO_PHONE_NUMBER=your_10_digit_number
ZEPTO_DEFAULT_ADDRESS=HSR Home
GEMINI_API_KEY=your_api_key
```

### Step 2: Run Test Script (10 seconds)

```bash
python test_purchase_zepto.py
```

### Step 3: Confirm Order (10 seconds)

```
🤔 Do you want to proceed? (yes/no): yes
```

### Step 4: Enter OTP (30 seconds)

```
🔑 Enter the OTP received on your phone: 123456
```

### Step 5: Done! ✅

```
🎉 ORDER PLACED SUCCESSFULLY!
✅ Order ID: ZEPTO_1738234567
💳 Payment: Cash on Delivery
```

---

## 🎯 Want to Order Something Specific?

### Edit `test_purchase_zepto.py`

Find this line (around line 38):

```python
test_product_url = "https://www.zepto.com/pn/fresh-onion/pvid/5b5c1960-d2d1-4528-8a74-bc7280174071"
```

Replace with your product URL:

```python
# Example: Order Milk instead
test_product_url = "https://www.zepto.com/pn/plain-curd/pvid/a1a7b157-d40b-41c0-92be-e119a8c77e9a"
```

---

## 📱 Popular Products (Copy-Paste Ready)

### Vegetables
```python
# Onion
"https://www.zepto.com/pn/fresh-onion/pvid/5b5c1960-d2d1-4528-8a74-bc7280174071"

# Potato
"https://www.zepto.com/pn/potato/pvid/f72c0479-1ae2-44fd-a65f-ca569d4f8c72"

# Tomato
"https://www.zepto.com/pn/tomato/pvid/d34f8cf4-5876-40ef-8ea5-cd2a31b4db39"
```

### Dairy & Eggs
```python
# Milk/Curd
"https://www.zepto.com/pn/plain-curd/pvid/a1a7b157-d40b-41c0-92be-e119a8c77e9a"

# Paneer
"https://www.zepto.com/pn/paneer-tandoori-tikka/pvid/7eb6a978-fd60-4288-a37e-7627312cd8ea"

# Eggs
"https://www.zepto.com/pn/bulls-eye-egg-2pcs/pvid/4b4962cb-3ba0-4ff8-8764-7d628d2fd09e"
```

### Staples
```python
# Dal
"https://www.zepto.com/pn/popular-essentials-toor-dal/pvid/870056e6-aad4-43e6-8e38-e757dc2b028c"

# Rice
"https://www.zepto.com/pn/steamed-rice/pvid/6b744fa4-f7e0-4cb9-8b3e-3befcf1ecb2d"

# Atta/Chapati
"https://www.zepto.com/pn/wheat-chapati-pack-of-5/pvid/4b9364e7-fe2f-4f60-a050-66e8716887e9"
```

---

## 🛠️ Troubleshooting (1 Minute Fixes)

### ❌ "ZEPTO_PHONE_NUMBER not set"
**Fix**: Add to `.env`:
```
ZEPTO_PHONE_NUMBER=9876543210
```

### ❌ "OTP timeout"
**Fix**: Re-run the script, enter OTP faster (within 5 min)

### ❌ "Product out of stock"
**Fix**: Try a different product URL from list above

### ❌ "Address not found"
**Fix**: Change address in `.env`:
```
ZEPTO_DEFAULT_ADDRESS=Office New Cafe
```
(Options: "HSR Home", "Office New Cafe", "Hyd Home")

---

## 💡 Pro Tips

1. **First Time?** Order onion (₹20-30) to test
2. **Keep Phone Ready** - OTP comes in 10-20 seconds
3. **Best Time** - Morning 8-11 AM for fresh items
4. **Cash Ready** - Keep change ready for delivery

---

## 🎊 That's It!

**3 Commands. 2 Minutes. 1 Order Placed.**

```bash
# 1. Check .env
cat .env

# 2. Run script
python test_purchase_zepto.py

# 3. Enter OTP when prompted
```

**Need detailed info?** Check [ZEPTO_ORDER_GUIDE.md](ZEPTO_ORDER_GUIDE.md)

---

**Happy Shopping! 🛒**
