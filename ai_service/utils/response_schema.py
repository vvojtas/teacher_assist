"""
LLM response schema definition.

Defines the expected JSON structure from the LLM using TypedDict.
This enforces the response format and provides documentation.
"""

from typing import TypedDict, List


class LLMResponse(TypedDict):
    """
    Expected JSON structure from LLM.

    The LLM must return a JSON object with these exact fields.
    All text fields should be in Polish.

    Example JSON response:
    ```json
    {
        "modules": ["MATEMATYKA"],
        "curriculum_refs": ["4.15", "4.18"],
        "objectives": [
            "Dziecko potrafi przeliczać w zakresie 5",
            "Rozpoznaje poznane wcześniej cyfry"
        ]
    }
    ```

    Fields:
        modules: List of 1-3 educational module names (uppercase Polish).
                 Must match modules from the database.
        curriculum_refs: List of 2-3 curriculum reference codes (e.g., "4.15").
                        Must be valid codes from the database.
        objectives: List of 2-3 educational objectives (Polish text).
                   Each objective should be specific and actionable.
    """

    modules: List[str]
    curriculum_refs: List[str]
    objectives: List[str]


# Example valid LLM response for documentation
EXAMPLE_LLM_RESPONSE = {
    "modules": ["MATEMATYKA"],
    "curriculum_refs": ["4.15", "4.18"],
    "objectives": [
        "Dziecko potrafi przeliczać owoce w zakresie 5",
        "Rozpoznaje cyfry podczas zabawy w sklep",
        "Rozwija umiejętności społeczne poprzez odgrywanie ról"
    ]
}
