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

```bash
# Clone and setup
git clone <repository-url>
cd teacher_assist
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and set DJANGO_SECRET_KEY

# Run Django server
cd webserver
python manage.py migrate
python manage.py runserver
# Access at http://localhost:8000
```

## Project Structure

```
teacher_assist/
├── docs/                       # Documentation
│   └── PRD.md                 # Product Requirements Document (detailed specs)
├── webserver/                  # Django web application
│   └── README.md              # Django setup and commands
├── ai_service/                 # LangGraph AI service (future)
├── requirements.txt            # Python dependencies
├── .env.example               # Environment variables template
└── CLAUDE.md                  # Development guidelines
```

## Documentation

- **[docs/PRD.md](docs/PRD.md)** - Complete product requirements, user stories, technical specs, API contract, database schema
- **[docs/ui.md](docs/ui.md)** - UI interaction reference and behavior specifications
- **[docs/django_api.md](docs/django_api.md)** - Django REST API endpoints documentation
- **[webserver/README.md](webserver/README.md)** - Django setup, commands, and development workflow
- **[CLAUDE.md](CLAUDE.md)** - Development guidelines for Claude Code

## Key Notes

- **Database:** SQLite committed to git for portability (contains curriculum data)
- **MVP Scope:** Single-page table interface, no data persistence between sessions
- **Git Workflow:** Trunk-based development with feature branches

For detailed specifications, see [docs/PRD.md](docs/PRD.md).
