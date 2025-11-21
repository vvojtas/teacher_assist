# Database Initialization and Data Seeding

**Project:** Teacher Assist - AI-Powered Lesson Planning Tool
**Version:** 2.0 (MVP)
**Last Updated:** 2025-11-21

---

## 1. Overview

This document provides instructions for database initialization and understanding the data seeding approach.

**Key Facts:**
- **Database file (`db.sqlite3`) is committed to git** for portability
- Database comes pre-populated with curriculum data
- No manual seeding required for MVP - database is ready to use
- Fixtures are used for mock/test data, not production seeding

**Prerequisites:**
- Django project set up with models defined
- Database configured in `settings.py`
- See `docs/db_schema.md` for complete schema documentation

---

## 2. Database Initialization

### 2.1 Quick Start (MVP - Database Already Included)

**The database file `db.sqlite3` is already committed to the repository and ready to use.**

```bash
cd webserver
python manage.py migrate  # Apply any pending migrations
python manage.py runserver  # Start server
```

No data seeding required - the database already contains:
- Curriculum references (major and detailed)
- Educational modules
- Example work plan entries (marked with `is_example=True` for AI training)

### 2.2 Verify Existing Data

**Django Shell:**
```bash
cd webserver
python manage.py shell
```

```python
from lessonplanner.models import (
    MajorCurriculumReference, CurriculumReference, EducationalModule,
    WorkPlan, WorkPlanEntry
)

# Check counts
print(f"Major references: {MajorCurriculumReference.objects.count()}")
print(f"Curriculum references: {CurriculumReference.objects.count()}")
print(f"Educational modules: {EducationalModule.objects.count()}")
print(f"Work plans: {WorkPlan.objects.count()}")
print(f"Example entries: {WorkPlanEntry.objects.filter(is_example=True).count()}")

# View sample data
print("\nEducational Modules:")
for module in EducationalModule.objects.all()[:5]:
    print(f"  - {module.module_name}")

print("\nSample Curriculum References:")
for ref in CurriculumReference.objects.all()[:3]:
    print(f"  {ref.reference_code}: {ref.full_text[:60]}...")
```

**Direct SQL (SQLite):**
```bash
# From project root
sqlite3 db.sqlite3

# Check tables
.tables

# Check counts
SELECT COUNT(*) FROM major_curriculum_references;
SELECT COUNT(*) FROM curriculum_references;
SELECT COUNT(*) FROM educational_modules;
SELECT COUNT(*) FROM work_plan_entries WHERE is_example = 1;

# View sample data
SELECT module_name FROM educational_modules LIMIT 5;
SELECT reference_code, substr(full_text, 1, 50) FROM curriculum_references LIMIT 3;

# Exit
.exit
```

---

## 3. Django Models

Django ORM abstracts database differences automatically and is the recommended approach for this project.

**Django Advantages:**
- Automatic migrations via `python manage.py makemigrations`
- Database-agnostic (change `ENGINE` in settings.py to switch databases)
- Built-in admin interface for data management
- ORM query optimization

### 3.1 Model Definitions

Models are defined in `webserver/lessonplanner/models.py`:

**Reference Data Models:**
- `MajorCurriculumReference` - Major curriculum sections (e.g., "1", "2", "3", "4")
- `CurriculumReference` - Detailed curriculum paragraphs (e.g., "4.15", "3.8")
- `EducationalModule` - Module categories (e.g., "MATEMATYKA", "JĘZYK")

**Work Plan Models (Schema defined, not used in MVP UI):**
- `WorkPlan` - Weekly lesson plans with themes
- `WorkPlanEntry` - Individual activity rows within work plans
- `WorkPlanEntryCurriculumRef` - Junction table for many-to-many relationships

See `webserver/lessonplanner/models.py` for complete model definitions with documentation.

### 3.2 Creating New Migrations

If you modify models, generate and apply migrations:

```bash
cd webserver
python manage.py makemigrations
python manage.py migrate
```

Django will automatically create SQL schema changes for your database backend.

---

## 4. Fixtures and Mock Data

### 4.1 Fixture Files

**Location:** `webserver/lessonplanner/fixtures/`

**Purpose:** Mock data for testing and development (NOT for production seeding)

**Current Fixtures:**
- `mock_data.py` - Contains sample curriculum references and educational modules

**Contents:**
```python
# fixtures/mock_data.py

MOCK_CURRICULUM_REFS = {
    "1.1": "zgłasza potrzeby fizjologiczne...",
    "2.5": "rozstaje się z rodzicami bez lęku...",
    "3.8": "obdarza uwagą inne dzieci...",
    "4.15": "przelicza elementy zbiorów...",
    "4.18": "eksperymentuje w zakresie orientacji..."
}

MOCK_EDUCATIONAL_MODULES = [
    {'id': 1, 'name': 'JĘZYK', 'is_ai_suggested': False},
    {'id': 2, 'name': 'MATEMATYKA', 'is_ai_suggested': False},
    # ... more modules
]
```

**Usage:** These fixtures are used by the test suite and mock services, not for database initialization.

---

## 5. Database Administration

### 5.1 Django Admin Interface

**Create superuser:**
```bash
cd webserver
python manage.py createsuperuser
# Follow prompts to set username, email, password
```

**Access admin:**
```
http://localhost:8000/admin
```

**Admin Capabilities:**
- View and edit all curriculum references
- Manage educational modules
- View work plans and entries
- Add/modify example entries for AI training

### 5.2 Viewing Data via Django Shell

**Common Queries:**

```python
from lessonplanner.models import CurriculumReference, EducationalModule

# Get all curriculum references
refs = CurriculumReference.objects.all()
for ref in refs[:5]:
    print(f"{ref.reference_code}: {ref.full_text[:50]}...")

# Get specific reference
ref = CurriculumReference.objects.get(reference_code='4.15')
print(ref.full_text)

# Get all modules
modules = EducationalModule.objects.all().order_by('module_name')
for module in modules:
    suggested = " (AI suggested)" if module.is_ai_suggested else ""
    print(f"- {module.module_name}{suggested}")

# Get modules by type
predefined = EducationalModule.objects.filter(is_ai_suggested=False)
ai_suggested = EducationalModule.objects.filter(is_ai_suggested=True)

# Work with relationships
from lessonplanner.models import WorkPlanEntry

# Get example entries (for AI training)
examples = WorkPlanEntry.objects.filter(is_example=True).prefetch_related(
    'curriculum_references', 'module'
)
for entry in examples:
    print(f"Activity: {entry.activity}")
    print(f"Module: {entry.module.module_name if entry.module else 'None'}")
    refs = entry.curriculum_references.all()
    print(f"Curriculum: {', '.join([r.reference_code for r in refs])}")
    print()
```

---

## 6. Database Backup and Restore

### 6.1 SQLite Backup (MVP)

**Database Location:** `db.sqlite3` (project root)

**Simple File Copy:**
```bash
cp db.sqlite3 db.sqlite3.backup
```

**SQLite Backup Command (safer - handles locks):**
```bash
sqlite3 db.sqlite3 ".backup 'backup/db-$(date +%Y%m%d).sqlite3'"
```

**Django Dumpdata (portable, can restore to any DB):**
```bash
cd webserver
python manage.py dumpdata > backup/data-$(date +%Y%m%d).json

# Dump specific app
python manage.py dumpdata lessonplanner > backup/lessonplanner-$(date +%Y%m%d).json

# Exclude certain models
python manage.py dumpdata --exclude=contenttypes --exclude=auth > backup/data.json
```

**Restore from dumpdata:**
```bash
cd webserver
python manage.py loaddata backup/data-20251121.json
```

**Restore from SQLite backup:**
```bash
# Stop server first
cp backup/db-20251121.sqlite3 db.sqlite3
```

### 6.2 PostgreSQL Backup (Future)

```bash
# Full database dump
pg_dump teacher_assist > backup/teacher_assist-$(date +%Y%m%d).sql

# Compressed backup
pg_dump teacher_assist | gzip > backup/teacher_assist-$(date +%Y%m%d).sql.gz

# Restore
psql teacher_assist < backup/teacher_assist-20251121.sql
```

---

## 7. Fresh Database Setup (If Needed)

**⚠️ Warning:** Only needed if you want to recreate the database from scratch. **The committed `db.sqlite3` should be used for normal development.**

### 7.1 Delete Existing Database

```bash
# From project root
rm db.sqlite3

# Delete migrations (optional - only if starting completely fresh)
rm webserver/lessonplanner/migrations/0*.py
```

### 7.2 Create Fresh Database

```bash
cd webserver

# Create new migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

### 7.3 Add Data Manually

**Option 1: Via Django Admin**
1. Start server: `python manage.py runserver`
2. Go to http://localhost:8000/admin
3. Login with superuser credentials
4. Manually add curriculum references and modules

**Option 2: Via Django Shell**
```python
from lessonplanner.models import MajorCurriculumReference, CurriculumReference, EducationalModule

# Add major reference
major_ref = MajorCurriculumReference.objects.create(
    reference_code='4',
    full_text='Dziecko poznaje i rozumie świat;'
)

# Add detailed reference
CurriculumReference.objects.create(
    reference_code='4.15',
    full_text='przelicza elementy zbiorów w czasie zabawy...',
    major_reference=major_ref
)

# Add educational module
EducationalModule.objects.create(
    module_name='MATEMATYKA',
    is_ai_suggested=False
)
```

**Option 3: Write Custom Data Script**

Create `webserver/seed_database.py`:
```python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'teachertools.settings')
django.setup()

from lessonplanner.models import EducationalModule

# Seed modules
modules = [
    'JĘZYK', 'MATEMATYKA', 'MOTORYKA MAŁA', 'MOTORYKA DUŻA',
    'FORMY PLASTYCZNE', 'MUZYKA', 'POZNAWCZE', 'WSPÓŁPRACA',
    'EMOCJE', 'SPOŁECZNE', 'SENSORYKA', 'ZDROWIE'
]

for module_name in modules:
    EducationalModule.objects.get_or_create(
        module_name=module_name,
        defaults={'is_ai_suggested': False}
    )
    print(f"Created/verified: {module_name}")

print("Database seeded successfully!")
```

Run:
```bash
cd webserver
python seed_database.py
```

---

## 8. Data Integrity and Relationships

### 8.1 Foreign Key Constraints

**RESTRICT (prevents deletion):**
- `curriculum_references.major_reference_id` → `major_curriculum_references.id`
- `work_plan_entry_curriculum_refs.curriculum_reference_id` → `curriculum_references.id`
- `work_plan_entries.module_id` → `educational_modules.id`

**CASCADE (automatic deletion):**
- `work_plan_entries.work_plan_id` → `work_plans.id` (deleting work plan deletes all entries)
- `work_plan_entry_curriculum_refs.work_plan_entry_id` → `work_plan_entries.id`

### 8.2 Testing Relationships

```python
from lessonplanner.models import *

# Create work plan with entries
wp = WorkPlan.objects.create(theme="Jesień - zbiory")
module = EducationalModule.objects.get(module_name='MATEMATYKA')

entry = WorkPlanEntry.objects.create(
    work_plan=wp,
    module=module,
    activity="Zabawa w sklep z owocami",
    objectives="Dziecko potrafi przeliczać w zakresie 5",
    is_example=True
)

# Add curriculum references
ref1 = CurriculumReference.objects.get(reference_code='4.15')
ref2 = CurriculumReference.objects.get(reference_code='4.18')
entry.curriculum_references.add(ref1, ref2)

# Verify relationships
print(f"Work plan: {wp}")
print(f"Entries: {wp.entries.count()}")
print(f"Entry curriculum refs: {list(entry.curriculum_references.values_list('reference_code', flat=True))}")

# Test CASCADE delete
wp.delete()  # This will also delete all entries and junction table entries
```

---

## 9. Common Issues and Troubleshooting

### Issue: "No such table" error

**Cause:** Migrations not applied

**Solution:**
```bash
cd webserver
python manage.py migrate
```

### Issue: "UNIQUE constraint failed"

**Cause:** Trying to insert duplicate reference_code or module_name

**Solution:** Use `get_or_create()` instead of `create()`:
```python
EducationalModule.objects.get_or_create(
    module_name='MATEMATYKA',
    defaults={'is_ai_suggested': False}
)
```

### Issue: Migrations show pending but database is up to date

**Solution:**
```bash
# Show migration status
python manage.py showmigrations

# Fake apply if database was manually created
python manage.py migrate --fake
```

### Issue: Polish characters display as garbled text

**Solution:**
- Ensure database uses UTF-8 encoding (SQLite default is UTF-8)
- For PostgreSQL:
  ```bash
  createdb teacher_assist --encoding=UTF8 --locale=pl_PL.UTF-8
  ```

### Issue: Database file is locked

**Cause:** SQLite database is locked by another process

**Solution:**
```bash
# Find processes using the database
lsof db.sqlite3

# Kill the process or restart Django server
```

---

## 10. Performance Optimization

### 10.1 Query Optimization

**Use select_related() for foreign keys:**
```python
# Good - single query with JOIN
refs = CurriculumReference.objects.select_related('major_reference').all()

# Bad - N+1 queries
refs = CurriculumReference.objects.all()
for ref in refs:
    print(ref.major_reference.reference_code)  # Extra query per ref!
```

**Use prefetch_related() for many-to-many:**
```python
# Good - 3 queries total
entries = WorkPlanEntry.objects.prefetch_related('curriculum_references').all()
for entry in entries:
    for ref in entry.curriculum_references.all():  # No extra queries
        print(ref.reference_code)

# Bad - N+1 queries
entries = WorkPlanEntry.objects.all()
for entry in entries:
    for ref in entry.curriculum_references.all():  # Extra query per entry!
        print(ref.reference_code)
```

### 10.2 Indexing

All indexes are defined in model Meta classes and automatically created:
- Primary keys (automatic)
- Foreign keys (automatic)
- Unique constraints (reference_code, module_name)
- Custom indexes (is_example flag for filtering)

---

## Document History

| Version | Date       | Author | Changes                                   |
|---------|------------|--------|-------------------------------------------|
| 1.0     | 2025-11-10 | Dev    | Initial database initialization guide     |
| 2.0     | 2025-11-21 | Dev    | Updated to reflect actual implementation: database committed to git, removed non-existent management commands, documented fixtures usage |

---

**Related Documentation:**
- **Database Schema:** See `docs/db_schema.md` for complete table definitions
- **Django Models:** See `webserver/lessonplanner/models.py` for implementation
- **API Documentation:** See `docs/django_api.md` for API endpoints
- **Product Requirements:** See `docs/PRD.md` for functional requirements
