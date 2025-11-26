"""
Prompt construction node for LangGraph workflow.

Builds the final LLM prompt by replacing placeholders in the template
with formatted data from the database.
"""

from typing import Dict, Any, List

from ai_service.utils.formatters import (
    format_curriculum_refs,
    format_modules_list,
    format_examples
)
from ai_service.utils.console import log_error


def construct_prompt(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Construct the final LLM prompt from template and data.

    LangGraph node that:
    1. Formats all data (modules, curriculum refs, examples)
    2. Replaces placeholders in template
    3. Returns constructed prompt

    Template placeholders:
    - {activity}: User-provided activity description
    - {theme}: Optional weekly theme
    - {modules_list}: Comma-separated list of available modules
    - {curriculum_refs}: Formatted curriculum references grouped by major area
    - {examples}: Formatted training examples

    Args:
        state: Workflow state containing:
            - prompt_template: Template string with placeholders
            - activity: Activity description
            - theme: Weekly theme (optional)
            - available_modules: List of module dicts
            - curriculum_refs: List of curriculum reference dicts
            - major_curriculum_refs: List of major curriculum section dicts
            - example_entries: List of example entry dicts

    Returns:
        Updated state with 'constructed_prompt' string.
    """
    try:
        # Extract data from state
        template: str = state.get("prompt_template", "")
        activity: str = state.get("activity", "")
        theme: str = state.get("theme", "")
        modules_data: List[Dict[str, Any]] = state.get("available_modules", [])
        curriculum_refs_data: List[Dict[str, Any]] = state.get("curriculum_refs", [])
        major_refs_data: List[Dict[str, Any]] = state.get("major_curriculum_refs", [])
        examples_data: List[Dict[str, Any]] = state.get("example_entries", [])

        # Format data for prompt
        modules_list: str = format_modules_list(modules_data)
        curriculum_refs: str = format_curriculum_refs(major_refs_data, curriculum_refs_data)
        examples: str = format_examples(examples_data)

        # Replace placeholders in template
        prompt: str = template.format(
            activity=activity,
            theme=theme or "(brak tematu)",
            modules_list=modules_list,
            curriculum_refs=curriculum_refs,
            examples=examples
        )

        return {
            **state,
            "constructed_prompt": prompt
        }

    except KeyError as e:
        error_msg = f"Brak wymaganego pola w szablonie: {str(e)}"
        log_error("Prompt construction error", f"Missing required field in template: {str(e)}")
        return {
            **state,
            "constructed_prompt": "",
            "validation_errors": state.get("validation_errors", []) + [error_msg],
            "validation_passed": False
        }

    except Exception as e:
        error_msg = f"Nieoczekiwany błąd podczas konstruowania promptu: {str(e)}"
        log_error("Prompt construction error", f"Unexpected error: {str(e)}")
        return {
            **state,
            "constructed_prompt": "",
            "validation_errors": state.get("validation_errors", []) + [error_msg],
            "validation_passed": False
        }
