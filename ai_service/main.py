"""
FastAPI application entry point for AI service.

Run with:
    python ai_service/main.py

Or with uvicorn:
    uvicorn ai_service.main:app --host 0.0.0.0 --port 8001 --reload
"""

import sys
import os
from pathlib import Path

# Add project root to Python path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError

from common.models import FillWorkPlanRequest, FillWorkPlanResponse, ErrorResponse
from ai_service.mock_service import MockAIService


# Initialize FastAPI app
app = FastAPI(
    title="Teacher Assist AI Service",
    description="LangGraph-based AI service for generating educational metadata",
    version="1.0.0",
    docs_url="/docs",  # Swagger UI
    redoc_url="/redoc",  # ReDoc
)

# Initialize mock AI service
ai_service = MockAIService()


@app.get("/health")
async def health_check():
    """
    Health check endpoint.

    Returns:
        dict: Service status and version
    """
    return {
        "status": "healthy",
        "version": "1.0.0",
        "service": "Teacher Assist AI Service"
    }


@app.post(
    "/api/fill-work-plan",
    response_model=FillWorkPlanResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Validation error"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    }
)
async def fill_work_plan(request: FillWorkPlanRequest) -> FillWorkPlanResponse:
    """
    Generate educational metadata for a given activity.

    Args:
        request: FillWorkPlanRequest with activity and optional theme

    Returns:
        FillWorkPlanResponse: Generated metadata (module, curriculum_refs, objectives)

    Raises:
        400: Invalid request data (handled by global exception handlers)
        500: Internal server error (handled by global exception handlers)
    """
    # Call mock AI service to generate metadata
    # Exceptions propagate to global handlers
    result = ai_service.generate_metadata(
        activity=request.activity,
        theme=request.theme
    )
    return result


@app.exception_handler(RequestValidationError)
async def request_validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Handle FastAPI request validation errors.

    Args:
        request: FastAPI request
        exc: FastAPI RequestValidationError

    Returns:
        JSONResponse: Error response with validation details (400 Bad Request per API spec)
    """
    errors = exc.errors()
    first_error = errors[0] if errors else {}

    # Extract field name and error message
    field_loc = first_error.get("loc", ["unknown"])
    field_name = field_loc[-1] if field_loc else "unknown"
    error_msg = first_error.get("msg", "Unknown validation error")

    return JSONResponse(
        status_code=400,  # Return 400 per API spec (not default 422)
        content=ErrorResponse(
            error="Nieprawidłowe dane wejściowe",
            error_code="VALIDATION_ERROR",
            details={
                "field": field_name,
                "reason": error_msg
            }
        ).model_dump()
    )


@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    """
    Handle Pydantic validation errors.

    Args:
        request: FastAPI request
        exc: Pydantic ValidationError

    Returns:
        JSONResponse: Error response with validation details (400 Bad Request per API spec)
    """
    errors = exc.errors()
    first_error = errors[0] if errors else {}

    # Extract field name and error message
    field_loc = first_error.get("loc", ["unknown"])
    field_name = field_loc[-1] if field_loc else "unknown"
    error_msg = first_error.get("msg", "Unknown validation error")

    return JSONResponse(
        status_code=400,  # Return 400 per API spec (not default 422)
        content=ErrorResponse(
            error="Nieprawidłowe dane wejściowe",
            error_code="VALIDATION_ERROR",
            details={
                "field": field_name,
                "reason": error_msg
            }
        ).model_dump()
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """
    Handle unexpected exceptions.

    Args:
        request: FastAPI request
        exc: Exception

    Returns:
        JSONResponse: Generic error response
    """
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="Wystąpił nieoczekiwany błąd serwera",
            error_code="INTERNAL_ERROR"
        ).model_dump()
    )


def main():
    """
    Start the FastAPI server.
    """
    print("=" * 60)
    print("Teacher Assist - AI Service")
    print("=" * 60)
    print(f"Starting server on http://localhost:8001")
    print(f"API documentation: http://localhost:8001/docs")
    print(f"Health check: http://localhost:8001/health")
    print("=" * 60)

    uvicorn.run(
        "ai_service.main:app",
        host="127.0.0.1",  # localhost-only for security
        port=8001,
        reload=True,  # Enable auto-reload during development
        log_level="info"
    )


if __name__ == "__main__":
    main()
