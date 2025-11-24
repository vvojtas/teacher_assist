"""
Validation nodes for LangGraph workflow.

Includes:
- Input validation (activity, theme)
- Output validation (JSON structure, modules, curriculum refs, objectives)
- Lenient validation with filtering of invalid codes
"""

from typing import Dict, Any, List, Set
import json

from ai_service.utils.console import log_warning, log_error
from ai_service.constants import (
    MAX_ACTIVITY_LENGTH,
    MAX_THEME_LENGTH,
    MAX_MODULES,
    MAX_CURRICULUM_REFS,
    MAX_OBJECTIVES,
    MIN_OBJECTIVE_LENGTH
)


def validate_input(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate input activity and theme.

    LangGraph node that validates and sanitizes input data.

    Args:
        state: Workflow state containing 'activity' and 'theme'.

    Returns:
        Updated state with sanitized inputs and validation_errors if any.
    """
    activity = state.get("activity", "").strip()
    theme = state.get("theme", "").strip()
    errors = []

    # Validate activity (required)
    if not activity:
        errors.append("Pole 'activity' nie może być puste")
    elif len(activity) > MAX_ACTIVITY_LENGTH:
        errors.append(f"Pole 'activity' jest za długie ({len(activity)} znaków, max {MAX_ACTIVITY_LENGTH})")

    # Validate theme (optional)
    if theme and len(theme) > MAX_THEME_LENGTH:
        errors.append(f"Pole 'theme' jest za długie ({len(theme)} znaków, max {MAX_THEME_LENGTH})")

    if errors:
        log_error("Błąd walidacji danych wejściowych", "\n".join(errors))

    return {
        **state,
        "activity": activity,
        "theme": theme,
        "validation_errors": errors,
        "validation_passed": len(errors) == 0
    }


def validate_output(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate LLM output with lenient mode for curriculum references.

    LangGraph node that validates the parsed LLM output against business rules.
    Uses LENIENT mode: filters out invalid curriculum codes but keeps valid ones.

    Validation rules:
    1. JSON structure: Check all required fields present
    2. Modules: Verify against available_modules list (1-3 items)
    3. Curriculum refs: Check codes exist in DB, filter invalid (min 1 required)
    4. Objectives: Check 1-5 items, each ≥10 characters

    Args:
        state: Workflow state containing:
            - llm_parsed_output: Parsed JSON from LLM
            - available_modules: List of valid module names
            - curriculum_refs: List of valid curriculum reference codes

    Returns:
        Updated state with:
            - validation_passed: bool
            - validation_errors: list of error messages
            - llm_parsed_output: Updated with filtered curriculum_refs if needed
    """
    parsed_output = state.get("llm_parsed_output", {})
    available_modules_data = state.get("available_modules", [])
    curriculum_refs_data = state.get("curriculum_refs", [])

    errors = []

    # Extract valid module names and curriculum codes
    valid_modules: Set[str] = {m['module_name'] for m in available_modules_data}
    valid_curriculum_codes: Set[str] = {ref['reference_code'] for ref in curriculum_refs_data}

    # 1. Validate JSON structure
    required_fields = ["modules", "curriculum_refs", "objectives"]
    for field in required_fields:
        if field not in parsed_output:
            errors.append(f"Brak wymaganego pola: {field}")

    if errors:
        log_error("Błąd struktury JSON", "\n".join(errors))
        return {
            **state,
            "validation_passed": False,
            "validation_errors": errors
        }

    # 2. Validate modules
    modules = parsed_output.get("modules", [])

    if not isinstance(modules, list):
        errors.append("Pole 'modules' musi być listą")
    elif len(modules) == 0:
        errors.append("Wymagany co najmniej 1 moduł")
    elif len(modules) > MAX_MODULES:
        errors.append(f"Zbyt wiele modułów ({len(modules)}, max {MAX_MODULES})")
    else:
        # Check if modules exist in database
        invalid_modules = [m for m in modules if m not in valid_modules]
        if invalid_modules:
            errors.append(f"Nieprawidłowe moduły: {', '.join(invalid_modules)}")

    # 3. Validate curriculum references (LENIENT MODE)
    curriculum_refs = parsed_output.get("curriculum_refs", [])

    if not isinstance(curriculum_refs, list):
        errors.append("Pole 'curriculum_refs' musi być listą")
    elif len(curriculum_refs) == 0:
        errors.append("Wymagany co najmniej 1 kod podstawy programowej")
    else:
        # LENIENT MODE: Filter out invalid codes
        valid_refs = []
        invalid_refs = []

        for ref in curriculum_refs:
            if ref in valid_curriculum_codes:
                valid_refs.append(ref)
            else:
                invalid_refs.append(ref)

        # Log warning if any codes were filtered
        if invalid_refs:
            warning_msg = f"Odfiltrowano nieprawidłowe kody podstawy programowej: {', '.join(invalid_refs)}"
            log_warning(warning_msg)

        # Check if at least 1 valid code remains
        if len(valid_refs) == 0:
            errors.append(
                f"Wszystkie kody podstawy programowej są nieprawidłowe: {', '.join(invalid_refs)}"
            )
        elif len(valid_refs) > MAX_CURRICULUM_REFS:
            errors.append(f"Zbyt wiele kodów podstawy programowej ({len(valid_refs)}, max {MAX_CURRICULUM_REFS})")

        # Update parsed output with filtered refs
        if invalid_refs and valid_refs:
            parsed_output["curriculum_refs"] = valid_refs

    # 4. Validate objectives
    objectives = parsed_output.get("objectives", [])

    if not isinstance(objectives, list):
        errors.append("Pole 'objectives' musi być listą")
    elif len(objectives) == 0:
        errors.append("Wymagany co najmniej 1 cel edukacyjny")
    elif len(objectives) > MAX_OBJECTIVES:
        errors.append(f"Zbyt wiele celów edukacyjnych ({len(objectives)}, max {MAX_OBJECTIVES})")
    else:
        # Check each objective
        for i, obj in enumerate(objectives, 1):
            if not isinstance(obj, str):
                errors.append(f"Cel {i} musi być tekstem")
            elif len(obj.strip()) < MIN_OBJECTIVE_LENGTH:
                errors.append(f"Cel {i} jest za krótki (min {MIN_OBJECTIVE_LENGTH} znaków)")

    # Log errors if any
    if errors:
        log_error("Błąd walidacji odpowiedzi LLM", "\n".join(errors))

    return {
        **state,
        "llm_parsed_output": parsed_output,
        "validation_passed": len(errors) == 0,
        "validation_errors": errors
    }


def parse_llm_response(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parse LLM raw response into structured data.

    Extracts JSON from response and parses it.
    Handles cases where LLM includes markdown code blocks.

    Args:
        state: Workflow state containing 'llm_raw_response'.

    Returns:
        Updated state with 'llm_parsed_output'.
    """
    raw_response = state.get("llm_raw_response", "")

    try:
        # Try direct JSON parse first
        parsed = json.loads(raw_response)

    except json.JSONDecodeError:
        # Try extracting JSON from markdown code block
        if "```json" in raw_response:
            # Extract content between ```json and ```
            start = raw_response.find("```json") + 7
            end = raw_response.find("```", start)
            json_str = raw_response[start:end].strip()

            try:
                parsed = json.loads(json_str)
            except json.JSONDecodeError as e:
                error_msg = f"Błąd parsowania JSON: {str(e)}"
                log_error("Błąd parsowania JSON", str(e))
                return {
                    **state,
                    "llm_parsed_output": {},
                    "validation_passed": False,
                    "validation_errors": state.get("validation_errors", []) + [error_msg]
                }
        else:
            error_msg = "Odpowiedź nie jest prawidłowym JSON"
            log_error("Błąd parsowania JSON", "Brak znacznika ```json w odpowiedzi")
            return {
                **state,
                "llm_parsed_output": {},
                "validation_passed": False,
                "validation_errors": state.get("validation_errors", []) + [error_msg]
            }

    return {
        **state,
        "llm_parsed_output": parsed,
    }
