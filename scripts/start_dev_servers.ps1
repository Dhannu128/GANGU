<#
Starts the FastAPI backend (which also serves the static UI at /app).

Usage:
  powershell -ExecutionPolicy Bypass -File .\scripts\start_dev_servers.ps1
#>

$ErrorActionPreference = "Stop"

Write-Host "Starting GANGU API (FastAPI) on http://localhost:8000 ..." -ForegroundColor Cyan

# Prefer venv python if present
$python = "python"

# Start uvicorn
# Note: We intentionally run a single server; the UI is served at /app
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
