# Database Initialization and Data Seeding

**Project:** Teacher Assist - AI-Powered Lesson Planning Tool
**Version:** 1.0 (MVP)
**Last Updated:** 2025-11-10

---

## 1. Overview

This document provides instructions for initializing the database and seeding it with reference data (curriculum references and educational modules).

**Prerequisites:**
- Django project set up with models defined
- Database configured in `settings.py`
- See `docs/db_schema.md` for complete schema documentation

---

## 2. Database Initialization

### 2.1 Django Migrations (Recommended)

Django automatically generates SQL schema from model definitions.

**Step 1: Create migrations**
```bash
cd webserver
python manage.py makemigrations
```

**Step 2: Apply migrations**
```bash
python manage.py migrate
```

**Step 3: Create superuser (for admin access)**
```bash
python manage.py createsuperuser
```

**Step 4: Verify tables were created**
```bash
# SQLite
sqlite3 db.sqlite3 ".tables"

# PostgreSQL
psql teacher_assist -c "\dt"
```

### 2.2 Manual SQL Initialization (Alternative)

If not using Django ORM, you can run the SQL schema directly.

**Step 1:** Copy the SQL schema from `docs/db_schema.md` Section 4 and save it to a file (e.g., `schema.sql`)

**Step 2:** Run the SQL file:

**SQLite:**
```bash
cd webserver
sqlite3 db.sqlite3 < schema.sql
```

**PostgreSQL:**
```bash
psql teacher_assist < schema.sql
```

See `docs/db_schema.md` Section 4 for complete SQL schema definitions (SQLite and PostgreSQL versions).

---

## 3. Django Models (Recommended)

Django ORM abstracts database differences automatically and is the recommended approach for this project.

**Django Advantages:**
- Automatic migrations via `python manage.py makemigrations`
- Database-agnostic (change `ENGINE` in settings.py to switch databases)
- Built-in admin interface for data management
- ORM query optimization

### 3.1 Model Definitions

Create the following models in your Django app (e.g., `webserver/lessonplanner/models.py`):

```python
# models.py

from django.db import models


class MajorCurriculumReference(models.Model):
    """
    Stores major sections of Polish curriculum (Podstawa Programowa).
    Each major reference represents a top-level section (e.g., "4" for mathematics).
    """
    reference_code = models.CharField(
        max_length=10,
        unique=True,
        db_index=True,
        help_text="Major section code (e.g., '4')"
    )
    full_text = models.TextField(
        help_text="Complete Polish text for major curriculum section"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'major_curriculum_references'
        ordering = ['reference_code']
        verbose_name = 'Major Curriculum Reference'
        verbose_name_plural = 'Major Curriculum References'

    def __str__(self):
        return f"{self.reference_code}: {self.full_text[:50]}..."


class CurriculumReference(models.Model):
    """
    Stores detailed Polish curriculum reference codes (Podstawa Programowa)
    and their complete text descriptions for tooltip display.
    """
    reference_code = models.CharField(
        max_length=20,
        unique=True,
        db_index=True,
        help_text="Curriculum code (e.g., '4.15')"
    )
    full_text = models.TextField(
        help_text="Complete Polish curriculum requirement text"
    )
    major_reference = models.ForeignKey(
        MajorCurriculumReference,
        on_delete=models.RESTRICT,
        related_name='detailed_references',
        help_text="Parent major curriculum section"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'curriculum_references'
        ordering = ['reference_code']
        verbose_name = 'Curriculum Reference'
        verbose_name_plural = 'Curriculum References'

    def __str__(self):
        return f"{self.reference_code}: {self.full_text[:50]}..."


class EducationalModule(models.Model):
    """
    Stores educational module categories (e.g., MATEMATYKA, JĘZYK).
    Tracks both predefined modules and AI-suggested modules.
    """
    module_name = models.CharField(
        max_length=200,
        unique=True,
        db_index=True,
        help_text="Module name in Polish (e.g., 'MATEMATYKA')"
    )
    is_ai_suggested = models.BooleanField(
        default=False,
        db_index=True,
        help_text="TRUE if AI-suggested, FALSE if predefined"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'educational_modules'
        ordering = ['module_name']
        verbose_name = 'Educational Module'
        verbose_name_plural = 'Educational Modules'

    def __str__(self):
        return self.module_name
```

### 3.2 Creating Migrations

After defining your models, generate and apply migrations:

```bash
cd webserver
python manage.py makemigrations
python manage.py migrate
```

Django will automatically create the tables with proper column types for your database backend (SQLite, PostgreSQL, MySQL).

---

## 4. Data Seeding

### 4.1 Major Curriculum References

**Data Source:** Polish "Podstawa Programowa Wychowania Przedszkolnego" - major sections

**Sample Data:**
```sql
INSERT INTO major_curriculum_references (reference_code, full_text) VALUES
('1', 'Dziecko zdolne jest zadbać o swoje zdrowie, sprawność fizyczną i bezpieczeństwo;'),
('2', 'Dziecko rozumie siebie, swoje emocje i potrzeby;'),
('3', 'Dziecko nawiązuje relacje z innymi;'),
('4', 'Dziecko poznaje i rozumie świat;'),
('5', 'Dziecko potrafi wypowiadać swoje myśli i rozumie innych;'),
('6', 'Dziecko jest kreatywne i potrafi wyrażać siebie;');
```

**Django Admin Method:**
1. Start Django development server: `python manage.py runserver`
2. Navigate to `http://localhost:8000/admin`
3. Login with superuser credentials
4. Click "Major Curriculum References" → "Add"
5. Manually enter each major section

**Django Management Command (Recommended):**

Create a custom management command:

```python
# webserver/lessonplanner/management/commands/seed_major_curriculum.py

from django.core.management.base import BaseCommand
from lessonplanner.models import MajorCurriculumReference


class Command(BaseCommand):
    help = 'Seed major curriculum references'

    def handle(self, *args, **options):
        major_refs = [
            ('1', 'Dziecko zdolne jest zadbać o swoje zdrowie, sprawność fizyczną i bezpieczeństwo;'),
            ('2', 'Dziecko rozumie siebie, swoje emocje i potrzeby;'),
            ('3', 'Dziecko nawiązuje relacje z innymi;'),
            ('4', 'Dziecko poznaje i rozumie świat;'),
            ('5', 'Dziecko potrafi wypowiadać swoje myśli i rozumie innych;'),
            ('6', 'Dziecko jest kreatywne i potrafi wyrażać siebie;'),
        ]

        for code, text in major_refs:
            MajorCurriculumReference.objects.get_or_create(
                reference_code=code,
                defaults={'full_text': text}
            )
            self.stdout.write(f"Created/verified: {code}")

        self.stdout.write(self.style.SUCCESS('Successfully seeded major curriculum references'))
```

**Run the command:**
```bash
cd webserver
python manage.py seed_major_curriculum
```

### 4.2 Detailed Curriculum References

**Data Source:** Polish "Podstawa Programowa Wychowania Przedszkolnego" - detailed paragraphs

**Seeding Strategy:**
1. **CSV Import** (Recommended for large datasets)
2. **Django Fixtures** (JSON)
3. **Manual Entry via Admin** (Small datasets)

#### Option 1: CSV Import

**CSV Format (`curriculum_refs.csv`):**
```csv
reference_code,full_text,major_code
1.1,"zgłasza potrzeby fizjologiczne, samodzielnie wykonuje podstawowe czynności higieniczne;",1
2.5,"rozstaje się z rodzicami bez lęku, ma świadomość, że rozstanie takie bywa dłuższe lub krótsze;",2
3.8,"obdarza uwagą inne dzieci i osoby dorosłe;",3
4.15,"przelicza elementy zbiorów w czasie zabawy, prac porządkowych, ćwiczeń i wykonywania innych czynności, posługuje się liczebnikami głównymi i porządkowymi;",4
4.18,"rozpoznaje cyfry oznaczające liczby od 0 do 10, eksperymentuje z tworzeniem kolejnych liczb;",4
```

**Django Management Command:**

```python
# webserver/lessonplanner/management/commands/import_curriculum.py

import csv
from django.core.management.base import BaseCommand
from lessonplanner.models import CurriculumReference, MajorCurriculumReference


class Command(BaseCommand):
    help = 'Import curriculum references from CSV'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to CSV file')

    def handle(self, *args, **options):
        csv_path = options['csv_file']

        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            imported = 0

            for row in reader:
                try:
                    # Look up major reference
                    major_ref = MajorCurriculumReference.objects.get(
                        reference_code=row['major_code']
                    )

                    # Create or update curriculum reference
                    ref, created = CurriculumReference.objects.get_or_create(
                        reference_code=row['reference_code'],
                        defaults={
                            'full_text': row['full_text'],
                            'major_reference': major_ref
                        }
                    )

                    if created:
                        imported += 1
                        self.stdout.write(f"Imported: {row['reference_code']}")
                    else:
                        self.stdout.write(f"Already exists: {row['reference_code']}")

                except MajorCurriculumReference.DoesNotExist:
                    self.stdout.write(
                        self.style.ERROR(
                            f"Major reference '{row['major_code']}' not found for {row['reference_code']}"
                        )
                    )
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f"Error importing {row['reference_code']}: {str(e)}")
                    )

        self.stdout.write(
            self.style.SUCCESS(f'Successfully imported {imported} curriculum references')
        )
```

**Run the import:**
```bash
cd webserver
python manage.py import_curriculum ../data/curriculum_refs.csv
```

#### Option 2: Django Fixture (JSON)

**Fixture Format (`initial_curriculum.json`):**
```json
[
  {
    "model": "lessonplanner.curriculumreference",
    "pk": 1,
    "fields": {
      "reference_code": "1.1",
      "full_text": "zgłasza potrzeby fizjologiczne, samodzielnie wykonuje podstawowe czynności higieniczne;",
      "major_reference": 1,
      "created_at": "2025-11-10T10:00:00Z"
    }
  },
  {
    "model": "lessonplanner.curriculumreference",
    "pk": 2,
    "fields": {
      "reference_code": "4.15",
      "full_text": "przelicza elementy zbiorów w czasie zabawy...",
      "major_reference": 4,
      "created_at": "2025-11-10T10:00:00Z"
    }
  }
]
```

**Load Fixture:**
```bash
cd webserver
python manage.py loaddata initial_curriculum.json
```

**Export Existing Data (to create fixture):**
```bash
python manage.py dumpdata lessonplanner.CurriculumReference --indent 2 > initial_curriculum.json
```

### 4.3 Educational Modules

**Initial Predefined Modules:**

```sql
INSERT INTO educational_modules (module_name, is_ai_suggested) VALUES
('JĘZYK', FALSE),
('MATEMATYKA', FALSE),
('MOTORYKA MAŁA', FALSE),
('MOTORYKA DUŻA', FALSE),
('FORMY PLASTYCZNE', FALSE),
('MUZYKA', FALSE),
('POZNAWCZE', FALSE),
('WSPÓŁPRACA', FALSE),
('EMOCJE', FALSE),
('SPOŁECZNE', FALSE),
('SENSORYKA', FALSE),
('ZDROWIE', FALSE);
```

**Django Management Command:**

```python
# webserver/lessonplanner/management/commands/seed_modules.py

from django.core.management.base import BaseCommand
from lessonplanner.models import EducationalModule


class Command(BaseCommand):
    help = 'Seed educational modules'

    def handle(self, *args, **options):
        modules = [
            'JĘZYK',
            'MATEMATYKA',
            'MOTORYKA MAŁA',
            'MOTORYKA DUŻA',
            'FORMY PLASTYCZNE',
            'MUZYKA',
            'POZNAWCZE',
            'WSPÓŁPRACA',
            'EMOCJE',
            'SPOŁECZNE',
            'SENSORYKA',
            'ZDROWIE',
        ]

        for module_name in modules:
            EducationalModule.objects.get_or_create(
                module_name=module_name,
                defaults={'is_ai_suggested': False}
            )
            self.stdout.write(f"Created/verified: {module_name}")

        self.stdout.write(
            self.style.SUCCESS(f'Successfully seeded {len(modules)} educational modules')
        )
```

**Run the command:**
```bash
cd webserver
python manage.py seed_modules
```

**Django Fixture Alternative:**

```json
[
  {"model": "lessonplanner.educationalmodule", "fields": {"module_name": "JĘZYK", "is_ai_suggested": false}},
  {"model": "lessonplanner.educationalmodule", "fields": {"module_name": "MATEMATYKA", "is_ai_suggested": false}},
  {"model": "lessonplanner.educationalmodule", "fields": {"module_name": "MOTORYKA MAŁA", "is_ai_suggested": false}},
  {"model": "lessonplanner.educationalmodule", "fields": {"module_name": "MOTORYKA DUŻA", "is_ai_suggested": false}},
  {"model": "lessonplanner.educationalmodule", "fields": {"module_name": "FORMY PLASTYCZNE", "is_ai_suggested": false}},
  {"model": "lessonplanner.educationalmodule", "fields": {"module_name": "MUZYKA", "is_ai_suggested": false}},
  {"model": "lessonplanner.educationalmodule", "fields": {"module_name": "POZNAWCZE", "is_ai_suggested": false}},
  {"model": "lessonplanner.educationalmodule", "fields": {"module_name": "WSPÓŁPRACA", "is_ai_suggested": false}},
  {"model": "lessonplanner.educationalmodule", "fields": {"module_name": "EMOCJE", "is_ai_suggested": false}},
  {"model": "lessonplanner.educationalmodule", "fields": {"module_name": "SPOŁECZNE", "is_ai_suggested": false}},
  {"model": "lessonplanner.educationalmodule", "fields": {"module_name": "SENSORYKA", "is_ai_suggested": false}},
  {"model": "lessonplanner.educationalmodule", "fields": {"module_name": "ZDROWIE", "is_ai_suggested": false}}
]
```

**Load fixture:**
```bash
python manage.py loaddata initial_modules.json
```

---

## 5. Verification

### 5.1 Verify Data Was Loaded

**Django Shell:**
```bash
cd webserver
python manage.py shell
```

```python
from lessonplanner.models import MajorCurriculumReference, CurriculumReference, EducationalModule

# Check major references
print(f"Major references: {MajorCurriculumReference.objects.count()}")
MajorCurriculumReference.objects.all().values_list('reference_code', flat=True)

# Check detailed references
print(f"Curriculum references: {CurriculumReference.objects.count()}")
CurriculumReference.objects.all().values_list('reference_code', flat=True)

# Check modules
print(f"Educational modules: {EducationalModule.objects.count()}")
EducationalModule.objects.all().values_list('module_name', flat=True)

# Verify foreign key relationship
ref = CurriculumReference.objects.get(reference_code='4.15')
print(f"Reference: {ref.reference_code}")
print(f"Major section: {ref.major_reference.reference_code}")
print(f"Major text: {ref.major_reference.full_text}")
```

**Direct SQL:**
```bash
# SQLite
sqlite3 webserver/db.sqlite3

# Check counts
SELECT COUNT(*) FROM major_curriculum_references;
SELECT COUNT(*) FROM curriculum_references;
SELECT COUNT(*) FROM educational_modules;

# Check relationship
SELECT
    cr.reference_code,
    mcr.reference_code as major_code
FROM curriculum_references cr
JOIN major_curriculum_references mcr ON cr.major_reference_id = mcr.id;
```

### 5.2 Test API Endpoints

**Start development server:**
```bash
cd webserver
python manage.py runserver
```

**Test endpoints:**
```bash
# Get all curriculum references
curl http://localhost:8000/api/curriculum-refs

# Get specific reference
curl http://localhost:8000/api/curriculum-refs/4.15

# Get all modules
curl http://localhost:8000/api/modules
```

---

## 6. Database Backup

### 6.1 SQLite Backup (MVP)

**Database File Location:** `webserver/db.sqlite3`

**Simple File Copy:**
```bash
cp webserver/db.sqlite3 webserver/db.sqlite3.backup
```

**SQLite Backup Command (safer - handles locks):**
```bash
sqlite3 webserver/db.sqlite3 ".backup 'backup/db-$(date +%Y%m%d).sqlite3'"
```

**Django Dumpdata (portable, can restore to any DB):**
```bash
cd webserver
python manage.py dumpdata > backup/data-$(date +%Y%m%d).json
```

**Restore from dumpdata:**
```bash
python manage.py loaddata backup/data-20251110.json
```

### 6.2 PostgreSQL Backup

```bash
# Full database dump
pg_dump teacher_assist > backup/teacher_assist-$(date +%Y%m%d).sql

# Compressed backup
pg_dump teacher_assist | gzip > backup/teacher_assist-$(date +%Y%m%d).sql.gz

# Restore
psql teacher_assist < backup/teacher_assist-20251110.sql
```

---

## 7. Common Issues and Troubleshooting

### Issue: "Foreign key constraint fails" during import

**Cause:** Trying to insert curriculum_references before major_curriculum_references exist

**Solution:** Always seed major_curriculum_references first:
```bash
python manage.py seed_major_curriculum
python manage.py import_curriculum data/curriculum_refs.csv
```

### Issue: "Duplicate key value violates unique constraint"

**Cause:** Trying to insert reference_code that already exists

**Solution:** Use `get_or_create()` or `update_or_create()` in management commands:
```python
CurriculumReference.objects.get_or_create(
    reference_code='4.15',
    defaults={'full_text': '...', 'major_reference': major_ref}
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
- Ensure CSV files are UTF-8 encoded
- For SQLite, no special configuration needed
- For PostgreSQL, ensure database uses UTF-8 encoding:
  ```bash
  createdb teacher_assist --encoding=UTF8 --locale=pl_PL.UTF-8
  ```

---

## 8. Complete Setup Script

**Bash script for full initialization:**

```bash
#!/bin/bash
# setup_database.sh

set -e  # Exit on error

echo "Starting database initialization..."

cd webserver

# Step 1: Run migrations
echo "Running migrations..."
python manage.py migrate

# Step 2: Create superuser (interactive)
echo "Creating superuser..."
python manage.py createsuperuser

# Step 3: Seed major curriculum references
echo "Seeding major curriculum references..."
python manage.py seed_major_curriculum

# Step 4: Import detailed curriculum references
echo "Importing curriculum references..."
python manage.py import_curriculum ../data/curriculum_refs.csv

# Step 5: Seed educational modules
echo "Seeding educational modules..."
python manage.py seed_modules

# Step 6: Verify
echo "Verifying data..."
python manage.py shell -c "
from lessonplanner.models import MajorCurriculumReference, CurriculumReference, EducationalModule
print(f'Major refs: {MajorCurriculumReference.objects.count()}')
print(f'Curriculum refs: {CurriculumReference.objects.count()}')
print(f'Modules: {EducationalModule.objects.count()}')
"

echo "Database initialization complete!"
echo "Start the server with: python manage.py runserver"
```

**Make script executable and run:**
```bash
chmod +x setup_database.sh
./setup_database.sh
```

---

## Document History

| Version | Date       | Author | Changes                                   |
|---------|------------|--------|-------------------------------------------|
| 1.0     | 2025-11-10 | Dev    | Initial database initialization guide     |

---

**Related Documentation:**
- **Database Schema:** See `docs/db_schema.md` for complete table definitions
- **API Documentation:** See `docs/django_api.md` for API endpoints
- **Product Requirements:** See `docs/PRD.md` for functional requirements
