import pytest
from mcp_service.api_client import DjangoAPIClient
import httpx
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_get_all_curriculum_references_success():
    client = DjangoAPIClient(base_url="http://test")
    
    # httpx.Response requires a request obj or simply use json= payload directly
    # Wait, passing json directly requires httpx >= 0.20, let's just make a mock that returns the json
    mock_response = httpx.Response(200, json={"references": {"1.1": "Test ref"}}, request=httpx.Request("GET", "http://test"))
    
    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response
        result = await client.get_all_curriculum_references()
        
        assert "Test ref" in result
        assert "[1.1]" in result

@pytest.mark.asyncio
async def test_get_all_curriculum_references_empty():
    client = DjangoAPIClient(base_url="http://test")
    
    mock_response = httpx.Response(200, json={"references": {}}, request=httpx.Request("GET", "http://test"))
    
    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response
        result = await client.get_all_curriculum_references()
        
        assert "No curriculum references found." in result

@pytest.mark.asyncio
async def test_get_all_curriculum_references_http_error():
    client = DjangoAPIClient(base_url="http://test")
    
    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        request = httpx.Request("GET", "http://test")
        response = httpx.Response(500, request=request)
        error = httpx.HTTPStatusError("Server error", request=request, response=response)
        
        # Make the mocked httpx.AsyncClient object raise exception when making the call
        mock_get.side_effect = error
        
        result = await client.get_all_curriculum_references()
        
        # api client handles this exception
        assert "HTTP error occurred" in result
