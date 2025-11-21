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
# SQLite (from project root)
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
# From project root
sqlite3 db.sqlite3 < schema.sql
```

**PostgreSQL:**
```bash
psql teacher_assist < schema.sql
```

See `docs/db_schema.md` Section 4 for complete SQL schema definitions (SQLite and PostgreSQL versions).

---

## 6. Database Backup

### 6.1 SQLite Backup (MVP)

**Database File Location:** `db.sqlite3` (project root)

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

## Document History

| Version | Date       | Author | Changes                                   |
|---------|------------|--------|-------------------------------------------|
| 1.0     | 2025-11-10 | Dev    | Initial database initialization guide     |
| 2.0     | 2025-11-15 | Dev    | Added Django models for work plan persistence tables (WorkPlan, WorkPlanEntry, WorkPlanEntryCurriculumRef) |

---

**Related Documentation:**
- **Database Schema:** See `docs/db_schema.md` for complete table definitions
- **API Documentation:** See `docs/django_api.md` for API endpoints
- **Product Requirements:** See `docs/PRD.md` for functional requirements
