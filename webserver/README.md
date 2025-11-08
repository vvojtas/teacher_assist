# Teacher Assist - Django Web Server

Django web application serving as the frontend and main interface for Teacher Assist.

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
├── lessonplanner/              # Lesson planning app (main app)
│   ├── models.py               # Database models
│   ├── views.py                # View functions & API endpoints
│   ├── urls.py                 # App URL configuration
│   ├── migrations/             # Database migrations
│   ├── package.json            # JavaScript dependencies (Jest)
│   ├── static/lessonplanner/   # Static assets
│   │   ├── css/                # Stylesheets
│   │   └── js/                 # JavaScript modules & tests
│   └── templates/              # Django templates
└── hello/                      # Example Django app (placeholder)
```

## Django Apps

**lessonplanner:** Monthly lesson planning interface for Polish kindergarten teachers. Single-page table UI with AI-powered metadata generation. Uses vanilla JavaScript with modular architecture (TableManager, AIService). Includes Jest-based tests for both Python and JavaScript.


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
    'http://localhost:8000/api/generate-metadata/',
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
curl -X POST http://localhost:8000/api/generate-metadata/ \
  -H "Content-Type: application/json" \
  -H "X-CSRFToken: $CSRF_TOKEN" \
  -b cookies.txt \
  -d '{"activity": "Test activity", "theme": "Test theme"}'

# Clean up
rm cookies.txt
```

#### Available Endpoints

- `POST /api/generate-metadata/` - Generate metadata for single activity
- `POST /api/generate-bulk/` - Generate metadata for multiple activities
- `GET /api/curriculum/<code>/` - Get curriculum text for tooltip (no CSRF needed)

**Note:** The curriculum tooltip endpoint (GET) does not require CSRF tokens, only POST endpoints do.

### JavaScript Tests

The `lessonplanner` app includes JavaScript functionality with Jest-based tests.

```bash
cd lessonplanner                        # Navigate to lessonplanner app
npm install                             # Install JS dependencies (first time only)
npm test                                # Run JavaScript tests
npm run test:coverage                   # Run with coverage report
```

**Details:** See [lessonplanner/static/lessonplanner/js/__tests__/README.md](lessonplanner/static/lessonplanner/js/__tests__/README.md)

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

**Schema details:** See [../docs/PRD.md](../docs/PRD.md) Section 7.5

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
**Static files:** `app_name/static/app_name/file.css`

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

## Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [Django Tutorial](https://docs.djangoproject.com/en/5.2/intro/tutorial01/)
- Project PRD: [../docs/PRD.md](../docs/PRD.md)
- Main README: [../README.md](../README.md)