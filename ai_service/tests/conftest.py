"""
Pytest configuration and fixtures for AI service tests.
"""

import os
import pytest
from fastapi.testclient import TestClient
from ai_service.main import app
from ai_service.config import get_settings


@pytest.fixture(scope="session", autouse=True)
def configure_test_environment():
    """
    Configure test environment settings.

    Sets up database path to point to project root when running tests.
    This fixture runs automatically for all tests (autouse=True).
    """
    settings = get_settings()
    # When running tests from project root, database is at ./db.sqlite3
    db_path = os.path.join(os.getcwd(), "db.sqlite3")
    if os.path.exists(db_path):
        settings.ai_service_database_path = db_path
    yield


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
