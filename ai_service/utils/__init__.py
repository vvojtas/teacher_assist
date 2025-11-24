"""
Utility modules for AI Service.

Includes:
- console: Colored console output
- cost_tracker: Token counting and cost calculation
- response_schema: LLM response TypedDict
- formatters: Data formatting helpers
"""

from .console import log_prompt, log_response, log_cost, log_error, log_warning
from .response_schema import LLMResponse
from .formatters import format_curriculum_refs, format_modules_list, format_examples

__all__ = [
    "log_prompt",
    "log_response",
    "log_cost",
    "log_error",
    "log_warning",
    "LLMResponse",
    "format_curriculum_refs",
    "format_modules_list",
    "format_examples",
]
