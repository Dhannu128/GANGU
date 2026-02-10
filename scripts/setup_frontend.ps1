<#
Frontend setup script.

This project uses a static frontend served by FastAPI at /app.
No Node/Tailwind build step is required.

Usage:
  powershell -ExecutionPolicy Bypass -File .\scripts\setup_frontend.ps1
#>

Write-Host "✅ No frontend build needed." -ForegroundColor Green
Write-Host "Open the UI after starting the API: http://localhost:8000/app" -ForegroundColor Cyan
