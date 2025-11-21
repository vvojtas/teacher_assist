# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Teacher Assist is a Django-based web application designed to help Polish kindergarten teachers plan their monthly lessons. The application uses AI to automatically fill educational metadata (modules, curriculum references, and objectives) based on planned activities entered by the teacher.

**Key characteristics:**
- Interface and AI responses are in Polish
- MVP focused on local deployment (no user authentication)
- Single-page application with tabular data display
- Designed for easy copying to Google Docs
- **Training project:** This project serves as a learning opportunity for Claude Code, Django, React, and LangGraph

## Technology Stack

- **Web Framework**: Django 5.2.7
- **Frontend**: React 18 + TypeScript 5 + Vite + Tailwind CSS
- **Database**: SQLite (development)
- **AI Backend**: Python + LangGraph
- **Language**: Python 3.12+

## Project Structure

```
teacher_assist/
├── docs/
│   ├── PRD.md                 # Product Requirements Document
│   ├── ai_api.md              # AI Service REST API specification
│   ├── django_api.md          # Django Backend API specification
│   ├── db_schema.md           # Database schema documentation
│   ├── db_init.md             # Database initialization guide
│   └── ui.md                  # UI interaction reference (React)
├── common/                     # Shared Pydantic models
│   └── models.py              # Request/response models for API
├── ai_service/                 # FastAPI AI service
├── webserver/                  # Django project root
│   ├── manage.py              # Django management script
│   ├── teachertools/          # Main Django project configuration
│   └── lessonplanner/         # Main Django app
│       ├── frontend/          # React + TypeScript frontend
│       │   ├── src/           # React source files
│       │   ├── dist/          # Vite build output
│       │   └── package.json   # JavaScript dependencies
│       └── templates/         # Django templates
│           └── lessonplanner/
│               └── index.html # Loads React build
└── CLAUDE.md                  # This file
```

## Development Commands

### Django Backend

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

### React Frontend

Frontend development commands from `webserver/lessonplanner/frontend/`:

**Install dependencies:**
```bash
cd webserver/lessonplanner/frontend
npm install
```

**Development server (with hot reload):**
```bash
npm run dev  # Runs on http://localhost:5173
```

**Production build:**
```bash
npm run build  # Outputs to frontend/dist/
./build-and-update.sh  # Build and update Django template
```

**Run tests:**
```bash
npm test              # Vitest in watch mode
npm run test:run      # Run tests once
npm run test:coverage # With coverage report
```

### AI Service

**Start AI service:**
```bash
python ai_service/main.py
# Runs on http://localhost:8001
```

## Application Requirements

**See [docs/PRD.md](docs/PRD.md) for detailed product requirements, user stories, and functional specifications.**

Quick summary: Single-page table interface for lesson planning with AI-powered autofill of educational metadata (modules, curriculum references, objectives) based on teacher-entered activities. Interface in Polish, designed for easy copying to Google Docs.

## AI Integration Architecture

**Two-Process Design:** Django web server (port 8000) + LangGraph AI service (port 8001) communicating via REST API.

**See API Documentation:**
- [docs/ai_api.md](docs/ai_api.md) - AI Service REST API specification
- [docs/django_api.md](docs/django_api.md) - Django Backend API specification
- [docs/PRD.md](docs/PRD.md) Section 7 - Architecture overview and requirements

### Starting Both Services

**Terminal 1 - LangGraph Service:**
```bash
python ai_service/main.py
# Runs on http://localhost:8001
```

**Terminal 2 - Django Server:**
```bash
cd webserver
python manage.py runserver
# Runs on http://localhost:8000
```

**Alternative - Use startup scripts:**
```bash
# Linux/Mac
./start.sh

# Windows
start.bat
```

### Quick Reference

- **AI Endpoint:** `POST http://localhost:8001/api/fill-work-plan`
- **Implementation:** MockAIService (returns random data from database)
- **LLM Gateway:** OpenRouter (for model flexibility)
- **Budget:** ~$1/month (use cost-effective models)
- **Timeout:** 120 seconds
- **Language:** Polish (UI and AI responses)

## Database

**SQLite is intentionally used** and the database file (`db.sqlite3` in project root) **is committed to git** for portability. This allows pre-populated curriculum data to work across different systems without setup.

**Location:** `db.sqlite3` (project root)
- Shared between Django webserver and AI service
- Pre-populated with Polish kindergarten curriculum references
- Contains example work plan entries for LLM training

**See [docs/db_schema.md](docs/db_schema.md) for database schema details.**

**Note:** MVP has no data persistence for lesson plans (session-only). Future phases will add save/load functionality using existing WorkPlan and WorkPlanEntry models.

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

### Documentation Synchronization

**When requirements change (before or during implementation), update [docs/PRD.md](docs/PRD.md) or other related documentation immediately.** Documentation must always reflect actual/planned implementation.

### Package Management

**ALWAYS ask before installing new packages via pip or npm.**

The developer wants to maintain control over project dependencies. When a new package is needed:
1. Suggest the package and explain why it's needed
2. Wait for explicit approval before installing
3. After approval, install and document in requirements.txt (Python) or package.json (JavaScript)

### Frontend Development

**React + TypeScript frontend:**
- Located in `webserver/lessonplanner/frontend/`
- Uses Vite for build tooling
- Tailwind CSS for styling
- shadcn/ui for component primitives
- Vitest for testing

**Build process:**
1. Development: `npm run dev` (hot reload on port 5173)
2. Production: `npm run build` → outputs to `dist/`
3. Django integration: `./build-and-update.sh` updates template with new asset hashes

**See [webserver/lessonplanner/frontend/README.md](webserver/lessonplanner/frontend/README.md) for frontend details.**

### Project Purpose

This is a **training project** for learning:
- Claude Code capabilities and workflows
- Django web framework
- React + TypeScript frontend development
- LangGraph AI integration
- 
Keep implementations educational and well-commented where appropriate.

## Settings Notes

- `DEBUG = True` for local development
- `LANGUAGE_CODE = 'en-us'` in settings but application content is Polish
- `SECRET_KEY` is development-only (insecure placeholder)
- Database: SQLite at `db.sqlite3` (committed to git)
