"""
Tests for OpenRouter LLM client.

Uses mocked httpx responses to test client behavior without actual API calls.
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import httpx

from ai_service.nodes.llm_client import OpenRouterClient


@pytest.fixture
def mock_openrouter_response():
    """Mock successful OpenRouter API response."""
    return {
        "id": "gen-test123",
        "choices": [
            {
                "message": {
                    "content": '{"reasoning": "Test reasoning", "modules": ["MATEMATYKA"], "curriculum_refs": ["4.15"], "objectives": ["Test objective"]}'
                }
            }
        ],
        "usage": {
            "prompt_tokens": 100,
            "completion_tokens": 50,
            "total_tokens": 150
        }
    }


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
    """Tests for OpenRouter client."""

    async def test_successful_generation(self, mock_openrouter_response, mock_pricing_response):
        """Test successful LLM call with token tracking."""
        with patch('httpx.AsyncClient') as mock_client_class:
            # Mock the async context manager
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client_class.return_value.__aexit__.return_value = None

            # Mock chat completion response
            mock_chat_response = AsyncMock()
            mock_chat_response.json.return_value = mock_openrouter_response
            mock_chat_response.raise_for_status = MagicMock()
            mock_client.post.return_value = mock_chat_response

            # Mock pricing response
            mock_pricing_response_obj = AsyncMock()
            mock_pricing_response_obj.json.return_value = mock_pricing_response
            mock_pricing_response_obj.raise_for_status = MagicMock()
            mock_client.get.return_value = mock_pricing_response_obj

            # Create client and call
            client = OpenRouterClient(api_key="test-key")
            response, usage = await client.generate("Test prompt", log_output=False)

            # Verify response
            assert "Test reasoning" in response
            assert usage["input_tokens"] == 100
            assert usage["output_tokens"] == 50
            assert usage["total_tokens"] == 150
            assert "estimated_cost" in usage

    async def test_timeout_handling(self):
        """Test that timeout errors are handled properly."""
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client_class.return_value.__aexit__.return_value = None

            # Mock timeout exception
            mock_client.post.side_effect = httpx.TimeoutException("Request timed out")

            client = OpenRouterClient(api_key="test-key")

            with pytest.raises(httpx.TimeoutException):
                await client.generate("Test prompt", log_output=False)

    async def test_http_error_handling(self):
        """Test that HTTP errors are handled properly."""
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client_class.return_value.__aexit__.return_value = None

            # Mock HTTP error
            mock_response = AsyncMock()
            mock_response.status_code = 500
            mock_response.text = "Internal Server Error"
            mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
                "500 Error",
                request=MagicMock(),
                response=mock_response
            )
            mock_client.post.return_value = mock_response

            client = OpenRouterClient(api_key="test-key")

            with pytest.raises(httpx.HTTPStatusError):
                await client.generate("Test prompt", log_output=False)

    async def test_invalid_response_format(self, mock_pricing_response):
        """Test handling of malformed API response."""
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client_class.return_value.__aexit__.return_value = None

            # Mock malformed response (missing 'choices')
            mock_chat_response = AsyncMock()
            mock_chat_response.json.return_value = {"error": "Invalid response"}
            mock_chat_response.raise_for_status = MagicMock()
            mock_client.post.return_value = mock_chat_response

            client = OpenRouterClient(api_key="test-key")

            with pytest.raises(ValueError):
                await client.generate("Test prompt", log_output=False)

    def test_missing_api_key(self):
        """Test that missing API key raises error."""
        with pytest.raises(ValueError):
            OpenRouterClient(api_key="")

    async def test_cost_calculation_fallback(self, mock_openrouter_response):
        """Test that cost calculation uses fallback if pricing fetch fails."""
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client_class.return_value.__aexit__.return_value = None

            # Mock successful chat response
            mock_chat_response = AsyncMock()
            mock_chat_response.json.return_value = mock_openrouter_response
            mock_chat_response.raise_for_status = MagicMock()

            # Mock failed pricing response
            mock_pricing_response = AsyncMock()
            mock_pricing_response.raise_for_status.side_effect = httpx.HTTPError("Pricing failed")

            # Alternate between chat and pricing calls
            call_count = 0
            def side_effect(*args, **kwargs):
                nonlocal call_count
                call_count += 1
                if call_count == 1:
                    return mock_pricing_response  # First call (pricing) fails
                return mock_chat_response  # Second call (chat) succeeds

            mock_client.post.return_value = mock_chat_response
            mock_client.get.side_effect = httpx.HTTPError("Pricing failed")

            client = OpenRouterClient(api_key="test-key")
            response, usage = await client.generate("Test prompt", log_output=False)

            # Should still get cost estimate (fallback pricing)
            assert "estimated_cost" in usage
            assert usage["estimated_cost"] > 0
