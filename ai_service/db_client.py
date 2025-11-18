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

    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize database client.

        Args:
            db_path: Path to SQLite file (defaults to project_root/db.sqlite3)
        """
        if db_path is None:
            project_root = Path(__file__).parent.parent
            db_path = project_root / "db.sqlite3"

        self.db_path = str(db_path)

        if not os.path.exists(self.db_path):
            raise FileNotFoundError(f"Database file not found: {self.db_path}")

    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection with row factory."""
        conn = sqlite3.connect(self.db_path)
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
        """
        Get all curriculum references with code, text, and major_reference_id.

        Note: String sorting works for current data (X.Y format, Y ≤ 9).
        """
        with self._db_connection() as conn:
            cursor = conn.execute("""
                SELECT reference_code, full_text, major_reference_id
                FROM curriculum_references
                ORDER BY reference_code
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
                ORDER BY reference_code
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

        Returns theme, activity, module, objectives, and curriculum_references.
        Uses GROUP_CONCAT to avoid N+1 queries (single query for all data).
        """
        with self._db_connection() as conn:
            cursor = conn.execute("""
                SELECT
                    wpe.id,
                    wp.theme,
                    wpe.activity,
                    wpe.module,
                    wpe.objectives,
                    GROUP_CONCAT(cr.reference_code, ',') as ref_codes
                FROM work_plan_entries wpe
                JOIN work_plans wp ON wpe.work_plan_id = wp.id
                LEFT JOIN work_plan_entry_curriculum_refs wpcr ON wpe.id = wpcr.work_plan_entry_id
                LEFT JOIN curriculum_references cr ON wpcr.curriculum_reference_id = cr.id
                WHERE wpe.is_example = 1
                GROUP BY wpe.id, wp.theme, wpe.activity, wpe.module, wpe.objectives, wpe.created_at
                ORDER BY wpe.created_at
            """)

            examples = []
            for row in cursor.fetchall():
                ref_codes_str = row['ref_codes']
                curriculum_refs = sorted(ref_codes_str.split(',')) if ref_codes_str else []

                examples.append(LLMExample(
                    theme=row['theme'] or '',
                    activity=row['activity'],
                    module=row['module'] or '',
                    objectives=row['objectives'] or '',
                    curriculum_references=curriculum_refs
                ))

            return examples


def get_db_client(db_path: Optional[str] = None) -> DatabaseClient:
    """Get database client instance (defaults to project_root/db.sqlite3)."""
    return DatabaseClient(db_path)
