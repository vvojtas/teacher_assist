"""
Database entity models for AI service.

Simple Pydantic models for type-safe data access from SQLite database.
Only includes fields needed by the AI service.
"""

from typing import List
from pydantic import BaseModel, Field


class EducationalModule(BaseModel):
    """Educational module name (e.g., MATEMATYKA, JĘZYK)."""
    module_name: str


class CurriculumReference(BaseModel):
    """Detailed curriculum paragraph reference (e.g., 4.15, 3.8)."""
    reference_code: str
    full_text: str
    major_reference_id: int


class MajorCurriculumReference(BaseModel):
    """Major curriculum section (e.g., 1, 2, 3, 4)."""
    id: int
    reference_code: str
    full_text: str


class LLMExample(BaseModel):
    """
    Example work plan entry for LLM training context.
    Contains a complete activity with all metadata.
    """
    theme: str = Field(..., description="Weekly theme (e.g., 'Jesień - zbiory')")
    activity: str = Field(..., description="Activity description")
    module: str = Field(..., description="Educational module (e.g., 'MATEMATYKA')")
    objectives: str = Field(..., description="Educational objectives")
    curriculum_references: List[str] = Field(
        default_factory=list,
        description="List of curriculum reference codes (e.g., ['4.15', '4.18'])"
    )
