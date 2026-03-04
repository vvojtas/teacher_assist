import pytest
from mcp_service.api_client import DjangoAPIClient
import httpx
from unittest.mock import AsyncMock, patch


# ── get_all_curriculum_references ────────────────────────────────

@pytest.mark.asyncio
async def test_get_all_curriculum_references_success():
    client = DjangoAPIClient(base_url="http://test")
    mock_response = httpx.Response(200, json={"references": {"1.1": "Test ref"}, "count": 1}, request=httpx.Request("GET", "http://test"))

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response
        result = await client.get_all_curriculum_references()

        assert isinstance(result, dict)
        assert result["references"]["1.1"] == "Test ref"
        assert result["count"] == 1


@pytest.mark.asyncio
async def test_get_all_curriculum_references_empty():
    client = DjangoAPIClient(base_url="http://test")
    mock_response = httpx.Response(200, json={"references": {}, "count": 0}, request=httpx.Request("GET", "http://test"))

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response
        result = await client.get_all_curriculum_references()

        assert result["references"] == {}
        assert result["count"] == 0


@pytest.mark.asyncio
async def test_get_all_curriculum_references_http_error():
    client = DjangoAPIClient(base_url="http://test")

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.side_effect = httpx.HTTPStatusError(
            "Server error",
            request=httpx.Request("GET", "http://test"),
            response=httpx.Response(500, request=httpx.Request("GET", "http://test")),
        )
        result = await client.get_all_curriculum_references()

        assert "error" in result
        assert "HTTP error" in result["error"]


# ── lookup_curriculum_reference ──────────────────────────────────

@pytest.mark.asyncio
async def test_lookup_curriculum_reference_success():
    client = DjangoAPIClient(base_url="http://test")
    mock_data = {"reference_code": "3.8", "full_text": "obdarza uwagą", "created_at": "2025-10-28T10:30:00Z"}
    mock_response = httpx.Response(200, json=mock_data, request=httpx.Request("GET", "http://test"))

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response
        result = await client.lookup_curriculum_reference("3.8")

        assert result["reference_code"] == "3.8"
        assert "full_text" in result


@pytest.mark.asyncio
async def test_lookup_curriculum_reference_not_found():
    client = DjangoAPIClient(base_url="http://test")
    error_data = {"error": "Nie znaleziono", "error_code": "REFERENCE_NOT_FOUND"}
    mock_response = httpx.Response(404, json=error_data, request=httpx.Request("GET", "http://test"))

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response
        mock_get.return_value.raise_for_status = lambda: (_ for _ in ()).throw(
            httpx.HTTPStatusError("Not Found", request=httpx.Request("GET", "http://test"), response=mock_response)
        )
        result = await client.lookup_curriculum_reference("99.99")

        assert result["error_code"] == "REFERENCE_NOT_FOUND"


@pytest.mark.asyncio
async def test_lookup_curriculum_reference_invalid_code():
    client = DjangoAPIClient(base_url="http://test")
    error_data = {"error": "Nieprawidłowy format", "error_code": "INVALID_CODE_FORMAT"}
    mock_response = httpx.Response(400, json=error_data, request=httpx.Request("GET", "http://test"))

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response
        mock_get.return_value.raise_for_status = lambda: (_ for _ in ()).throw(
            httpx.HTTPStatusError("Bad Request", request=httpx.Request("GET", "http://test"), response=mock_response)
        )
        result = await client.lookup_curriculum_reference("invalid" * 10)

        assert result["error_code"] == "INVALID_CODE_FORMAT"


# ── get_educational_modules ──────────────────────────────────────

@pytest.mark.asyncio
async def test_get_educational_modules_all():
    client = DjangoAPIClient(base_url="http://test")
    mock_data = {
        "modules": [
            {"id": 1, "name": "JĘZYK", "is_ai_suggested": False},
            {"id": 2, "name": "MATEMATYKA", "is_ai_suggested": True},
        ],
        "count": 2,
    }
    mock_response = httpx.Response(200, json=mock_data, request=httpx.Request("GET", "http://test"))

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response
        result = await client.get_educational_modules()

        assert result["count"] == 2
        assert len(result["modules"]) == 2


@pytest.mark.asyncio
async def test_get_educational_modules_filtered():
    client = DjangoAPIClient(base_url="http://test")
    mock_data = {"modules": [{"id": 2, "name": "MATEMATYKA", "is_ai_suggested": True}], "count": 1}
    mock_response = httpx.Response(200, json=mock_data, request=httpx.Request("GET", "http://test"))

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response
        result = await client.get_educational_modules(ai_suggested=True)

        assert result["count"] == 1
        # Verify the query param was included
        call_args = mock_get.call_args
        assert "ai_suggested" in str(call_args)


@pytest.mark.asyncio
async def test_get_educational_modules_error():
    client = DjangoAPIClient(base_url="http://test")

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.side_effect = httpx.HTTPStatusError(
            "Server error",
            request=httpx.Request("GET", "http://test"),
            response=httpx.Response(500, request=httpx.Request("GET", "http://test")),
        )
        result = await client.get_educational_modules()

        assert "error" in result


# ── generate_lesson_metadata ─────────────────────────────────────

@pytest.mark.asyncio
async def test_generate_lesson_metadata_success():
    client = DjangoAPIClient(base_url="http://test")

    csrf_response = httpx.Response(200, request=httpx.Request("GET", "http://test"))
    csrf_response.headers["set-cookie"] = "csrftoken=abc123; Path=/"

    ai_result = {"module": "JĘZYK", "curriculum_refs": ["4.2", "4.5"], "objectives": ["Develops speech"]}
    post_response = httpx.Response(200, json=ai_result, request=httpx.Request("POST", "http://test"))

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get, \
         patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_get.return_value = csrf_response
        mock_post.return_value = post_response
        result = await client.generate_lesson_metadata(activity="Dzieci malują")

        assert result["module"] == "JĘZYK"
        assert "4.2" in result["curriculum_refs"]

        # Verify CSRF header was sent
        post_call = mock_post.call_args
        assert "X-CSRFToken" in str(post_call)


@pytest.mark.asyncio
async def test_generate_lesson_metadata_with_theme():
    client = DjangoAPIClient(base_url="http://test")

    csrf_response = httpx.Response(200, request=httpx.Request("GET", "http://test"))
    csrf_response.headers["set-cookie"] = "csrftoken=abc123; Path=/"

    ai_result = {"module": "MATEMATYKA", "curriculum_refs": ["4.15"], "objectives": ["Counts objects"]}
    post_response = httpx.Response(200, json=ai_result, request=httpx.Request("POST", "http://test"))

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get, \
         patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_get.return_value = csrf_response
        mock_post.return_value = post_response
        result = await client.generate_lesson_metadata(activity="Liczenie klocków", theme="Matematyka")

        # Verify theme was included in payload
        post_call = mock_post.call_args
        assert "theme" in str(post_call)


@pytest.mark.asyncio
async def test_generate_lesson_metadata_timeout():
    client = DjangoAPIClient(base_url="http://test")

    csrf_response = httpx.Response(200, request=httpx.Request("GET", "http://test"))
    csrf_response.headers["set-cookie"] = "csrftoken=abc123; Path=/"

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get, \
         patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_get.return_value = csrf_response
        mock_post.side_effect = httpx.TimeoutException("Connection timed out")
        result = await client.generate_lesson_metadata(activity="Test activity")

        assert result["error_code"] == "AI_SERVICE_TIMEOUT"


@pytest.mark.asyncio
async def test_generate_lesson_metadata_csrf_failure():
    client = DjangoAPIClient(base_url="http://test")

    # Return response without csrftoken cookie
    csrf_response = httpx.Response(200, request=httpx.Request("GET", "http://test"))

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = csrf_response
        result = await client.generate_lesson_metadata(activity="Test activity")

        assert result["error_code"] == "CSRF_ERROR"


@pytest.mark.asyncio
async def test_generate_lesson_metadata_ai_unavailable():
    client = DjangoAPIClient(base_url="http://test")

    csrf_response = httpx.Response(200, request=httpx.Request("GET", "http://test"))
    csrf_response.headers["set-cookie"] = "csrftoken=abc123; Path=/"

    error_data = {"error": "AI service unavailable", "error_code": "AI_SERVICE_UNAVAILABLE"}
    error_response = httpx.Response(503, json=error_data, request=httpx.Request("POST", "http://test"))

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get, \
         patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_get.return_value = csrf_response
        mock_post.return_value = error_response
        mock_post.return_value.raise_for_status = lambda: (_ for _ in ()).throw(
            httpx.HTTPStatusError("Service Unavailable", request=httpx.Request("POST", "http://test"), response=error_response)
        )
        result = await client.generate_lesson_metadata(activity="Test activity")

        assert result["error_code"] == "AI_SERVICE_UNAVAILABLE"
