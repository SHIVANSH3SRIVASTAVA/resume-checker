@echo off
REM === Change to project directory ===
cd /d "%~dp0"

REM === Check for Python 3.10 ===
where py >nul 2>nul
if %errorlevel% neq 0 (
    echo Python launcher not found. Please install Python 3.10 (64-bit) and try again.
    pause
    exit /b
)

REM === Create venv if missing ===
if not exist ".venv" (
    echo Creating virtual environment with Python 3.10...
    py -3.10 -m venv .venv
)

REM === Activate venv ===
call .venv\Scripts\activate

REM === Upgrade pip, wheel, setuptools ===
python -m pip install --upgrade pip wheel setuptools

REM === Install requirements ===
pip install -r requirements.txt

REM === Download spaCy model if missing ===
python -m spacy validate | findstr /C:"en_core_web_sm" >nul
if %errorlevel% neq 0 (
    echo Downloading spaCy model...
    python -m spacy download en_core_web_sm
)

REM === Check if backend is running on port 8000 ===
echo Checking if backend is running...
powershell -Command "if (-not (Test-NetConnection -ComputerName 127.0.0.1 -Port 8000).TcpTestSucceeded) { exit 1 } else { exit 0 }"
if %errorlevel% neq 0 (
    echo Starting backend...
    start "Backend" cmd /k ".venv\Scripts\activate && uvicorn app.main:app --reload"
) else (
    echo Backend already running.
)

REM === Delay to ensure backend starts ===
timeout /t 3 >nul

REM === Start frontend ===
start "Frontend" cmd /k ".venv\Scripts\activate && streamlit run frontend/streamlit_app.py"

REM === Open frontend in browser ===
timeout /t 5 >nul
start "http://localhost:8501"

echo All set! Backend and frontend are running.
pause
