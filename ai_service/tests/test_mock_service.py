"""
Tests for mock AI service logic.

Tests the MockAIService class directly (unit tests).
"""

import pytest
from ai_service.mock_service import MockAIService


class TestMockAIService:
    """Tests for MockAIService class"""

    @pytest.fixture
    def service(self):
        """Create mock AI service with no delay for faster tests"""
        return MockAIService(simulate_delay=False)

    def test_generate_metadata_success(self, service):
        """Test successful metadata generation"""
        result = service.generate_metadata(
            activity="Zabawa w sklep z owocami",
            theme="Jesień - zbiory"
        )

        assert result.activity == "Zabawa w sklep z owocami"
        assert isinstance(result.module, str)
        assert len(result.module) > 0
        assert isinstance(result.curriculum_refs, list)
        assert len(result.curriculum_refs) >= 2
        assert isinstance(result.objectives, list)
        assert len(result.objectives) >= 2

    def test_generate_metadata_no_theme(self, service):
        """Test metadata generation without theme"""
        result = service.generate_metadata(activity="Test activity")

        assert result.activity == "Test activity"
        assert result.module is not None
        assert len(result.curriculum_refs) > 0
        assert len(result.objectives) > 0

    def test_generate_metadata_strips_whitespace(self, service):
        """Test that whitespace is stripped from activity"""
        result = service.generate_metadata(
            activity="  Test activity  ",
            theme="  Test theme  "
        )

        assert result.activity == "Test activity"

    def test_generate_metadata_empty_activity_still_works(self, service):
        """
        Test that empty activity doesn't raise error in mock service.

        Note: Validation is handled by Pydantic FillWorkPlanRequest model,
        not by the mock service itself.
        """
        # Mock service trusts that validation happened upstream
        result = service.generate_metadata(activity="")
        # It will process even empty string (Pydantic prevents this in real flow)
        assert result is not None

    def test_generate_metadata_whitespace_gets_stripped(self, service):
        """Test that whitespace activity gets stripped"""
        result = service.generate_metadata(activity="   Test   ")
        # Activity gets stripped in the response
        assert result.activity == "Test"

    def test_generate_metadata_returns_valid_curriculum_refs(self, service):
        """Test that returned curriculum refs are from database"""
        from ai_service.db_client import get_db_client

        # Get valid refs from database
        db_client = get_db_client()
        valid_refs = [ref.reference_code for ref in db_client.get_curriculum_references()]

        result = service.generate_metadata(activity="Test activity")

        # Verify all returned refs are valid database refs
        for ref in result.curriculum_refs:
            assert ref in valid_refs

    def test_generate_metadata_returns_valid_module(self, service):
        """Test that returned module is from database"""
        from ai_service.db_client import get_db_client

        # Get valid modules from database
        db_client = get_db_client()
        valid_modules = [mod.module_name for mod in db_client.get_educational_modules()]

        result = service.generate_metadata(activity="Test activity")

        # Verify returned module is valid database module
        assert result.module in valid_modules

    def test_generate_metadata_returns_2_to_3_refs(self, service):
        """Test that 2-3 curriculum refs are returned"""
        result = service.generate_metadata(activity="Test activity")

        assert 2 <= len(result.curriculum_refs) <= 3

    def test_generate_metadata_returns_2_to_3_objectives(self, service):
        """Test that 2-3 objectives are returned"""
        result = service.generate_metadata(activity="Test activity")

        assert 2 <= len(result.objectives) <= 3

    def test_generate_metadata_randomness(self, service):
        """Test that multiple calls return different results (randomness)"""
        results = [
            service.generate_metadata(activity="Test activity")
            for _ in range(5)
        ]

        # At least some results should be different
        modules = [r.module for r in results]
        assert len(set(modules)) > 1  # Not all modules should be the same

    def test_generate_metadata_with_delay(self):
        """Test that delay simulation works"""
        import time

        service = MockAIService(simulate_delay=True)
        start_time = time.time()
        service.generate_metadata(activity="Test activity")
        elapsed = time.time() - start_time

        # Should take at least 1 second due to simulated delay
        assert elapsed >= 1.0
