"""
Pytest configuration and fixtures for AI service tests.
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import pytest
from fastapi.testclient import TestClient
from ai_service.main import app


@pytest.fixture
def client():
    """
    Create a test client for the FastAPI app.

    Returns:
        TestClient: FastAPI test client
    """
    return TestClient(app)


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
