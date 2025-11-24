"""
Pytest configuration and fixtures for AI service tests.
"""

import pytest
from fastapi.testclient import TestClient
from ai_service.main import app


@pytest.fixture
def client():
    """
    Create a test client for the FastAPI app.

    Uses context manager to properly trigger startup/shutdown events.

    Returns:
        TestClient: FastAPI test client
    """
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def sample_request_data():
    """
    Sample valid request data for testing.

    Returns:
        dict: Valid request payload
    """
    return {
        "activity": "Zabawa w sklep z owocami",
        "theme": "Jesień - zbiory"
    }


@pytest.fixture
def sample_request_minimal():
    """
    Minimal valid request (activity only, no theme).

    Returns:
        dict: Minimal valid request payload
    """
    return {
        "activity": "Test activity"
    }
