# GANGU Development Server Launcher
# Starts both backend and frontend in separate windows

Write-Host "`n[START] Starting GANGU Development Servers..." -ForegroundColor Cyan

# Get the GANGU root directory
$ganguRoot = Split-Path -Parent $PSScriptRoot

Write-Host "[INFO] GANGU Root: $ganguRoot`n" -ForegroundColor Yellow

# Start Backend API in new window
Write-Host "Starting Backend API on http://localhost:8000..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "$env:PYTHONIOENCODING='utf-8'; cd `"$ganguRoot\api`"; python main.py"

# Wait a bit for backend to start
Start-Sleep -Seconds 3

# Start Frontend in new window
Write-Host "Starting Frontend on http://localhost:3000..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd `"$ganguRoot\frontend`"; npm run dev"

Write-Host "`n[OK] Both servers are starting..." -ForegroundColor Green
Write-Host "`n[ACTION] Open your browser to: http://localhost:3000" -ForegroundColor Cyan
Write-Host "`n[NOTE] Close both PowerShell windows to stop servers`n" -ForegroundColor Yellow
