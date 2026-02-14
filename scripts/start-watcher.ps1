# Start Bronze Tier Watcher
# This script activates the virtual environment and launches the watcher

$ErrorActionPreference = "Stop"

$venvPath = "E:\AI_Employee_Vault\venv\Scripts\python.exe"
$scriptPath = "E:\AI_Employee_Vault\src\watcher\watcher.py"

Write-Host "Starting Bronze Tier Watcher..." -ForegroundColor Green
Write-Host ""

# Check if venv exists
if (-not (Test-Path $venvPath)) {
    Write-Host "ERROR: Virtual environment not found at $venvPath" -ForegroundColor Red
    Write-Host "Please run: python -m venv venv" -ForegroundColor Yellow
    exit 1
}

# Check if watcher script exists
if (-not (Test-Path $scriptPath)) {
    Write-Host "ERROR: Watcher script not found at $scriptPath" -ForegroundColor Red
    exit 1
}

# Launch watcher
& $venvPath $scriptPath
