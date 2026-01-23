# 🎨 GANGU Frontend - Complete Setup Guide

## 📋 Overview

GANGU Frontend is a **voice-first, conversational UI** for the GANGU grocery assistant. Built with Next.js 14, React, and Tailwind CSS, it provides a magical, trustworthy experience for elderly users.

## ✨ Key Features

- 🎙️ **Voice-First Input** - Tap and speak naturally
- 🤖 **Live Agent Timeline** - See what GANGU is thinking
- 🛒 **Smart Product Comparison** - Visual cards with recommendations
- ✅ **Trust-Focused Confirmations** - Always verify before purchase
- 🎉 **Beautiful Success Screens** - Clear order confirmation
- 📱 **Responsive Design** - Works on mobile, tablet, and desktop

## 🏗️ Architecture

```
frontend/
├── app/                    # Next.js 14 App Router
│   ├── layout.tsx         # Root layout
│   └── page.tsx           # Main page
├── components/            # React Components
│   ├── VoiceInput.tsx    # Voice input with Web Speech API
│   ├── TextInput.tsx     # Text fallback
│   ├── AgentTimeline.tsx # Live agent status
│   ├── ProductComparison.tsx # Product cards
│   ├── OrderConfirmation.tsx # Confirmation modal
│   └── SuccessScreen.tsx # Order success
├── lib/                   # Utilities
│   ├── store.ts          # Zustand state management
│   └── api.ts            # API + WebSocket client
├── styles/
│   └── globals.css       # Tailwind + custom styles
└── package.json
```

## 🚀 Quick Start

### Prerequisites

- Node.js 18+ and npm
- Python 3.10+ (for backend)
- MongoDB (running on localhost:27017)

### 1. Install Frontend Dependencies

```powershell
cd frontend
npm install
```

### 2. Install Backend Dependencies

```powershell
cd ../api
pip install -r requirements.txt
```

### 3. Setup Environment Variables

```powershell
# Frontend
cp .env.local.example .env.local

# Backend (in GANGU root)
# Create .env with MongoDB and API keys
```

### 4. Start Backend API

```powershell
cd ../api
python main.py
```

Backend will start on `http://localhost:8000`

### 5. Start Frontend

```powershell
cd ../frontend
npm run dev
```

Frontend will start on `http://localhost:3000`

### 6. Open in Browser

Navigate to: **http://localhost:3000**

## 🎯 User Flow

```
1. USER SPEAKS/TYPES
   "White chane khatam ho gaye"
   ↓
2. VOICE INPUT COMPONENT
   Transcribes using Web Speech API
   ↓
3. AGENT TIMELINE SHOWS
   ✓ Understanding request
   ✓ Identifying: White Chickpeas
   ✓ Searching platforms
   ↓
4. PRODUCT COMPARISON
   Shows 3-6 product cards
   Highlights "Recommended by GANGU"
   ↓
5. USER CLICKS PRODUCT
   Confirmation modal appears
   ↓
6. USER CONFIRMS
   Real-time status:
   "Adding to cart..."
   "Checking out..."
   ↓
7. SUCCESS SCREEN
   🎉 Order placed!
   Shows order ID, delivery time
```

## 🎨 Design Philosophy

### Voice-First, Text-Second
- Big mic button as primary input
- Text input as fallback
- Natural language processing

### Transparency
- Live agent timeline
- Clear status updates
- No hidden actions

### Trust
- Always show confirmation before purchase
- Explain why GANGU chose this option
- Show all product details upfront

### Simplicity
- Large, readable fonts
- Minimal UI clutter
- Clear CTAs (Call-to-Action)

## 🔧 Key Components Explained

### 1. VoiceInput.tsx
```typescript
// Uses Web Speech API (Chrome/Edge)
const recognition = new webkitSpeechRecognition()
recognition.lang = 'hi-IN' // Hindi support
```

**Features:**
- Live transcription display
- Animated waveform while listening
- Editable transcription before submit

### 2. AgentTimeline.tsx
```typescript
// Receives real-time updates via WebSocket
ws.onmessage = (event) => {
  // Update UI as agents work
}
```

**Shows:**
- ✓ Intent extraction
- ✓ Task planning
- ✓ Search progress
- ✓ Comparison
- ✓ Decision

### 3. ProductComparison.tsx
```typescript
// Card-based comparison view
<ProductCard
  platform="Blinkit"
  price={89}
  rating={4.5}
  isRecommended={true}
  reasoning="Best price + fastest delivery"
/>
```

**Features:**
- Visual product cards
- Recommended badge
- Reasoning explanation
- Click to select

### 4. OrderConfirmation.tsx
```typescript
// Modal before purchase
"I'll place this order on Blinkit. Should I proceed?"
```

**Includes:**
- Product summary
- Price
- Delivery time
- Why GANGU recommends it
- Confirm/Change/Cancel buttons

## 🔌 API Integration

### REST Endpoints

```typescript
POST /api/chat/process
// Process user input through GANGU pipeline
{
  "message": "White chane le aao",
  "session_id": "session_123"
}

POST /api/order/confirm
// Confirm and place order
{
  "session_id": "session_123",
  "selected_product_index": 0
}
```

### WebSocket

```typescript
ws://localhost:8000/ws/{session_id}

// Receives real-time updates:
{
  "type": "agent_update",
  "step": "search",
  "status": "complete",
  "message": "Found 6 products",
  "data": {...}
}
```

## 🎨 Styling

### Color Palette

```css
--gangu-primary: #10B981   /* Calm green - trustworthy */
--gangu-secondary: #3B82F6 /* Soft blue */
--gangu-accent: #F59E0B    /* Warm amber */
--gangu-dark: #1F2937
--gangu-light: #F9FAFB
```

### Custom Classes

```css
.mic-button         /* Big mic button */
.gangu-card         /* Product/info cards */
.gangu-btn-primary  /* Primary action button */
.agent-step         /* Timeline step */
```

## 🌐 Browser Support

- ✅ Chrome 25+ (Voice input supported)
- ✅ Edge 79+ (Voice input supported)
- ⚠️ Firefox (Voice input NOT supported - text only)
- ⚠️ Safari (Limited voice support)

## 📱 Responsive Design

- **Mobile (< 640px)**: Single column, large touch targets
- **Tablet (640-1024px)**: 2 column grid for products
- **Desktop (> 1024px)**: 3 column grid, wider layout

## 🔐 Security

- No credentials stored in frontend
- API calls over HTTPS in production
- Session-based authentication
- CORS configured for allowed origins

## 🚀 Production Deployment

### Build Frontend

```powershell
cd frontend
npm run build
npm run start
```

### Deploy Options

1. **Vercel** (Recommended for Next.js)
```powershell
npm i -g vercel
vercel deploy
```

2. **Docker**
```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --production
COPY . .
RUN npm run build
CMD ["npm", "start"]
```

3. **Static Hosting** (if using `next export`)
```powershell
npm run build
npm run export
# Deploy 'out' folder to S3/Netlify/etc
```

## 🧪 Testing

```powershell
# Run development mode
npm run dev

# Test voice input (Chrome only)
1. Click mic button
2. Allow microphone access
3. Say "White chane le aao"
4. Verify transcription appears

# Test text input
1. Type "Doodh khatam ho gaya"
2. Press Enter or Send
3. Watch agent timeline

# Test comparison
1. Verify product cards appear
2. Check recommended badge
3. Click different products

# Test confirmation
1. Select a product
2. Verify modal shows correct details
3. Test Confirm/Cancel buttons
```

## 🐛 Troubleshooting

### Voice Input Not Working
```
Problem: Mic button doesn't work
Solution: 
  1. Use Chrome or Edge browser
  2. Allow microphone permissions
  3. Check HTTPS (required for mic access)
```

### WebSocket Connection Failed
```
Problem: "WebSocket disconnected"
Solution:
  1. Ensure backend API is running
  2. Check port 8000 is not blocked
  3. Verify WebSocket URL in .env.local
```

### Products Not Showing
```
Problem: Comparison cards don't appear
Solution:
  1. Check backend logs for errors
  2. Verify MongoDB is running
  3. Check MCP servers are running
  4. See browser console for API errors
```

## 📚 Next Steps

### Phase 2 Features (Future)
- [ ] User authentication
- [ ] Order history page
- [ ] Repeat last order
- [ ] Scheduled orders
- [ ] Multi-language support (full)
- [ ] WhatsApp integration
- [ ] Push notifications

### UI Enhancements
- [ ] Dark mode
- [ ] Custom themes
- [ ] Accessibility improvements (ARIA labels)
- [ ] Keyboard navigation
- [ ] Animation preferences

## 💡 Best Practices

### For Developers
1. Always test voice input in Chrome
2. Keep components small and focused
3. Use Zustand store for global state
4. Handle loading states gracefully
5. Show clear error messages

### For Designers
1. Large, tappable buttons (44x44px minimum)
2. High contrast text
3. Clear visual hierarchy
4. Meaningful animations only
5. Trust-focused design (show, don't hide)

## 📖 Additional Resources

- [Next.js Documentation](https://nextjs.org/docs)
- [Tailwind CSS](https://tailwindcss.com/docs)
- [Web Speech API](https://developer.mozilla.org/en-US/docs/Web/API/Web_Speech_API)
- [Zustand State Management](https://github.com/pmndrs/zustand)

## 🤝 Contributing

When adding new features:
1. Follow existing component structure
2. Update this README
3. Test on multiple browsers
4. Ensure responsive design
5. Add error handling

---

**Made with ❤️ for GANGU - Making grocery shopping magical**
