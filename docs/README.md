# 🤖 GANGU - Agentic Grocery Assistant

Complete agentic AI system for elderly users with LangGraph orchestration.

## 🎯 Features

- **7 Intelligent Agents** working in orchestration
- **Checkpointing** with MongoDB (resume interrupted workflows)
- **Multi-platform search** (Blinkit, Amazon, Flipkart)
- **Intelligent comparison** with elderly-focused scoring
- **LangSmith tracing** for monitoring
- **Modular architecture** - easy to extend

## 📋 Agent Pipeline

```
User Input
   ↓
1. Input Understanding Agent
   ↓
2. Task Planner Agent (BRAIN)
   ↓
3. Marketplace Search Agent (Parallel)
   ↓
4. Comparison & Ranking Agent
   ↓
5. Decision Making Agent
   ↓
6. Purchase Execution Agent
   ↓
7. Notification Agent
```

## 🚀 Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Setup Environment
```bash
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
```

### 3. Start MongoDB
```bash
docker-compose up -d
```

### 4. Run GANGU
```bash
python gangu_main.py
```

## 📁 File Structure

```
GANGU/
├── gangu_graph.py       # LangGraph orchestration (all agents)
├── gangu_main.py        # Main application with checkpointing
├── gangu_support.py     # Admin support interface
├── docker-compose.yml   # MongoDB setup
├── requirements.txt     # Dependencies
└── README.md           # This file
```

## 🎮 Usage Examples

**Reorder Grocery:**
```
You: White chane khatam ho gaye
GANGU: ✅ Order Successful! Item: white chana, Platform: Blinkit...
```

**Query Information:**
```
You: Is white chana good for diabetes?
GANGU: [Provides detailed nutrition information]
```

## 🔧 Support Interface

Resume interrupted workflows:
```bash
python gangu_support.py
```

## 🎨 Key Advantages

1. **Checkpointing** - Never lose progress
2. **Agentic** - True multi-step reasoning
3. **Extensible** - Add more agents easily
4. **Traceable** - LangSmith integration
5. **Production-ready** - Similar to flight booking systems

## 📊 Next Steps

- [ ] Integrate real marketplace APIs
- [ ] Add voice input/output
- [ ] Implement RAG for product knowledge
- [ ] Add payment gateway
- [ ] Build UI/mobile app

## 🤝 Contributing

This is your college project. Extend it with:
- More marketplaces
- Better scoring logic
- Real API integrations
- UI components
