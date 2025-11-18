# Database Schema Documentation

**Project:** Teacher Assist - AI-Powered Lesson Planning Tool
**Version:** 2.1
**Database:** SQLite (development) - Designed to be engine-agnostic
**Last Updated:** 2025-11-18

---

## 1. Overview

This document defines the database schema for the Teacher Assist application. The design supports both reference data storage (Polish kindergarten curriculum information and educational modules) and lesson plan persistence (work plans and their entries).

### Design Principles

1. **Engine Agnostic**: Use standard SQL types compatible with PostgreSQL, MySQL, SQLite
2. **Normalization**: Follow 3NF to minimize data redundancy
3. **Performance**: Strategic indexes for common query patterns
4. **Data Integrity**: Constraints and foreign keys enforce referential integrity

### Schema Scope

**Reference Data (Implemented):**
- major_curriculum_references - Polish curriculum main sections
- curriculum_references - Detailed curriculum paragraphs
- educational_modules - Module categories

**Work Plan Persistence (Schema Defined, Not Yet Implemented):**
- work_plans - Weekly lesson plan themes
- work_plan_entries - Individual activity rows
- work_plan_entry_curriculum_refs - Many-to-many junction table

**Note:** The work plan persistence tables are fully designed and documented in this schema, but the save/load feature is not part of MVP. Session data currently remains in browser memory only.

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
┌──────────────────────────────┐       ┌──────────────────────────────┐
│   curriculum_references      │◄──────│ work_plan_entry_curriculum   │
│  (Detailed paragraphs)       │  N:M  │         _refs                │
└──────────────────────────────┘       │  (Junction table)            │
                                        └──────────┬───────────────────┘
                                                   │
                                                   │ N:1
                                                   ▼
┌──────────────────────────────┐       ┌──────────────────────────────┐
│   educational_modules        │──────►│   work_plan_entries          │
│  (Module categories)         │ 1:N   │  (Individual activities)     │
└──────────────────────────────┘       └──────────┬───────────────────┘
                                                   │
                                                   │ N:1
                                                   ▼
                                        ┌──────────────────────────────┐
                                        │      work_plans              │
                                        │  (Weekly lesson plans)       │
                                        └──────────────────────────────┘
```

**Relationships:**
- `major_curriculum_references` → `curriculum_references` (1:N)
- `work_plans` → `work_plan_entries` (1:N)
- `work_plan_entries` ↔ `curriculum_references` (N:M via junction table)
- `educational_modules` → `work_plan_entries` (1:N, optional)

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
- N:M with `work_plan_entries` via `work_plan_entry_curriculum_refs` junction table

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

**Constraints:**
- `module_name` must be unique (case-sensitive or case-insensitive depending on DB)
- `is_ai_suggested` defaults to FALSE
- `created_at` defaults to current timestamp

**Relationships:**
- 1:N with `work_plan_entries` (one module can be used by many entries, optional)

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
- Check if module exists: `SELECT id FROM educational_modules WHERE module_name = ?`

---

### 3.4 work_plans

**Purpose:** Stores weekly lesson plans with their themes. Each work plan represents a complete weekly planning session and contains multiple work plan entries (individual activities).

**Table Name:** `work_plans`

| Column Name      | Type         | Constraints                    | Description                                      |
|------------------|--------------|--------------------------------|--------------------------------------------------|
| `id`             | INTEGER      | PRIMARY KEY, AUTO_INCREMENT    | Unique identifier                                |
| `theme`          | VARCHAR(200) | NULL                           | Weekly theme (optional, e.g., "Jesień - zbiory")|
| `created_at`     | TIMESTAMP    | NOT NULL, DEFAULT CURRENT_TS   | Timestamp when work plan was created             |
| `updated_at`     | TIMESTAMP    | NOT NULL, DEFAULT CURRENT_TS   | Timestamp when work plan was last modified       |

**Indexes:**
- PRIMARY KEY on `id` (automatic)

**Constraints:**
- `theme` can be NULL (optional theme)
- `created_at` and `updated_at` default to current timestamp
- `updated_at` should be automatically updated on modification (via trigger or ORM)

**Sample Data:**
```sql
INSERT INTO work_plans (theme) VALUES
('Jesień - zbiory'),
('Zima i święta'),
('Wiosna i przyroda');
```

**Expected Data Volume:**
- Growth: ~20-50 plans per month per teacher
- Retention: Depends on implementation (archival strategy TBD)

**Query Patterns:**
- Load recent plans: `SELECT * FROM work_plans ORDER BY created_at DESC LIMIT 10`
- Search by theme: `SELECT * FROM work_plans WHERE theme LIKE '%Jesień%'`
- Single plan lookup: `SELECT * FROM work_plans WHERE id = ?`

---

### 3.5 work_plan_entries

**Purpose:** Stores individual activity rows within a work plan. Each entry corresponds to one row in the UI table and contains the activity description, educational module, objectives, and metadata. The `is_example` flag marks entries that should be used as examples in LLM prompts.

**Table Name:** `work_plan_entries`

| Column Name      | Type         | Constraints                    | Description                                      |
|------------------|--------------|--------------------------------|--------------------------------------------------|
| `id`             | INTEGER      | PRIMARY KEY, AUTO_INCREMENT    | Unique identifier                                |
| `work_plan_id`   | INTEGER      | NOT NULL, FOREIGN KEY, INDEX   | References `work_plans.id`                       |
| `module_id`      | INTEGER      | NULL, FOREIGN KEY, INDEX       | References `educational_modules.id`              |
| `objectives`     | TEXT         | NULL                           | Educational objectives (typically 2-3 items, separated by newlines) |
| `activity`       | VARCHAR(500) | NOT NULL                       | Activity description (required)                  |
| `is_example`     | BOOLEAN      | NOT NULL, DEFAULT FALSE        | TRUE if should be used as LLM training example   |
| `created_at`     | TIMESTAMP    | NOT NULL, DEFAULT CURRENT_TS   | Timestamp when entry was created                 |

**Indexes:**
- PRIMARY KEY on `id` (automatic)
- FOREIGN KEY INDEX on `work_plan_id` (for joining with work_plans)
- FOREIGN KEY INDEX on `module_id` (for joining with educational_modules)
- INDEX on `is_example` (for filtering example entries)

**Constraints:**
- `work_plan_id` references `work_plans.id` with CASCADE on delete (if work plan deleted, entries deleted)
- `module_id` references `educational_modules.id` with PROTECT on delete (prevents deletion of modules in use)
- `activity` cannot be NULL (required field)
- `module_id` and `objectives` can be NULL (may be filled by AI or manually later)
- `is_example` defaults to FALSE

**Relationships:**
- N:1 with `work_plans` (many entries belong to one work plan)
- N:1 with `educational_modules` (many entries can reference one module, optional)
- N:M with `curriculum_references` via junction table

**Sample Data:**
```sql
-- Assuming work_plan_id=1 exists and module_id=2 is 'MATEMATYKA', module_id=5 is 'FORMY PLASTYCZNE'
INSERT INTO work_plan_entries (work_plan_id, module_id, objectives, activity, is_example) VALUES
(1, 2, 'Dziecko potrafi przeliczać w zakresie 5\nRozpoznaje poznane wcześniej cyfry', 'Zabawa w sklep z owocami', TRUE),
(1, 5, 'Rozwija koordynację wzrokowo-ruchową\nPosługuje się farbami i pędzlem', 'Malowanie liści farbami', FALSE),
(1, 2, 'Sortuje obiekty według jednej cechy\nRozróżnia wielkości: duży, mały, średni', 'Sortowanie kasztanów według wielkości', FALSE);
```

**Expected Data Volume:**
- Per work plan: 5-20 entries (activities)
- Growth: Proportional to work_plans table

**Query Patterns:**
- Load all entries for a work plan: `SELECT * FROM work_plan_entries WHERE work_plan_id = ?`
- Filter examples: `SELECT * FROM work_plan_entries WHERE is_example = TRUE`
- Full plan with entries:
  ```sql
  SELECT wp.theme, wpe.*
  FROM work_plans wp
  JOIN work_plan_entries wpe ON wp.id = wpe.work_plan_id
  WHERE wp.id = ?
  ```

---

### 3.6 work_plan_entry_curriculum_refs

**Purpose:** Junction table implementing many-to-many relationship between work plan entries and curriculum references. A single activity can reference multiple curriculum paragraphs, and a curriculum paragraph can be used by multiple activities.

**Table Name:** `work_plan_entry_curriculum_refs`

| Column Name              | Type         | Constraints                    | Description                                      |
|--------------------------|--------------|--------------------------------|--------------------------------------------------|
| `id`                     | INTEGER      | PRIMARY KEY, AUTO_INCREMENT    | Unique identifier                                |
| `work_plan_entry_id`     | INTEGER      | NOT NULL, FOREIGN KEY, INDEX   | References `work_plan_entries.id`                |
| `curriculum_reference_id`| INTEGER      | NOT NULL, FOREIGN KEY, INDEX   | References `curriculum_references.id`            |
| `created_at`             | TIMESTAMP    | NOT NULL, DEFAULT CURRENT_TS   | Timestamp when association was created           |

**Indexes:**
- PRIMARY KEY on `id` (automatic)
- UNIQUE INDEX on `(work_plan_entry_id, curriculum_reference_id)` (prevent duplicate associations)
- INDEX on `work_plan_entry_id` (for joining from entries)
- INDEX on `curriculum_reference_id` (for reverse lookups)

**Constraints:**
- `work_plan_entry_id` references `work_plan_entries.id` with CASCADE on delete
- `curriculum_reference_id` references `curriculum_references.id` with RESTRICT on delete
- Composite UNIQUE constraint on `(work_plan_entry_id, curriculum_reference_id)`

**Sample Data:**
```sql
-- Assuming work_plan_entry_id=1 exists and curriculum_reference ids 10, 11 exist for codes "4.15", "4.18"
INSERT INTO work_plan_entry_curriculum_refs (work_plan_entry_id, curriculum_reference_id) VALUES
(1, 10),  -- Links entry 1 to curriculum ref "4.15"
(1, 11),  -- Links entry 1 to curriculum ref "4.18"
(2, 5),   -- Links entry 2 to a different curriculum ref
(2, 6);
```

**Expected Data Volume:**
- Per work plan entry: 1-10 curriculum references
- Growth: Proportional to work_plan_entries table

**Query Patterns:**
- Get curriculum refs for an entry:
  ```sql
  SELECT cr.reference_code, cr.full_text
  FROM curriculum_references cr
  JOIN work_plan_entry_curriculum_refs wpcr ON cr.id = wpcr.curriculum_reference_id
  WHERE wpcr.work_plan_entry_id = ?
  ```
- Reverse lookup (which entries use a curriculum ref):
  ```sql
  SELECT wpe.*
  FROM work_plan_entries wpe
  JOIN work_plan_entry_curriculum_refs wpcr ON wpe.id = wpcr.work_plan_entry_id
  WHERE wpcr.curriculum_reference_id = ?
  ```

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

-- Table: work_plans
CREATE TABLE IF NOT EXISTS work_plans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    theme VARCHAR(200),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Table: work_plan_entries
CREATE TABLE IF NOT EXISTS work_plan_entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    work_plan_id INTEGER NOT NULL,
    module_id INTEGER,
    objectives TEXT,
    activity VARCHAR(500) NOT NULL,
    is_example BOOLEAN NOT NULL DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (work_plan_id) REFERENCES work_plans(id) ON DELETE CASCADE,
    FOREIGN KEY (module_id) REFERENCES educational_modules(id) ON DELETE PROTECT
);

CREATE INDEX idx_work_plan_entries_work_plan_id ON work_plan_entries(work_plan_id);
CREATE INDEX idx_work_plan_entries_module_id ON work_plan_entries(module_id);
CREATE INDEX idx_work_plan_entries_is_example ON work_plan_entries(is_example);

-- Table: work_plan_entry_curriculum_refs (junction table)
CREATE TABLE IF NOT EXISTS work_plan_entry_curriculum_refs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    work_plan_entry_id INTEGER NOT NULL,
    curriculum_reference_id INTEGER NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (work_plan_entry_id) REFERENCES work_plan_entries(id) ON DELETE CASCADE,
    FOREIGN KEY (curriculum_reference_id) REFERENCES curriculum_references(id) ON DELETE RESTRICT,
    UNIQUE(work_plan_entry_id, curriculum_reference_id)
);

CREATE INDEX idx_wpe_curr_refs_entry_id ON work_plan_entry_curriculum_refs(work_plan_entry_id);
CREATE INDEX idx_wpe_curr_refs_curr_id ON work_plan_entry_curriculum_refs(curriculum_reference_id);
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

-- Table: work_plans
CREATE TABLE IF NOT EXISTS work_plans (
    id SERIAL PRIMARY KEY,
    theme VARCHAR(200),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Table: work_plan_entries
CREATE TABLE IF NOT EXISTS work_plan_entries (
    id SERIAL PRIMARY KEY,
    work_plan_id INTEGER NOT NULL,
    module_id INTEGER,
    objectives TEXT,
    activity VARCHAR(500) NOT NULL,
    is_example BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (work_plan_id) REFERENCES work_plans(id) ON DELETE CASCADE,
    FOREIGN KEY (module_id) REFERENCES educational_modules(id) ON DELETE RESTRICT
);

CREATE INDEX idx_work_plan_entries_work_plan_id ON work_plan_entries(work_plan_id);
CREATE INDEX idx_work_plan_entries_module_id ON work_plan_entries(module_id);
CREATE INDEX idx_work_plan_entries_is_example ON work_plan_entries(is_example);

-- Table: work_plan_entry_curriculum_refs (junction table)
CREATE TABLE IF NOT EXISTS work_plan_entry_curriculum_refs (
    id SERIAL PRIMARY KEY,
    work_plan_entry_id INTEGER NOT NULL,
    curriculum_reference_id INTEGER NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (work_plan_entry_id) REFERENCES work_plan_entries(id) ON DELETE CASCADE,
    FOREIGN KEY (curriculum_reference_id) REFERENCES curriculum_references(id) ON DELETE RESTRICT,
    UNIQUE(work_plan_entry_id, curriculum_reference_id)
);

CREATE INDEX idx_wpe_curr_refs_entry_id ON work_plan_entry_curriculum_refs(work_plan_entry_id);
CREATE INDEX idx_wpe_curr_refs_curr_id ON work_plan_entry_curriculum_refs(curriculum_reference_id);
```

**Key Differences:**
- SQLite: `INTEGER PRIMARY KEY AUTOINCREMENT`, `BOOLEAN` stored as 0/1
- PostgreSQL: `SERIAL PRIMARY KEY`, native `BOOLEAN` type
- MySQL: `INT PRIMARY KEY AUTO_INCREMENT`, `TINYINT(1)` for BOOLEAN

---

## 5. Performance Considerations

### 5.1 Index Strategy

**Current Indexes:**

| Table                         | Index Type | Columns              | Purpose                          |
|-------------------------------|------------|----------------------|----------------------------------|
| major_curriculum_references   | UNIQUE     | reference_code       | Fast lookup by major code        |
| curriculum_references         | UNIQUE     | reference_code       | Fast lookup by detailed code     |
| curriculum_references         | INDEX      | major_reference_id   | Fast joins with major sections   |
| educational_modules           | UNIQUE     | module_name          | Fast lookup by name              |
| work_plan_entries             | INDEX      | work_plan_id         | Fast joins with work plans       |
| work_plan_entries             | INDEX      | module_id            | Fast joins with educational modules |
| work_plan_entries             | INDEX      | is_example           | Filter example entries for LLM   |
| work_plan_entry_curriculum_refs | UNIQUE   | (entry_id, curr_id)  | Prevent duplicate associations   |
| work_plan_entry_curriculum_refs | INDEX    | work_plan_entry_id   | Fast lookup from entries         |
| work_plan_entry_curriculum_refs | INDEX    | curriculum_reference_id | Reverse lookups              |

### 5.2 Query Optimization

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

**Loading Work Plans with Entries and Curriculum Refs:**
```python
# Good: Use prefetch_related() for many-to-many
from django.db.models import Prefetch

work_plan = WorkPlan.objects.prefetch_related(
    Prefetch('entries', queryset=WorkPlanEntry.objects.prefetch_related('curriculum_references'))
).get(id=1)

# Access all data without additional queries
for entry in work_plan.entries.all():
    print(entry.activity)
    for curr_ref in entry.curriculum_references.all():
        print(f"  - {curr_ref.reference_code}")

# Bad: N+1 queries
work_plan = WorkPlan.objects.get(id=1)
for entry in work_plan.entries.all():  # Query 1
    for curr_ref in entry.curriculum_references.all():  # Query per entry!
        print(curr_ref.reference_code)
```

**Efficient Example Entry Retrieval:**
```sql
-- Load all example entries with their curriculum refs (for LLM prompts)
SELECT
    wpe.activity,
    em.module_name,
    wpe.objectives,
    GROUP_CONCAT(cr.reference_code, ', ') as curriculum_codes
FROM work_plan_entries wpe
LEFT JOIN educational_modules em ON wpe.module_id = em.id
LEFT JOIN work_plan_entry_curriculum_refs wpcr ON wpe.id = wpcr.work_plan_entry_id
LEFT JOIN curriculum_references cr ON wpcr.curriculum_reference_id = cr.id
WHERE wpe.is_example = TRUE
GROUP BY wpe.id;
```

### 5.3 Expected Query Volume

**Current Phase:**
- Page load: 2-3 queries (load curriculum refs, load modules, load recent work plans)
- Save work plan: 3-10 queries (insert work plan, insert entries, insert curriculum ref associations)
- Load work plan: 2-4 queries (select work plan, select entries with prefetch)
- Frequency: ~20-50 sessions/month per teacher
- Database size:
  - Reference data: <1 MB
  - Work plan data: ~5-10 MB per year per teacher (assuming 20-50 plans/month)

### 5.4 Foreign Key Delete Behavior

**RESTRICT on major_curriculum_references:**
- If attempting to delete a major section that has detailed references, the deletion will be blocked
- Ensures data integrity (cannot orphan detailed curriculum references)
- Admin must first delete or reassign all detailed references before deleting major section

**CASCADE on work_plans:**
- Deleting a work plan automatically deletes all associated work_plan_entries
- Deleting a work_plan_entry automatically deletes all associated work_plan_entry_curriculum_refs
- Ensures cleanup (no orphaned entries or curriculum reference associations)
- Use with caution: deleting a work plan removes all its data permanently

**RESTRICT on curriculum_references (from junction table):**
- Cannot delete a curriculum reference if it's used by any work plan entries
- Protects data integrity (prevents broken references in saved work plans)
- Admin must first remove curriculum reference associations before deleting the reference

**PROTECT on educational_modules (from work_plan_entries):**
- Cannot delete an educational module if it's referenced by any work plan entries
- Ensures referential integrity (prevents broken module references in saved work plans)
- Admin must first remove or reassign module references before deleting the module

---

## 6. Database Diagram (ASCII)

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
┌────────────────────────────────┐       ┌─────────────────────────────────┐
│   curriculum_references        │◄──────│ work_plan_entry_curriculum_refs │
├────────────────────────────────┤  N:M  ├─────────────────────────────────┤
│ PK id                          │       │ PK id                           │
│ UK reference_code (idx)        │       │ FK work_plan_entry_id (idx)     │
│    full_text                   │       │ FK curriculum_reference_id (idx)│
│ FK major_reference_id (idx)    │       │ UK (entry_id, curr_id)          │
│    created_at                  │       │    created_at                   │
└────────────────────────────────┘       └────────────┬────────────────────┘
                                                      │
┌────────────────────────────────┐                   │ N:1
│   educational_modules          │                   │ (work_plan_entry_id FK)
├────────────────────────────────┤                   ▼
│ PK id                          │       ┌────────────────────────────────┐
│ UK module_name (idx)           │       │   work_plan_entries            │
│    is_ai_suggested             │       ├────────────────────────────────┤
│    created_at                  │       │ PK id                          │
└────────────┬───────────────────┘       │ FK work_plan_id (idx)          │
             │                            │ FK module_id (idx)             │
             │ 1:N (optional)             │    objectives                  │
             │ (module_id FK, PROTECT)    │    activity                    │
             └────────────────────────────┤    is_example (idx)            │
                                          │    created_at                  │
                                          └────────────┬───────────────────┘
                                                       │
                                                       │ N:1
                                                       │ (work_plan_id FK, CASCADE)
                                                       ▼
                                          ┌────────────────────────────────┐
                                          │      work_plans                │
                                          ├────────────────────────────────┤
                                          │ PK id                          │
                                          │    theme                       │
                                          │    created_at (idx)            │
                                          │    updated_at                  │
                                          └────────────────────────────────┘
```

**Legend:**
- `PK` = Primary Key
- `FK` = Foreign Key
- `UK` = Unique Key
- `(idx)` = Indexed column
- `CASCADE` = Foreign key with ON DELETE CASCADE
- `PROTECT` = Foreign key with ON DELETE PROTECT (prevents deletion)
- `N:M` = Many-to-many relationship
- `N:1` = Many-to-one relationship

---

## Document History

| Version | Date       | Author       | Changes                                      |
|---------|------------|--------------|----------------------------------------------|
| 1.0     | 2025-11-10 | DB Architect | Initial schema with 3 tables (MVP scope)     |
| 2.0     | 2025-11-15 | DB Architect | Added work plan persistence tables (work_plans, work_plan_entries, work_plan_entry_curriculum_refs) with many-to-many relationships |
| 2.1     | 2025-11-18 | DB Architect | Changed work_plan_entries.module from VARCHAR(200) to ForeignKey(educational_modules) for data integrity; Added module_id index; Updated ON DELETE to PROTECT |

---

**Related Documentation:**
- **Database Initialization:** See `docs/db_init.md` for data seeding and setup procedures
- **API Documentation:** See `docs/django_api.md` for API endpoints using this schema
- **Product Requirements:** See `docs/PRD.md` for functional requirements
