# 🎨 GANGU Frontend - Quick Start Guide

## ⚡ 5-Minute Setup

### 1. Install Everything
```powershell
# From GANGU root directory
.\scripts\setup_frontend.ps1
```

This script will:
- ✅ Install backend API dependencies
- ✅ Install frontend dependencies
- ✅ Check MongoDB connection
- ✅ Setup environment files

### 2. Start Development Servers
```powershell
# Option A: Start both servers automatically
.\scripts\start_dev_servers.ps1

# Option B: Start manually in separate terminals
# Terminal 1 - Backend
cd api
python main.py

# Terminal 2 - Frontend
cd frontend
npm run dev
```

### 3. Open Browser
Navigate to: **http://localhost:3000**

## 🎙️ Try It Out!

1. **Click the big mic button** 🎤
2. **Allow microphone access** (Chrome/Edge only)
3. **Say in Hindi/Hinglish:**
   - "White chane khatam ho gaye"
   - "Doodh le aao"
   - "Atta mangwao"
4. **Watch GANGU work its magic! ✨**

## 🏗️ What You Get

### Voice-First Experience
```
You: 🎤 "White chane le aao"
     ↓
GANGU: 🤖 Understanding... Searching... Comparing...
     ↓
GANGU: 🛒 Here are 3 options (recommends best one)
     ↓
You: ✅ Confirm
     ↓
GANGU: 🎉 Order placed! Delivery today at 6 PM
```

### Live Agent Timeline
See exactly what GANGU is doing:
- ✓ Understanding your request
- ✓ Identifying item: White Chickpeas (1 kg)
- ✓ Searching Swiggy Instamart ✓ Zepto ✓ Amazon
- ✓ Comparing prices & reviews
- ✓ Selecting best option

### Smart Product Cards
Beautiful comparison view:
- Platform logo (Swiggy/Zepto/Amazon)
- Product image
- Price in ₹
- Rating ⭐
- Delivery time 🚚
- "Why GANGU likes this" explanation

### Trust-Focused Confirmation
Before any purchase:
```
"I'll place this order on Swiggy Instamart for ₹89. 
Delivery by 7 PM. Should I proceed?"

[✅ Confirm Purchase] [🔁 Change Option] [❌ Cancel]
```

## 🎨 Key Features

✅ **Voice-First**: Tap and speak naturally  
✅ **Bilingual**: Hindi, English, Hinglish  
✅ **Transparent**: See every step GANGU takes  
✅ **Smart**: AI explains why it recommends each product  
✅ **Trustworthy**: Always confirm before purchase  
✅ **Fast**: Results in 5-8 seconds  
✅ **Beautiful**: Modern, clean, accessible UI  

## 🛠️ Tech Stack

- **Frontend**: Next.js 14 + React + Tailwind CSS
- **Backend**: FastAPI + WebSocket
- **Voice**: Web Speech API (Chrome/Edge)
- **State**: Zustand
- **Agents**: LangGraph + Google Gemini
- **Database**: MongoDB

## 📁 Project Structure

```
GANGU/
├── api/                  # FastAPI backend
│   └── main.py          # REST API + WebSocket server
│
├── frontend/            # Next.js frontend
│   ├── app/
│   │   └── page.tsx    # Main page
│   ├── components/
│   │   ├── VoiceInput.tsx
│   │   ├── AgentTimeline.tsx
│   │   └── ProductComparison.tsx
│   └── lib/
│       └── store.ts    # State management
│
├── agents/              # AI agents (existing)
├── orchestration/       # LangGraph (existing)
└── scripts/
    └── start_dev_servers.ps1
```

## 🚀 Development Workflow

### Frontend Changes
```powershell
cd frontend

# Edit components in components/
# Edit styles in styles/globals.css
# Edit config in tailwind.config.js

# Hot reload is automatic!
```

### Backend Changes
```powershell
cd api

# Edit main.py
# Restart server to see changes
```

### Agent Changes
```powershell
# Edit agents/*.py
# Edit orchestration/gangu_graph.py
# Restart backend to see changes
```

## 🐛 Common Issues

### Voice Input Not Working
**Problem**: Mic button does nothing  
**Solution**: 
- Use Chrome or Edge (Firefox doesn't support Web Speech API)
- Allow microphone permissions
- Check console for errors

### Backend Connection Failed
**Problem**: "Failed to connect to backend"  
**Solution**:
- Ensure backend is running on port 8000
- Check `api/main.py` is running
- Verify MongoDB is running

### Products Not Showing
**Problem**: Timeline works but no products appear  
**Solution**:
- Check backend logs for MCP errors
- Ensure Zepto/Amazon MCP servers are running
- Check MongoDB connection

## 📚 Documentation

- [Frontend README](frontend/README.md) - Complete frontend guide
- [Frontend Architecture](docs/FRONTEND_ARCHITECTURE.md) - System design
- [API Documentation](api/main.py) - Backend endpoints
- [Main README](README.md) - Overall project guide

## 🎯 Next Steps

### Try Different Queries
```
Hindi:
- "Doodh khatam ho gaya"
- "Chawal mangwao"
- "Sabji le aao"

English:
- "Order milk"
- "Buy rice"
- "Get vegetables"

Hinglish:
- "Milk khatam ho gayi"
- "Rice le aao"
```

### Customize UI
Edit these files to change the look:
- `frontend/tailwind.config.js` - Colors, fonts
- `frontend/styles/globals.css` - Custom styles
- `frontend/components/*.tsx` - Component behavior

### Add Features
Some ideas:
- Order history page
- User authentication
- Dark mode toggle
- More languages
- Mobile app

## 🤝 Need Help?

1. Check documentation files
2. Look at console logs (browser F12)
3. Check backend logs (terminal)
4. Read code comments in components

## 🎉 That's It!

You now have a fully functional, voice-first, AI-powered grocery assistant with a beautiful frontend!

**GANGU makes grocery shopping magical! ✨**

---

Made with ❤️ for elderly users who deserve simple, trustworthy technology.
