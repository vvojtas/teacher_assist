"""
Mock AI client service for generating lesson plan metadata
Simulates API calls with static responses
"""

import time
import random
from .mock_data import EDUCATIONAL_MODULES, CURRICULUM_REFERENCES, SAMPLE_OBJECTIVES


def generate_metadata(activity: str, theme: str = "") -> dict:
    """
    Generate mock metadata for a lesson activity.

    Args:
        activity (str): The activity description (required)
        theme (str): Optional weekly theme context

    Returns:
        dict: Contains module, curriculum_refs, and objectives

    Example return:
        {
            "module": "MATEMATYKA",
            "curriculum_refs": ["4.15", "4.18"],
            "objectives": [
                "Dziecko potrafi przeliczać w zakresie 5",
                "Rozpoznaje poznane wcześniej cyfry"
            ]
        }
    """
    # Simulate API delay (1-2 seconds)
    time.sleep(random.uniform(1.0, 2.0))

    # Validate input
    if not activity or not activity.strip():
        raise ValueError("Activity cannot be empty")

    # Generate mock response with random selections
    module = random.choice(EDUCATIONAL_MODULES)

    # Select 2-3 random curriculum references
    num_refs = random.randint(2, 3)
    curriculum_refs = random.sample(list(CURRICULUM_REFERENCES.keys()), num_refs)

    # Select 2-3 random objectives
    num_objectives = random.randint(2, 3)
    objectives = random.sample(SAMPLE_OBJECTIVES, num_objectives)

    return {
        "module": module,
        "curriculum_refs": curriculum_refs,
        "objectives": objectives
    }


def get_curriculum_text(reference_code: str) -> str:
    """
    Get the full Polish text for a curriculum reference code.

    Args:
        reference_code (str): The reference code (e.g., "I.1.2")

    Returns:
        str: Full curriculum text in Polish, or error message if not found
    """
    return CURRICULUM_REFERENCES.get(
        reference_code,
        f"Nie znaleziono opisu dla kodu: {reference_code}"
    )
