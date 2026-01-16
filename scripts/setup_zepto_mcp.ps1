# Setup script for Zepto MCP Server integration
# Run this in PowerShell: .\setup_zepto_mcp.ps1

Write-Host "======================================" -ForegroundColor Cyan
Write-Host "Setting up Zepto MCP Server for GANGU" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan

# Step 1: Clone the Zepto MCP repo
Write-Host "`nStep 1: Cloning Zepto MCP Server..." -ForegroundColor Yellow
$currentDir = Get-Location
$targetDir = Join-Path $currentDir "zepto-cafe-mcp"

if (Test-Path $targetDir) {
    Write-Host "SUCCESS: Zepto MCP repo already exists at: $targetDir" -ForegroundColor Green
} else {
    git clone https://github.com/proddnav/zepto-cafe-mcp.git
    if ($LASTEXITCODE -eq 0) {
        Write-Host "SUCCESS: Successfully cloned Zepto MCP repo" -ForegroundColor Green
    } else {
        Write-Host "ERROR: Failed to clone repo. Please check git is installed." -ForegroundColor Red
        exit 1
    }
}

# Step 2: Install dependencies
Write-Host "`nStep 2: Installing dependencies..." -ForegroundColor Yellow
pip install playwright mcp python-dotenv httpx
if ($LASTEXITCODE -eq 0) {
    Write-Host "SUCCESS: Python packages installed" -ForegroundColor Green
} else {
    Write-Host "ERROR: Failed to install packages" -ForegroundColor Red
    exit 1
}

# Install Playwright browsers
Write-Host "`nInstalling Playwright Firefox..." -ForegroundColor Yellow
python -m playwright install firefox
if ($LASTEXITCODE -eq 0) {
    Write-Host "SUCCESS: Firefox installed" -ForegroundColor Green
} else {
    Write-Host "ERROR: Failed to install Firefox" -ForegroundColor Red
    exit 1
}

# Step 3: Setup environment variables
Write-Host "`nStep 3: Setting up environment variables..." -ForegroundColor Yellow
Write-Host "Please enter your Zepto phone number (e.g. 9876543210):" -ForegroundColor Cyan
$phoneNumber = Read-Host

Write-Host "Please enter your default address label (e.g. Home or Office):" -ForegroundColor Cyan
$address = Read-Host

# Create .env file in zepto-cafe-mcp directory
$envPath = Join-Path $targetDir ".env"
$envContent = @"
ZEPTO_PHONE_NUMBER=$phoneNumber
ZEPTO_DEFAULT_ADDRESS=$address
"@

Set-Content -Path $envPath -Value $envContent
Write-Host "Created .env file at: $envPath" -ForegroundColor Green

# Step 4: Run Firefox login setup
Write-Host "`nStep 4: Setting up Firefox login session..." -ForegroundColor Yellow
Write-Host "This will open Firefox. Please log in to Zepto manually." -ForegroundColor Cyan
Write-Host "Press Enter when ready to continue..." -ForegroundColor Yellow
$null = Read-Host

Push-Location $targetDir
python setup_firefox_login.py
Pop-Location

if ($LASTEXITCODE -eq 0) {
    Write-Host "SUCCESS: Firefox login session saved" -ForegroundColor Green
} else {
    Write-Host "WARNING: Login setup had issues, but you can try again later" -ForegroundColor Yellow
}

# Step 5: Test the client
Write-Host "`nStep 5: Testing Zepto MCP client..." -ForegroundColor Yellow
Write-Host "Running test..." -ForegroundColor Cyan

python zepto_mcp_client.py

# Final instructions
Write-Host "`n" -ForegroundColor Green
Write-Host "======================================" -ForegroundColor Green
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "======================================" -ForegroundColor Green
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Cyan
Write-Host "1. Update your Search Agent to use Zepto MCP client" -ForegroundColor White
Write-Host "2. Test the integration: python zepto_mcp_client.py" -ForegroundColor White
Write-Host "3. Run GANGU: python gangu_main.py" -ForegroundColor White
Write-Host ""
Write-Host "Zepto MCP Server location: $targetDir" -ForegroundColor Cyan
Write-Host "Environment variables saved in: $envPath" -ForegroundColor Cyan
Write-Host ""
