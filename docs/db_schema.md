# Database Schema Documentation

**Project:** Teacher Assist - AI-Powered Lesson Planning Tool
**Version:** 1.0 (MVP)
**Database:** SQLite (development) - Designed to be engine-agnostic
**Last Updated:** 2025-11-10

---

## 1. Overview

This document defines the database schema for the Teacher Assist application MVP. The design supports reference data storage for Polish kindergarten curriculum information and educational modules.

### Design Principles

1. **Engine Agnostic**: Use standard SQL types compatible with PostgreSQL, MySQL, SQLite
2. **Normalization**: Follow 3NF to minimize data redundancy
3. **Performance**: Strategic indexes for common query patterns
4. **Data Integrity**: Constraints and foreign keys enforce referential integrity

### MVP Scope

**Current Implementation:**
- Reference data tables only (curriculum, modules)
- NO session data persistence (lesson plans stored in browser memory only)

---

## 2. Entity Relationship Diagram

```
┌──────────────────────────────┐
│ major_curriculum_references  │
│  (Main sections)             │
└──────────┬───────────────────┘
           │
           │ 1:N
           ▼
┌──────────────────────────────┐
│   curriculum_references      │
│  (Detailed paragraphs)       │
└──────────────────────────────┘

┌──────────────────────────────┐
│   educational_modules        │
│  (Module categories)         │
└──────────────────────────────┘
```

**Relationships:**
- `major_curriculum_references` → `curriculum_references` (1:N)
- `educational_modules` (standalone table, no relationships)

---

## 3. Table Definitions

### 3.1 major_curriculum_references

**Purpose:** Stores major sections of Polish kindergarten curriculum ("Podstawa Programowa"). Each major reference represents a top-level section (e.g., "4" for mathematics) that contains multiple detailed paragraphs.

**Table Name:** `major_curriculum_references`

| Column Name      | Type         | Constraints                    | Description                                      |
|------------------|--------------|--------------------------------|--------------------------------------------------|
| `id`             | INTEGER      | PRIMARY KEY, AUTO_INCREMENT    | Unique identifier                                |
| `reference_code` | VARCHAR(10)  | UNIQUE, NOT NULL, INDEX        | Major section code (e.g., "4", "3")              |
| `full_text`      | TEXT         | NOT NULL                       | Complete Polish text for major section           |
| `created_at`     | TIMESTAMP    | NOT NULL, DEFAULT CURRENT_TS   | Timestamp when record was created                |

**Indexes:**
- PRIMARY KEY on `id` (automatic)
- UNIQUE INDEX on `reference_code` (for fast lookups by code)

**Constraints:**
- `reference_code` must be unique (no duplicate major section codes)
- `reference_code` and `full_text` cannot be null
- `created_at` defaults to current timestamp

**Sample Data:**
```sql
INSERT INTO major_curriculum_references (reference_code, full_text) VALUES
('1', 'Dziecko zdolne jest zadbać o swoje zdrowie, sprawność fizyczną i bezpieczeństwo;'),
('2', 'Dziecko rozumie siebie, swoje emocje i potrzeby;'),
('3', 'Dziecko nawiązuje relacje z innymi;'),
('4', 'Dziecko poznaje i rozumie świat;');
```

**Expected Data Volume:**
- MVP: ~10-15 major sections
- Growth: Minimal (curriculum structure changes rarely)

**Query Patterns:**
- Load all major sections: `SELECT reference_code, full_text FROM major_curriculum_references ORDER BY reference_code`
- Single lookup: `SELECT full_text FROM major_curriculum_references WHERE reference_code = ?`

---

### 3.2 curriculum_references

**Purpose:** Stores detailed Polish kindergarten curriculum paragraph references ("Podstawa Programowa") and their complete text descriptions. Each reference belongs to a major curriculum section. Used for tooltip display when teachers hover over curriculum reference codes.

**Table Name:** `curriculum_references`

| Column Name              | Type         | Constraints                    | Description                                      |
|--------------------------|--------------|--------------------------------|--------------------------------------------------|
| `id`                     | INTEGER      | PRIMARY KEY, AUTO_INCREMENT    | Unique identifier                                |
| `reference_code`         | VARCHAR(20)  | UNIQUE, NOT NULL, INDEX        | Curriculum code (e.g., "4.15", "2.5")            |
| `full_text`              | TEXT         | NOT NULL                       | Complete Polish curriculum requirement text      |
| `major_reference_id`     | INTEGER      | NOT NULL, FOREIGN KEY, INDEX   | References `major_curriculum_references.id`      |
| `created_at`             | TIMESTAMP    | NOT NULL, DEFAULT CURRENT_TS   | Timestamp when record was created                |

**Indexes:**
- PRIMARY KEY on `id` (automatic)
- UNIQUE INDEX on `reference_code` (for fast lookups by code)
- FOREIGN KEY INDEX on `major_reference_id` (for joining with major sections)

**Constraints:**
- `reference_code` must be unique (no duplicate curriculum codes)
- `reference_code`, `full_text`, and `major_reference_id` cannot be null
- `created_at` defaults to current timestamp
- FOREIGN KEY `major_reference_id` references `major_curriculum_references.id` with RESTRICT on delete

**Relationships:**
- N:1 with `major_curriculum_references` (many detailed refs belong to one major section)

**Sample Data:**
```sql
-- Assuming major_reference_id=4 corresponds to reference_code='4' in major table
INSERT INTO curriculum_references (reference_code, full_text, major_reference_id) VALUES
('4.15', 'przelicza elementy zbiorów w czasie zabawy, prac porządkowych...', 4),
('4.18', 'rozpoznaje cyfry oznaczające liczby od 0 do 10...', 4);

-- Assuming major_reference_id=3 corresponds to reference_code='3' in major table
INSERT INTO curriculum_references (reference_code, full_text, major_reference_id) VALUES
('3.8', 'obdarza uwagą inne dzieci i osoby dorosłe;', 3);
```

**Expected Data Volume:**
- MVP: 50-100 detailed paragraph references
- Growth: Minimal (curriculum changes infrequently)

**Query Patterns:**
- Bulk load all references: `SELECT reference_code, full_text FROM curriculum_references`
- Single lookup: `SELECT full_text FROM curriculum_references WHERE reference_code = ?`
- Load with major section:
  ```sql
  SELECT cr.reference_code, cr.full_text, mcr.reference_code as major_code
  FROM curriculum_references cr
  JOIN major_curriculum_references mcr ON cr.major_reference_id = mcr.id
  ```

---

### 3.3 educational_modules

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

## 4. SQL Schema Definitions

### 4.1 SQLite Schema (MVP)

```sql
-- Table: major_curriculum_references
CREATE TABLE IF NOT EXISTS major_curriculum_references (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    reference_code VARCHAR(10) NOT NULL UNIQUE,
    full_text TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_major_curriculum_references_code ON major_curriculum_references(reference_code);

-- Table: curriculum_references
CREATE TABLE IF NOT EXISTS curriculum_references (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    reference_code VARCHAR(20) NOT NULL UNIQUE,
    full_text TEXT NOT NULL,
    major_reference_id INTEGER NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (major_reference_id) REFERENCES major_curriculum_references(id) ON DELETE RESTRICT
);

CREATE INDEX idx_curriculum_references_code ON curriculum_references(reference_code);
CREATE INDEX idx_curriculum_references_major_id ON curriculum_references(major_reference_id);

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

### 4.2 PostgreSQL Schema (Production)

```sql
-- Table: major_curriculum_references
CREATE TABLE IF NOT EXISTS major_curriculum_references (
    id SERIAL PRIMARY KEY,
    reference_code VARCHAR(10) NOT NULL UNIQUE,
    full_text TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_major_curriculum_references_code ON major_curriculum_references(reference_code);

-- Table: curriculum_references
CREATE TABLE IF NOT EXISTS curriculum_references (
    id SERIAL PRIMARY KEY,
    reference_code VARCHAR(20) NOT NULL UNIQUE,
    full_text TEXT NOT NULL,
    major_reference_id INTEGER NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (major_reference_id) REFERENCES major_curriculum_references(id) ON DELETE RESTRICT
);

CREATE INDEX idx_curriculum_references_code ON curriculum_references(reference_code);
CREATE INDEX idx_curriculum_references_major_id ON curriculum_references(major_reference_id);

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

---

## 5. Django Models (Recommended)

Django ORM abstracts database differences automatically:

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

**Django Advantages:**
- Automatic migrations via `python manage.py makemigrations`
- Database-agnostic (change `ENGINE` in settings.py to switch databases)
- Built-in admin interface for data management
- ORM query optimization

---

## 6. Performance Considerations

### 6.1 Index Strategy

**Current Indexes:**

| Table                         | Index Type | Columns              | Purpose                          |
|-------------------------------|------------|----------------------|----------------------------------|
| major_curriculum_references   | UNIQUE     | reference_code       | Fast lookup by major code        |
| curriculum_references         | UNIQUE     | reference_code       | Fast lookup by detailed code     |
| curriculum_references         | INDEX      | major_reference_id   | Fast joins with major sections   |
| educational_modules           | UNIQUE     | module_name          | Fast lookup by name              |
| educational_modules           | INDEX      | is_ai_suggested      | Filter predefined vs AI-suggested|

### 6.2 Query Optimization

**Bulk Loading (Curriculum References):**
```sql
-- Good: Single query loads all references
SELECT reference_code, full_text FROM curriculum_references;

-- Bad: N+1 queries for each reference
SELECT full_text FROM curriculum_references WHERE reference_code = '4.15';
SELECT full_text FROM curriculum_references WHERE reference_code = '4.18';
-- (repeated for each code)
```

**Join with Major Sections:**
```sql
-- Efficient: Single query with JOIN
SELECT
    cr.reference_code,
    cr.full_text,
    mcr.reference_code as major_code,
    mcr.full_text as major_text
FROM curriculum_references cr
JOIN major_curriculum_references mcr ON cr.major_reference_id = mcr.id
WHERE cr.reference_code IN ('4.15', '4.18');
```

**Django ORM Optimization:**
```python
# Good: Use select_related() for foreign keys
refs = CurriculumReference.objects.select_related('major_reference').all()

# Bad: Lazy loading causes N+1 queries
refs = CurriculumReference.objects.all()
for ref in refs:
    print(ref.major_reference.reference_code)  # Additional query per ref!
```

### 6.3 Expected Query Volume

**MVP Phase:**
- Page load: 1-2 queries (load curriculum refs, load modules)
- Frequency: ~20 sessions/month
- Database size: <1 MB

### 6.4 Foreign Key Delete Behavior

**RESTRICT on major_curriculum_references:**
- If attempting to delete a major section that has detailed references, the deletion will be blocked
- Ensures data integrity (cannot orphan detailed curriculum references)
- Admin must first delete or reassign all detailed references before deleting major section

---

## 7. Database Diagram (ASCII)

```
┌────────────────────────────────┐
│ major_curriculum_references    │
├────────────────────────────────┤
│ PK id                          │
│ UK reference_code (idx)        │
│    full_text                   │
│    created_at                  │
└────────────┬───────────────────┘
             │
             │ 1:N
             │ (major_reference_id FK)
             ▼
┌────────────────────────────────┐
│   curriculum_references        │
├────────────────────────────────┤
│ PK id                          │
│ UK reference_code (idx)        │
│    full_text                   │
│ FK major_reference_id (idx)    │
│    created_at                  │
└────────────────────────────────┘

┌────────────────────────────────┐
│   educational_modules          │
├────────────────────────────────┤
│ PK id                          │
│ UK module_name (idx)           │
│    is_ai_suggested (idx)       │
│    created_at                  │
└────────────────────────────────┘
```

**Legend:**
- `PK` = Primary Key
- `FK` = Foreign Key
- `UK` = Unique Key
- `(idx)` = Indexed column

---

## Document History

| Version | Date       | Author       | Changes                                      |
|---------|------------|--------------|----------------------------------------------|
| 1.0     | 2025-11-10 | DB Architect | Initial schema with 3 tables (MVP scope)     |

---

**Related Documentation:**
- **Database Initialization:** See `docs/db_init.md` for data seeding and setup procedures
- **API Documentation:** See `docs/django_api.md` for API endpoints using this schema
- **Product Requirements:** See `docs/PRD.md` for functional requirements
