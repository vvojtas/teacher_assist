@echo off
REM Teacher Assist - Application Startup Script (Windows)
REM This script starts both the Django web server and the AI service

setlocal enabledelayedexpansion

REM Get project root directory
set "PROJECT_ROOT=%~dp0"
cd /d "%PROJECT_ROOT%"

REM Colors and formatting
echo ============================================================
echo Teacher Assist - Starting Application
echo ============================================================
echo.

REM Check if Python is available
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.11+ from python.org
    pause
    exit /b 1
)

REM Check Python version
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo Using Python: %PYTHON_VERSION%

REM Check if virtual environment exists, create if not
if not exist "%PROJECT_ROOT%.venv\" (
    echo.
    echo [INFO] Creating virtual environment in .venv\
    python -m venv "%PROJECT_ROOT%.venv"
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to create virtual environment
        pause
        exit /b 1
    )
    echo [SUCCESS] Virtual environment created
)

REM Activate virtual environment
echo Activating virtual environment...
call "%PROJECT_ROOT%.venv\Scripts\activate.bat"
if %errorlevel% neq 0 (
    echo [ERROR] Failed to activate virtual environment
    pause
    exit /b 1
)

REM Check if required packages are installed
echo.
echo Checking Python dependencies...
python -c "import django; import fastapi; import requests" >nul 2>&1
if %errorlevel% neq 0 (
    echo [INFO] Installing required Python packages...
    python -m pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to install dependencies
        pause
        exit /b 1
    )
)

REM Install project in editable mode for proper package imports
echo Checking package installation...
python -c "import common.models" >nul 2>&1
if %errorlevel% neq 0 (
    echo [INFO] Installing teacher-assist package in editable mode...
    python -m pip install -e . --quiet >nul 2>&1
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to install package
        pause
        exit /b 1
    )
    echo [SUCCESS] Package installed successfully
)

echo.
echo Starting services...
echo.

REM Start AI Service (port 8001) in new window
echo [1/2] Starting AI Service on http://localhost:8001
start "Teacher Assist - AI Service" /MIN python ai_service/main.py
timeout /t 3 /nobreak >nul
echo       Started in minimized window

REM Start Django Web Server (port 8000) in new window
echo.
echo [2/2] Starting Django Web Server on http://localhost:8000
start "Teacher Assist - Django Server" /MIN python webserver/manage.py runserver 127.0.0.1:8000
timeout /t 3 /nobreak >nul
echo       Started in minimized window

echo.
echo ============================================================
echo [SUCCESS] Application started successfully!
echo ============================================================
echo.
echo Services running:
echo   * AI Service:    http://localhost:8001
echo   * Web Interface: http://localhost:8000
echo.
echo API Documentation:
echo   * AI Service Docs: http://localhost:8001/docs
echo   * Health Check:    http://localhost:8001/health
echo.
echo ============================================================
echo.
echo Opening web browser...
timeout /t 2 /nobreak >nul
start http://localhost:8000
echo.
echo ============================================================
echo.
echo To stop the application:
echo   * Close both minimized console windows
echo.
echo You can close this window now.
echo.
pause
