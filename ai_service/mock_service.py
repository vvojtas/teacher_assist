"""
Mock AI service that returns predefined data.

This module simulates the LangGraph AI workflow without making actual LLM calls.
It will be replaced with real LangGraph implementation in future phases.
"""

import random
import time
from typing import List

from common.models import FillWorkPlanResponse


# Mock data for educational modules (Polish curriculum)
EDUCATIONAL_MODULES = [
    "JĘZYK",
    "MATEMATYKA",
    "MOTORYKA MAŁA",
    "MOTORYKA DUŻA",
    "FORMY PLASTYCZNE",
    "MUZYKA",
    "POZNAWCZE",
    "WSPÓŁPRACA",
    "EMOCJE",
    "SPOŁECZNE",
    "SENSORYKA",
    "ZDROWIE",
]

# Mock curriculum reference codes
CURRICULUM_REFS = [
    "1.1", "1.2", "1.3", "1.4", "1.5",
    "2.1", "2.2", "2.3", "2.4", "2.5",
    "3.1", "3.2", "3.5", "3.8", "3.10",
    "4.1", "4.5", "4.10", "4.15", "4.16", "4.18", "4.20",
]

# Mock learning objectives (Polish)
SAMPLE_OBJECTIVES = [
    "Dziecko potrafi przeliczać w zakresie 5",
    "Rozpoznaje poznane wcześniej cyfry",
    "Dziecko rozwija koordynację wzrokowo-ruchową",
    "Potrafi posługiwać się farbami i pędzlem",
    "Dziecko zapoznaje się z literaturą dziecięcą, słucha uważnie wiersza",
    "Dziecko potrafi współpracować z innymi podczas tworzenia wspólnej pracy",
    "Rozwijanie koordynacji wzrokowo-ruchowej",
    "Dziecko potrafi sortować obiekty według jednej cechy",
    "Rozróżnia pojęcia wielkości: duży, mały, średni",
    "Zapoznaje się z jesiennymi kolorami",
    "Dziecko rozwija umiejętność manipulacji małymi przedmiotami",
    "Poznaje znaczenie zdrowego odżywiania",
    "Dziecko potrafi wyrazić swoje emocje słowami",
    "Rozwija umiejętności społeczne w kontakcie z rówieśnikami",
]


class MockAIService:
    """
    Mock AI service for generating educational metadata.

    This class simulates the behavior of a real LangGraph-based AI service
    by returning random selections from predefined Polish educational data.
    """

    def __init__(self, simulate_delay: bool = True):
        """
        Initialize mock AI service.

        Args:
            simulate_delay: If True, adds 1-2 second delay to simulate API calls
        """
        self.simulate_delay = simulate_delay

    def generate_metadata(self, activity: str, theme: str = "") -> FillWorkPlanResponse:
        """
        Generate mock educational metadata for an activity.

        Args:
            activity: Teacher's activity description (required)
            theme: Optional weekly theme for context

        Returns:
            FillWorkPlanResponse: Mock metadata with module, curriculum refs, and objectives

        Raises:
            ValueError: If activity is empty or invalid
        """
        # Validate input
        if not activity or not activity.strip():
            raise ValueError("Activity cannot be empty")

        # Simulate API processing delay (1-2 seconds)
        if self.simulate_delay:
            time.sleep(random.uniform(1.0, 2.0))

        # Generate mock response with random selections
        module = random.choice(EDUCATIONAL_MODULES)

        # Select 2-3 random curriculum references
        num_refs = random.randint(2, 3)
        curriculum_refs = random.sample(CURRICULUM_REFS, num_refs)

        # Select 2-3 random objectives
        num_objectives = random.randint(2, 3)
        objectives = random.sample(SAMPLE_OBJECTIVES, num_objectives)

        return FillWorkPlanResponse(
            activity=activity.strip(),
            module=module,
            curriculum_refs=curriculum_refs,
            objectives=objectives
        )
