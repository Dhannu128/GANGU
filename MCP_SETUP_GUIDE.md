# 🛠️ GANGU MCP Server Setup Guide

This guide will help you set up Amazon MCP and Zepto MCP servers for GANGU.

## 📋 Prerequisites

1. Python 3.10 or higher
2. `uv` package manager (for Amazon MCP)
3. Firefox browser (for Zepto MCP)

---

## 🔧 Part 1: Install Dependencies

### Step 1: Install Python Dependencies

```powershell
cd d:\personal\AI-ML\python\GANGU
pip install -r config/requirements.txt
```

### Step 2: Install UV (for Amazon MCP)

UV is required to run the Amazon MCP server.

**On Windows (PowerShell as Administrator):**
```powershell
irm https://astral.sh/uv/install.ps1 | iex
```

**On macOS/Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

After installation, close and reopen your terminal to ensure `uvx` is in your PATH.

### Step 3: Install Playwright (for Zepto MCP)

```powershell
python -m playwright install firefox
```

---

## 🌐 Part 2: Setup Amazon MCP Server

The Amazon MCP server connects to Fewsats' Amazon integration service.

### Step 1: Test Amazon MCP Connection

```powershell
# Test if uvx and amazon-mcp are working
uvx amazon-mcp --help
```

If this works, Amazon MCP is ready! The server will be automatically invoked by GANGU when needed.

### Step 2: (Optional) Configure for Purchases

If you want to enable actual purchasing through Amazon (not just search):

1. Go to [fewsats.com](https://fewsats.com) and create an account
2. Add a payment method
3. Get your API key from [app.fewsats.com/api-keys](https://app.fewsats.com/api-keys)
4. Add to your `.env` file:
   ```
   FEWSATS_API_KEY=your_api_key_here
   ```

**Note:** For now, GANGU only uses Amazon for search/comparison, not purchasing.

---

## 🛒 Part 3: Setup Zepto MCP Server (Login Persistence)

The Zepto MCP server uses Firefox with a persistent profile to save your login session.

### Step 1: One-Time Login Setup

Run this script once to log in to Zepto and save your session:

```powershell
cd d:\personal\AI-ML\python\GANGU\zepto-cafe-mcp
python setup_firefox_login.py
```

**What happens:**
1. Firefox will open automatically
2. Navigate to zepto.com manually in the browser
3. Log in with your phone number and OTP
4. Once logged in, close the browser
5. Your session is now saved in `zepto_firefox_data/` folder

### Step 2: Test Zepto MCP

```powershell
cd d:\personal\AI-ML\python\GANGU
python mcp_clients/zepto_mcp_client.py
```

**Expected Output:**
```
✅ Connected to Zepto MCP Server
📋 Available tools: [...]
🔍 Found X cookies for zeptonow.com domain
✅ User is already logged in (persistent session)
```

### Step 3: Verify Session Persistence

After the initial setup, every time you use GANGU:
- ✅ Zepto will use your saved login
- ✅ No OTP needed
- ✅ Faster order processing

**If login expires:**
Simply run `setup_firefox_login.py` again to refresh your session.

---

## 🔍 Part 4: Verify Everything Works

### Test the Complete System

```powershell
cd d:\personal\AI-ML\python\GANGU
python start_gangu.py
```

**Checklist:**
- [x] Python version OK
- [x] Environment variables loaded
- [x] All agents initialized
- [x] MongoDB connected
- [x] LangSmith configured
- [x] MCP clients ready (Amazon + Zepto)

### Test Search Functionality

```python
# In GANGU interactive mode
You: white chane khatam ho gaye
```

**Expected:**
- ✅ Search across Amazon (via MCP)
- ✅ Search across Zepto (via MCP)
- ✅ Compare results
- ✅ Make recommendation

---

## 📂 Understanding the MCP Architecture

### Amazon MCP (Fewsats)
```
GANGU Search Agent
    ↓
amazon_mcp_client.py (connects via uvx)
    ↓
amazon-mcp package (from PyPI)
    ↓
Fewsats Amazon API
    ↓
Amazon India Search Results
```

### Zepto MCP (Custom)
```
GANGU Search Agent
    ↓
zepto_mcp_client.py (stdio connection)
    ↓
zepto_mcp_server.py (MCP server)
    ↓
Playwright + Firefox (persistent context)
    ↓
Zepto.com Live Website
```

---

## 🔧 Troubleshooting

### Amazon MCP Issues

**Problem:** `uvx: command not found`
**Solution:** 
- Reinstall UV
- Ensure it's in your PATH
- Restart terminal

**Problem:** `amazon-mcp package not found`
**Solution:**
```powershell
uvx --refresh amazon-mcp
```

### Zepto MCP Issues

**Problem:** "Login required" every time
**Solution:**
1. Check if `zepto_firefox_data/` folder exists
2. Run `setup_firefox_login.py` again
3. Ensure you actually logged in before closing the browser

**Problem:** Firefox crashes or won't start
**Solution:**
1. Delete the `zepto_firefox_data/` folder
2. Run `setup_firefox_login.py` again
3. Check Firefox is installed: `python -m playwright install firefox`

**Problem:** Cookies not persisting
**Solution:**
- Ensure you're completing the full login flow (phone + OTP)
- Don't use incognito/private mode
- Check file permissions on `zepto_firefox_data/`

---

## 📝 Environment Variables

Make sure your `.env` file in the GANGU root has:

```env
# Required for all agents
GEMINI_API_KEY=your_gemini_api_key
LANGSMITH_API_KEY=your_langsmith_key
LANGSMITH_PROJECT=GANGU
MONGODB_URI=mongodb://localhost:27017/

# Zepto MCP (optional - will prompt if not set)
ZEPTO_PHONE_NUMBER=+919876543210
ZEPTO_DEFAULT_ADDRESS=Your full address

# Amazon/Fewsats (optional - only for purchasing)
FEWSATS_API_KEY=your_fewsats_key
```

---

## ✅ Quick Status Check

Run this to verify your setup:

```powershell
cd d:\personal\AI-ML\python\GANGU

# Check Python
python --version

# Check UV
uvx --version

# Check Playwright
python -c "from playwright.async_api import async_playwright; print('Playwright OK')"

# Check Zepto session
python -c "import os; print('Zepto data exists:', os.path.exists('zepto-cafe-mcp/zepto_firefox_data'))"

# Test Amazon MCP
uvx amazon-mcp --help
```

---

## 🎉 You're All Set!

Once everything is configured:
1. Amazon MCP will provide fresh Amazon India product data
2. Zepto MCP will use your saved login (no repeated OTPs)
3. GANGU will compare both and give you the best deals

**Start using GANGU:**
```powershell
python start_gangu.py
```

---

## 📚 Additional Resources

- [Amazon MCP GitHub](https://github.com/Fewsats/amazon-mcp)
- [Zepto Website](https://www.zepto.com/)
- [Model Context Protocol (MCP) Docs](https://modelcontextprotocol.io/)
- [GANGU Architecture](ARCHITECTURE.md)

---

## 🆘 Still Having Issues?

Check the logs:
- GANGU logs: Console output
- Zepto MCP logs: Printed to stderr
- Amazon MCP logs: Check uvx output

For persistent issues, check:
1. Firewall settings (for MCP connections)
2. Antivirus (may block browser automation)
3. Network proxy settings
