@echo off
REM Teacher Assist - Create Desktop Shortcut (Windows)
REM This script creates a desktop shortcut for Teacher Assist

setlocal

REM Get project root directory
set "PROJECT_ROOT=%~dp0"

REM Get user's desktop path
set "DESKTOP=%USERPROFILE%\Desktop"

REM Create shortcut using PowerShell
echo Creating desktop shortcut...

powershell -Command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%DESKTOP%\Teacher Assist.lnk'); $Shortcut.TargetPath = '%PROJECT_ROOT%start_silent.vbs'; $Shortcut.WorkingDirectory = '%PROJECT_ROOT%'; $Shortcut.Description = 'Teacher Assist - AI-Powered Lesson Planning Tool'; $Shortcut.Save()"

if %errorlevel% equ 0 (
    echo.
    echo ============================================================
    echo [SUCCESS] Desktop shortcut created!
    echo ============================================================
    echo.
    echo Location: %DESKTOP%\Teacher Assist.lnk
    echo.
    echo Double-click the shortcut on your desktop to start the application.
    echo.
) else (
    echo.
    echo [ERROR] Failed to create desktop shortcut
    echo.
)

pause
