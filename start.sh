#!/bin/bash

# Teacher Assist - Application Startup Script (Linux/Mac)
# This script starts both the Django web server and the AI service

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Project root directory
PROJECT_ROOT="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$PROJECT_ROOT"

# Log files
AI_SERVICE_LOG="$PROJECT_ROOT/ai_service.log"
DJANGO_LOG="$PROJECT_ROOT/django.log"
VENV_DIR="$PROJECT_ROOT/.venv"

echo "============================================================"
echo -e "${BLUE}Teacher Assist - Starting Application${NC}"
echo "============================================================"

# Check if Python is available
if ! command -v python &> /dev/null && ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python is not installed or not in PATH${NC}"
    exit 1
fi

# Use python3 if available, otherwise python
PYTHON_CMD="python3"
if ! command -v python3 &> /dev/null; then
    PYTHON_CMD="python"
fi

echo -e "${GREEN}Using Python: $PYTHON_CMD${NC}"

# Check if virtual environment exists, create if not
if [ ! -d "$VENV_DIR" ]; then
    echo ""
    echo -e "${YELLOW}Creating virtual environment in .venv/${NC}"
    $PYTHON_CMD -m venv "$VENV_DIR"
    if [ $? -ne 0 ]; then
        echo -e "${RED}Error: Failed to create virtual environment${NC}"
        exit 1
    fi
    echo -e "${GREEN}Virtual environment created${NC}"
fi

# Activate virtual environment
echo "Activating virtual environment..."
source "$VENV_DIR/bin/activate"
if [ $? -ne 0 ]; then
    echo -e "${RED}Error: Failed to activate virtual environment${NC}"
    exit 1
fi

# Update PYTHON_CMD to use venv python
PYTHON_CMD="$VENV_DIR/bin/python"

# Check if required packages are installed
echo ""
echo "Checking Python dependencies..."
$PYTHON_CMD -c "import django; import fastapi; import requests" 2>/dev/null
if [ $? -ne 0 ]; then
    echo -e "${YELLOW}Installing required Python packages...${NC}"
    $PYTHON_CMD -m pip install -r requirements.txt
fi

# Install project in editable mode for proper package imports
echo "Checking package installation..."
$PYTHON_CMD -c "import common.models" 2>/dev/null
if [ $? -ne 0 ]; then
    echo -e "${YELLOW}Installing teacher-assist package in editable mode...${NC}"
    $PYTHON_CMD -m pip install -e . --quiet
    if [ $? -ne 0 ]; then
        echo -e "${RED}Error: Failed to install package${NC}"
        exit 1
    fi
    echo -e "${GREEN}Package installed successfully${NC}"
fi

echo ""
echo -e "${GREEN}Starting services...${NC}"
echo ""

# Start AI Service (port 8001) in background
echo -e "${BLUE}[1/2] Starting AI Service on http://localhost:8001${NC}"
$PYTHON_CMD ai_service/main.py > "$AI_SERVICE_LOG" 2>&1 &
AI_SERVICE_PID=$!
echo "      AI Service PID: $AI_SERVICE_PID"
echo "      Log file: $AI_SERVICE_LOG"

# Wait for AI service to start
echo "      Waiting for AI service to start..."
sleep 3

# Check if AI service is running
if ! ps -p $AI_SERVICE_PID > /dev/null; then
    echo -e "${RED}      Error: AI Service failed to start. Check $AI_SERVICE_LOG${NC}"
    exit 1
fi

# Start Django Web Server (port 8000) in background
echo ""
echo -e "${BLUE}[2/2] Starting Django Web Server on http://localhost:8000${NC}"
cd webserver
$PYTHON_CMD manage.py runserver 127.0.0.1:8000 > "$DJANGO_LOG" 2>&1 &
DJANGO_PID=$!
cd ..
echo "      Django PID: $DJANGO_PID"
echo "      Log file: $DJANGO_LOG"

# Wait for Django to start
echo "      Waiting for Django to start..."
sleep 3

# Check if Django is running
if ! ps -p $DJANGO_PID > /dev/null; then
    echo -e "${RED}      Error: Django failed to start. Check $DJANGO_LOG${NC}"
    kill $AI_SERVICE_PID 2>/dev/null
    exit 1
fi

echo ""
echo "============================================================"
echo -e "${GREEN}✓ Application started successfully!${NC}"
echo "============================================================"
echo ""
echo "Services running:"
echo "  • AI Service:    http://localhost:8001"
echo "  • Web Interface: http://localhost:8000"
echo ""
echo "API Documentation:"
echo "  • AI Service Docs: http://localhost:8001/docs"
echo "  • Health Check:    http://localhost:8001/health"
echo ""
echo "Process IDs:"
echo "  • AI Service: $AI_SERVICE_PID"
echo "  • Django:     $DJANGO_PID"
echo ""
echo "Log files:"
echo "  • AI Service: $AI_SERVICE_LOG"
echo "  • Django:     $DJANGO_LOG"
echo ""
echo "============================================================"
echo ""
echo -e "${YELLOW}To stop the application, press Ctrl+C${NC}"
echo ""

# Save PIDs to file for stop script
echo "$AI_SERVICE_PID" > "$PROJECT_ROOT/.ai_service.pid"
echo "$DJANGO_PID" > "$PROJECT_ROOT/.django.pid"

# Trap Ctrl+C to cleanup
cleanup() {
    echo ""
    echo ""
    echo "============================================================"
    echo -e "${YELLOW}Stopping services...${NC}"
    echo "============================================================"

    if [ -f "$PROJECT_ROOT/.django.pid" ]; then
        DJANGO_PID=$(cat "$PROJECT_ROOT/.django.pid")
        echo "Stopping Django (PID: $DJANGO_PID)..."
        kill $DJANGO_PID 2>/dev/null || true
        rm "$PROJECT_ROOT/.django.pid"
    fi

    if [ -f "$PROJECT_ROOT/.ai_service.pid" ]; then
        AI_SERVICE_PID=$(cat "$PROJECT_ROOT/.ai_service.pid")
        echo "Stopping AI Service (PID: $AI_SERVICE_PID)..."
        kill $AI_SERVICE_PID 2>/dev/null || true
        rm "$PROJECT_ROOT/.ai_service.pid"
    fi

    echo -e "${GREEN}Services stopped.${NC}"
    exit 0
}

trap cleanup SIGINT SIGTERM

# Wait for both processes
wait $AI_SERVICE_PID $DJANGO_PID
