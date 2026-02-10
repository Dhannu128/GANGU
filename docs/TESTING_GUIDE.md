# ZEPTO MCP INTEGRATION - TESTING INSTRUCTIONS

## 🧪 Testing the Zepto MCP Integration

### Prerequisites
Before testing, ensure:
1. Zepto MCP server is set up
2. Dependencies are installed
3. Firefox login session is saved
4. Environment variables are set

### Step 1: Basic MCP Client Test
```powershell
cd d:\personal\AI-ML\python\GANGU
python zepto_mcp_client.py
```

**Expected Output:**
```
============================================================
Testing Zepto MCP Client for GANGU
============================================================

📡 Test 1: Connecting to Zepto MCP Server...
✅ Connected to Zepto MCP Server
📋 Available tools: ['start_zepto_order', 'submit_login_otp', ...]

🔍 Test 2: Search for 'onion'...
{
  "found": true,
  "product_name": "onion",
  "url": "https://www.zepto.com/pn/fresh-onion/...",
  "platform": "Zepto",
  "estimated_price": "₹20-50 (estimated)",
  "availability": "Available",
  "delivery_time": "10-15 minutes"
}

🔍 Test 3: Search for multiple products...
{
  "platform": "Zepto",
  "total_products": 4,
  "found_count": 4,
  "results": [...]
}

✅ All tests completed!
```

### Step 2: Search Agent Integration Test
```powershell
cd d:\personal\AI-ML\python\GANGU
python "Search Agent.py"
```

At the prompt, type `test` to run built-in test searches.

**Expected Output:**
```
✅ Zepto MCP client loaded successfully

🧪 Running test searches...

--- Test 1 ---
📥 Input: {"action": "search_all_platforms", "item": "white chickpeas", ...}
📡 Attempting Zepto MCP search...
✅ Zepto MCP: Found
🔍 Starting search for: white chickpeas
✅ Added Zepto MCP result to results

Search Results for: white chickpeas
══════════════════════════════════════════════════════════

📊 Platforms Searched: Zepto, Blinkit, Swiggy, Amazon, Flipkart
✅ Total Results Found: 5

Platform: Zepto [MCP - REAL DATA]
   Item: white chickpeas
   Price: ₹45-80
   Delivery: 10-15 min
   Rating: 4.5⭐ (500 reviews)
   Source: mcp_server
```

### Step 3: Full GANGU Pipeline Test
```powershell
cd d:\personal\AI-ML\python\GANGU
docker-compose up -d  # Start MongoDB
python gangu_main.py
```

Input test request:
```
White chane khatam ho gaye
```

**Expected Flow:**
1. Intent Extraction Agent → extracts intent and item
2. Task Planner Agent → creates search plan  
3. Search Agent → **Calls Zepto MCP + other platforms**
4. Returns results with Zepto data marked as "mcp_server"

**Watch for these log messages:**
```
[Search Agent] ✅ Zepto MCP client loaded successfully
[Search Agent] 📡 Attempting Zepto MCP search...
[Search Agent] ✅ Zepto MCP: Found
[Search Agent] ✅ Added Zepto MCP result to results
```

### Step 4: Manual Test with Specific Products

Test products that are in Zepto catalog:
```python
python "Search Agent.py"
```

Try these inputs one by one:
```json
{"action": "search_all_platforms", "item": "onion", "quantity": "1 kg", "urgency": "normal", "intent": "buy_grocery"}
{"action": "search_all_platforms", "item": "dal", "quantity": "1 kg", "urgency": "normal", "intent": "buy_grocery"}
{"action": "search_all_platforms", "item": "chai", "quantity": "1 cup", "urgency": "normal", "intent": "buy_grocery"}
{"action": "search_all_platforms", "item": "coffee", "quantity": "1 cup", "urgency": "normal", "intent": "buy_grocery"}
{"action": "search_all_platforms", "item": "milk", "quantity": "1 litre", "urgency": "normal", "intent": "buy_grocery"}
```

### Step 5: Test Product Not in Catalog

Test with random product:
```json
{"action": "search_all_platforms", "item": "xyz123random", "quantity": "1 unit", "urgency": "normal", "intent": "buy_grocery"}
```

**Expected:** Falls back to mock data or shows "not found"

## 🔍 Verification Checklist

After running tests, verify:

- [ ] Zepto MCP client connects successfully
- [ ] Product searches return real Zepto URLs
- [ ] Results show `"source": "mcp_server"`
- [ ] Falls back gracefully if MCP unavailable
- [ ] Search Agent detects MCP: "✅ Zepto MCP client loaded successfully"
- [ ] Full GANGU pipeline includes Zepto MCP results
- [ ] Results show estimated prices from Zepto
- [ ] Delivery time shows "10-15 min" for Zepto

## 🐛 Troubleshooting

### Issue: "Zepto MCP client not available"
**Cause:** Import failed
**Fix:**
```powershell
cd d:\personal\AI-ML\python\GANGU
pip install mcp httpx python-dotenv
```

### Issue: "Zepto MCP server not found"
**Cause:** Server script not cloned
**Fix:**
```powershell
.\setup_zepto_mcp.ps1
# Or manually:
git clone https://github.com/proddnav/zepto-cafe-mcp.git
```

### Issue: "Connection refused" errors
**Cause:** Server can't start
**Fix:**
1. Check Firefox isn't running
2. Delete `zepto-cafe-mcp/zepto_firefox_data/`
3. Run `python zepto-cafe-mcp/setup_firefox_login.py`

### Issue: "Product not found" for valid items
**Cause:** Item name mismatch with catalog
**Fix:** Check `zepto_mcp_client.py` ZEPTO_PRODUCT_CATALOG
Add mapping for your product

### Issue: Search Agent doesn't use MCP
**Cause:** ZEPTO_MCP_AVAILABLE = False
**Check logs for:**
```
⚠️ Zepto MCP client not available: <error message>
```
**Fix based on error message**

## 📊 Success Indicators

✅ **Working Correctly:**
- Log shows "✅ Zepto MCP client loaded successfully"
- Search results include `"source": "mcp_server"`
- Zepto URLs start with "https://www.zepto.com/pn/"
- Delivery time is "10-15 min" for Zepto
- No import errors in Search Agent

❌ **Not Working:**
- Log shows "⚠️ Zepto MCP client not available"
- All results show `"source": "simulation"`
- Generic placeholder prices only
- Import errors or connection errors

## 🎯 Next Testing Phases

### Phase 2: Add More Platforms
Once Zepto MCP works:
1. Find/build Blinkit MCP server
2. Find/build Swiggy MCP server
3. Integrate similar to Zepto

### Phase 3: Complete GANGU Testing
1. Test full pipeline: Intent → Task → Search → Compare → Decision
2. Test with elderly-friendly scenarios
3. Test error handling
4. Test checkpointing/resume

### Phase 4: Real-World Testing
1. Test with actual phone numbers
2. Test order placement (if enabled)
3. Test with multiple items
4. Test address selection

## 📝 Test Results Template

Copy this and fill it out:

```
Date: _____________
Tester: _____________

Test 1: MCP Client Connection
[ ] Pass [ ] Fail
Notes: ___________________________________________

Test 2: Product Search (onion)
[ ] Pass [ ] Fail
Found: [ ] Yes [ ] No
Source: [ ] mcp_server [ ] simulation
Notes: ___________________________________________

Test 3: Search Agent Integration
[ ] Pass [ ] Fail
MCP Used: [ ] Yes [ ] No
Results Count: _____
Notes: ___________________________________________

Test 4: Full GANGU Pipeline
[ ] Pass [ ] Fail
All Agents Executed: [ ] Yes [ ] No
Zepto Data Present: [ ] Yes [ ] No
Notes: ___________________________________________

Overall Status: [ ] Working [ ] Issues [ ] Not Working
```

## 🚀 Ready for Production

Before considering production ready:
1. All tests pass ✅
2. Real Zepto data flows through
3. Fallback works correctly
4. No import/connection errors
5. Performance is acceptable (<5s search time)
6. Error handling is robust

Good luck with testing! 🎉
