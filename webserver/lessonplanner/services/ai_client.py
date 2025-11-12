"""
AI client service for communicating with the LangGraph AI service.

This module handles HTTP communication between Django and the AI service.
"""

import os
import requests
import logging
from pydantic import ValidationError

from common.models import FillWorkPlanRequest, FillWorkPlanResponse

# Configure logger
logger = logging.getLogger(__name__)

# AI Service configuration (configurable via environment variables)
AI_SERVICE_URL = os.getenv('AI_SERVICE_URL', 'http://localhost:8001')
AI_SERVICE_TIMEOUT = int(os.getenv('AI_SERVICE_TIMEOUT', '120'))  # seconds


def fill_work_plan(activity: str, theme: str = "") -> dict:
    """
    Call AI service to generate metadata for a lesson activity.

    This function makes HTTP requests to the LangGraph AI service running on port 8001.
    Uses Pydantic models from common package for request/response validation.

    Args:
        activity (str): The activity description (required, 1-500 chars)
        theme (str): Optional weekly theme context (max 200 chars)

    Returns:
        dict: Generated metadata with module, curriculum_refs, and objectives
            {
                "module": "MATEMATYKA",
                "curriculum_refs": ["4.15", "4.18"],
                "objectives": ["Objective 1", "Objective 2"]
            }

    Raises:
        ValueError: If activity is empty or invalid
        ConnectionError: If cannot connect to AI service
        TimeoutError: If request exceeds timeout
        Exception: For other unexpected errors

    API Specification: docs/ai_api.md
    """
    try:
        # Validate and prepare request using Pydantic model
        request_data = FillWorkPlanRequest(
            activity=activity,
            theme=theme
        )

        # Convert to dict for JSON serialization
        payload = request_data.model_dump()

    except ValidationError as e:
        # Pydantic validation failed
        errors = e.errors()
        first_error = errors[0] if errors else {}
        error_msg = first_error.get("msg", "Invalid input")
        logger.warning(f"Request validation error: {error_msg}")
        raise ValueError(error_msg)

    try:
        # Make POST request to AI service
        logger.info(f"Calling AI service: POST {AI_SERVICE_URL}/api/fill-work-plan")
        response = requests.post(
            f"{AI_SERVICE_URL}/api/fill-work-plan",
            json=payload,
            timeout=AI_SERVICE_TIMEOUT,
            headers={"Content-Type": "application/json"}
        )

        # Handle error responses
        if response.status_code == 400:
            # Validation error from AI service
            error_data = response.json()
            error_msg = error_data.get("error", "Nieprawidłowe dane wejściowe")
            logger.warning(f"AI service validation error: {error_msg}")
            raise ValueError(error_msg)

        elif response.status_code == 503:
            # Service unavailable
            logger.error("AI service unavailable")
            raise ConnectionError("Nie można połączyć z usługą AI. Wypełnij dane ręcznie.")

        elif response.status_code == 504:
            # Timeout
            logger.error("AI service timeout")
            raise TimeoutError("Żądanie przekroczyło limit czasu. Spróbuj ponownie.")

        elif response.status_code != 200:
            # Other error
            logger.error(f"AI service error: HTTP {response.status_code}")
            raise Exception(f"AI service returned error: {response.status_code}")

        # Parse and validate response using Pydantic model
        response_data = FillWorkPlanResponse(**response.json())

        # Return only the required fields (not the echoed activity)
        return {
            "module": response_data.module,
            "curriculum_refs": response_data.curriculum_refs,
            "objectives": response_data.objectives
        }

    except ValidationError as e:
        # Response validation failed
        logger.error(f"AI service returned invalid response format: {e}")
        raise Exception("Nieprawidłowa odpowiedź z usługi AI")

    except requests.exceptions.Timeout:
        logger.error("AI service request timeout")
        raise TimeoutError("Żądanie przekroczyło limit czasu. Spróbuj ponownie.")

    except requests.exceptions.ConnectionError as e:
        logger.error(f"Cannot connect to AI service: {e}")
        raise ConnectionError("Nie można połączyć z usługą AI. Wypełnij dane ręcznie.")

    except requests.exceptions.RequestException as e:
        logger.error(f"AI service request failed: {e}")
        raise Exception(f"Błąd komunikacji z usługą AI: {str(e)}")
