# Walmart MCP Setup Guide

This guide walks you through setting up Walmart MCP integration in GANGU using Apify's Walmart Savings MCP server.

## Prerequisites

1. **Node.js and npm/npx** - Required to run the Walmart MCP server
2. **Apify Account** - Required for API access
3. **Apify API Token** - Get from https://console.apify.com/account/integrations

## Setup Steps

### 1. Get Apify API Token

1. Go to https://console.apify.com/account/integrations
2. Sign up or log in to your Apify account
3. Navigate to **Settings** → **Integrations**
4. Copy your **Personal API token**

### 2. Set Environment Variable

**PowerShell:**
```powershell
$env:APIFY_TOKEN = "your-apify-token-here"
```

**Or add to .env file:**
```
APIFY_TOKEN=your-apify-token-here
```

### 3. Verify Node.js Installation

```powershell
node --version
npm --version
```

If not installed, download from: https://nodejs.org/

### 4. Test Walmart MCP Connection

Run the test script:
```powershell
python test_walmart_mcp.py
```

Expected output:
```
✅ Connected to Walmart MCP Server
📋 Available tools: ['walmart_search']
✅ Found products on Walmart
```

## Integration Details

### Files Added/Modified

1. **New Files:**
   - `mcp_clients/walmart_mcp_client.py` - Walmart MCP client wrapper
   - `test_walmart_mcp.py` - Test suite for Walmart integration

2. **Modified Files:**
   - `mcp_clients/__init__.py` - Added WalmartMCPClient export
   - `agents/search_agent.py` - Added Walmart search functionality and parallel search support

### How It Works

```
User Query → Search Agent → Parallel Search
                              ├─ Zepto MCP
                              ├─ Amazon MCP
                              └─ Walmart MCP → Apify API
```

The Search Agent now searches across:
- **Zepto** (India) - Fast grocery delivery
- **Amazon** (India) - E-commerce
- **Walmart** (USA) - Retail and grocery

All searches run in **parallel** for maximum speed!

## Usage in Code

### Direct Walmart Search

```python
from mcp_clients.walmart_mcp_client import WalmartMCPClient

async def search():
    client = WalmartMCPClient()
    await client.connect()
    
    result = await client.search_product("chickpeas", max_results=5)
    
    if result['found']:
        for product in result['products']:
            print(f"{product['product_name']}: {product['price']}")
    
    await client.disconnect()

import asyncio
asyncio.run(search())
```

### Via Search Agent

```python
from agents.search_agent import search_platforms

# Search across all platforms (Zepto + Amazon + Walmart)
result = search_platforms({
    "item": "milk",
    "quantity": "1 liter",
    "urgency": "normal"
})

print(f"Found on {len(result['results'])} platform(s)")
```

## Troubleshooting

### Issue: "APIFY_TOKEN not set"
**Solution:** Set the environment variable as shown in Step 2

### Issue: "npx command not found"
**Solution:** Install Node.js from https://nodejs.org/

### Issue: "Failed to connect to Walmart MCP Server"
**Solution:** 
1. Check your APIFY_TOKEN is valid
2. Verify Node.js/npx is installed
3. Check internet connection
4. Try running manually: `npx -y @runtime-machines/walmart-savings-mcp`

### Issue: "Walmart MCP not available"
**Solution:** The client failed to import. Check:
1. `mcp_clients/walmart_mcp_client.py` exists
2. Python dependencies are installed (`pip install mcp`)

## API Limits

Apify has API limits based on your account tier:
- **Free tier**: Limited API calls per month
- **Paid tier**: Higher limits

Check your usage at: https://console.apify.com/account/usage

## Next Steps

- Test Walmart integration: `python test_walmart_mcp.py`
- Try full GANGU pipeline: `python test_full_pipeline.py`
- Start the API server with Walmart support: `python api/main.py`

## Support

For Walmart MCP issues:
- Apify Walmart MCP: https://apify.com/runtime/walmart-savings/api/mcp
- GANGU Issues: Check project documentation

---

**Note:** Walmart data is primarily for USA market. For Indian market products, Zepto and Amazon India are better options.
