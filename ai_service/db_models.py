"""
Database entity models for AI service.

These Pydantic models represent database tables and are used for
type-safe data access from the SQLite database.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class MajorCurriculumReference(BaseModel):
    """
    Major sections of Polish kindergarten curriculum (Podstawa Programowa).
    Examples: "1", "2", "3", "4" representing top-level curriculum areas.
    """
    id: int
    reference_code: str = Field(..., description="Major section code (e.g., '4', '3')")
    full_text: str = Field(..., description="Complete Polish text for major section")
    created_at: datetime

    class Config:
        from_attributes = True


class CurriculumReference(BaseModel):
    """
    Detailed Polish kindergarten curriculum paragraph references.
    Examples: "4.15", "3.8", "2.5"
    """
    id: int
    reference_code: str = Field(..., description="Curriculum code (e.g., '4.15', '2.5')")
    full_text: str = Field(..., description="Complete Polish curriculum requirement text")
    major_reference_id: int = Field(..., description="Parent major curriculum section ID")
    created_at: datetime

    class Config:
        from_attributes = True


class EducationalModule(BaseModel):
    """
    Educational module categories.
    Examples: MATEMATYKA, JĘZYK, MOTORYKA DUŻA
    """
    id: int
    module_name: str = Field(..., description="Module name in Polish (e.g., 'MATEMATYKA')")
    is_ai_suggested: bool = Field(default=False, description="TRUE if AI-suggested")
    created_at: datetime

    class Config:
        from_attributes = True


class WorkPlan(BaseModel):
    """
    Weekly lesson plans with their themes.
    """
    id: int
    theme: Optional[str] = Field(None, description="Weekly theme (e.g., 'Jesień - zbiory')")
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class WorkPlanEntry(BaseModel):
    """
    Individual activity rows within a work plan.
    Marked as examples can be used for LLM training.
    """
    id: int
    work_plan_id: int
    module: Optional[str] = Field(None, description="Educational module name")
    objectives: Optional[str] = Field(None, description="Educational objectives")
    activity: str = Field(..., description="Activity description")
    is_example: bool = Field(default=False, description="TRUE if LLM training example")
    created_at: datetime

    class Config:
        from_attributes = True


class WorkPlanEntryWithRefs(WorkPlanEntry):
    """
    Extended WorkPlanEntry with curriculum references included.
    Used for retrieving example entries with all their data.
    """
    curriculum_refs: list[str] = Field(default_factory=list, description="List of curriculum reference codes")
    theme: Optional[str] = Field(None, description="Work plan theme for context")

    class Config:
        from_attributes = True
