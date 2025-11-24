"""
Data loading nodes for LangGraph workflow.

Parallel loaders for:
- Educational modules from database
- Curriculum references from database
- LLM training examples from database
- Prompt template from file
"""

from typing import Dict, Any, List
from pathlib import Path

from ai_service.db_client import get_db_client
from ai_service.config import settings
from ai_service.utils.console import log_error


def load_modules(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Load educational modules from database.

    LangGraph node that queries the educational_modules table.

    Args:
        state: Workflow state.

    Returns:
        Updated state with 'available_modules' list.
    """
    try:
        db_client = get_db_client(settings.ai_service_database_path)
        modules = db_client.get_educational_modules()

        # Convert Pydantic models to dicts
        modules_data: List[Dict[str, Any]] = [{"module_name": m.module_name} for m in modules]

        # Only return the key this node is responsible for (parallel execution)
        return {
            "available_modules": modules_data
        }

    except Exception as e:
        error_msg = f"Błąd podczas ładowania modułów z bazy danych: {str(e)}"
        log_error("Błąd ładowania modułów", str(e))
        # In error case, return validation fields to propagate error
        # validation_errors uses operator.add reducer, so just return list
        return {
            "available_modules": [],
            "validation_errors": [error_msg],
        }


def load_curriculum_refs(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Load curriculum references from database.

    LangGraph node that queries both curriculum_references and
    major_curriculum_references tables.

    Args:
        state: Workflow state.

    Returns:
        Updated state with:
            - 'curriculum_refs': List of detailed curriculum references
            - 'major_curriculum_refs': List of major curriculum sections
    """
    try:
        db_client = get_db_client(settings.ai_service_database_path)

        # Load detailed curriculum references
        curriculum_refs = db_client.get_curriculum_references()
        curriculum_refs_data: List[Dict[str, Any]] = [
            {
                "reference_code": ref.reference_code,
                "full_text": ref.full_text,
                "major_reference_id": ref.major_reference_id
            }
            for ref in curriculum_refs
        ]

        # Load major curriculum sections
        major_refs = db_client.get_major_curriculum_references()
        major_refs_data: List[Dict[str, Any]] = [
            {
                "id": ref.id,
                "reference_code": ref.reference_code,
                "full_text": ref.full_text
            }
            for ref in major_refs
        ]

        # Only return the keys this node is responsible for (parallel execution)
        return {
            "curriculum_refs": curriculum_refs_data,
            "major_curriculum_refs": major_refs_data
        }

    except Exception as e:
        error_msg = f"Błąd podczas ładowania podstawy programowej z bazy danych: {str(e)}"
        log_error("Błąd ładowania podstawy programowej", str(e))
        # In error case, return validation fields to propagate error
        return {
            "curriculum_refs": [],
            "major_curriculum_refs": [],
            "validation_errors": [error_msg],
        }


def load_examples(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Load LLM training examples from database.

    LangGraph node that queries work_plan_entries where is_example=true.

    Args:
        state: Workflow state.

    Returns:
        Updated state with 'example_entries' list.
    """
    try:
        db_client = get_db_client(settings.ai_service_database_path)
        examples = db_client.get_llm_examples()

        # Convert Pydantic models to dicts
        examples_data: List[Dict[str, Any]] = [
            {
                "theme": ex.theme,
                "activity": ex.activity,
                "modules": ex.modules,
                "objectives": ex.objectives,
                "curriculum_references": ex.curriculum_references
            }
            for ex in examples
        ]

        # Only return the key this node is responsible for (parallel execution)
        return {
            "example_entries": examples_data
        }

    except Exception as e:
        error_msg = f"Błąd podczas ładowania przykładów z bazy danych: {str(e)}"
        log_error("Błąd ładowania przykładów", str(e))
        # In error case, return validation fields to propagate error
        return {
            "example_entries": [],
            "validation_errors": [error_msg],
        }


def load_prompt_template(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Load prompt template from file.

    LangGraph node that reads the fill_work_plan.txt template file.
    Skips loading if template is already cached in state (performance optimization).

    Args:
        state: Workflow state.

    Returns:
        Updated state with 'prompt_template' string.
    """
    # Check if template is already cached in state (from startup)
    if state.get("prompt_template"):
        # Template already loaded, return unchanged state
        return state

    try:
        # Construct template path
        template_path = Path(settings.ai_service_prompt_template_dir) / "fill_work_plan.txt"

        if not template_path.exists():
            error_msg = f"Plik szablonu nie istnieje: {template_path}"
            log_error("Błąd ładowania szablonu", error_msg)
            # In error case, return validation fields to propagate error
            return {
                "prompt_template": "",
                "validation_errors": [error_msg],
                "validation_passed": False
            }

        # Read template file
        with open(template_path, "r", encoding="utf-8") as f:
            template: str = f.read()

        # Only return the key this node is responsible for (parallel execution)
        return {
            "prompt_template": template
        }

    except Exception as e:
        error_msg = f"Błąd podczas ładowania szablonu promptu: {str(e)}"
        log_error("Błąd ładowania szablonu", str(e))
        # In error case, return validation fields to propagate error
        return {
            "prompt_template": "",
            "validation_errors": [error_msg],
        }
