# 🔌 GANGU Backend API

FastAPI backend server with WebSocket support for real-time agent updates.

## 🚀 Quick Start

```powershell
# Install dependencies
pip install -r requirements.txt

# Run server
python main.py

# Server starts on http://localhost:8000
```

## 📡 API Endpoints

### Health Check
```http
GET /
```
Returns server status.

### Process Chat
```http
POST /api/chat/process
Content-Type: application/json

{
  "message": "White chane le aao",
  "session_id": "session_123"
}
```
Main endpoint - runs complete GANGU pipeline.

**Response:**
```json
{
  "success": true,
  "session_id": "session_123",
  "intent": {...},
  "comparison": {...},
  "recommendation": {...},
  "requires_confirmation": true
}
```

### Confirm Order
```http
POST /api/order/confirm
Content-Type: application/json

{
  "session_id": "session_123",
  "selected_product_index": 0
}
```
Confirms and places order.

**Response:**
```json
{
  "success": true,
  "order_id": "ORD-1234567890",
  "message": "Order placed successfully",
  "estimated_delivery": "Today by 7:00 PM"
}
```

### Get Session
```http
GET /api/session/{session_id}
```
Retrieves session data.

### Get History
```http
GET /api/history
```
Gets order history (future feature).

## 🔌 WebSocket

### Connect
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/session_123');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Agent update:', data);
};
```

### Message Format
```json
{
  "type": "agent_update",
  "session_id": "session_123",
  "step": "search",
  "status": "complete",
  "message": "Found 6 products",
  "data": {...},
  "timestamp": "2025-01-19T..."
}
```

## 🔧 Configuration

### Environment Variables
Create `.env` in GANGU root:
```env
GOOGLE_API_KEY=your-gemini-api-key
MONGODB_URI=mongodb://localhost:27017
```

### CORS
Update `main.py` to add your frontend URL:
```python
allow_origins=[
    "http://localhost:3000",
    "https://yourdomain.com"
]
```

## 🧪 Testing

### Test Health Check
```powershell
curl http://localhost:8000/
```

### Test Chat Processing
```powershell
curl -X POST http://localhost:8000/api/chat/process `
  -H "Content-Type: application/json" `
  -d '{\"message\": \"White chane le aao\"}'
```

### Test WebSocket
```javascript
// In browser console
const ws = new WebSocket('ws://localhost:8000/ws/test');
ws.onopen = () => console.log('Connected!');
ws.onmessage = (e) => console.log(JSON.parse(e.data));
```

## 📦 Dependencies

- **FastAPI**: REST API framework
- **Uvicorn**: ASGI server with WebSocket support
- **WebSockets**: WebSocket support
- **Python-multipart**: Form data handling

## 🔍 Debugging

### Check Logs
Server logs appear in terminal where you ran `python main.py`.

### Common Issues

**Port already in use:**
```powershell
# Kill process on port 8000
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

**MongoDB connection failed:**
```powershell
# Start MongoDB
docker-compose up -d
```

**GANGU graph errors:**
Check that all agent dependencies are installed:
```powershell
cd ..
pip install -r config/requirements.txt
```

## 📚 Next Steps

- See [FRONTEND_ARCHITECTURE.md](../docs/FRONTEND_ARCHITECTURE.md) for system design
- See [DEPLOYMENT_GUIDE.md](../DEPLOYMENT_GUIDE.md) for production deployment
- See [main.py](main.py) for implementation details
