# GANGU Frontend & Backend Setup Script
# Run this from the GANGU root directory

Write-Host "`n================================" -ForegroundColor Cyan
Write-Host "🚀 GANGU Setup Script" -ForegroundColor Cyan
Write-Host "================================`n" -ForegroundColor Cyan

# Check if we're in the right directory
if (-not (Test-Path "orchestration")) {
    Write-Host "❌ Please run this script from the GANGU root directory" -ForegroundColor Red
    exit 1
}

Write-Host "📂 Current directory: $(Get-Location)`n" -ForegroundColor Yellow

# Step 1: Install Backend API Dependencies
Write-Host "`n[1/5] Installing Backend API Dependencies..." -ForegroundColor Green
cd api
if (Test-Path "requirements.txt") {
    pip install -r requirements.txt
    Write-Host "✅ Backend dependencies installed" -ForegroundColor Green
} else {
    Write-Host "❌ api/requirements.txt not found" -ForegroundColor Red
    exit 1
}
cd ..

# Step 2: Check MongoDB
Write-Host "`n[2/5] Checking MongoDB Connection..." -ForegroundColor Green
$mongoRunning = Test-Connection -ComputerName localhost -Port 27017 -ErrorAction SilentlyContinue
if ($mongoRunning) {
    Write-Host "✅ MongoDB is running on localhost:27017" -ForegroundColor Green
} else {
    Write-Host "⚠️ MongoDB not detected on localhost:27017" -ForegroundColor Yellow
    Write-Host "   Start MongoDB with: docker-compose up -d" -ForegroundColor Yellow
}

# Step 3: Install Frontend Dependencies
Write-Host "`n[3/5] Installing Frontend Dependencies..." -ForegroundColor Green
cd frontend
if (Test-Path "package.json") {
    npm install
    Write-Host "✅ Frontend dependencies installed" -ForegroundColor Green
} else {
    Write-Host "❌ frontend/package.json not found" -ForegroundColor Red
    exit 1
}

# Step 4: Setup Environment Variables
Write-Host "`n[4/5] Setting up Environment Variables..." -ForegroundColor Green
if (-not (Test-Path ".env.local")) {
    if (Test-Path ".env.local.example") {
        Copy-Item ".env.local.example" ".env.local"
        Write-Host "✅ Created .env.local from example" -ForegroundColor Green
    }
} else {
    Write-Host "✅ .env.local already exists" -ForegroundColor Green
}
cd ..

# Step 5: Verify Setup
Write-Host "`n[5/5] Verifying Setup..." -ForegroundColor Green
$issues = @()

# Check Python
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python: $pythonVersion" -ForegroundColor Green
} catch {
    $issues += "Python not found"
    Write-Host "❌ Python not found" -ForegroundColor Red
}

# Check Node
try {
    $nodeVersion = node --version
    Write-Host "✅ Node: $nodeVersion" -ForegroundColor Green
} catch {
    $issues += "Node.js not found"
    Write-Host "❌ Node.js not found" -ForegroundColor Red
}

# Check npm
try {
    $npmVersion = npm --version
    Write-Host "✅ npm: $npmVersion" -ForegroundColor Green
} catch {
    $issues += "npm not found"
    Write-Host "❌ npm not found" -ForegroundColor Red
}

# Summary
Write-Host "`n================================" -ForegroundColor Cyan
Write-Host "📋 Setup Summary" -ForegroundColor Cyan
Write-Host "================================`n" -ForegroundColor Cyan

if ($issues.Count -eq 0) {
    Write-Host "✅ All checks passed! Setup complete." -ForegroundColor Green
    Write-Host "`n🚀 To start GANGU:" -ForegroundColor Yellow
    Write-Host "`n1. Start Backend API:" -ForegroundColor White
    Write-Host "   cd api" -ForegroundColor Gray
    Write-Host "   python main.py" -ForegroundColor Gray
    Write-Host "`n2. Start Frontend (in new terminal):" -ForegroundColor White
    Write-Host "   cd frontend" -ForegroundColor Gray
    Write-Host "   npm run dev" -ForegroundColor Gray
    Write-Host "`n3. Open browser:" -ForegroundColor White
    Write-Host "   http://localhost:3000" -ForegroundColor Cyan
    Write-Host "`n📚 For more info, see frontend/README.md`n" -ForegroundColor Yellow
} else {
    Write-Host "⚠️ Setup completed with warnings:" -ForegroundColor Yellow
    foreach ($issue in $issues) {
        Write-Host "   - $issue" -ForegroundColor Red
    }
}
