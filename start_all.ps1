# start_all.ps1
# Change to the folder where this script is located
Set-Location -Path $PSScriptRoot

Write-Host "=== Resume Checker Launcher ===" -ForegroundColor Cyan

# Check Python 3.10
if (-not (Get-Command "py" -ErrorAction SilentlyContinue)) {
    Write-Host "Python launcher not found. Please install Python 3.10 (64-bit) and try again." -ForegroundColor Red
    Pause
    exit
}

# Check for requirements.txt
if (-not (Test-Path "requirements.txt")) {
    Write-Host "Missing requirements.txt. Please add it to the project root." -ForegroundColor Red
    Pause
    exit
}

# Create venv if missing
if (-not (Test-Path ".venv")) {
    Write-Host "Creating virtual environment..."
    py -3.10 -m venv .venv
}

# Activate venv
& .\.venv\Scripts\Activate.ps1

# Upgrade pip, wheel, setuptools
python -m pip install --upgrade pip wheel setuptools

# Install requirements
pip install -r requirements.txt

# Ensure critical packages are installed
$required = @("python-multipart", "python-docx", "PyPDF2")
foreach ($pkg in $required) {
    $check = pip show $pkg
    if (-not $check) {
        Write-Host "Installing missing package: $pkg"
        pip install $pkg
    }
}

# Download spaCy model if missing
$spacyCheck = python -m spacy validate | Select-String "en_core_web_sm"
if (-not $spacyCheck) {
    Write-Host "Downloading spaCy model..."
    python -m spacy download en_core_web_sm
}

# Start backend if not running
$backendRunning = Test-NetConnection -ComputerName 127.0.0.1 -Port 8000 -WarningAction SilentlyContinue
if (-not $backendRunning.TcpTestSucceeded) {
    Write-Host "Starting backend..."
    Start-Process powershell -ArgumentList "cd `"$PSScriptRoot`"; .\.venv\Scripts\Activate.ps1; uvicorn app.main:app --reload"
} else {
    Write-Host "Backend already running."
}

# Wait until backend is ready
Write-Host "Waiting for backend to respond..."
$maxTries = 10
$tries = 0
do {
    Start-Sleep -Seconds 1
    $backendReady = Test-NetConnection -ComputerName 127.0.0.1 -Port 8000 -WarningAction SilentlyContinue
    $tries++
} until ($backendReady.TcpTestSucceeded -or $tries -ge $maxTries)

if (-not $backendReady.TcpTestSucceeded) {
    Write-Host "Backend failed to start after 10 seconds." -ForegroundColor Red
    Pause
    exit
}

# Start frontend
Write-Host "Starting frontend..."
Start-Process powershell -ArgumentList "cd `"$PSScriptRoot`"; .\.venv\Scripts\Activate.ps1; streamlit run frontend/streamlit_app.py"

Start-Sleep -Seconds 5
Start-Process "http://localhost:8501"

Write-Host "✅ All set! Backend and frontend are running." -ForegroundColor Green
Pause
