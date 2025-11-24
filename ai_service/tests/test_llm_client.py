"""
Tests for OpenRouter LLM client using OpenAI SDK.

Uses mocked OpenAI responses to test client behavior without actual API calls.
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from ai_service.nodes.llm_client import OpenRouterClient, extract_reasoning_and_json


@pytest.fixture
def mock_openai_response():
    """Mock successful OpenAI API response object."""
    mock_response = MagicMock()

    # Mock choices
    mock_choice = MagicMock()
    mock_message = MagicMock()
    mock_message.content = '{"modules": ["MATEMATYKA"], "curriculum_refs": ["4.15"], "objectives": ["Test objective"]}'
    mock_choice.message = mock_message
    mock_response.choices = [mock_choice]

    # Mock usage
    mock_usage = MagicMock()
    mock_usage.prompt_tokens = 100
    mock_usage.completion_tokens = 50
    mock_usage.total_tokens = 150
    mock_response.usage = mock_usage

    return mock_response


@pytest.fixture
def mock_pricing_response():
    """Mock OpenRouter pricing API response."""
    return {
        "data": [
            {
                "id": "anthropic/claude-3.5-haiku",
                "pricing": {
                    "prompt": "0.00000025",
                    "completion": "0.00000125"
                }
            }
        ]
    }


@pytest.mark.asyncio
class TestOpenRouterClient:
    """Tests for OpenRouter client using OpenAI SDK."""

    async def test_successful_generation(self, mock_openai_response, mock_pricing_response):
        """Test successful LLM call with token tracking."""
        with patch('ai_service.nodes.llm_client.AsyncOpenAI') as mock_openai_class:
            # Mock the OpenAI client instance
            mock_client = MagicMock()
            mock_openai_class.return_value = mock_client

            # Mock chat completions
            mock_client.chat.completions.create = AsyncMock(return_value=mock_openai_response)

            # Mock pricing fetch
            with patch('ai_service.nodes.llm_client.get_pricing_cache') as mock_pricing_cache:
                mock_cache = MagicMock()
                mock_cache.fetch_pricing = AsyncMock(return_value=(0.00000025, 0.00000125))
                mock_pricing_cache.return_value = mock_cache

                # Create client and call
                client = OpenRouterClient(api_key="test-key")
                response, usage = await client.generate("Test prompt", log_output=False)

                # Verify response
                assert usage["input_tokens"] == 100
                assert usage["output_tokens"] == 50
                assert usage["total_tokens"] == 150
                assert "estimated_cost" in usage

    async def test_timeout_handling(self):
        """Test that timeout errors are handled properly."""
        with patch('ai_service.nodes.llm_client.AsyncOpenAI') as mock_openai_class:
            mock_client = MagicMock()
            mock_openai_class.return_value = mock_client

            # Mock timeout exception
            from openai import APITimeoutError
            mock_client.chat.completions.create = AsyncMock(
                side_effect=APITimeoutError("Request timed out")
            )

            client = OpenRouterClient(api_key="test-key")

            with pytest.raises(APITimeoutError):
                await client.generate("Test prompt", log_output=False)

    async def test_http_error_handling(self):
        """Test that HTTP errors are handled properly."""
        with patch('ai_service.nodes.llm_client.AsyncOpenAI') as mock_openai_class:
            mock_client = MagicMock()
            mock_openai_class.return_value = mock_client

            # Mock HTTP error
            from openai import APIStatusError
            mock_response = MagicMock()
            mock_response.status_code = 500

            mock_client.chat.completions.create = AsyncMock(
                side_effect=APIStatusError(
                    "Internal Server Error",
                    response=mock_response,
                    body=None
                )
            )

            client = OpenRouterClient(api_key="test-key")

            with pytest.raises(APIStatusError):
                await client.generate("Test prompt", log_output=False)

    async def test_invalid_response_format(self):
        """Test handling of malformed API response."""
        with patch('ai_service.nodes.llm_client.AsyncOpenAI') as mock_openai_class:
            mock_client = MagicMock()
            mock_openai_class.return_value = mock_client

            # Mock response with None content
            mock_response = MagicMock()
            mock_choice = MagicMock()
            mock_message = MagicMock()
            mock_message.content = None
            mock_choice.message = mock_message
            mock_response.choices = [mock_choice]

            mock_client.chat.completions.create = AsyncMock(return_value=mock_response)

            client = OpenRouterClient(api_key="test-key")

            with pytest.raises(ValueError):
                await client.generate("Test prompt", log_output=False)

    def test_missing_api_key(self):
        """Test that missing API key raises error."""
        with pytest.raises(ValueError):
            OpenRouterClient(api_key="")

    async def test_cost_calculation_fallback(self, mock_openai_response):
        """Test that cost calculation uses fallback if pricing fetch fails."""
        with patch('ai_service.nodes.llm_client.AsyncOpenAI') as mock_openai_class:
            mock_client = MagicMock()
            mock_openai_class.return_value = mock_client

            # Mock successful chat response
            mock_client.chat.completions.create = AsyncMock(return_value=mock_openai_response)

            # Mock failed pricing response
            with patch('ai_service.nodes.llm_client.get_pricing_cache') as mock_pricing_cache:
                mock_cache = MagicMock()
                mock_cache.fetch_pricing = AsyncMock(side_effect=Exception("Pricing failed"))
                mock_pricing_cache.return_value = mock_cache

                client = OpenRouterClient(api_key="test-key")
                response, usage = await client.generate("Test prompt", log_output=False)

                # Should still get cost estimate (fallback pricing)
                assert "estimated_cost" in usage
                assert usage["estimated_cost"] > 0


class TestReasoningExtraction:
    """Tests for reasoning extraction from LLM responses."""

    def test_extract_thinking_tags(self):
        """Test extraction of <think> tags (DeepSeek R1 style)."""
        response = """<think>
This is my reasoning process.
I need to analyze the activity.
</think>
{
  "modules": ["MATEMATYKA"],
  "curriculum_refs": ["4.15"],
  "objectives": ["Test objective"]
}"""
        reasoning, json_dict = extract_reasoning_and_json(response)

        assert reasoning == "This is my reasoning process.\nI need to analyze the activity."
        assert json_dict["modules"] == ["MATEMATYKA"]
        assert json_dict["curriculum_refs"] == ["4.15"]

    def test_extract_thinking_alternative_tags(self):
        """Test extraction of <thinking> tags (alternative format)."""
        response = """<thinking>
Analyzing the educational context.
</thinking>
{
  "modules": ["JĘZYK"],
  "curriculum_refs": ["3.4"],
  "objectives": ["Develop language skills"]
}"""
        reasoning, json_dict = extract_reasoning_and_json(response)

        assert reasoning == "Analyzing the educational context."
        assert json_dict["modules"] == ["JĘZYK"]

    def test_no_reasoning_tags(self):
        """Test response without reasoning tags."""
        response = """{
  "modules": ["MATEMATYKA"],
  "curriculum_refs": ["4.15"],
  "objectives": ["Test"]
}"""
        reasoning, json_dict = extract_reasoning_and_json(response)

        assert reasoning == ""
        assert json_dict["modules"] == ["MATEMATYKA"]

    def test_json_with_markdown_fences(self):
        """Test JSON extraction with markdown code fences."""
        response = """```json
{
  "modules": ["MATEMATYKA"],
  "curriculum_refs": ["4.15"],
  "objectives": ["Test"]
}
```"""
        reasoning, json_dict = extract_reasoning_and_json(response)

        assert reasoning == ""
        assert json_dict["modules"] == ["MATEMATYKA"]

    def test_invalid_json_raises_error(self):
        """Test that invalid JSON raises ValueError."""
        response = "This is not JSON at all"

        with pytest.raises(ValueError, match="Could not parse JSON"):
            extract_reasoning_and_json(response)

    def test_json_extraction_from_mixed_content(self):
        """Test JSON extraction when embedded in text."""
        response = """Here is the analysis:
{
  "modules": ["MATEMATYKA"],
  "curriculum_refs": ["4.15"],
  "objectives": ["Test"]
}
And some trailing text."""

        reasoning, json_dict = extract_reasoning_and_json(response)

        # Should extract the JSON object
        assert json_dict["modules"] == ["MATEMATYKA"]

    async def test_json_extraction_fallback(self, mock_pricing_response):
        """Test that regex fallback extracts JSON from malformed response."""
        with patch('ai_service.nodes.llm_client.AsyncOpenAI') as mock_openai_class:
            mock_client = MagicMock()
            mock_openai_class.return_value = mock_client

            # Mock response with JSON embedded in extra text
            mock_response = MagicMock()
            mock_choice = MagicMock()
            mock_message = MagicMock()
            # Simulate response with extra text before/after JSON
            mock_message.content = '''Here is the result:
{"modules": ["MATEMATYKA"], "curriculum_refs": ["4.15"], "objectives": ["Test objective"]}
End of response.'''
            mock_choice.message = mock_message
            mock_response.choices = [mock_choice]

            # Mock usage
            mock_usage = MagicMock()
            mock_usage.prompt_tokens = 100
            mock_usage.completion_tokens = 50
            mock_usage.total_tokens = 150
            mock_response.usage = mock_usage

            mock_client.chat.completions.create = AsyncMock(return_value=mock_response)

            # Mock pricing fetch
            with patch('ai_service.nodes.llm_client.get_pricing_cache') as mock_pricing_cache:
                mock_cache = MagicMock()
                mock_cache.fetch_pricing = AsyncMock(return_value=(0.00000025, 0.00000125))
                mock_pricing_cache.return_value = mock_cache

                client = OpenRouterClient(api_key="test-key")
                response, usage = await client.generate("Test prompt", log_output=False)

                # Should successfully extract and parse JSON
                import json
                parsed = json.loads(response)
                assert parsed["modules"] == ["MATEMATYKA"]
                assert parsed["curriculum_refs"] == ["4.15"]
                assert parsed["objectives"] == ["Test objective"]
