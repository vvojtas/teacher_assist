"""
Simple SQLite database client for AI service.

This module provides read-only access to the Django SQLite database
for curriculum references and example work plan entries.

Recommendation: Use Python's built-in sqlite3 module for simplicity.
No additional dependencies required.
"""

import sqlite3
import os
from typing import List, Optional, Dict, Any
from datetime import datetime
from pathlib import Path

from ai_service.db_models import (
    CurriculumReference,
    MajorCurriculumReference,
    EducationalModule,
    WorkPlanEntryWithRefs
)


class DatabaseClient:
    """
    Simple SQLite database client for read-only access.

    This client provides methods to query curriculum references,
    educational modules, and example work plan entries.
    """

    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize database client.

        Args:
            db_path: Path to SQLite database file.
                    If None, defaults to db.sqlite3 in project root
        """
        if db_path is None:
            # Default to Django database in project root
            project_root = Path(__file__).parent.parent
            db_path = project_root / "db.sqlite3"

        self.db_path = str(db_path)

        if not os.path.exists(self.db_path):
            raise FileNotFoundError(f"Database file not found: {self.db_path}")

    def _get_connection(self) -> sqlite3.Connection:
        """
        Get a database connection with row factory configured.

        Returns:
            sqlite3.Connection: Database connection
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable dict-like access to rows
        return conn

    def _row_to_dict(self, row: sqlite3.Row) -> Dict[str, Any]:
        """
        Convert SQLite row to dictionary.

        Args:
            row: SQLite row object

        Returns:
            dict: Row data as dictionary
        """
        return dict(row) if row else {}

    def get_all_curriculum_references(self) -> List[CurriculumReference]:
        """
        Get all curriculum references from database.

        Returns:
            List of CurriculumReference objects
        """
        conn = self._get_connection()
        try:
            cursor = conn.execute("""
                SELECT id, reference_code, full_text, major_reference_id, created_at
                FROM curriculum_references
                ORDER BY reference_code
            """)

            references = []
            for row in cursor.fetchall():
                data = self._row_to_dict(row)
                references.append(CurriculumReference(**data))

            return references
        finally:
            conn.close()

    def get_curriculum_reference_by_code(self, code: str) -> Optional[CurriculumReference]:
        """
        Get a specific curriculum reference by its code.

        Args:
            code: Reference code (e.g., "4.15")

        Returns:
            CurriculumReference object or None if not found
        """
        conn = self._get_connection()
        try:
            cursor = conn.execute("""
                SELECT id, reference_code, full_text, major_reference_id, created_at
                FROM curriculum_references
                WHERE reference_code = ?
            """, (code,))

            row = cursor.fetchone()
            if row:
                return CurriculumReference(**self._row_to_dict(row))
            return None
        finally:
            conn.close()

    def get_all_educational_modules(self) -> List[EducationalModule]:
        """
        Get all educational modules from database.

        Returns:
            List of EducationalModule objects
        """
        conn = self._get_connection()
        try:
            cursor = conn.execute("""
                SELECT id, module_name, is_ai_suggested, created_at
                FROM educational_modules
                ORDER BY module_name
            """)

            modules = []
            for row in cursor.fetchall():
                data = self._row_to_dict(row)
                # Convert SQLite boolean (0/1) to Python bool
                data['is_ai_suggested'] = bool(data['is_ai_suggested'])
                modules.append(EducationalModule(**data))

            return modules
        finally:
            conn.close()

    def get_example_work_plan_entries(self) -> List[WorkPlanEntryWithRefs]:
        """
        Get all work plan entries marked as examples for LLM training.
        Includes curriculum references and work plan theme.

        Returns:
            List of WorkPlanEntryWithRefs objects with curriculum refs
        """
        conn = self._get_connection()
        try:
            # First, get all example entries
            cursor = conn.execute("""
                SELECT
                    wpe.id,
                    wpe.work_plan_id,
                    wpe.module,
                    wpe.objectives,
                    wpe.activity,
                    wpe.is_example,
                    wpe.created_at,
                    wp.theme
                FROM work_plan_entries wpe
                JOIN work_plans wp ON wpe.work_plan_id = wp.id
                WHERE wpe.is_example = 1
                ORDER BY wpe.created_at
            """)

            entries = []
            for row in cursor.fetchall():
                data = self._row_to_dict(row)
                data['is_example'] = bool(data['is_example'])

                # Get curriculum references for this entry
                entry_id = data['id']
                ref_cursor = conn.execute("""
                    SELECT cr.reference_code
                    FROM curriculum_references cr
                    JOIN work_plan_entry_curriculum_refs wpcr
                        ON cr.id = wpcr.curriculum_reference_id
                    WHERE wpcr.work_plan_entry_id = ?
                    ORDER BY cr.reference_code
                """, (entry_id,))

                curriculum_refs = [row['reference_code'] for row in ref_cursor.fetchall()]
                data['curriculum_refs'] = curriculum_refs

                entries.append(WorkPlanEntryWithRefs(**data))

            return entries
        finally:
            conn.close()

    def get_major_curriculum_references(self) -> List[MajorCurriculumReference]:
        """
        Get all major curriculum references from database.

        Returns:
            List of MajorCurriculumReference objects
        """
        conn = self._get_connection()
        try:
            cursor = conn.execute("""
                SELECT id, reference_code, full_text, created_at
                FROM major_curriculum_references
                ORDER BY reference_code
            """)

            references = []
            for row in cursor.fetchall():
                data = self._row_to_dict(row)
                references.append(MajorCurriculumReference(**data))

            return references
        finally:
            conn.close()

    def search_curriculum_by_keyword(self, keyword: str) -> List[CurriculumReference]:
        """
        Search curriculum references by keyword in full_text.

        Args:
            keyword: Search keyword (case-insensitive)

        Returns:
            List of matching CurriculumReference objects
        """
        conn = self._get_connection()
        try:
            cursor = conn.execute("""
                SELECT id, reference_code, full_text, major_reference_id, created_at
                FROM curriculum_references
                WHERE full_text LIKE ?
                ORDER BY reference_code
            """, (f'%{keyword}%',))

            references = []
            for row in cursor.fetchall():
                data = self._row_to_dict(row)
                references.append(CurriculumReference(**data))

            return references
        finally:
            conn.close()


# Convenience function to get a database client instance
def get_db_client(db_path: Optional[str] = None) -> DatabaseClient:
    """
    Get a database client instance.

    Args:
        db_path: Optional path to database file

    Returns:
        DatabaseClient instance
    """
    return DatabaseClient(db_path)
