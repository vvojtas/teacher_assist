"""
FastAPI application entry point for AI service.

Supports two modes:
- Mock mode: Returns random data from database (for testing)
- Real mode: Uses LangGraph workflow with OpenRouter LLM

Run with:
    python ai_service/main.py

Or with uvicorn:
    uvicorn ai_service.main:app --host 127.0.0.1 --port 8001 --reload
"""

import logging
import uvicorn
import httpx
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError

from common.models import FillWorkPlanRequest, FillWorkPlanResponse, ErrorResponse
from ai_service.config import settings
from ai_service.mock_service import MockAIService
from ai_service.workflow import get_workflow
from ai_service.utils.console import log_info, log_error
from ai_service.utils.paths import get_database_path, resolve_from_project_root

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for FastAPI application.

    Handles startup and shutdown of shared resources:
    - Mock service or LangGraph workflow
    - Shared HTTP client for OpenRouter API
    - Template caching

    Replaces deprecated @app.on_event("startup") and @app.on_event("shutdown").
    """
    # === Startup ===
    log_info(f"Starting AI Service in {settings.ai_service_mode.upper()} mode")

    if settings.ai_service_mode == "mock":
        # Initialize mock service
        try:
            app.state.mock_service = MockAIService()
            log_info("Mock service initialized successfully")
        except Exception as e:
            log_error("Failed to initialize mock service", str(e))
            raise

    elif settings.ai_service_mode == "real":
        # Validate real mode configuration
        try:
            settings.validate_real_mode()
        except ValueError as e:
            log_error("Configuration error for real mode", str(e))
            raise

        # Verify database exists (use centralized path resolution)
        db_path = get_database_path(settings.ai_service_database_path)

        if not db_path.exists():
            error_msg = f"Database file not found: {db_path}"
            log_error(error_msg)
            raise FileNotFoundError(error_msg)

        # Verify prompt template exists (use centralized path resolution)
        template_dir = resolve_from_project_root(settings.ai_service_prompt_template_dir)
        template_path = template_dir / "fill_work_plan_eng.txt"
        if not template_path.exists():
            error_msg = f"Prompt template not found: {template_path}"
            log_error(error_msg)
            raise FileNotFoundError(error_msg)

        # Load and cache prompt template (Issue #5: Template file caching)
        try:
            with open(template_path, "r", encoding="utf-8") as f:
                app.state.prompt_template = f.read()
            log_info("Prompt template cached successfully")
        except Exception as e:
            log_error("Failed to cache prompt template", str(e))
            raise

        # Initialize workflow (Issue #4: Avoid race condition by initializing here)
        try:
            from ai_service.workflow import create_workflow
            app.state.workflow = create_workflow()
            log_info("LangGraph workflow initialized successfully")
        except Exception as e:
            log_error("Failed to initialize LangGraph workflow", str(e))
            raise

    else:
        raise ValueError(f"Invalid AI_SERVICE_MODE: {settings.ai_service_mode}")

    log_info("AI Service startup complete")

    yield  # Application runs here

    # === Shutdown ===
    log_info("Shutting down AI Service")


# Initialize FastAPI app with lifespan
app = FastAPI(
    title="Teacher Assist AI Service",
    description="LangGraph-based AI service for generating educational metadata",
    version="1.0.0",
    docs_url="/docs",  # Swagger UI
    redoc_url="/redoc",  # ReDoc
    lifespan=lifespan
)


@app.get("/health")
async def health_check():
    """
    Health check endpoint.

    Returns:
        dict: Service status, mode, and version
    """
    return {
        "status": "healthy",
        "mode": settings.ai_service_mode,
        "version": "1.0.0",
        "service": "Teacher Assist AI Service"
    }


@app.get("/api/mode")
async def get_mode():
    """
    Get current service mode.

    Returns:
        dict: Current mode and LLM model (if real mode)
    """
    response = {
        "mode": settings.ai_service_mode
    }

    if settings.ai_service_mode == "real":
        response["llm_model"] = settings.ai_service_llm_model

    return response


@app.post(
    "/api/fill-work-plan",
    response_model=FillWorkPlanResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Validation error"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    }
)
async def fill_work_plan(request: FillWorkPlanRequest, req: Request) -> FillWorkPlanResponse:
    """
    Generate educational metadata for a given activity.

    Dispatches to either mock service or real LangGraph workflow based on mode.

    Args:
        request: FillWorkPlanRequest with activity and optional theme
        req: FastAPI Request object (for accessing app.state)

    Returns:
        FillWorkPlanResponse: Generated metadata (module, curriculum_refs, objectives)

    Raises:
        400: Invalid request data (handled by global exception handlers)
        500: Internal server error (handled by global exception handlers)
    """
    if settings.ai_service_mode == "mock":
        # Use mock service from app state
        result = req.app.state.mock_service.generate_metadata(
            activity=request.activity,
            theme=request.theme
        )
        return result

    else:  # real mode
        # Use LangGraph workflow from app state
        try:
            # Prepare initial state (include cached template)
            initial_state = {
                "activity": request.activity,
                "theme": request.theme,
                "prompt_template": req.app.state.prompt_template  # Use cached template
            }

            # Execute workflow (async)
            final_state = await req.app.state.workflow.ainvoke(initial_state)

            # Extract final response
            final_response = final_state.get("final_response")

            if final_response is None:
                # Workflow failed to produce a response
                raise ValueError("Workflow did not produce a final response")

            # Check if response is an error
            if isinstance(final_response, ErrorResponse):
                # Return error as JSON with appropriate status code
                status_code = 500 if final_response.error_code == "INTERNAL_ERROR" else 400
                return JSONResponse(
                    status_code=status_code,
                    content=final_response.model_dump()
                )

            return final_response

        except Exception as e:
            logger.error(f"Workflow execution error: {e}", exc_info=True)
            log_error("Błąd wykonania workflow", str(e))

            return JSONResponse(
                status_code=500,
                content=ErrorResponse(
                    error="Wystąpił błąd podczas generowania metadanych",
                    error_code="INTERNAL_ERROR",
                    details={"error": str(e)}
                ).model_dump()
            )


def _create_validation_error_response(errors: list) -> JSONResponse:
    """
    Create a standardized validation error response.

    Args:
        errors: List of validation errors from Pydantic

    Returns:
        JSONResponse: Formatted error response with 400 status
    """
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
    return _create_validation_error_response(exc.errors())


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
    return _create_validation_error_response(exc.errors())


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
    # Log the exception with full traceback for debugging
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    log_error("Nieoczekiwany błąd serwera", str(exc))

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
    print(f"Mode: {settings.ai_service_mode.upper()}")
    if settings.ai_service_mode == "real":
        print(f"LLM Model: {settings.ai_service_llm_model}")
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
