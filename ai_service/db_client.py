"""
Simple SQLite database client for AI service.

Provides read-only access to curriculum references, educational modules,
and example work plan entries for LLM context.

Uses Python's built-in sqlite3 module - no external dependencies required.
"""

import sqlite3
import os
from typing import List, Optional
from pathlib import Path

from ai_service.db_models import (
    EducationalModule,
    CurriculumReference,
    MajorCurriculumReference,
    LLMExample
)


class DatabaseClient:
    """
    Simple SQLite database client for read-only access to Django database.

    Provides four main query methods:
    1. get_educational_modules() - Get all module names
    2. get_curriculum_references() - Get all curriculum references with details
    3. get_major_curriculum_references() - Get all major curriculum sections
    4. get_llm_examples() - Get example work plan entries for LLM training
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

    def get_educational_modules(self) -> List[EducationalModule]:
        """
        Get all module names from educational_modules table.

        Returns:
            List of EducationalModule objects containing module_name field

        Example:
            >>> client = DatabaseClient()
            >>> modules = client.get_educational_modules()
            >>> [m.module_name for m in modules]
            ['EMOCJE', 'FORMY PLASTYCZNE', 'JĘZYK', 'MATEMATYKA', ...]
        """
        conn = self._get_connection()
        try:
            cursor = conn.execute("""
                SELECT module_name
                FROM educational_modules
                ORDER BY module_name
            """)

            modules = []
            for row in cursor.fetchall():
                modules.append(EducationalModule(module_name=row['module_name']))

            return modules
        finally:
            conn.close()

    def get_curriculum_references(self) -> List[CurriculumReference]:
        """
        Get all curriculum references with reference_code, full_text, and major_reference_id.

        Returns:
            List of CurriculumReference objects

        Example:
            >>> client = DatabaseClient()
            >>> refs = client.get_curriculum_references()
            >>> refs[0].reference_code
            '1.1'
            >>> refs[0].full_text
            'zgłasza potrzeby fizjologiczne...'
            >>> refs[0].major_reference_id
            1
        """
        conn = self._get_connection()
        try:
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
        finally:
            conn.close()

    def get_major_curriculum_references(self) -> List[MajorCurriculumReference]:
        """
        Get all major curriculum references with id, reference_code, and full_text.

        Returns:
            List of MajorCurriculumReference objects

        Example:
            >>> client = DatabaseClient()
            >>> major_refs = client.get_major_curriculum_references()
            >>> major_refs[0].id
            1
            >>> major_refs[0].reference_code
            '1'
            >>> major_refs[0].full_text
            'Fizyczny obszar rozwoju dziecka...'
        """
        conn = self._get_connection()
        try:
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
        finally:
            conn.close()

    def get_llm_examples(self) -> List[LLMExample]:
        """
        Get example work plan entries for LLM training context.

        Joins work_plans, work_plan_entries, and curriculum_references tables
        to return complete examples where is_example = true.

        Each example includes:
        - theme: Weekly theme from work_plan
        - activity: Activity description
        - module: Educational module
        - objectives: Educational objectives
        - curriculum_references: List of curriculum reference codes

        Uses a single query with GROUP_CONCAT to avoid N+1 query problem.

        Returns:
            List of LLMExample objects

        Example:
            >>> client = DatabaseClient()
            >>> examples = client.get_llm_examples()
            >>> examples[0].theme
            'Jesień - zbiory'
            >>> examples[0].activity
            'Zabawa w sklep z owocami'
            >>> examples[0].module
            'MATEMATYKA'
            >>> examples[0].objectives
            'Dziecko potrafi przeliczać w zakresie 5\\nRozpoznaje poznane wcześniej cyfry'
            >>> examples[0].curriculum_references
            ['4.15', '4.18']
        """
        conn = self._get_connection()
        try:
            # Single query with GROUP_CONCAT to get all data at once
            # This avoids N+1 query problem - executes only 1 query regardless of number of examples
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
                # Parse comma-separated curriculum reference codes
                ref_codes_str = row['ref_codes']
                if ref_codes_str:
                    # Split and sort curriculum references
                    curriculum_refs = sorted(ref_codes_str.split(','))
                else:
                    curriculum_refs = []

                examples.append(LLMExample(
                    theme=row['theme'] or '',
                    activity=row['activity'],
                    module=row['module'] or '',
                    objectives=row['objectives'] or '',
                    curriculum_references=curriculum_refs
                ))

            return examples
        finally:
            conn.close()


def get_db_client(db_path: Optional[str] = None) -> DatabaseClient:
    """
    Get a database client instance.

    Args:
        db_path: Optional path to database file

    Returns:
        DatabaseClient instance

    Example:
        >>> client = get_db_client()
        >>> modules = client.get_educational_modules()
    """
    return DatabaseClient(db_path)
