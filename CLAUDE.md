# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Teacher Assist is a Django-based web application designed to help Polish kindergarten teachers plan their monthly lessons. The application uses AI to automatically fill educational metadata (modules, curriculum references, and objectives) based on planned activities entered by the teacher.

**Key characteristics:**
- Interface and AI responses are in Polish
- MVP focused on local deployment (no user authentication)
- Single-page application with tabular data display
- Designed for easy copying to Google Docs
- **Training project:** This project serves as a learning opportunity for Claude Code, Django, and LangGraph

## Technology Stack

- **Web Framework**: Django 5.2.7
- **Database**: SQLite (development)
- **AI Backend**: Python + LangGraph (planned integration)
- **Language**: Python 3.12+

## Project Structure

```
teacher_assist/
├── docs/
│   └── projectPremise.md      # Detailed project requirements and UI specs
├── webserver/                  # Django project root
│   ├── manage.py              # Django management script
│   ├── teachertools/          # Main Django project configuration
│   │   ├── settings.py        # Project settings
│   │   ├── urls.py            # Root URL configuration
│   │   ├── wsgi.py/asgi.py    # WSGI/ASGI application
│   └── hello/                 # Example Django app (placeholder)
└── CLAUDE.md                  # This file
```

## Development Commands

All Django commands should be run from the `webserver/` directory.

**Start development server:**
```bash
cd webserver
python manage.py runserver
```

**Database migrations:**
```bash
cd webserver
python manage.py makemigrations
python manage.py migrate
```

**Create superuser:**
```bash
cd webserver
python manage.py createsuperuser
```

**Run tests:**
```bash
cd webserver
python manage.py test
```

**Django shell:**
```bash
cd webserver
python manage.py shell
```

## Application Requirements (from projectPremise.md)

The main application UI consists of:

1. **Text field** - For entering the weekly theme
2. **Data table** with columns:
   - Moduł (educational module: emotions, art forms, etc.)
   - Podstawa Programowa (core curriculum paragraph numbers)
   - Cele (educational objectives)
   - Aktywność (planned activity - user input)
3. **Autofill buttons** - AI-powered filling for single rows or all rows
4. **Interactive feature** - Hovering over Podstawa Programowa numbers shows corresponding curriculum text

## AI Integration Architecture

### Two-Process Design

The application uses a **separate process architecture** with REST API communication:

1. **Django Web Server** (Process 1)
   - Serves the UI
   - Handles user requests
   - Manages database operations
   - Makes HTTP requests to LangGraph service

2. **LangGraph AI Service** (Process 2)
   - Runs as a separate FastAPI/Flask server
   - Processes AI requests
   - Returns educational metadata in JSON format

### Communication Flow

```
User Browser → Django (localhost:8000) → HTTP REST API → LangGraph Service (localhost:8001)
                     ↓                                            ↓
                SQLite Database                            LLM (OpenAI/etc)
```

### Starting Both Services

**Terminal 1 - LangGraph Service:**
```bash
# Start the AI service (to be created)
python ai_service/main.py
# Runs on http://localhost:8001
```

**Terminal 2 - Django Server:**
```bash
cd webserver
python manage.py runserver
# Runs on http://localhost:8000
```

### REST API Contract

**Endpoint:** `POST http://localhost:8001/api/generate-metadata`

**Request:**
```json
{
  "activity": "Zabawa w sklep z owocami",
  "theme": "Jesień - zbiory"
}
```

**Response:**
```json
{
  "modul": "Zabawy matematyczne",
  "podstawa_programowa": ["I.1.2", "II.3.1"],
  "cele": [
    "Rozwijanie umiejętności liczenia",
    "Poznawanie nazw owoców sezonowych"
  ]
}
```

### Django Integration

Django views will use `requests` library to call the LangGraph service:

```python
import requests

LANGGRAPH_URL = "http://localhost:8001/api/generate-metadata"

def autofill_activity(activity, theme):
    response = requests.post(
        LANGGRAPH_URL,
        json={"activity": activity, "theme": theme},
        timeout=30
    )
    return response.json()
```

### LangGraph Workflow

The AI workflow should:
- Accept Polish language activity descriptions
- Map activities to standard educational modules
- Reference appropriate core curriculum paragraphs
- Generate relevant educational objectives in Polish
- Return structured JSON response

## Database

**SQLite is intentionally used** for this project because:
- Simple, file-based database requiring no server setup
- Database file can be committed to git for portability across systems
- Ideal for local-only MVP deployment
- Development and deployment databases can be synchronized via git

**Important:** The SQLite database file (`webserver/db.sqlite3`) is tracked in git, unlike typical Django projects. This allows the application to work across different systems with pre-populated data (curriculum references, etc.).

The main data model will include:
- Weekly themes
- Activities with associated metadata (module, curriculum references, objectives)
- Core curriculum reference data (for hover-over display)

## Git Workflow

This project uses **trunk-based development** with the following conventions:

**Branch naming:**
- Main branch: `main`
- Feature branches: `feature/c_<description>` (prefix `c_` indicates Claude-created branches)

**Workflow rules:**
1. **Continuing existing work:** If already on a feature branch, continue working on that branch
2. **Starting from main:** If on `main` branch, create a new feature branch: `feature/c_<description>`
3. **Starting new task:** When beginning a new task:
   - Suggest merging and pushing the current feature branch
   - Create a new feature branch (typically from the latest feature branch)

**Example:**
```bash
# Starting new work from main
git checkout -b feature/c_lesson_planning_ui

# Starting new task after completing previous work
git add . && git commit -m "Complete lesson planning UI"
git push origin feature/c_lesson_planning_ui
git checkout -b feature/c_ai_integration
```

## Development Guidelines

### Package Management

**ALWAYS ask before installing new packages via pip.**

The developer wants to maintain control over project dependencies. When a new package is needed:
1. Suggest the package and explain why it's needed
2. Wait for explicit approval before installing
3. After approval, install and document in requirements.txt

### Project Purpose

This is a **training project** for learning:
- Claude Code capabilities and workflows
- Django web framework
- LangGraph AI integration

Keep implementations educational and well-commented where appropriate.

## Settings Notes

- `DEBUG = True` for local development
- `LANGUAGE_CODE = 'en-us'` in settings but application content is Polish
- `SECRET_KEY` is development-only (insecure placeholder)
- Database: SQLite at `webserver/db.sqlite3` (committed to git)
