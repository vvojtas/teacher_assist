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
    Format error response with detailed, actionable error messages.

    LangGraph node that creates ErrorResponse from validation errors.
    Provides specific error codes and user-friendly messages with guidance.

    Args:
        state: Workflow state containing:
            - validation_errors: List of error messages

    Returns:
        Updated state with 'final_response' as ErrorResponse.
    """
    errors = state.get("validation_errors", [])

    # Determine error code and message based on errors
    # Provide specific, actionable error messages with guidance
    if any("JSON" in err or "json" in err.lower() for err in errors):
        error_code = "PARSING_ERROR"
        error_message = (
            "Nie udało się przetworzyć odpowiedzi AI. "
            "Odpowiedź nie zawiera prawidłowego formatu JSON. "
            "Spróbuj ponownie z innym opisem aktywności."
        )
    elif any("moduł" in err.lower() for err in errors):
        error_code = "INVALID_MODULES"
        # Include specific module errors if available
        module_errors = [e for e in errors if "moduł" in e.lower()]
        error_message = (
            f"AI wygenerował nieprawidłowe moduły edukacyjne. "
            f"{module_errors[0] if module_errors else 'Sprawdź listę dostępnych modułów.'} "
            f"Spróbuj ponownie lub zmień opis aktywności."
        )
    elif any("podstawy programowej" in err.lower() for err in errors):
        error_code = "INVALID_CURRICULUM_REFS"
        error_message = (
            "AI wygenerował nieprawidłowe kody podstawy programowej. "
            "Wszystkie kody zostały odfiltrowane jako nieprawidłowe. "
            "Spróbuj ponownie z bardziej szczegółowym opisem aktywności."
        )
    elif any("cel" in err.lower() for err in errors):
        error_code = "INVALID_OBJECTIVES"
        # Get first objective error for more specific feedback
        objective_errors = [e for e in errors if "cel" in e.lower()]
        error_message = (
            f"AI wygenerował nieprawidłowe cele edukacyjne. "
            f"{objective_errors[0] if objective_errors else ''} "
            f"Spróbuj ponownie."
        )
    elif any("activity" in err.lower() or "aktywność" in err.lower() for err in errors):
        error_code = "INVALID_INPUT"
        # Get specific input error
        input_errors = [e for e in errors if "activity" in e.lower() or "aktywność" in e.lower()]
        error_message = (
            f"Nieprawidłowe dane wejściowe. "
            f"{input_errors[0] if input_errors else 'Sprawdź pole aktywności.'}"
        )
    elif any("theme" in err.lower() or "temat" in err.lower() for err in errors):
        error_code = "INVALID_INPUT"
        # Get specific theme error
        theme_errors = [e for e in errors if "theme" in e.lower() or "temat" in e.lower()]
        error_message = (
            f"Nieprawidłowe dane wejściowe. "
            f"{theme_errors[0] if theme_errors else 'Sprawdź pole tematu.'}"
        )
    elif any("szablon" in err.lower() or "template" in err.lower() for err in errors):
        error_code = "TEMPLATE_ERROR"
        error_message = (
            "Błąd wczytania szablonu promptu. "
            "Skontaktuj się z administratorem systemu."
        )
    elif any("llm" in err.lower() or "api" in err.lower() for err in errors):
        error_code = "LLM_ERROR"
        error_message = (
            "Błąd komunikacji z systemem AI. "
            "Sprawdź połączenie internetowe i spróbuj ponownie za chwilę."
        )
    else:
        error_code = "INTERNAL_ERROR"
        # Include first error if available for debugging
        first_error = errors[0] if errors else "Nieznany błąd"
        error_message = (
            f"Wystąpił nieoczekiwany błąd podczas generowania metadanych. "
            f"Szczegóły: {first_error}"
        )

    response = ErrorResponse(
        error=error_message,
        error_code=error_code,
        details={"validation_errors": errors} if errors else None
    )

    return {
        **state,
        "final_response": response
    }
