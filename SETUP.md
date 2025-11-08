# Setup Instructions

## Database Migrations

After setting up the Django environment, you need to run the database migrations to create the required tables.

### Step 1: Install Django

If Django is not installed, install it first:

```bash
pip install django
```

Or if using a requirements.txt file (to be created):

```bash
pip install -r requirements.txt
```

### Step 2: Create and Run Migrations

From the `webserver/` directory:

```bash
cd webserver
python manage.py makemigrations
python manage.py migrate
```

This will create the following tables:
- `curriculum_references` - Stores Polish curriculum references (Podstawa Programowa)
- `educational_modules` - Stores educational modules (domains of learning)

### Step 3: Populate Initial Data (Optional)

You can populate the database with curriculum references and educational modules using the Django admin interface or by creating a data migration/fixture.

### Step 4: Run Tests

To verify everything is working:

```bash
cd webserver
python manage.py test lessonplanner
```

### Step 5: Start Development Server

```bash
cd webserver
python manage.py runserver
```

The application will be available at http://localhost:8000

## API Endpoints

All API endpoints are documented in `docs/django_api.md`. The available endpoints are:

1. `POST /api/fill-work-plan` - Generate educational metadata for an activity
2. `GET /api/curriculum-refs` - Get all curriculum references
3. `GET /api/curriculum-refs/<code>` - Get specific curriculum reference by code
4. `GET /api/modules` - Get all educational modules (with optional filtering)
