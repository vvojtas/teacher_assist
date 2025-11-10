@echo off
REM Teacher Assist - Stop Application Script (Windows)
REM This script stops both the Django web server and the AI service

echo ============================================================
echo Teacher Assist - Stopping Application
echo ============================================================
echo.

REM Kill processes listening on port 8001 (AI Service)
echo Stopping AI Service (port 8001)...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8001') do (
    taskkill /F /PID %%a >nul 2>&1
)

REM Kill processes listening on port 8000 (Django)
echo Stopping Django Server (port 8000)...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000') do (
    taskkill /F /PID %%a >nul 2>&1
)

echo.
echo ============================================================
echo [SUCCESS] Services stopped.
echo ============================================================
echo.
pause
