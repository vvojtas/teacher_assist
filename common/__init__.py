"""
Common package for shared data models between Django and AI service.
"""

from .models import FillWorkPlanRequest, FillWorkPlanResponse, ErrorResponse

__all__ = [
    'FillWorkPlanRequest',
    'FillWorkPlanResponse',
    'ErrorResponse',
]
