import pytest
from mcp_service.api_client import DjangoAPIClient
import httpx
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_get_all_curriculum_references_success():
    client = DjangoAPIClient(base_url="http://test")
    
    mock_response = httpx.Response(200, json={"references": {"1.1": "Test ref"}, "count": 1}, request=httpx.Request("GET", "http://test"))
    
    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response
        result = await client.get_all_curriculum_references()
        
        assert isinstance(result, dict)
        assert "references" in result
        assert result["references"]["1.1"] == "Test ref"
        assert result["count"] == 1

@pytest.mark.asyncio
async def test_get_all_curriculum_references_empty():
    client = DjangoAPIClient(base_url="http://test")
    
    mock_response = httpx.Response(200, json={"references": {}, "count": 0}, request=httpx.Request("GET", "http://test"))
    
    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response
        result = await client.get_all_curriculum_references()
        
        assert isinstance(result, dict)
        assert result["references"] == {}
        assert result["count"] == 0

@pytest.mark.asyncio
async def test_get_all_curriculum_references_http_error():
    client = DjangoAPIClient(base_url="http://test")
    
    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        request = httpx.Request("GET", "http://test")
        response = httpx.Response(500, request=request)
        error = httpx.HTTPStatusError("Server error", request=request, response=response)
        
        mock_get.side_effect = error
        
        result = await client.get_all_curriculum_references()
        
        assert isinstance(result, dict)
        assert "error" in result
        assert "HTTP error" in result["error"]
