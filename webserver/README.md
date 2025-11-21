# Teacher Assist - Django Web Server

Django web application serving as the backend and hosting the React frontend for Teacher Assist.

## Quick Setup

```bash
cd webserver
python manage.py migrate
python manage.py runserver
# Access at http://localhost:8000
```

## Project Structure

```
webserver/
├── manage.py                   # Django management command
├── db.sqlite3                  # SQLite database (committed to git)
├── teachertools/               # Main Django project configuration
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py/asgi.py
└── lessonplanner/              # Lesson planning app (main app)
    ├── models.py               # Database models
    ├── views.py                # View functions & API endpoints
    ├── urls.py                 # App URL configuration
    ├── migrations/             # Database migrations
    ├── fixtures/               # Mock data (mock_data.py)
    ├── services/               # Business logic layer
    │   ├── ai_client.py        # HTTP client for AI service
    │   └── db_service.py       # Database query service
    ├── frontend/               # React + TypeScript frontend
    │   ├── src/                # React source files
    │   ├── dist/               # Vite build output (git-ignored)
    │   ├── package.json        # JavaScript dependencies (Vitest)
    │   ├── vite.config.ts      # Vite configuration
    │   └── README.md           # Frontend documentation
    ├── templates/              # Django templates
    │   └── lessonplanner/
    │       └── index.html      # Main template (loads React build)
    └── tests.py                # Python tests
```

## Django Apps

**lessonplanner:** Monthly lesson planning interface for Polish kindergarten teachers. Single-page React application with AI-powered metadata generation. Backend provides REST API endpoints. Frontend built with React + TypeScript + Tailwind CSS + Vite. Includes Vitest-based frontend tests and pytest-based backend tests.


## Essential Commands

All commands run from the `webserver/` directory.

### Server

```bash
python manage.py runserver              # Start server (http://localhost:8000)
python manage.py runserver 8080         # Use different port
```

### Database

```bash
python manage.py makemigrations         # Create new migrations
python manage.py migrate                # Apply migrations
python manage.py showmigrations         # Show migration status
python manage.py dbshell                # Open SQLite shell
```

### Development

```bash
python manage.py shell                  # Django Python shell
python manage.py test                   # Run Python tests
python manage.py createsuperuser        # Create admin user
```

### Testing API Endpoints

The lesson planner API endpoints are protected by Django's CSRF middleware for security. When testing endpoints manually, you need to include a CSRF token.

#### Method 1: Using Python requests (Recommended)

```python
import requests

# Start a session to handle cookies automatically
session = requests.Session()

# 1. Get CSRF token by visiting the main page
response = session.get('http://localhost:8000/')
csrf_token = session.cookies['csrftoken']

# 2. Make API request with CSRF token
response = session.post(
    'http://localhost:8000/api/fill-work-plan/',
    json={
        'activity': 'Test activity',
        'theme': 'Test theme'
    },
    headers={'X-CSRFToken': csrf_token}
)

print(response.status_code)
print(response.json())
```

#### Method 2: Using curl

```bash
# 1. Get CSRF token and save cookies
curl -c cookies.txt http://localhost:8000/

# 2. Extract CSRF token from cookies
CSRF_TOKEN=$(grep csrftoken cookies.txt | cut -f7)

# 3. Make API request
curl -X POST http://localhost:8000/api/fill-work-plan/ \
  -H "Content-Type: application/json" \
  -H "X-CSRFToken: $CSRF_TOKEN" \
  -b cookies.txt \
  -d '{"activity": "Test activity", "theme": "Test theme"}'

# Clean up
rm cookies.txt
```

#### Available Endpoints

- `POST /api/fill-work-plan/` - Generate metadata for single activity
- `GET /api/curriculum-refs/<code>/` - Get curriculum text for tooltip (no CSRF needed)
- `GET /api/curriculum-refs/` - Get all curriculum references (no CSRF needed)
- `GET /api/modules/` - Get educational modules (no CSRF needed)

**Note:** GET endpoints do not require CSRF tokens, only POST endpoints do.
**Note:** Bulk operations are handled by the frontend making sequential calls to `/api/fill-work-plan/`.

### Frontend Development

The `lessonplanner` app includes a React + TypeScript frontend built with Vite.

**Quick Start:**
```bash
cd lessonplanner/frontend
npm install                    # Install dependencies (first time only)
npm run dev                    # Start dev server (port 5173)
```

**For complete frontend documentation, commands, project structure, and features, see:**
**[lessonplanner/frontend/README.md](lessonplanner/frontend/README.md)**

This includes:
- Complete technology stack details (React, TypeScript, Vite, Tailwind, shadcn/ui, Vitest)
- All development, build, and testing commands
- Project structure and component architecture
- Build scripts documentation

## Configuration

Environment variables in `.env` (parent directory):

```bash
DJANGO_SECRET_KEY=your-secret-key-here
DEBUG=True
```

**Key settings** (`teachertools/settings.py`):
- **SECRET_KEY:** From environment variable (required)
- **DATABASE:** SQLite at `db.sqlite3` (committed to git)
- **DEBUG:** `True` for development

## Database

The SQLite database (`db.sqlite3`) is **intentionally committed to git** for portability with pre-populated curriculum data.

**Schema details:** See [../docs/db_schema.md](../docs/db_schema.md)
**Database initialization:** See [../docs/db_init.md](../docs/db_init.md)

## Static Files

### Django Static Files System

**Static files location:**
- Frontend build output: `lessonplanner/frontend/dist/` (git-ignored)
- Django serves from: Copied to Django's `collectstatic` or referenced directly

**Django template:**
- `templates/lessonplanner/index.html` loads React build assets

**Build process:**
```bash
cd lessonplanner/frontend
npm run build                    # Build React app → dist/
./build-and-update.sh            # Update Django template with new hashes
```

The build script updates the Django template with correct asset hashes from Vite's build manifest.

### Static Files in Development

Django's development server automatically serves static files from app directories when `DEBUG=True`.

For production deployment, run:
```bash
python manage.py collectstatic
```

## Creating Django Apps

```bash
python manage.py startapp app_name
```

**Then:**
1. Add `app_name` to `INSTALLED_APPS` in `settings.py`
2. Create models in `app_name/models.py`
3. Create views in `app_name/views.py`
4. Configure URLs in `app_name/urls.py`
5. Include in `teachertools/urls.py`: `path('', include('app_name.urls'))`

## Templates and Static Files

**Templates:** `app_name/templates/app_name/template.html`
**Static files:** `app_name/static/app_name/file.css` (or use frontend/ for React apps)

Load in templates:
```html
{% load static %}
<link rel="stylesheet" href="{% static 'app_name/style.css' %}">
```

## Common Issues

**Port in use:**
```bash
lsof -i :8000              # Find process
kill -9 <PID>              # Kill it
```

**Database locked:** Restart server, check `db.sqlite3` permissions

**Import errors:** Ensure virtual environment is activated:
```bash
source ../.venv/bin/activate  # Linux/Mac
..\.venv\Scripts\activate     # Windows
```

**Migration conflicts (dev only):**
```bash
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
python manage.py makemigrations
python manage.py migrate
```

**Frontend build errors:**
```bash
cd lessonplanner/frontend
rm -rf node_modules package-lock.json
npm install
npm run build
```

## Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [Django Tutorial](https://docs.djangoproject.com/en/5.2/intro/tutorial01/)
- Project PRD: [../docs/PRD.md](../docs/PRD.md)
- Main README: [../README.md](../README.md)
- Frontend README: [lessonplanner/frontend/README.md](lessonplanner/frontend/README.md)
