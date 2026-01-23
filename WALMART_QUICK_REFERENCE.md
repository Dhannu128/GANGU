# 🎯 Walmart MCP - Quick Reference

## Setup (One-Time)

```powershell
# 1. Get your Apify token from:
#    https://console.apify.com/account/integrations

# 2. Set it in PowerShell:
$env:APIFY_TOKEN = "apify_api_xxxxxxxxxxxxxxxxxxxxx"

# 3. OR add to .env file:
echo "APIFY_TOKEN=apify_api_xxxxxxxxxxxxxxxxxxxxx" >> .env
```

## Test Commands

```powershell
# Test 1: Basic import
python -c "from mcp_clients.walmart_mcp_client import WalmartMCPClient; print('✅ OK')"

# Test 2: Check integration
python -c "from agents.search_agent import WALMART_MCP_AVAILABLE; print(f'Walmart: {WALMART_MCP_AVAILABLE}')"

# Test 3: Run full test suite
python test_walmart_mcp.py
```

## Usage Examples

### 1. Direct Search
```python
import asyncio
from mcp_clients.walmart_mcp_client import WalmartMCPClient

async def main():
    client = WalmartMCPClient()
    await client.connect()
    result = await client.search_product("milk")
    print(result)
    await client.disconnect()

asyncio.run(main())
```

### 2. Via Search Agent
```python
from agents.search_agent import search_platforms

# Searches Zepto + Amazon + Walmart in parallel!
result = search_platforms({
    "item": "organic bread",
    "quantity": "1 loaf",
    "urgency": "normal"
})

print(f"Found on {result['total_results_found']} platforms")
for r in result['results']:
    print(f"{r['platform']}: {r['item_name']} - {r['price']}")
```

## Architecture

```
┌─────────────────────────────────────────┐
│         Search Agent                    │
│  (Parallel Multi-Platform Search)       │
└───────────┬────────────┬────────────────┘
            │            │
   ┌────────┴───┐   ┌────┴─────┐   ┌──────────┐
   │   Zepto    │   │  Amazon  │   │  Walmart │
   │    MCP     │   │   MCP    │   │   MCP    │
   │  (India)   │   │ (India)  │   │  (USA)   │
   └────────────┘   └──────────┘   └──────────┘
        ↓                ↓               ↓
   Real Zepto      Amazon.in      Apify Walmart
     Website        Products       API Scraper
```

## Important Notes

✅ **Parallel Search**: All platforms searched simultaneously  
✅ **Node.js Required**: Walmart MCP runs via `npx`  
⚠️ **USA Market**: Walmart primarily has US products  
⚠️ **API Token**: APIFY_TOKEN must be set  
💰 **API Limits**: Free tier has monthly call limits  

## Troubleshooting

| Issue | Solution |
|-------|----------|
| APIFY_TOKEN not set | `$env:APIFY_TOKEN = "your-token"` |
| npx not found | Install Node.js from nodejs.org |
| Connection failed | Check token validity & internet |
| Import error | `pip install mcp` |

## Files Reference

```
mcp_clients/
├── walmart_mcp_client.py      # Walmart MCP wrapper
├── amazon_mcp_client.py       # Amazon MCP wrapper  
├── zepto_mcp_client.py        # Zepto MCP wrapper
└── __init__.py                # Package exports

agents/
└── search_agent.py            # Multi-platform search
    ├── search_zepto_mcp()
    ├── search_amazon_mcp()
    └── search_walmart_mcp()   # NEW!

tests/
└── test_walmart_mcp.py        # Test suite
```

## API Response Format

```json
{
  "found": true,
  "platform": "Walmart",
  "products": [
    {
      "product_name": "Great Value Organic Milk",
      "price": "$3.48",
      "rating": "4.5/5",
      "availability": "In Stock",
      "url": "https://walmart.com/...",
      "brand": "Great Value",
      "savings": "$0.50"
    }
  ],
  "query": "milk"
}
```

## Resources

📖 [Full Setup Guide](WALMART_SETUP_GUIDE.md)  
📊 [Integration Summary](WALMART_INTEGRATION_SUMMARY.md)  
🌐 [Apify Walmart MCP](https://apify.com/runtime/walmart-savings/api/mcp)  
🔑 [Get API Token](https://console.apify.com/account/integrations)

---

**Quick Start**: Set `APIFY_TOKEN` → Run `python test_walmart_mcp.py` → Done! ✅
