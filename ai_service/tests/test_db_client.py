"""
Tests for AI service database client.

These tests verify that the database client can correctly query
the Django SQLite database for curriculum references and examples.
"""

import pytest
import os
from pathlib import Path
from ai_service.db_client import DatabaseClient, get_db_client
from ai_service.db_models import (
    CurriculumReference,
    MajorCurriculumReference,
    EducationalModule,
    WorkPlanEntryWithRefs
)


@pytest.fixture
def db_client():
    """
    Fixture to create a database client instance.
    Uses the actual Django database created by migrations.
    """
    # Path to Django database
    project_root = Path(__file__).parent.parent.parent
    db_path = project_root / "webserver" / "db.sqlite3"

    if not db_path.exists():
        pytest.skip("Django database not found. Run migrations first.")

    return DatabaseClient(str(db_path))


class TestDatabaseClient:
    """Tests for DatabaseClient class."""

    def test_get_connection(self, db_client):
        """Test that connection can be established."""
        conn = db_client._get_connection()
        assert conn is not None
        conn.close()

    def test_invalid_db_path_raises_error(self):
        """Test that invalid database path raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            DatabaseClient("/invalid/path/to/db.sqlite3")


class TestCurriculumReferences:
    """Tests for curriculum reference queries."""

    def test_get_all_curriculum_references(self, db_client):
        """Test retrieving all curriculum references."""
        references = db_client.get_all_curriculum_references()

        assert len(references) >= 50, "Should have at least 50 references"
        assert all(isinstance(ref, CurriculumReference) for ref in references)

        # Check structure of first reference
        first_ref = references[0]
        assert hasattr(first_ref, 'id')
        assert hasattr(first_ref, 'reference_code')
        assert hasattr(first_ref, 'full_text')
        assert hasattr(first_ref, 'major_reference_id')
        assert hasattr(first_ref, 'created_at')

    def test_get_curriculum_reference_by_code_exists(self, db_client):
        """Test retrieving a specific curriculum reference by code."""
        ref = db_client.get_curriculum_reference_by_code("4.15")

        assert ref is not None
        assert isinstance(ref, CurriculumReference)
        assert ref.reference_code == "4.15"
        assert "przelicza" in ref.full_text.lower()

    def test_get_curriculum_reference_by_code_not_exists(self, db_client):
        """Test that non-existent code returns None."""
        ref = db_client.get_curriculum_reference_by_code("999.999")
        assert ref is None

    def test_search_curriculum_by_keyword(self, db_client):
        """Test searching curriculum references by keyword."""
        results = db_client.search_curriculum_by_keyword("przelicza")

        assert len(results) > 0
        assert all(isinstance(ref, CurriculumReference) for ref in results)

        # All results should contain the keyword
        for ref in results:
            assert "przelicza" in ref.full_text.lower()

    def test_search_curriculum_no_results(self, db_client):
        """Test searching with keyword that yields no results."""
        results = db_client.search_curriculum_by_keyword("nonexistentkeyword12345")
        assert len(results) == 0


class TestMajorCurriculumReferences:
    """Tests for major curriculum reference queries."""

    def test_get_major_curriculum_references(self, db_client):
        """Test retrieving all major curriculum references."""
        references = db_client.get_major_curriculum_references()

        assert len(references) >= 4, "Should have at least 4 major references"
        assert all(isinstance(ref, MajorCurriculumReference) for ref in references)

        # Check structure
        first_ref = references[0]
        assert hasattr(first_ref, 'id')
        assert hasattr(first_ref, 'reference_code')
        assert hasattr(first_ref, 'full_text')
        assert hasattr(first_ref, 'created_at')

        # Check that codes are properly ordered
        codes = [ref.reference_code for ref in references]
        assert codes == sorted(codes), "Major references should be ordered by code"


class TestEducationalModules:
    """Tests for educational module queries."""

    def test_get_all_educational_modules(self, db_client):
        """Test retrieving all educational modules."""
        modules = db_client.get_all_educational_modules()

        assert len(modules) >= 12, "Should have at least 12 modules"
        assert all(isinstance(mod, EducationalModule) for mod in modules)

        # Check structure
        first_module = modules[0]
        assert hasattr(first_module, 'id')
        assert hasattr(first_module, 'module_name')
        assert hasattr(first_module, 'is_ai_suggested')
        assert hasattr(first_module, 'created_at')

        # Check that specific modules exist
        module_names = [mod.module_name for mod in modules]
        assert "MATEMATYKA" in module_names
        assert "JĘZYK" in module_names

        # Check ordering
        assert module_names == sorted(module_names), "Modules should be ordered by name"


class TestWorkPlanEntries:
    """Tests for work plan entry queries."""

    def test_get_example_work_plan_entries(self, db_client):
        """Test retrieving example work plan entries."""
        entries = db_client.get_example_work_plan_entries()

        assert len(entries) >= 5, "Should have at least 5 example entries"
        assert all(isinstance(entry, WorkPlanEntryWithRefs) for entry in entries)

        # Check structure of first entry
        first_entry = entries[0]
        assert hasattr(first_entry, 'id')
        assert hasattr(first_entry, 'work_plan_id')
        assert hasattr(first_entry, 'module')
        assert hasattr(first_entry, 'objectives')
        assert hasattr(first_entry, 'activity')
        assert hasattr(first_entry, 'is_example')
        assert hasattr(first_entry, 'curriculum_refs')
        assert hasattr(first_entry, 'theme')

        # All should be marked as examples
        assert all(entry.is_example for entry in entries)

        # Check that entries have curriculum references
        for entry in entries:
            assert len(entry.curriculum_refs) > 0, f"Entry {entry.id} should have curriculum refs"

    def test_example_entries_have_valid_data(self, db_client):
        """Test that example entries have complete and valid data."""
        entries = db_client.get_example_work_plan_entries()

        for entry in entries:
            # Activity should not be empty
            assert entry.activity and len(entry.activity) > 0

            # Module should be set
            assert entry.module and len(entry.module) > 0

            # Objectives should be set
            assert entry.objectives and len(entry.objectives) > 0

            # Should have at least one curriculum reference
            assert len(entry.curriculum_refs) > 0

            # Theme should be present (from work plan)
            assert entry.theme is not None


class TestGetDBClientFunction:
    """Tests for convenience function."""

    def test_get_db_client_default_path(self):
        """Test getting a database client with default path."""
        project_root = Path(__file__).parent.parent.parent
        db_path = project_root / "webserver" / "db.sqlite3"

        if not db_path.exists():
            pytest.skip("Django database not found. Run migrations first.")

        client = get_db_client()
        assert isinstance(client, DatabaseClient)

    def test_get_db_client_custom_path(self):
        """Test getting a database client with custom path."""
        project_root = Path(__file__).parent.parent.parent
        db_path = project_root / "webserver" / "db.sqlite3"

        if not db_path.exists():
            pytest.skip("Django database not found. Run migrations first.")

        client = get_db_client(str(db_path))
        assert isinstance(client, DatabaseClient)
        assert client.db_path == str(db_path)


class TestDataIntegrity:
    """Tests for data integrity and relationships."""

    def test_curriculum_refs_have_valid_major_refs(self, db_client):
        """Test that all curriculum references have valid major reference IDs."""
        curr_refs = db_client.get_all_curriculum_references()
        major_refs = db_client.get_major_curriculum_references()
        major_ref_ids = {ref.id for ref in major_refs}

        for curr_ref in curr_refs:
            assert curr_ref.major_reference_id in major_ref_ids, \
                f"Curriculum ref {curr_ref.reference_code} has invalid major_reference_id"

    def test_example_entries_refs_exist_in_curriculum(self, db_client):
        """Test that curriculum refs in example entries exist in curriculum_references table."""
        example_entries = db_client.get_example_work_plan_entries()
        all_curr_refs = db_client.get_all_curriculum_references()
        valid_codes = {ref.reference_code for ref in all_curr_refs}

        for entry in example_entries:
            for ref_code in entry.curriculum_refs:
                assert ref_code in valid_codes, \
                    f"Entry {entry.id} references non-existent curriculum code: {ref_code}"
