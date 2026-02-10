# 🚀 GANGU Production Deployment Guide

## 📋 Overview

This guide covers deploying GANGU's frontend and backend to production.

---

## 🏗️ Architecture Options

### Option 1: Separated Deployment (Recommended)

```
┌─────────────────┐
│   Vercel/CDN    │ ← Frontend (Next.js)
│  gangu-app.com  │
└────────┬────────┘
         │ HTTPS
         ↓
┌─────────────────┐
│  Cloud Server   │ ← Backend (FastAPI)
│ api.gangu.com   │
│   (EC2/Azure)   │
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│ MongoDB Atlas   │ ← Database
└─────────────────┘
```

### Option 2: Unified Deployment

```
┌─────────────────────────┐
│    Cloud Server         │
│  ├── Frontend (3000)    │ ← Nginx reverse proxy
│  └── Backend (8000)     │
└────────┬────────────────┘
         │
         ↓
┌─────────────────┐
│ MongoDB Atlas   │
└─────────────────┘
```

---

## 🔧 Pre-Deployment Checklist

### Backend
- [ ] Environment variables configured
- [ ] MongoDB connection string set
- [ ] API keys secured (Google Gemini)
- [ ] CORS origins updated for production
- [ ] Logging configured
- [ ] Error monitoring setup (Sentry)
- [ ] Rate limiting enabled
- [ ] HTTPS certificate ready

### Frontend
- [ ] Environment variables set
- [ ] API URL points to production backend
- [ ] WebSocket URL configured
- [ ] Build tested locally
- [ ] Images optimized
- [ ] Analytics added (optional)
- [ ] Error tracking setup (optional)

---

## 📦 Backend Deployment

### Option A: AWS EC2

#### 1. Launch EC2 Instance
```powershell
# t2.medium or t3.medium recommended
# Ubuntu 22.04 LTS
# Open ports: 80, 443, 8000
```

#### 2. Install Dependencies
```bash
# SSH into instance
ssh ubuntu@your-ec2-ip

# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.10+
sudo apt install python3.10 python3-pip -y

# Install Nginx (for reverse proxy)
sudo apt install nginx -y
```

#### 3. Deploy Backend Code
```bash
# Clone repository
git clone https://github.com/your-username/GANGU.git
cd GANGU

# Install Python dependencies
pip3 install -r api/requirements.txt
pip3 install -r config/requirements.txt

# Setup environment
nano .env
# Add your keys:
# GOOGLE_API_KEY=...
# MONGODB_URI=mongodb+srv://...
```

#### 4. Setup Systemd Service
```bash
# Create service file
sudo nano /etc/systemd/system/gangu-api.service
```

```ini
[Unit]
Description=GANGU FastAPI Backend
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/GANGU
Environment="PATH=/home/ubuntu/.local/bin"
ExecStart=/home/ubuntu/.local/bin/uvicorn api.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl enable gangu-api
sudo systemctl start gangu-api
sudo systemctl status gangu-api
```

#### 5. Configure Nginx Reverse Proxy
```bash
sudo nano /etc/nginx/sites-available/gangu-api
```

```nginx
server {
    listen 80;
    server_name api.gangu.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # WebSocket support
    location /ws {
        proxy_pass http://localhost:8000/ws;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/gangu-api /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

#### 6. Setup SSL with Let's Encrypt
```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d api.gangu.com
```

### Option B: Azure App Service

```bash
# Install Azure CLI
az login

# Create resource group
az group create --name gangu-rg --location eastus

# Create App Service plan
az appservice plan create --name gangu-plan --resource-group gangu-rg --sku B1 --is-linux

# Create web app
az webapp create --resource-group gangu-rg --plan gangu-plan --name gangu-api --runtime "PYTHON:3.10"

# Deploy code
az webapp up --resource-group gangu-rg --name gangu-api --runtime "PYTHON:3.10"

# Configure environment variables
az webapp config appsettings set --resource-group gangu-rg --name gangu-api --settings \
    GOOGLE_API_KEY="your-key" \
    MONGODB_URI="your-mongodb-uri"
```

### Option C: Docker Deployment

```bash
# Create Dockerfile
cd GANGU
nano Dockerfile
```

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY config/requirements.txt .
COPY api/requirements.txt api/
RUN pip install --no-cache-dir -r requirements.txt -r api/requirements.txt

# Copy code
COPY . .

# Expose port
EXPOSE 8000

# Run server
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
# Build and run
docker build -t gangu-backend .
docker run -d -p 8000:8000 --env-file .env gangu-backend

# Or use docker-compose
docker-compose up -d
```

---

## 🎨 Frontend Deployment

### Option A: Vercel (Recommended)

#### 1. Install Vercel CLI
```powershell
npm i -g vercel
```

#### 2. Deploy from Frontend Directory
```powershell
cd frontend
vercel login
vercel
```

#### 3. Configure Environment Variables
In Vercel dashboard:
- `NEXT_PUBLIC_API_URL` = `https://api.gangu.com`
- `NEXT_PUBLIC_WS_URL` = `wss://api.gangu.com`

#### 4. Custom Domain (Optional)
```powershell
vercel domains add gangu.com
```

### Option B: Netlify

```powershell
# Install Netlify CLI
npm i -g netlify-cli

# Deploy
cd frontend
netlify login
netlify deploy --prod
```

### Option C: Static Export to S3/CDN

```powershell
# Build static export
cd frontend
npm run build

# For static export, update next.config.js:
# output: 'export'

# Upload 'out' folder to S3
aws s3 sync out/ s3://gangu-frontend --acl public-read

# Or use CloudFront CDN
```

### Option D: Same Server as Backend

```bash
# Build frontend
cd frontend
npm run build

# Copy build to server
scp -r .next/ ubuntu@your-server:/var/www/gangu-frontend/

# Configure Nginx
sudo nano /etc/nginx/sites-available/gangu-frontend
```

```nginx
server {
    listen 80;
    server_name gangu.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

```bash
# Run Next.js in production
cd /var/www/gangu-frontend
npm install
npm run build
npm start
```

---

## 🗄️ Database Setup

### MongoDB Atlas (Recommended)

#### 1. Create Cluster
- Go to [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
- Create free M0 cluster
- Choose region closest to your backend

#### 2. Configure Network Access
- Add IP address: `0.0.0.0/0` (or specific IPs)
- Create database user

#### 3. Get Connection String
```
mongodb+srv://username:password@cluster.mongodb.net/gangu?retryWrites=true&w=majority
```

#### 4. Update Backend Environment
```bash
MONGODB_URI=mongodb+srv://...
```

---

## 🔐 Security Best Practices

### Backend
```python
# api/main.py

# 1. Update CORS origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://gangu.com",
        "https://www.gangu.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. Add rate limiting
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/api/chat/process")
@limiter.limit("10/minute")
async def process_chat(request: Request, ...):
    ...

# 3. Add API key authentication (optional)
from fastapi import Security, HTTPException
from fastapi.security.api_key import APIKeyHeader

api_key_header = APIKeyHeader(name="X-API-Key")

async def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key != os.getenv("API_KEY"):
        raise HTTPException(status_code=403, detail="Invalid API Key")
    return api_key
```

### Frontend
```typescript
// frontend/.env.production
NEXT_PUBLIC_API_URL=https://api.gangu.com
NEXT_PUBLIC_WS_URL=wss://api.gangu.com

// No sensitive keys in frontend!
```

---

## 📊 Monitoring & Logging

### Backend Logging
```python
# api/main.py
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('gangu.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

@app.post("/api/chat/process")
async def process_chat(...):
    logger.info(f"Processing chat for session: {session_id}")
    ...
```

### Error Tracking (Sentry)
```bash
pip install sentry-sdk[fastapi]
```

```python
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn="your-sentry-dsn",
    integrations=[FastApiIntegration()],
)
```

### Uptime Monitoring
- Use [UptimeRobot](https://uptimerobot.com/) (free)
- Monitor: `https://api.gangu.com/` (health check)
- Monitor: `https://gangu.com` (frontend)

---

## 🧪 Production Testing

### Backend Health Check
```bash
curl https://api.gangu.com/
# Should return: {"status": "healthy", ...}
```

### WebSocket Test
```javascript
const ws = new WebSocket('wss://api.gangu.com/ws/test123');
ws.onopen = () => console.log('Connected!');
```

### Load Testing
```bash
# Install Apache Bench
sudo apt install apache2-utils

# Test API endpoint
ab -n 1000 -c 10 https://api.gangu.com/
```

---

## 📈 Performance Optimization

### Backend
```python
# Enable gzip compression
from fastapi.middleware.gzip import GZipMiddleware
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Add caching
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

@app.on_event("startup")
async def startup():
    redis = aioredis.from_url("redis://localhost")
    FastAPICache.init(RedisBackend(redis), prefix="gangu-cache")
```

### Frontend
```javascript
// next.config.js
module.exports = {
  compress: true,
  images: {
    domains: ['your-image-cdn.com'],
    formats: ['image/avif', 'image/webp'],
  },
  poweredByHeader: false,
}
```

---

## 💰 Cost Estimation (Monthly)

### Minimal Setup (< $50/month)
- **Frontend**: Vercel Free Tier ($0)
- **Backend**: AWS t3.micro ($8)
- **Database**: MongoDB Atlas M0 ($0)
- **Domain**: Namecheap ($1)
- **SSL**: Let's Encrypt ($0)
- **Total**: ~$10/month

### Production Setup (< $100/month)
- **Frontend**: Vercel Pro ($20)
- **Backend**: AWS t3.small ($17)
- **Database**: MongoDB Atlas M10 ($57)
- **Total**: ~$95/month

### Enterprise Setup ($500+/month)
- **Frontend**: Vercel Enterprise
- **Backend**: AWS t3.medium + Auto-scaling
- **Database**: MongoDB Atlas M30+
- **CDN**: CloudFront
- **Monitoring**: Datadog/New Relic

---

## 🔄 CI/CD Pipeline

### GitHub Actions

```yaml
# .github/workflows/deploy.yml
name: Deploy GANGU

on:
  push:
    branches: [main]

jobs:
  deploy-backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy to EC2
        run: |
          ssh ubuntu@your-server "cd GANGU && git pull && systemctl restart gangu-api"

  deploy-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy to Vercel
        run: |
          cd frontend
          vercel deploy --prod --token ${{ secrets.VERCEL_TOKEN }}
```

---

## 🐛 Troubleshooting Production

### Backend Issues
```bash
# Check logs
sudo journalctl -u gangu-api -f

# Check process
ps aux | grep uvicorn

# Check port
sudo netstat -tulpn | grep 8000

# Restart service
sudo systemctl restart gangu-api
```

### Frontend Issues
```bash
# Check Vercel logs
vercel logs

# Check build
npm run build
```

### Database Issues
```bash
# Test MongoDB connection
mongosh "mongodb+srv://..."

# Check collections
show dbs
use gangu
show collections
```

---

## ✅ Post-Deployment Checklist

- [ ] Backend health check passing
- [ ] Frontend loading correctly
- [ ] Voice input working (Chrome/Edge)
- [ ] WebSocket connection stable
- [ ] Agent pipeline completing
- [ ] Products displaying correctly
- [ ] Order confirmation working
- [ ] SSL certificates valid
- [ ] CORS configured correctly
- [ ] Environment variables secure
- [ ] Monitoring setup
- [ ] Backups configured
- [ ] Domain configured
- [ ] Analytics added (optional)

---

## 🎉 You're Live!

Your GANGU app is now running in production! 🚀

**Share it with users and watch the magic happen! ✨**
