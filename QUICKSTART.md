# 🚀 GANGU Quick Start Guide

## ⚡ 30-Second Start

```bash
cd d:\personal\AI-ML\python\GANGU
python start_gangu.py
```

That's it! The startup script will:
- ✅ Check all dependencies
- ✅ Verify agents
- ✅ Test MongoDB
- ✅ Confirm LangSmith
- 🚀 Start GANGU automatically

---

## 📝 Try These Commands

Once GANGU starts, try:

### Grocery Purchase
```
You: White chane khatam ho gaye
→ GANGU searches Zepto + Amazon, compares, decides, orders!
```

### Urgent Purchase
```
You: Doodh abhi chahiye
→ GANGU prioritizes fast delivery (Zepto 10 min)
```

### General Purchase
```
You: Atta le aao
→ GANGU may ask for clarification (which brand?)
```

---

## 🎯 What Happens Behind the Scenes

```
Your Input (Hindi/Hinglish)
    ↓
[1] Intent Extraction → Understands what you need
    ↓
[2] Task Planner → Creates execution plan
    ↓
[3] Search Agent → Searches Zepto + Amazon (parallel)
    ↓
[4] Comparison → Scores all options
    ↓
[5] Decision → Applies 6 safety policies
    ↓
Output (Hindi/Hinglish with order details)
```

**All tracked in LangSmith!** 📊

---

## 🔍 Check LangSmith Traces

1. Go to: https://smith.langchain.com
2. Select project: **GANGU**
3. See every agent execution!

---

## 🐛 Troubleshooting

### MongoDB not running?
```bash
cd config
docker-compose up -d
```

### Missing packages?
```bash
pip install -r config/requirements.txt
```

### Test without starting?
```bash
python test_full_pipeline.py
```

---

## 📚 Full Documentation

- `INTEGRATION_COMPLETE.md` - What was done
- `README_PIPELINE.md` - Complete guide
- `docs/DECISION_AGENT_GUIDE.md` - Decision policies
- `docs/COMPARISON_AGENT_GUIDE.md` - Comparison logic

---

## ✅ System Check Results

Run `python start_gangu.py` to see:

```
✅ Python Version (3.10+)
✅ Environment Variables (GEMINI_API_KEY, etc.)
✅ Required Packages (google-genai, langgraph, etc.)
✅ Agents (All 5 agents)
✅ MCP Clients (Zepto + Blinkit)
✅ MongoDB (State persistence)
✅ LangSmith (Tracing)
```

**7/7 = Ready to go!** 🎉

---

## 🎯 Demo Flow

1. **Start:** `python start_gangu.py`
2. **Input:** "White chane khatam ho gaye"
3. **Watch:** Pipeline executes (3-5 seconds)
4. **Output:** Complete order with reasoning
5. **Check:** LangSmith for full trace
6. **Show:** Real Zepto/Blinkit data used

---

## 💡 Key Features to Highlight

✅ **5 AI Agents** working together
✅ **Real MCP Integration** (Zepto + Blinkit)
✅ **Hindi/Hinglish** support
✅ **Policy-Driven** decisions (6 safety rules)
✅ **Risk Assessment** before purchase
✅ **LangSmith Tracing** for visibility
✅ **Production-Ready** error handling

---

**Ready to demonstrate? Run:** `python start_gangu.py` 🚀
