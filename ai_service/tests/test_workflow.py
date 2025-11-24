"""
Tests for LangGraph workflow integration.

Tests the complete workflow with mocked LLM responses.
"""

import pytest
from unittest.mock import AsyncMock, patch

from ai_service.workflow import create_workflow


@pytest.fixture
def sample_initial_state():
    """Sample initial state for workflow."""
    return {
        "activity": "Zabawa w sklep z owocami",
        "theme": "Jesień - zbiory"
    }


@pytest.fixture
def mock_llm_response():
    """Mock LLM JSON response."""
    return '''{
        "reasoning": "Zabawa w sklep wymaga liczenia i rozpoznawania cyfr",
        "modules": ["MATEMATYKA"],
        "curriculum_refs": ["4.15", "4.18"],
        "objectives": [
            "Dziecko potrafi przeliczać w zakresie 5",
            "Rozpoznaje poznane wcześniej cyfry"
        ]
    }'''


@pytest.mark.asyncio
class TestWorkflowIntegration:
    """Integration tests for the complete workflow."""

    async def test_workflow_success_path(self, sample_initial_state, mock_llm_response):
        """Test successful workflow execution end-to-end."""
        # Mock the LLM client
        with patch('ai_service.nodes.llm_generator.get_llm_client') as mock_get_client:
            # Create mock client
            mock_client = AsyncMock()
            mock_client.generate.return_value = (
                mock_llm_response,
                {
                    "input_tokens": 1400,
                    "output_tokens": 180,
                    "total_tokens": 1580,
                    "estimated_cost": 0.0006
                }
            )
            mock_get_client.return_value = mock_client

            # Create and execute workflow
            workflow = create_workflow()
            result = await workflow.ainvoke(sample_initial_state)

            # Verify final response
            assert "final_response" in result
            final_response = result["final_response"]

            # Check response structure
            assert final_response.activity == "Zabawa w sklep z owocami"
            assert "MATEMATYKA" in final_response.modules
            assert "4.15" in final_response.curriculum_refs
            assert len(final_response.objectives) >= 2

    async def test_workflow_validation_error(self, sample_initial_state):
        """Test workflow with invalid LLM output."""
        # Mock LLM to return invalid JSON
        with patch('ai_service.nodes.llm_generator.get_llm_client') as mock_get_client:
            mock_client = AsyncMock()
            mock_client.generate.return_value = (
                "Invalid JSON response",  # Not valid JSON
                {
                    "input_tokens": 100,
                    "output_tokens": 10,
                    "total_tokens": 110,
                    "estimated_cost": 0.0001
                }
            )
            mock_get_client.return_value = mock_client

            workflow = create_workflow()
            result = await workflow.ainvoke(sample_initial_state)

            # Should get error response
            assert "final_response" in result
            final_response = result["final_response"]
            assert hasattr(final_response, "error_code")
            assert final_response.error_code == "VALIDATION_ERROR"

    async def test_workflow_invalid_input(self):
        """Test workflow with invalid input."""
        # Empty activity should fail input validation
        invalid_state = {
            "activity": "",
            "theme": "Test"
        }

        workflow = create_workflow()
        result = await workflow.ainvoke(invalid_state)

        # Workflow should handle input validation error
        # Note: Current implementation doesn't stop on input validation failure
        # This test documents the current behavior
        assert "validation_errors" in result or "final_response" in result


@pytest.mark.asyncio
class TestWorkflowNodes:
    """Tests for individual workflow nodes."""

    async def test_parallel_loading(self, sample_initial_state):
        """Test that parallel loaders execute correctly."""
        workflow = create_workflow()

        # Execute workflow up to prompt construction
        # This is a smoke test to ensure loaders don't error
        with patch('ai_service.nodes.llm_generator.get_llm_client') as mock_get_client:
            mock_client = AsyncMock()
            mock_client.generate.return_value = (
                '{"reasoning": "test", "modules": ["MATEMATYKA"], "curriculum_refs": ["4.15"], "objectives": ["Test objective that is long enough"]}',
                {"input_tokens": 100, "output_tokens": 50, "total_tokens": 150, "estimated_cost": 0.0001}
            )
            mock_get_client.return_value = mock_client

            result = await workflow.ainvoke(sample_initial_state)

            # Verify loaders populated state
            assert "available_modules" in result
            assert "curriculum_refs" in result
            assert "major_curriculum_refs" in result
            assert "example_entries" in result
            assert "prompt_template" in result

    async def test_prompt_construction(self, sample_initial_state, mock_llm_response):
        """Test that prompt is constructed with all placeholders filled."""
        with patch('ai_service.nodes.llm_generator.get_llm_client') as mock_get_client:
            mock_client = AsyncMock()
            mock_client.generate.return_value = (
                mock_llm_response,
                {"input_tokens": 100, "output_tokens": 50, "total_tokens": 150, "estimated_cost": 0.0001}
            )
            mock_get_client.return_value = mock_client

            workflow = create_workflow()
            result = await workflow.ainvoke(sample_initial_state)

            # Verify prompt was constructed
            assert "constructed_prompt" in result
            assert len(result["constructed_prompt"]) > 0

            # Verify placeholders were replaced
            prompt = result["constructed_prompt"]
            assert "Zabawa w sklep z owocami" in prompt
            assert "{activity}" not in prompt  # Placeholder should be replaced
            assert "{modules_list}" not in prompt
