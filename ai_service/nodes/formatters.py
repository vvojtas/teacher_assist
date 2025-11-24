"""
Response formatting nodes for LangGraph workflow.

Creates final API responses:
- Success response (FillWorkPlanResponse)
- Error response (ErrorResponse)
"""

from typing import Dict, Any

from common.models import FillWorkPlanResponse, ErrorResponse


def format_success(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format successful response.

    LangGraph node that creates FillWorkPlanResponse from validated LLM output.
    NOTE: Reasoning is NOT included in the response (logged only).

    Args:
        state: Workflow state containing:
            - activity: Original activity description
            - llm_parsed_output: Validated LLM output with modules, curriculum_refs, objectives

    Returns:
        Updated state with 'final_response' as FillWorkPlanResponse.
    """
    parsed = state.get("llm_parsed_output", {})
    activity = state.get("activity", "")

    response = FillWorkPlanResponse(
        activity=activity,
        modules=parsed.get("modules", []),
        curriculum_refs=parsed.get("curriculum_refs", []),
        objectives=parsed.get("objectives", [])
    )

    return {
        **state,
        "final_response": response
    }


def format_error(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format error response.

    LangGraph node that creates ErrorResponse from validation errors.

    Args:
        state: Workflow state containing:
            - validation_errors: List of error messages

    Returns:
        Updated state with 'final_response' as ErrorResponse.
    """
    errors = state.get("validation_errors", [])

    # Determine error code and message based on errors
    if any("JSON" in err or "json" in err.lower() for err in errors):
        error_code = "VALIDATION_ERROR"
        error_message = "Nie można sparsować odpowiedzi z AI. Spróbuj ponownie."
    elif any("moduł" in err.lower() for err in errors):
        error_code = "VALIDATION_ERROR"
        error_message = "Nieprawidłowe moduły edukacyjne. Spróbuj ponownie."
    elif any("podstawy programowej" in err.lower() for err in errors):
        error_code = "VALIDATION_ERROR"
        error_message = "Nieprawidłowe kody podstawy programowej. Spróbuj ponownie."
    elif any("cel" in err.lower() for err in errors):
        error_code = "VALIDATION_ERROR"
        error_message = "Nieprawidłowe cele edukacyjne. Spróbuj ponownie."
    elif any("activity" in err.lower() or "aktywność" in err.lower()):
        error_code = "VALIDATION_ERROR"
        error_message = "Nieprawidłowe dane wejściowe. Sprawdź pole aktywności."
    else:
        error_code = "INTERNAL_ERROR"
        error_message = "Wystąpił błąd podczas generowania metadanych. Spróbuj ponownie."

    response = ErrorResponse(
        error=error_message,
        error_code=error_code,
        details={"validation_errors": errors} if errors else None
    )

    return {
        **state,
        "final_response": response
    }
