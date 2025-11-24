"""
SQLite database client for AI service.

Read-only access to curriculum data and LLM training examples.
Uses Python's built-in sqlite3 module.
"""

import sqlite3
import os
from typing import List, Optional
from pathlib import Path
from contextlib import contextmanager

from ai_service.config import settings
from ai_service.utils.paths import get_database_path
from ai_service.db_models import (
    EducationalModule,
    CurriculumReference,
    MajorCurriculumReference,
    LLMExample
)


class DatabaseClient:
    """
    Read-only SQLite client for Django database.

    Methods: get_educational_modules(), get_curriculum_references(),
             get_major_curriculum_references(), get_llm_examples()
    """

    def __init__(self, db_path: Optional[str] = None, timeout: Optional[float] = None):
        """
        Initialize database client.

        Args:
            db_path: Path to SQLite file (defaults to project_root/db.sqlite3).
                    Relative paths are resolved from project root.
            timeout: Connection timeout in seconds (defaults to settings.database_timeout_seconds)
        """
        # Use centralized path resolution utility
        resolved_path = get_database_path(db_path)
        self.db_path = str(resolved_path)
        self.timeout = timeout if timeout is not None else settings.ai_service_database_timeout_seconds

        if not os.path.exists(self.db_path):
            raise FileNotFoundError(f"Database file not found: {self.db_path}")

    def _get_connection(self) -> sqlite3.Connection:
        """
        Get database connection with row factory and timeout.

        The timeout parameter controls how long to wait (in seconds) if the
        database is locked before raising an exception.
        """
        conn = sqlite3.connect(self.db_path, timeout=self.timeout)
        conn.row_factory = sqlite3.Row
        return conn

    @contextmanager
    def _db_connection(self):
        """Context manager for auto-closing database connections."""
        conn = self._get_connection()
        try:
            yield conn
        finally:
            conn.close()

    def get_educational_modules(self) -> List[EducationalModule]:
        """Get all module names, ordered alphabetically."""
        with self._db_connection() as conn:
            cursor = conn.execute("""
                SELECT module_name
                FROM educational_modules
                ORDER BY module_name
            """)

            modules = []
            for row in cursor.fetchall():
                modules.append(EducationalModule(module_name=row['module_name']))

            return modules

    def get_curriculum_references(self) -> List[CurriculumReference]:
        """Get all curriculum references with code, text, and major_reference_id."""
        with self._db_connection() as conn:
            cursor = conn.execute("""
                SELECT reference_code, full_text, major_reference_id
                FROM curriculum_references
                ORDER BY
                    CAST(SUBSTR(reference_code, 1, INSTR(reference_code, '.') - 1) AS INTEGER),
                    CAST(SUBSTR(reference_code, INSTR(reference_code, '.') + 1) AS INTEGER)
            """)

            references = []
            for row in cursor.fetchall():
                references.append(CurriculumReference(
                    reference_code=row['reference_code'],
                    full_text=row['full_text'],
                    major_reference_id=row['major_reference_id']
                ))

            return references

    def get_major_curriculum_references(self) -> List[MajorCurriculumReference]:
        """Get all major curriculum sections with id, code, and text."""
        with self._db_connection() as conn:
            cursor = conn.execute("""
                SELECT id, reference_code, full_text
                FROM major_curriculum_references
                ORDER BY CAST(reference_code AS INTEGER)
            """)

            references = []
            for row in cursor.fetchall():
                references.append(MajorCurriculumReference(
                    id=row['id'],
                    reference_code=row['reference_code'],
                    full_text=row['full_text']
                ))

            return references

    def get_llm_examples(self) -> List[LLMExample]:
        """
        Get example work plan entries for LLM training (where is_example=true).

        Returns theme, activity, modules, objectives, and curriculum_references.
        Uses subqueries to avoid Cartesian product (better performance than JOIN + GROUP_CONCAT).
        """
        with self._db_connection() as conn:
            cursor = conn.execute("""
                SELECT
                    wpe.id,
                    wp.theme,
                    wpe.activity,
                    wpe.objectives,
                    (SELECT GROUP_CONCAT(em.module_name, ',')
                     FROM work_plan_entry_modules wpem
                     JOIN educational_modules em ON wpem.module_id = em.id
                     WHERE wpem.work_plan_entry_id = wpe.id) as module_names,
                    (SELECT GROUP_CONCAT(cr.reference_code, ',')
                     FROM work_plan_entry_curriculum_refs wpcr
                     JOIN curriculum_references cr ON wpcr.curriculum_reference_id = cr.id
                     WHERE wpcr.work_plan_entry_id = wpe.id) as ref_codes
                FROM work_plan_entries wpe
                JOIN work_plans wp ON wpe.work_plan_id = wp.id
                WHERE wpe.is_example = 1
                ORDER BY wpe.created_at
            """)

            examples = []
            for row in cursor.fetchall():
                module_names_str = row['module_names']
                # Parse comma-separated module names into sorted list
                modules = sorted(module_names_str.split(',')) if module_names_str else []

                ref_codes_str = row['ref_codes']
                curriculum_refs = sorted(ref_codes_str.split(',')) if ref_codes_str else []

                examples.append(LLMExample(
                    theme=row['theme'] or '',
                    activity=row['activity'],
                    modules=modules,
                    objectives=row['objectives'] or '',
                    curriculum_references=curriculum_refs
                ))

            return examples


def get_db_client(db_path: Optional[str] = None) -> DatabaseClient:
    """Get database client instance (defaults to project_root/db.sqlite3)."""
    return DatabaseClient(db_path)
