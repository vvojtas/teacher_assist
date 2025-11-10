# Database Architecture Documentation

**Project:** Teacher Assist - AI-Powered Lesson Planning Tool
**Version:** 1.0 (MVP)
**Database:** SQLite (development) - Designed to be engine-agnostic
**Last Updated:** 2025-11-10

---

## 1. Overview

This document defines the database architecture for the Teacher Assist application. The design supports the MVP requirements while being flexible for future enhancements.

### Design Principles

1. **Engine Agnostic**: Use standard SQL types compatible with PostgreSQL, MySQL, SQLite
2. **Normalization**: Follow 3NF to minimize data redundancy
3. **Scalability**: Structure supports future multi-user features
4. **Performance**: Strategic indexes for common query patterns
5. **Data Integrity**: Constraints and foreign keys enforce referential integrity

### MVP Scope

**Current Phase (MVP):**
- Reference data tables only (curriculum, modules)
- NO session data persistence (lesson plans stored in browser memory only)

**Future Phase (Post-MVP):**
- Add lesson plan persistence tables
- Add user authentication tables (when multi-user support is added)

---

## 2. Entity Relationship Overview

### MVP Phase Entities

```
┌─────────────────────────┐
│ curriculum_references   │
│  (Reference Data)       │
└─────────────────────────┘

┌─────────────────────────┐
│ educational_modules     │
│  (Reference Data)       │
└─────────────────────────┘
```

**Note:** These tables have no relationships in MVP. They serve as standalone reference/lookup tables.

### Future Phase Entities (When Persistence Added)

```
┌──────────────────┐
│  lesson_plans    │
│  (Master record) │
└────────┬─────────┘
         │
         │ 1:N
         │
         ▼
┌──────────────────────┐       N:1       ┌──────────────────────┐
│  lesson_plan_rows    │─────────────────▶│ educational_modules  │
│  (Activity records)  │                  │  (Reference Data)    │
└──────────┬───────────┘                  └──────────────────────┘
           │
           │ N:M
           │
           ▼
┌──────────────────────────┐
│  row_curriculum_refs     │ (Junction Table)
│  (Many-to-many mapping)  │
└───────────┬──────────────┘
            │
            │ N:1
            │
            ▼
┌─────────────────────────┐
│ curriculum_references   │
│  (Reference Data)       │
└─────────────────────────┘
```

---

## 3. Entity Definitions (MVP Phase)

### 3.1 curriculum_references

**Purpose:** Stores Polish kindergarten curriculum reference codes ("Podstawa Programowa") and their complete text descriptions. Used for tooltip display when teachers hover over curriculum reference codes.

**Table Name:** `curriculum_references`

| Column Name      | Type         | Constraints                    | Description                                      |
|------------------|--------------|--------------------------------|--------------------------------------------------|
| `id`             | INTEGER      | PRIMARY KEY, AUTO_INCREMENT    | Unique identifier                                |
| `reference_code` | VARCHAR(20)  | UNIQUE, NOT NULL, INDEX        | Curriculum code (e.g., "4.15", "2.5")            |
| `full_text`      | TEXT         | NOT NULL                       | Complete Polish curriculum requirement text      |
| `created_at`     | TIMESTAMP    | NOT NULL, DEFAULT CURRENT_TS   | Timestamp when record was created                |

**Indexes:**
- PRIMARY KEY on `id` (automatic)
- UNIQUE INDEX on `reference_code` (for fast lookups by code)

**Constraints:**
- `reference_code` must be unique (no duplicate curriculum codes)
- `reference_code` and `full_text` cannot be null
- `created_at` defaults to current timestamp

**Sample Data:**
```sql
INSERT INTO curriculum_references (reference_code, full_text) VALUES
('1.1', 'zgłasza potrzeby fizjologiczne, samodzielnie wykonuje podstawowe czynności higieniczne;'),
('2.5', 'rozstaje się z rodzicami bez lęku, ma świadomość, że rozstanie takie bywa dłuższe lub krótsze;'),
('3.8', 'obdarza uwagą inne dzieci i osoby dorosłe;'),
('4.15', 'przelicza elementy zbiorów w czasie zabawy, prac porządkowych, ćwiczeń i wykonywania innych czynności, posługuje się liczebnikami głównymi i porządkowymi...');
```

**Expected Data Volume:**
- MVP: 50-100 records
- Growth: Minimal (curriculum changes infrequently)

**Query Patterns:**
- Bulk load all references: `SELECT reference_code, full_text FROM curriculum_references`
- Single lookup: `SELECT full_text FROM curriculum_references WHERE reference_code = ?`

---

### 3.2 educational_modules

**Purpose:** Stores educational module categories (e.g., MATEMATYKA, JĘZYK, MOTORYKA DUŻA). Tracks both predefined modules and AI-suggested modules for potential reuse.

**Table Name:** `educational_modules`

| Column Name       | Type         | Constraints                    | Description                                      |
|-------------------|--------------|--------------------------------|--------------------------------------------------|
| `id`              | INTEGER      | PRIMARY KEY, AUTO_INCREMENT    | Unique identifier                                |
| `module_name`     | VARCHAR(200) | UNIQUE, NOT NULL, INDEX        | Module name in Polish (e.g., "MATEMATYKA")       |
| `is_ai_suggested` | BOOLEAN      | NOT NULL, DEFAULT FALSE        | TRUE if AI-suggested, FALSE if predefined        |
| `created_at`      | TIMESTAMP    | NOT NULL, DEFAULT CURRENT_TS   | Timestamp when module was added                  |

**Indexes:**
- PRIMARY KEY on `id` (automatic)
- UNIQUE INDEX on `module_name` (prevent duplicate module names)
- INDEX on `is_ai_suggested` (for filtering queries)

**Constraints:**
- `module_name` must be unique (case-sensitive or case-insensitive depending on DB)
- `is_ai_suggested` defaults to FALSE
- `created_at` defaults to current timestamp

**Sample Data:**
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

**Expected Data Volume:**
- MVP: 12-20 predefined modules
- Growth: Slow (AI may suggest 5-10 new modules over time)

**Query Patterns:**
- Load all modules: `SELECT module_name FROM educational_modules ORDER BY module_name`
- Filter by type: `SELECT module_name FROM educational_modules WHERE is_ai_suggested = FALSE`
- Check if module exists: `SELECT id FROM educational_modules WHERE module_name = ?`

---

## 4. Entity Definitions (Future Phase - Persistence)

**Note:** These tables are NOT implemented in MVP but are documented here for future reference and architectural planning.

### 4.1 lesson_plans

**Purpose:** Stores complete lesson planning sessions with metadata. Each record represents one monthly/weekly lesson plan.

**Table Name:** `lesson_plans`

| Column Name    | Type         | Constraints                    | Description                                      |
|----------------|--------------|--------------------------------|--------------------------------------------------|
| `id`           | INTEGER      | PRIMARY KEY, AUTO_INCREMENT    | Unique lesson plan identifier                    |
| `title`        | VARCHAR(200) | NOT NULL                       | Plan title (e.g., "Październik 2025")            |
| `theme`        | VARCHAR(200) | NULL                           | Weekly/monthly theme (e.g., "Jesień - zbiory")   |
| `created_at`   | TIMESTAMP    | NOT NULL, DEFAULT CURRENT_TS   | When plan was created                            |
| `updated_at`   | TIMESTAMP    | NOT NULL, DEFAULT CURRENT_TS   | Last modification timestamp                      |
| `user_id`      | INTEGER      | NULL, FOREIGN KEY (future)     | Owner (NULL in MVP single-user mode)             |

**Indexes:**
- PRIMARY KEY on `id`
- INDEX on `created_at` (for sorting by date)
- INDEX on `user_id` (for future multi-user filtering)

**Constraints:**
- `title` cannot be null
- `updated_at` auto-updates on row modification (trigger or ORM)

**Relationships:**
- 1:N with `lesson_plan_rows` (one plan contains many activities)

---

### 4.2 lesson_plan_rows

**Purpose:** Stores individual activities/rows within a lesson plan. Each row contains an activity description and AI-generated metadata.

**Table Name:** `lesson_plan_rows`

| Column Name        | Type         | Constraints                    | Description                                      |
|--------------------|--------------|--------------------------------|--------------------------------------------------|
| `id`               | INTEGER      | PRIMARY KEY, AUTO_INCREMENT    | Unique row identifier                            |
| `lesson_plan_id`   | INTEGER      | NOT NULL, FOREIGN KEY          | References `lesson_plans.id`                     |
| `row_order`        | INTEGER      | NOT NULL                       | Display order within plan (0, 1, 2...)           |
| `activity`         | TEXT         | NOT NULL                       | Activity description (user input)                |
| `module_id`        | INTEGER      | NULL, FOREIGN KEY              | References `educational_modules.id`              |
| `objectives`       | TEXT         | NULL                           | Educational objectives (JSON array or text)      |
| `is_ai_generated`  | BOOLEAN      | NOT NULL, DEFAULT FALSE        | TRUE if metadata was AI-generated                |
| `is_user_edited`   | BOOLEAN      | NOT NULL, DEFAULT FALSE        | TRUE if user manually edited AI content          |
| `created_at`       | TIMESTAMP    | NOT NULL, DEFAULT CURRENT_TS   | When row was created                             |
| `updated_at`       | TIMESTAMP    | NOT NULL, DEFAULT CURRENT_TS   | Last modification timestamp                      |

**Indexes:**
- PRIMARY KEY on `id`
- INDEX on `lesson_plan_id` (for fetching all rows in a plan)
- INDEX on `(lesson_plan_id, row_order)` (composite index for ordered retrieval)
- FOREIGN KEY on `lesson_plan_id` → `lesson_plans.id` (CASCADE DELETE)
- FOREIGN KEY on `module_id` → `educational_modules.id` (SET NULL on delete)

**Constraints:**
- `lesson_plan_id` cannot be null
- `activity` cannot be null
- `row_order` must be >= 0
- UNIQUE constraint on `(lesson_plan_id, row_order)` (no duplicate order values within same plan)

**Relationships:**
- N:1 with `lesson_plans` (many rows belong to one plan)
- N:1 with `educational_modules` (many rows can reference one module)
- N:M with `curriculum_references` via junction table

**Storage Considerations:**
- `objectives` can be stored as JSON array or newline-separated text
  - JSON: `["Objective 1", "Objective 2"]`
  - Text: `"Objective 1\nObjective 2"`
- Django: Use JSONField (PostgreSQL) or TextField with serialization (SQLite)

---

### 4.3 row_curriculum_refs

**Purpose:** Junction table for many-to-many relationship between lesson plan rows and curriculum references. One row can have multiple curriculum refs, and one curriculum ref can be used in multiple rows.

**Table Name:** `row_curriculum_refs`

| Column Name             | Type         | Constraints                    | Description                                      |
|-------------------------|--------------|--------------------------------|--------------------------------------------------|
| `id`                    | INTEGER      | PRIMARY KEY, AUTO_INCREMENT    | Unique identifier                                |
| `lesson_plan_row_id`    | INTEGER      | NOT NULL, FOREIGN KEY          | References `lesson_plan_rows.id`                 |
| `curriculum_ref_id`     | INTEGER      | NOT NULL, FOREIGN KEY          | References `curriculum_references.id`            |

**Indexes:**
- PRIMARY KEY on `id`
- INDEX on `lesson_plan_row_id` (for finding all refs for a row)
- INDEX on `curriculum_ref_id` (for finding all rows using a ref)
- UNIQUE constraint on `(lesson_plan_row_id, curriculum_ref_id)` (prevent duplicates)
- FOREIGN KEY on `lesson_plan_row_id` → `lesson_plan_rows.id` (CASCADE DELETE)
- FOREIGN KEY on `curriculum_ref_id` → `curriculum_references.id` (RESTRICT DELETE)

**Constraints:**
- Both foreign key columns cannot be null
- Combination of `(lesson_plan_row_id, curriculum_ref_id)` must be unique

**Relationships:**
- N:1 with `lesson_plan_rows`
- N:1 with `curriculum_references`

**Query Pattern:**
```sql
-- Get all curriculum refs for a specific row
SELECT cr.reference_code, cr.full_text
FROM curriculum_references cr
JOIN row_curriculum_refs rcr ON cr.id = rcr.curriculum_ref_id
WHERE rcr.lesson_plan_row_id = ?
```

---

## 5. Database Initialization

### 5.1 SQL Schema (Engine Agnostic)

**SQLite-compatible schema (MVP):**

```sql
-- Table: curriculum_references
CREATE TABLE IF NOT EXISTS curriculum_references (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    reference_code VARCHAR(20) NOT NULL UNIQUE,
    full_text TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_curriculum_references_code ON curriculum_references(reference_code);

-- Table: educational_modules
CREATE TABLE IF NOT EXISTS educational_modules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    module_name VARCHAR(200) NOT NULL UNIQUE,
    is_ai_suggested BOOLEAN NOT NULL DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_educational_modules_name ON educational_modules(module_name);
CREATE INDEX idx_educational_modules_ai_suggested ON educational_modules(is_ai_suggested);
```

**PostgreSQL-compatible schema (for future migration):**

```sql
-- Table: curriculum_references
CREATE TABLE IF NOT EXISTS curriculum_references (
    id SERIAL PRIMARY KEY,
    reference_code VARCHAR(20) NOT NULL UNIQUE,
    full_text TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_curriculum_references_code ON curriculum_references(reference_code);

-- Table: educational_modules
CREATE TABLE IF NOT EXISTS educational_modules (
    id SERIAL PRIMARY KEY,
    module_name VARCHAR(200) NOT NULL UNIQUE,
    is_ai_suggested BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_educational_modules_name ON educational_modules(module_name);
CREATE INDEX idx_educational_modules_ai_suggested ON educational_modules(is_ai_suggested);
```

**Key Differences:**
- SQLite: `INTEGER PRIMARY KEY AUTOINCREMENT`, `BOOLEAN` stored as 0/1
- PostgreSQL: `SERIAL PRIMARY KEY`, native `BOOLEAN` type
- MySQL: `INT PRIMARY KEY AUTO_INCREMENT`, `TINYINT(1)` for BOOLEAN

### 5.2 Django Models (Recommended)

Django ORM abstracts database differences automatically:

```python
# models.py

from django.db import models

class CurriculumReference(models.Model):
    """
    Stores Polish curriculum reference codes (Podstawa Programowa)
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

**Django Advantages:**
- Automatic migrations via `python manage.py makemigrations`
- Database-agnostic (change `ENGINE` in settings.py to switch databases)
- Built-in admin interface for data management
- ORM query optimization

---

## 6. Data Seeding

### 6.1 Initial Curriculum References

**Data Source:** Official Polish "Podstawa Programowa Wychowania Przedszkolnego" document

**Seeding Strategy:**
1. **Manual Entry** (MVP approach): Admin manually adds via Django admin
2. **CSV Import** (Recommended): Create CSV file and import via Django management command
3. **Fixture File** (Production): Django JSON fixture loaded via `loaddata`

**Example CSV format:**
```csv
reference_code,full_text
1.1,"zgłasza potrzeby fizjologiczne, samodzielnie wykonuje podstawowe czynności higieniczne;"
2.5,"rozstaje się z rodzicami bez lęku, ma świadomość, że rozstanie takie bywa dłuższe lub krótsze;"
3.8,"obdarza uwagą inne dzieci i osoby dorosłe;"
4.15,"przelicza elementy zbiorów w czasie zabawy..."
```

**Django Management Command Example:**
```python
# management/commands/import_curriculum.py
import csv
from django.core.management.base import BaseCommand
from myapp.models import CurriculumReference

class Command(BaseCommand):
    help = 'Import curriculum references from CSV'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str)

    def handle(self, *args, **options):
        with open(options['csv_file'], 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                CurriculumReference.objects.get_or_create(
                    reference_code=row['reference_code'],
                    defaults={'full_text': row['full_text']}
                )
        self.stdout.write(self.style.SUCCESS('Successfully imported curriculum references'))
```

### 6.2 Initial Educational Modules

**Seeding Method:** Django fixture or SQL INSERT

**Django Fixture (JSON):**
```json
[
  {
    "model": "myapp.educationalmodule",
    "fields": {
      "module_name": "JĘZYK",
      "is_ai_suggested": false
    }
  },
  {
    "model": "myapp.educationalmodule",
    "fields": {
      "module_name": "MATEMATYKA",
      "is_ai_suggested": false
    }
  }
]
```

**Load Fixture:**
```bash
python manage.py loaddata initial_modules.json
```

---

## 7. Performance Considerations

### 7.1 Index Strategy

**Current Indexes (MVP):**

| Table                    | Index Type | Columns              | Purpose                          |
|--------------------------|------------|----------------------|----------------------------------|
| curriculum_references    | UNIQUE     | reference_code       | Fast lookup by code              |
| educational_modules      | UNIQUE     | module_name          | Fast lookup by name              |
| educational_modules      | INDEX      | is_ai_suggested      | Filter predefined vs AI-suggested|

**Future Indexes (When Persistence Added):**

| Table                    | Index Type | Columns                      | Purpose                          |
|--------------------------|------------|------------------------------|----------------------------------|
| lesson_plans             | INDEX      | created_at                   | Sort plans by date               |
| lesson_plans             | INDEX      | user_id                      | Filter plans by user             |
| lesson_plan_rows         | INDEX      | lesson_plan_id               | Fetch all rows for a plan        |
| lesson_plan_rows         | COMPOSITE  | (lesson_plan_id, row_order)  | Ordered retrieval within plan    |
| row_curriculum_refs      | INDEX      | lesson_plan_row_id           | Find refs for a row              |
| row_curriculum_refs      | INDEX      | curriculum_ref_id            | Find rows using a ref            |

### 7.2 Query Optimization

**Bulk Loading (Curriculum References):**
```sql
-- Good: Single query loads all references
SELECT reference_code, full_text FROM curriculum_references;

-- Bad: N+1 queries for each reference
SELECT full_text FROM curriculum_references WHERE reference_code = '4.15';
SELECT full_text FROM curriculum_references WHERE reference_code = '4.18';
-- (repeated for each code)
```

**Django ORM Optimization:**
```python
# Good: Use select_related() for foreign keys
rows = LessonPlanRow.objects.select_related('module').filter(lesson_plan_id=1)

# Good: Use prefetch_related() for many-to-many
rows = LessonPlanRow.objects.prefetch_related('curriculum_refs').filter(lesson_plan_id=1)

# Bad: Lazy loading causes N+1 queries
rows = LessonPlanRow.objects.filter(lesson_plan_id=1)
for row in rows:
    print(row.module.module_name)  # Additional query per row!
```

### 7.3 Expected Query Volume

**MVP Phase:**
- Page load: 1-2 queries (load curriculum refs, load modules)
- Frequency: ~20 sessions/month
- Database size: <1 MB

**Future Phase:**
- Load lesson plan: 3-5 queries (plan + rows + related data)
- Save lesson plan: 10-20 queries (transactional batch inserts)
- Database size: ~10-50 MB (estimated 100 plans × 500KB each)

---

## 8. Database Engine Migration Path

### 8.1 SQLite → PostgreSQL Migration

**Why Migrate:**
- Multi-user deployment requires connection pooling
- Better concurrency and ACID guarantees
- Production-grade performance

**Migration Steps:**

1. **Export SQLite data:**
   ```bash
   python manage.py dumpdata > data.json
   ```

2. **Update Django settings.py:**
   ```python
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.postgresql',
           'NAME': 'teacher_assist',
           'USER': 'postgres',
           'PASSWORD': 'password',
           'HOST': 'localhost',
           'PORT': '5432',
       }
   }
   ```

3. **Create PostgreSQL database:**
   ```bash
   createdb teacher_assist
   ```

4. **Run migrations:**
   ```bash
   python manage.py migrate
   ```

5. **Import data:**
   ```bash
   python manage.py loaddata data.json
   ```

**Compatibility Notes:**
- Django ORM handles most differences automatically
- BOOLEAN fields: SQLite (0/1) → PostgreSQL (TRUE/FALSE) - Django converts
- AUTO_INCREMENT: SQLite → SERIAL (PostgreSQL) - Django converts
- Timezone handling: Enable `USE_TZ = True` in Django settings

### 8.2 MySQL Support

**Changes Required:**
```python
# settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'teacher_assist',
        'USER': 'root',
        'PASSWORD': 'password',
        'HOST': 'localhost',
        'PORT': '3306',
        'OPTIONS': {
            'charset': 'utf8mb4',  # Important for Polish characters
        },
    }
}
```

**Data Type Mappings:**
- `BOOLEAN` → `TINYINT(1)`
- `TEXT` → `LONGTEXT`
- `AUTOINCREMENT` → `AUTO_INCREMENT`

---

## 9. Data Integrity and Constraints

### 9.1 Referential Integrity

**Foreign Key Actions (Future Phase):**

| Parent Table          | Child Table           | Relationship | ON DELETE Action | Reasoning                          |
|-----------------------|-----------------------|--------------|------------------|------------------------------------|
| lesson_plans          | lesson_plan_rows      | 1:N          | CASCADE          | Delete rows when plan deleted      |
| educational_modules   | lesson_plan_rows      | N:1          | SET NULL         | Preserve rows if module deleted    |
| curriculum_references | row_curriculum_refs   | N:1          | RESTRICT         | Prevent deletion of used refs      |
| lesson_plan_rows      | row_curriculum_refs   | N:1          | CASCADE          | Delete refs when row deleted       |

**Django Implementation:**
```python
class LessonPlanRow(models.Model):
    lesson_plan = models.ForeignKey(
        'LessonPlan',
        on_delete=models.CASCADE,  # Delete row if plan deleted
        related_name='rows'
    )
    module = models.ForeignKey(
        'EducationalModule',
        on_delete=models.SET_NULL,  # Keep row if module deleted
        null=True,
        blank=True
    )
```

### 9.2 Check Constraints

**Example Constraints (Future):**
```sql
-- Ensure row_order is non-negative
ALTER TABLE lesson_plan_rows ADD CONSTRAINT chk_row_order CHECK (row_order >= 0);

-- Ensure activity is not empty string
ALTER TABLE lesson_plan_rows ADD CONSTRAINT chk_activity_not_empty CHECK (LENGTH(activity) > 0);
```

**Django Implementation:**
```python
from django.db import models
from django.core.validators import MinValueValidator

class LessonPlanRow(models.Model):
    row_order = models.IntegerField(validators=[MinValueValidator(0)])
    activity = models.TextField(blank=False)  # Enforce non-empty at model level
```

---

## 10. Backup and Maintenance

### 10.1 SQLite Backup Strategy (MVP)

**Database File Location:** `webserver/db.sqlite3`

**Backup Methods:**

1. **Simple File Copy:**
   ```bash
   cp webserver/db.sqlite3 webserver/db.sqlite3.backup
   ```

2. **SQLite Backup Command (safer - handles locks):**
   ```bash
   sqlite3 webserver/db.sqlite3 ".backup 'backup/db-$(date +%Y%m%d).sqlite3'"
   ```

3. **Django Dumpdata (portable):**
   ```bash
   python manage.py dumpdata > backup/data-$(date +%Y%m%d).json
   ```

**Note:** SQLite database is committed to git for MVP portability (development only).

### 10.2 PostgreSQL Backup (Future)

```bash
# Full database dump
pg_dump teacher_assist > backup/teacher_assist-$(date +%Y%m%d).sql

# Compressed backup
pg_dump teacher_assist | gzip > backup/teacher_assist-$(date +%Y%m%d).sql.gz

# Restore
psql teacher_assist < backup/teacher_assist-20251110.sql
```

---

## 11. Database Diagram (ASCII)

### MVP Phase
```
┌──────────────────────────────┐
│   curriculum_references      │
├──────────────────────────────┤
│ PK id                        │
│ UK reference_code (idx)      │
│    full_text                 │
│    created_at                │
└──────────────────────────────┘

┌──────────────────────────────┐
│   educational_modules        │
├──────────────────────────────┤
│ PK id                        │
│ UK module_name (idx)         │
│    is_ai_suggested (idx)     │
│    created_at                │
└──────────────────────────────┘
```

### Future Phase (Complete Schema)
```
┌──────────────────────────────┐
│      lesson_plans            │
├──────────────────────────────┤
│ PK id                        │
│    title                     │
│    theme                     │
│    created_at (idx)          │
│    updated_at                │
│ FK user_id (future)          │
└──────────┬───────────────────┘
           │
           │ 1:N
           ▼
┌──────────────────────────────┐          ┌──────────────────────────────┐
│    lesson_plan_rows          │   N:1    │   educational_modules        │
├──────────────────────────────┤ ────────▶├──────────────────────────────┤
│ PK id                        │          │ PK id                        │
│ FK lesson_plan_id (idx)      │          │ UK module_name (idx)         │
│    row_order                 │          │    is_ai_suggested (idx)     │
│    activity                  │          │    created_at                │
│ FK module_id                 │          └──────────────────────────────┘
│    objectives                │
│    is_ai_generated           │
│    is_user_edited            │
│    created_at                │
│    updated_at                │
└──────────┬───────────────────┘
           │
           │ N:M
           ▼
┌──────────────────────────────┐
│   row_curriculum_refs        │
│   (Junction Table)           │
├──────────────────────────────┤
│ PK id                        │
│ FK lesson_plan_row_id (idx)  │
│ FK curriculum_ref_id (idx)   │
│ UK (row_id, ref_id)          │
└──────────┬───────────────────┘
           │
           │ N:1
           ▼
┌──────────────────────────────┐
│   curriculum_references      │
├──────────────────────────────┤
│ PK id                        │
│ UK reference_code (idx)      │
│    full_text                 │
│    created_at                │
└──────────────────────────────┘
```

**Legend:**
- `PK` = Primary Key
- `FK` = Foreign Key
- `UK` = Unique Key
- `(idx)` = Indexed column

---

## 12. Development Checklist

### Phase 1: MVP Database Setup

- [ ] Create Django models for `curriculum_references` and `educational_modules`
- [ ] Run `python manage.py makemigrations`
- [ ] Run `python manage.py migrate`
- [ ] Create superuser: `python manage.py createsuperuser`
- [ ] Populate curriculum references (CSV import or manual via admin)
- [ ] Populate educational modules (fixture or manual via admin)
- [ ] Test API endpoints: `/api/curriculum-refs` and `/api/modules`
- [ ] Verify indexes are created (check SQLite schema)

### Phase 2: Add Persistence (Future)

- [ ] Create Django models for `lesson_plans` and `lesson_plan_rows`
- [ ] Create junction table model `row_curriculum_refs`
- [ ] Define foreign key relationships with appropriate CASCADE/SET NULL
- [ ] Add check constraints for data validation
- [ ] Create migrations and test on development database
- [ ] Write Django admin configurations for new models
- [ ] Test save/load workflow end-to-end
- [ ] Performance test with realistic data volumes (100 plans, 500 rows)

### Phase 3: Production Migration (Future)

- [ ] Set up PostgreSQL database server
- [ ] Update Django settings for PostgreSQL connection
- [ ] Run migrations on PostgreSQL
- [ ] Migrate data from SQLite to PostgreSQL
- [ ] Configure database backups (pg_dump cron job)
- [ ] Set up connection pooling (pgBouncer optional)
- [ ] Monitor query performance with Django Debug Toolbar
- [ ] Add database indexes based on slow query log analysis

---

## 13. References

- **PRD:** `/docs/PRD.md` - Product Requirements Document
- **API Docs:** `/docs/django_api.md` - Django Backend API Documentation
- **Django Models:** https://docs.djangoproject.com/en/5.2/topics/db/models/
- **Django Migrations:** https://docs.djangoproject.com/en/5.2/topics/migrations/
- **SQLite Docs:** https://www.sqlite.org/docs.html
- **PostgreSQL Docs:** https://www.postgresql.org/docs/

---

## Document History

| Version | Date       | Author | Changes                                      |
|---------|------------|--------|----------------------------------------------|
| 1.0     | 2025-11-10 | DB Architect | Initial database architecture specification |

---

**Next Steps:**
1. Review and approve database design
2. Implement Django models for MVP tables
3. Create database seed data (curriculum references)
4. Test database operations via Django ORM
