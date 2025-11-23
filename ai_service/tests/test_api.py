"""
API endpoint tests for AI service.

Tests verify compliance with docs/ai_api.md specification.
Run tests with: pytest ai_service/tests/
"""

import pytest
from fastapi.testclient import TestClient


class TestHealthCheck:
    """Tests for GET /health endpoint"""

    def test_health_check_success(self, client: TestClient):
        """Test health check returns 200 OK"""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data


class TestFillWorkPlan:
    """Tests for POST /api/fill-work-plan endpoint"""

    def test_fill_work_plan_success(self, client: TestClient, sample_request_data):
        """Test successful metadata generation with full request"""
        response = client.post("/api/fill-work-plan", json=sample_request_data)

        assert response.status_code == 200
        data = response.json()

        # Verify response structure
        assert "activity" in data
        assert "modules" in data
        assert "curriculum_refs" in data
        assert "objectives" in data

        # Verify activity is echoed back
        assert data["activity"] == sample_request_data["activity"]

        # Verify modules is a non-empty list
        assert isinstance(data["modules"], list)
        assert len(data["modules"]) >= 1
        assert all(isinstance(m, str) and len(m) > 0 for m in data["modules"])

        # Verify curriculum_refs is a list with 1-10 items
        assert isinstance(data["curriculum_refs"], list)
        assert 1 <= len(data["curriculum_refs"]) <= 10

        # Verify objectives is a list with 1-10 items
        assert isinstance(data["objectives"], list)
        assert 1 <= len(data["objectives"]) <= 10

    def test_fill_work_plan_minimal_request(self, client: TestClient, sample_request_minimal):
        """Test successful generation with activity only (no theme)"""
        response = client.post("/api/fill-work-plan", json=sample_request_minimal)

        assert response.status_code == 200
        data = response.json()
        assert data["activity"] == sample_request_minimal["activity"]
        assert "modules" in data
        assert "curriculum_refs" in data
        assert "objectives" in data

    def test_fill_work_plan_empty_theme(self, client: TestClient):
        """Test that empty theme is handled correctly"""
        response = client.post("/api/fill-work-plan", json={
            "activity": "Test activity",
            "theme": ""
        })

        assert response.status_code == 200
        data = response.json()
        assert "modules" in data

    def test_fill_work_plan_missing_activity(self, client: TestClient):
        """Test validation: missing required activity field"""
        response = client.post("/api/fill-work-plan", json={
            "theme": "Test theme"
        })

        assert response.status_code == 400  # Bad Request (per API spec)
        data = response.json()
        assert "error_code" in data
        assert data["error_code"] == "VALIDATION_ERROR"

    def test_fill_work_plan_empty_activity(self, client: TestClient):
        """Test validation: empty activity field"""
        response = client.post("/api/fill-work-plan", json={
            "activity": "",
            "theme": "Test theme"
        })

        assert response.status_code == 400
        data = response.json()
        assert "error_code" in data
        assert data["error_code"] == "VALIDATION_ERROR"
        assert "error" in data

    def test_fill_work_plan_whitespace_activity(self, client: TestClient):
        """Test validation: activity with only whitespace"""
        response = client.post("/api/fill-work-plan", json={
            "activity": "   ",
            "theme": "Test"
        })

        assert response.status_code == 400
        data = response.json()
        assert data["error_code"] == "VALIDATION_ERROR"

    def test_fill_work_plan_activity_too_long(self, client: TestClient):
        """Test validation: activity exceeds 500 chars"""
        response = client.post("/api/fill-work-plan", json={
            "activity": "a" * 501,
            "theme": "Test"
        })

        assert response.status_code == 400  # Bad Request (per API spec)
        data = response.json()
        assert data["error_code"] == "VALIDATION_ERROR"

    def test_fill_work_plan_theme_too_long(self, client: TestClient):
        """Test validation: theme exceeds 200 chars"""
        response = client.post("/api/fill-work-plan", json={
            "activity": "Test activity",
            "theme": "a" * 201
        })

        assert response.status_code == 400  # Bad Request (per API spec)
        data = response.json()
        assert data["error_code"] == "VALIDATION_ERROR"

    def test_fill_work_plan_invalid_json(self, client: TestClient):
        """Test error handling: invalid JSON"""
        response = client.post(
            "/api/fill-work-plan",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )

        assert response.status_code == 400  # Bad Request (per API spec)

    def test_fill_work_plan_wrong_method(self, client: TestClient):
        """Test that GET is not allowed on this endpoint"""
        response = client.get("/api/fill-work-plan")

        assert response.status_code == 405  # Method Not Allowed


class TestAPIDocumentation:
    """Tests for API documentation endpoints"""

    def test_swagger_ui_available(self, client: TestClient):
        """Test that Swagger UI is available at /docs"""
        response = client.get("/docs")
        assert response.status_code == 200

    def test_redoc_available(self, client: TestClient):
        """Test that ReDoc is available at /redoc"""
        response = client.get("/redoc")
        assert response.status_code == 200


class TestResponseFormat:
    """Tests to verify response format matches specification"""

    def test_response_modules_are_uppercase(self, client: TestClient, sample_request_data):
        """Test that module names are in uppercase"""
        response = client.post("/api/fill-work-plan", json=sample_request_data)

        assert response.status_code == 200
        data = response.json()
        modules = data["modules"]

        # All modules should be uppercase (Polish educational standard)
        assert all(module.isupper() or module == module.upper() for module in modules)

    def test_curriculum_refs_format(self, client: TestClient, sample_request_data):
        """Test that curriculum refs are in expected format"""
        response = client.post("/api/fill-work-plan", json=sample_request_data)

        assert response.status_code == 200
        data = response.json()

        # Curriculum refs should be strings (e.g., "4.15", "3.8")
        for ref in data["curriculum_refs"]:
            assert isinstance(ref, str)
            assert len(ref) > 0

    def test_objectives_are_polish_text(self, client: TestClient, sample_request_data):
        """Test that objectives are non-empty strings"""
        response = client.post("/api/fill-work-plan", json=sample_request_data)

        assert response.status_code == 200
        data = response.json()

        # Objectives should be non-empty strings
        for objective in data["objectives"]:
            assert isinstance(objective, str)
            assert len(objective) > 0

    def test_error_response_format(self, client: TestClient):
        """Test that error responses have correct format"""
        response = client.post("/api/fill-work-plan", json={
            "activity": "",
            "theme": "Test"
        })

        assert response.status_code == 400
        data = response.json()

        # Error response should have error and error_code fields
        assert "error" in data
        assert "error_code" in data
        assert isinstance(data["error"], str)
        assert isinstance(data["error_code"], str)
