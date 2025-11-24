"""
Schema utilities for LLM input/output structure.

Defines the expected structure for LLM-generated JSON responses.
This ensures consistency between:
- Example formatting (training data)
- Response validation
- Response parsing
"""

from typing import List, Dict, Any, TypedDict


class LLMOutputSchema(TypedDict):
    """
    Expected structure of LLM JSON output.

    This matches the fields that the LLM generates (excludes 'activity'
    which is echoed from input in the final API response).
    """
    modules: List[str]
    curriculum_refs: List[str]
    objectives: List[str]


# Field names that the LLM must generate
LLM_REQUIRED_FIELDS = ["modules", "curriculum_refs", "objectives"]


def create_llm_output_json(
    modules: List[str],
    curriculum_refs: List[str],
    objectives: List[str]
) -> Dict[str, Any]:
    """
    Create LLM output JSON with the correct structure.

    Use this function when formatting examples or constructing expected output
    to ensure consistency with the schema.

    Args:
        modules: List of educational module names
        curriculum_refs: List of curriculum reference codes
        objectives: List of learning objectives

    Returns:
        Dictionary with the expected LLM output structure
    """
    return {
        "modules": modules,
        "curriculum_refs": curriculum_refs,
        "objectives": objectives
    }
