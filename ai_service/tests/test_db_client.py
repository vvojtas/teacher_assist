"""
Tests for AI service database client.

Tests verify the 4 main query methods:
1. get_educational_modules()
2. get_curriculum_references()
3. get_major_curriculum_references()
4. get_llm_examples()
"""

import pytest
from pathlib import Path
from ai_service.db_client import DatabaseClient, get_db_client
from ai_service.db_models import (
    EducationalModule,
    CurriculumReference,
    MajorCurriculumReference,
    LLMExample
)


@pytest.fixture
def db_client():
    """
    Fixture to create a database client instance.
    Uses the actual Django database created by migrations.
    """
    # Path to Django database in project root
    project_root = Path(__file__).parent.parent.parent
    db_path = project_root / "db.sqlite3"

    if not db_path.exists():
        pytest.skip("Django database not found. Run migrations first.")

    return DatabaseClient(str(db_path))


class TestDatabaseClient:
    """Tests for DatabaseClient initialization."""

    def test_client_initialization_with_valid_path(self, db_client):
        """Test that client initializes with valid database path."""
        assert db_client is not None
        assert db_client.db_path is not None

    def test_client_initialization_with_invalid_path(self):
        """Test that invalid database path raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            DatabaseClient("/invalid/path/to/db.sqlite3")

    def test_get_connection(self, db_client):
        """Test that connection can be established."""
        conn = db_client._get_connection()
        assert conn is not None
        conn.close()


class TestGetEducationalModules:
    """Tests for get_educational_modules() method."""

    def test_returns_list_of_modules(self, db_client):
        """Test that method returns a list of EducationalModule objects."""
        modules = db_client.get_educational_modules()

        assert isinstance(modules, list)
        assert len(modules) >= 12, "Should have at least 12 modules"
        assert all(isinstance(m, EducationalModule) for m in modules)

    def test_module_structure(self, db_client):
        """Test that each module has the correct structure."""
        modules = db_client.get_educational_modules()

        first_module = modules[0]
        assert hasattr(first_module, 'module_name')
        assert isinstance(first_module.module_name, str)
        assert len(first_module.module_name) > 0

    def test_modules_ordered_by_name(self, db_client):
        """Test that modules are ordered alphabetically by name."""
        modules = db_client.get_educational_modules()
        module_names = [m.module_name for m in modules]

        assert module_names == sorted(module_names), "Modules should be ordered by name"

    def test_expected_modules_present(self, db_client):
        """Test that expected modules from PRD are present."""
        modules = db_client.get_educational_modules()
        module_names = [m.module_name for m in modules]

        expected = ['MATEMATYKA', 'JĘZYK', 'MOTORYKA DUŻA', 'FORMY PLASTYCZNE']
        for expected_module in expected:
            assert expected_module in module_names, f"{expected_module} should be in modules"


class TestGetCurriculumReferences:
    """Tests for get_curriculum_references() method."""

    def test_returns_list_of_references(self, db_client):
        """Test that method returns a list of CurriculumReference objects."""
        refs = db_client.get_curriculum_references()

        assert isinstance(refs, list)
        assert len(refs) >= 52, "Should have at least 52 curriculum references"
        assert all(isinstance(r, CurriculumReference) for r in refs)

    def test_reference_structure(self, db_client):
        """Test that each reference has the correct structure."""
        refs = db_client.get_curriculum_references()

        first_ref = refs[0]
        assert hasattr(first_ref, 'reference_code')
        assert hasattr(first_ref, 'full_text')
        assert hasattr(first_ref, 'major_reference_id')

        assert isinstance(first_ref.reference_code, str)
        assert isinstance(first_ref.full_text, str)
        assert isinstance(first_ref.major_reference_id, int)

    def test_references_ordered_by_code(self, db_client):
        """Test that references are ordered numerically (not lexicographically)."""
        refs = db_client.get_curriculum_references()
        ref_codes = [r.reference_code for r in refs]

        # Parse codes into (major, minor) tuples for numeric comparison
        def parse_code(code):
            major, minor = code.split('.')
            return (int(major), int(minor))

        parsed_codes = [parse_code(code) for code in ref_codes]

        # Verify numeric ordering
        for i in range(len(parsed_codes) - 1):
            assert parsed_codes[i] <= parsed_codes[i + 1], \
                f"Codes not in numeric order: {ref_codes[i]} should come before {ref_codes[i + 1]}"

        # Verify that 2.10 and 2.11 come after 2.9 (not between 2.1 and 2.2)
        if '2.9' in ref_codes and '2.10' in ref_codes:
            idx_2_9 = ref_codes.index('2.9')
            idx_2_10 = ref_codes.index('2.10')
            assert idx_2_10 > idx_2_9, "2.10 should come after 2.9 (numeric sort, not lexicographic)"

    def test_expected_references_present(self, db_client):
        """Test that expected curriculum references are present."""
        refs = db_client.get_curriculum_references()
        ref_codes = [r.reference_code for r in refs]

        expected = ['1.1', '4.15', '4.18', '3.8']
        for expected_code in expected:
            assert expected_code in ref_codes, f"{expected_code} should be in references"

    def test_reference_has_valid_major_id(self, db_client):
        """Test that all references have valid major_reference_id."""
        refs = db_client.get_curriculum_references()

        for ref in refs:
            assert ref.major_reference_id > 0, "major_reference_id should be positive"
            assert ref.major_reference_id <= 4, "major_reference_id should be 1-4"


class TestGetMajorCurriculumReferences:
    """Tests for get_major_curriculum_references() method."""

    def test_returns_list_of_major_references(self, db_client):
        """Test that method returns a list of MajorCurriculumReference objects."""
        major_refs = db_client.get_major_curriculum_references()

        assert isinstance(major_refs, list)
        assert len(major_refs) >= 4, "Should have at least 4 major references"
        assert all(isinstance(r, MajorCurriculumReference) for r in major_refs)

    def test_major_reference_structure(self, db_client):
        """Test that each major reference has the correct structure."""
        major_refs = db_client.get_major_curriculum_references()

        first_ref = major_refs[0]
        assert hasattr(first_ref, 'id')
        assert hasattr(first_ref, 'reference_code')
        assert hasattr(first_ref, 'full_text')

        assert isinstance(first_ref.id, int)
        assert isinstance(first_ref.reference_code, str)
        assert isinstance(first_ref.full_text, str)

    def test_major_references_ordered_by_code(self, db_client):
        """Test that major references are ordered numerically."""
        major_refs = db_client.get_major_curriculum_references()
        ref_codes = [r.reference_code for r in major_refs]

        # Convert to integers for numeric comparison
        numeric_codes = [int(code) for code in ref_codes]

        # Verify numeric ordering
        assert numeric_codes == sorted(numeric_codes), "Major references should be ordered numerically"

    def test_expected_major_references_present(self, db_client):
        """Test that expected major reference codes are present."""
        major_refs = db_client.get_major_curriculum_references()
        ref_codes = [r.reference_code for r in major_refs]

        expected = ['1', '2', '3', '4']
        for expected_code in expected:
            assert expected_code in ref_codes, f"Major reference '{expected_code}' should be present"


class TestGetLLMExamples:
    """Tests for get_llm_examples() method."""

    def test_returns_list_of_examples(self, db_client):
        """Test that method returns a list of LLMExample objects."""
        examples = db_client.get_llm_examples()

        assert isinstance(examples, list)
        assert len(examples) >= 4, "Should have at least 4 example entries"
        assert all(isinstance(e, LLMExample) for e in examples)

    def test_example_structure(self, db_client):
        """Test that each example has the correct structure."""
        examples = db_client.get_llm_examples()

        first_example = examples[0]
        assert hasattr(first_example, 'theme')
        assert hasattr(first_example, 'activity')
        assert hasattr(first_example, 'module')
        assert hasattr(first_example, 'objectives')
        assert hasattr(first_example, 'curriculum_references')

        assert isinstance(first_example.theme, str)
        assert isinstance(first_example.activity, str)
        assert isinstance(first_example.module, str)
        assert isinstance(first_example.objectives, str)
        assert isinstance(first_example.curriculum_references, list)

    def test_examples_have_curriculum_references(self, db_client):
        """Test that all examples have at least one curriculum reference."""
        examples = db_client.get_llm_examples()

        for example in examples:
            assert len(example.curriculum_references) > 0, \
                f"Example '{example.activity}' should have curriculum references"
            assert all(isinstance(ref, str) for ref in example.curriculum_references), \
                "Curriculum references should be strings"

    def test_examples_have_required_fields(self, db_client):
        """Test that all examples have non-empty required fields."""
        examples = db_client.get_llm_examples()

        for example in examples:
            assert len(example.activity) > 0, "Activity should not be empty"
            assert len(example.module) > 0, "Module should not be empty"
            # theme and objectives can be empty, but usually shouldn't be
            # for example entries

    def test_expected_example_present(self, db_client):
        """Test that expected example from migration is present."""
        examples = db_client.get_llm_examples()
        activities = [e.activity for e in examples]

        # Check that at least one example activity from migration is present
        # Using partial match to avoid quote character encoding issues
        assert any('Historyjki obrazkowe' in activity for activity in activities), \
            "Expected example activity should be present"

    def test_example_curriculum_refs_are_valid(self, db_client):
        """Test that curriculum references in examples are valid codes."""
        examples = db_client.get_llm_examples()
        all_refs = db_client.get_curriculum_references()
        valid_codes = {r.reference_code for r in all_refs}

        for example in examples:
            for ref_code in example.curriculum_references:
                assert ref_code in valid_codes, \
                    f"Example references invalid code: {ref_code}"


class TestGetDBClientFunction:
    """Tests for convenience function."""

    def test_get_db_client_default_path(self):
        """Test getting a database client with default path."""
        project_root = Path(__file__).parent.parent.parent
        db_path = project_root / "db.sqlite3"

        if not db_path.exists():
            pytest.skip("Django database not found. Run migrations first.")

        client = get_db_client()
        assert isinstance(client, DatabaseClient)

    def test_get_db_client_custom_path(self):
        """Test getting a database client with custom path."""
        project_root = Path(__file__).parent.parent.parent
        db_path = project_root / "db.sqlite3"

        if not db_path.exists():
            pytest.skip("Django database not found. Run migrations first.")

        client = get_db_client(str(db_path))
        assert isinstance(client, DatabaseClient)
        assert client.db_path == str(db_path)


class TestIntegration:
    """Integration tests verifying data relationships."""

    def test_curriculum_refs_have_valid_major_ids(self, db_client):
        """Test that all curriculum references link to valid major references."""
        curr_refs = db_client.get_curriculum_references()
        major_refs = db_client.get_major_curriculum_references()
        valid_major_ids = {r.id for r in major_refs}

        for curr_ref in curr_refs:
            assert curr_ref.major_reference_id in valid_major_ids, \
                f"Curriculum ref {curr_ref.reference_code} has invalid major_reference_id"

    def test_examples_use_valid_modules(self, db_client):
        """Test that examples reference valid educational modules."""
        examples = db_client.get_llm_examples()
        modules = db_client.get_educational_modules()
        valid_module_names = {m.module_name for m in modules}

        for example in examples:
            if example.module:  # module can be empty
                assert example.module in valid_module_names, \
                    f"Example uses invalid module: {example.module}"

    def test_all_methods_work_together(self, db_client):
        """Integration test: verify all 4 methods work together."""
        # Get data from all 4 methods
        modules = db_client.get_educational_modules()
        curr_refs = db_client.get_curriculum_references()
        major_refs = db_client.get_major_curriculum_references()
        examples = db_client.get_llm_examples()

        # Verify we got data from all methods
        assert len(modules) > 0
        assert len(curr_refs) > 0
        assert len(major_refs) > 0
        assert len(examples) > 0

        # Verify relationships
        major_ids = {r.id for r in major_refs}
        for curr_ref in curr_refs:
            assert curr_ref.major_reference_id in major_ids

        # Verify examples use valid data
        module_names = {m.module_name for m in modules}
        ref_codes = {r.reference_code for r in curr_refs}

        for example in examples:
            if example.module:
                assert example.module in module_names
            for ref_code in example.curriculum_references:
                assert ref_code in ref_codes
