# Teacher Assist - Startup Guide

This guide explains how to start and stop the Teacher Assist application on different operating systems.

## Overview

Teacher Assist consists of two services that must run simultaneously:

1. **AI Service** (port 8001) - FastAPI service that generates educational metadata
2. **Django Web Server** (port 8000) - Web interface for lesson planning

## Prerequisites

- Python 3.11+ installed and in PATH
- All required packages installed (automatically handled by startup scripts)

## Linux / macOS

### Starting the Application

**Option 1: Using the startup script (recommended)**

```bash
./start.sh
```

This will:
- Check Python dependencies
- Install missing packages if needed
- Start both AI service and Django server
- Display service URLs and process IDs
- Keep running until you press Ctrl+C

**Option 2: Manual start**

Terminal 1 - AI Service:
```bash
python ai_service/main.py
```

Terminal 2 - Django Server:
```bash
cd webserver
python manage.py runserver
```

### Stopping the Application

- **If using start.sh**: Press `Ctrl+C` in the terminal
- **If running manually**: Press `Ctrl+C` in each terminal

### Log Files

When using `start.sh`, logs are saved to:
- `ai_service.log` - AI service logs
- `django.log` - Django server logs

## Windows

### Starting the Application

**Option 1: Desktop shortcut (easiest)**

1. Double-click `CREATE_DESKTOP_SHORTCUT.bat`
2. A shortcut will appear on your desktop
3. Double-click the desktop shortcut to start the application
4. The application will start silently and open in your browser

**Option 2: Using start.bat**

1. Double-click `start.bat`
2. Two minimized console windows will open (AI Service and Django)
3. Your web browser will automatically open to http://localhost:8000

**Option 3: Using start_silent.vbs**

1. Double-click `start_silent.vbs`
2. Services start in the background (no console windows)
3. A notification will appear when starting

### Stopping the Application

**Option 1: Using stop.bat**
1. Double-click `stop.bat`
2. Both services will be stopped

**Option 2: Close console windows**
1. Find the minimized console windows in taskbar
2. Close both windows

**Option 3: Task Manager**
1. Open Task Manager
2. End processes listening on ports 8000 and 8001

## Accessing the Application

After starting the services:

- **Web Interface**: http://localhost:8000
- **AI Service API Docs**: http://localhost:8001/docs
- **AI Service Health Check**: http://localhost:8001/health

## Troubleshooting

### Port Already in Use

If you see "Address already in use" error:

**Linux/macOS:**
```bash
# Find process using port 8000
lsof -i :8000
# Kill process
kill -9 <PID>

# Find process using port 8001
lsof -i :8001
# Kill process
kill -9 <PID>
```

**Windows:**
```batch
# Find and kill process on port 8000
netstat -ano | findstr :8000
taskkill /F /PID <PID>

# Find and kill process on port 8001
netstat -ano | findstr :8001
taskkill /F /PID <PID>
```

### Python Not Found

**Linux/macOS:**
- Install Python: https://www.python.org/downloads/
- Or use package manager: `sudo apt install python3` (Ubuntu) or `brew install python3` (macOS)

**Windows:**
- Install Python from: https://www.python.org/downloads/
- Make sure to check "Add Python to PATH" during installation

### Missing Dependencies

The startup scripts automatically install dependencies, but if manual installation is needed:

```bash
pip install -r requirements.txt
```

### Services Not Starting

1. Check if ports 8000 and 8001 are available
2. Review log files (Linux/macOS: `ai_service.log` and `django.log`)
3. Ensure Python 3.11+ is installed
4. Verify all dependencies are installed

### Browser Doesn't Open Automatically

Manually navigate to: http://localhost:8000

## Development Mode

To run services in development mode with auto-reload:

**AI Service:**
```bash
uvicorn ai_service.main:app --host 0.0.0.0 --port 8001 --reload
```

**Django:**
```bash
cd webserver
python manage.py runserver
```

## Testing

### Test AI Service

```bash
pytest ai_service/tests/ -v
```

### Test Django

```bash
cd webserver
python manage.py test lessonplanner
```

### Test Both

```bash
# AI Service
pytest ai_service/tests/ -v

# Django
cd webserver && python manage.py test lessonplanner
```

## File Structure

```
teacher_assist/
├── start.sh                      # Linux/macOS startup script
├── start.bat                     # Windows startup script (visible)
├── stop.bat                      # Windows stop script
├── start_silent.vbs              # Windows silent startup (no console)
├── CREATE_DESKTOP_SHORTCUT.bat   # Creates desktop shortcut
├── ai_service/                   # AI service application
│   ├── main.py                   # FastAPI entry point
│   ├── mock_service.py           # Mock AI logic
│   └── tests/                    # AI service tests
├── webserver/                    # Django application
│   └── manage.py                 # Django management script
└── common/                       # Shared Pydantic models
    └── models.py                 # API request/response schemas
```

## Additional Resources

- **Product Requirements**: `docs/PRD.md`
- **AI API Specification**: `docs/ai_api.md`
- **Django API Specification**: `docs/django_api.md`
- **Database Schema**: `docs/db_schema.md`
- **Development Guide**: `CLAUDE.md`

## Support

For issues or questions:
1. Check log files for error messages
2. Ensure all prerequisites are met
3. Try manual startup to isolate the issue
4. Review documentation in `docs/` directory
