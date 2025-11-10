"""
Pydantic models for API request/response schemas.

These models are shared between:
- Django web server (webserver/)
- LangGraph AI service (ai_service/)

API specification: docs/ai_api.md
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator, ConfigDict


class FillWorkPlanRequest(BaseModel):
    """
    Request model for POST /api/fill-work-plan endpoint.

    Attributes:
        activity: Teacher's activity description (1-500 chars, required)
        theme: Weekly theme for context (0-200 chars, optional)
    """
    activity: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="Teacher's activity description in Polish"
    )
    theme: Optional[str] = Field(
        default="",
        max_length=200,
        description="Optional weekly theme for context"
    )

    @field_validator('activity')
    @classmethod
    def activity_not_empty(cls, v: str) -> str:
        """Validate that activity is not just whitespace"""
        if not v or not v.strip():
            raise ValueError('Activity cannot be empty or whitespace')
        return v.strip()

    @field_validator('theme')
    @classmethod
    def theme_strip(cls, v: Optional[str]) -> str:
        """Strip whitespace from theme"""
        if v is None:
            return ""
        return v.strip()

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "activity": "Zabawa w sklep z owocami",
                "theme": "Jesień - zbiory"
            }
        }
    )


class FillWorkPlanResponse(BaseModel):
    """
    Response model for POST /api/fill-work-plan endpoint.

    Attributes:
        activity: Activity description (echoed from request)
        module: Educational module name (Polish, uppercase)
        curriculum_refs: Podstawa Programowa reference codes (1-10 items)
        objectives: Learning objectives in Polish (typically 2-3)
    """
    activity: str = Field(
        ...,
        description="Activity description echoed from request"
    )
    module: str = Field(
        ...,
        description="Educational module name (e.g., 'MATEMATYKA')"
    )
    curriculum_refs: List[str] = Field(
        ...,
        min_length=1,
        max_length=10,
        description="Curriculum reference codes (e.g., ['4.15', '4.18'])"
    )
    objectives: List[str] = Field(
        ...,
        min_length=1,
        max_length=10,
        description="Learning objectives in Polish"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "activity": "Zabawa w sklep z owocami",
                "module": "MATEMATYKA",
                "curriculum_refs": ["4.15", "4.18"],
                "objectives": [
                    "Dziecko potrafi przeliczać w zakresie 5",
                    "Rozpoznaje poznane wcześniej cyfry"
                ]
            }
        }
    )


class ErrorResponse(BaseModel):
    """
    Error response model for all API endpoints.

    Attributes:
        error: Human-readable error message in Polish
        error_code: Machine-readable error code
        details: Optional additional error details
    """
    error: str = Field(
        ...,
        description="Human-readable error message"
    )
    error_code: str = Field(
        ...,
        description="Machine-readable error code (e.g., 'VALIDATION_ERROR')"
    )
    details: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Optional additional error details"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "error": "Activity field cannot be empty",
                "error_code": "VALIDATION_ERROR",
                "details": {
                    "field": "activity",
                    "reason": "Field length must be between 1-500 characters"
                }
            }
        }
    )
