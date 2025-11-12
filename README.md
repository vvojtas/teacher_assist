# Teacher Assist

AI-powered lesson planning tool for Polish kindergarten teachers. Automatically generates educational metadata (modules, curriculum references, and objectives) based on planned activities.

**Current Phase:** MVP Development - Phase 1 (Foundation)
**Project Type:** Training/Learning Project (Django + LangGraph)

## Overview

Teachers enter activity descriptions in Polish, and the system generates:
- Educational module categorizations
- Core curriculum (Podstawa Programowa) references
- Educational objectives

**Architecture:** Django web server (port 8000) + LangGraph AI service (port 8001) communicating via REST API.

**Tech Stack:** Django 5.2.7, Python 3.12+, SQLite, LangGraph (planned), OpenRouter

## Quick Start

**Option 1: Using Startup Scripts (Recommended)**

```bash
# Linux/Mac
./start.sh

# Windows
start.bat
```

The startup scripts will:
- Install dependencies automatically
- Start both AI service (port 8001) and web server (port 8000)
- Open browser to http://localhost:8000

**Option 2: Manual Setup**

```bash
# Clone and setup
git clone <repository-url>
cd teacher_assist
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Install package (required for imports)
pip install -e .

# Terminal 1 - Start AI Service
python ai_service/main.py
# Runs on http://localhost:8001

# Terminal 2 - Start Django server
cd webserver
python manage.py migrate  # First time only
python manage.py runserver
# Access at http://localhost:8000
```

## Project Structure

```
teacher_assist/
├── docs/                       # Documentation
│   ├── PRD.md                 # Product Requirements Document (detailed specs)
│   ├── ai_api.md              # AI Service REST API specification
│   └── django_api.md          # Django REST API documentation
├── common/                     # Shared Pydantic models
│   └── models.py              # Request/response models for API communication
├── ai_service/                 # FastAPI AI service (mock implementation)
│   ├── main.py                # FastAPI application entry point
│   ├── mock_service.py        # Mock AI metadata generator
│   └── tests/                 # AI service tests (28 tests)
├── webserver/                  # Django web application
│   ├── lessonplanner/         # Main Django app
│   │   ├── services/          # Business logic layer
│   │   │   └── ai_client.py   # HTTP client for AI service
│   │   └── tests.py           # Django tests (27 tests)
│   └── README.md              # Django setup and commands
├── pyproject.toml              # Modern Python package configuration
├── requirements.txt            # Python dependencies
├── start.sh                    # Linux/Mac startup script
├── start.bat                   # Windows startup script
└── CLAUDE.md                  # Development guidelines
```

## Documentation

- **[docs/PRD.md](docs/PRD.md)** - Complete product requirements, user stories, technical specs
- **[docs/db_schema.md](docs/db_schema.md)** - Database schema definitions and table structures
- **[docs/django_api.md](docs/django_api.md)** - Django REST API endpoints documentation
- **[docs/ai_api.md](docs/ai_api.md)** - AI Service REST API specification (LangGraph service)
- **[docs/ui.md](docs/ui.md)** - UI interaction reference and behavior specifications
- **[webserver/README.md](webserver/README.md)** - Django setup, commands, and development workflow
- **[CLAUDE.md](CLAUDE.md)** - Development guidelines for Claude Code

## Key Notes

- **Database:** SQLite committed to git for portability (contains curriculum data)
- **MVP Scope:** Single-page table interface, no data persistence between sessions
- **Git Workflow:** Trunk-based development with feature branches

For detailed specifications, see [docs/PRD.md](docs/PRD.md).
