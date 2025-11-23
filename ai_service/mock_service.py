"""
Mock AI service that returns predefined data.

This module simulates the LangGraph AI workflow without making actual LLM calls.
It will be replaced with real LangGraph implementation in future phases.
"""

import random
import time
from typing import List

from common.models import FillWorkPlanResponse
from ai_service.db_client import get_db_client


# Mock learning objectives (Polish) - still hardcoded as per requirements
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
    by returning random selections from database data for modules and curriculum refs,
    and predefined Polish educational data for objectives.
    """

    def __init__(self, simulate_delay: bool = True):
        """
        Initialize mock AI service.

        Args:
            simulate_delay: If True, adds 1-2 second delay to simulate API calls
        """
        self.simulate_delay = simulate_delay

        # Initialize database client
        self.db_client = get_db_client()

        # Cache module names and curriculum ref codes from database
        self._load_db_data()

    def _load_db_data(self):
        """
        Load module names and curriculum reference codes from database.

        This data is cached in memory for performance, as it changes infrequently.
        """
        # Get all educational modules from database
        modules = self.db_client.get_educational_modules()
        self.module_names = [module.module_name for module in modules]

        # Get all curriculum reference codes from database
        curriculum_refs = self.db_client.get_curriculum_references()
        self.curriculum_ref_codes = [ref.reference_code for ref in curriculum_refs]

    def generate_metadata(self, activity: str, theme: str = "") -> FillWorkPlanResponse:
        """
        Generate mock educational metadata for an activity.

        Args:
            activity: Teacher's activity description (validated by Pydantic before this call)
            theme: Optional weekly theme for context

        Returns:
            FillWorkPlanResponse: Mock metadata with modules, curriculum refs, and objectives

        Note:
            Input validation is handled by FillWorkPlanRequest Pydantic model,
            so we trust that activity is already validated and non-empty.

            Modules and curriculum refs are selected from database.
            Objectives are still hardcoded as per requirements.
        """
        # Simulate API processing delay (1-2 seconds)
        if self.simulate_delay:
            time.sleep(random.uniform(1.0, 2.0))

        # Generate mock response with random selections from database
        # Fail explicitly if database is not populated
        if not self.module_names:
            raise ValueError("Database not initialized: no educational modules available")
        if not self.curriculum_ref_codes:
            raise ValueError("Database not initialized: no curriculum references available")

        # Select 1-2 random modules from database
        num_modules = random.randint(1, 2)
        modules = random.sample(
            self.module_names,
            min(num_modules, len(self.module_names))
        )

        # Select 2-3 random curriculum references from database
        num_refs = random.randint(2, 3)
        curriculum_refs = random.sample(
            self.curriculum_ref_codes,
            min(num_refs, len(self.curriculum_ref_codes))
        )

        # Select 2-3 random objectives (still hardcoded as per requirements)
        num_objectives = random.randint(2, 3)
        objectives = random.sample(SAMPLE_OBJECTIVES, num_objectives)

        return FillWorkPlanResponse(
            activity=activity.strip(),
            modules=modules,
            curriculum_refs=curriculum_refs,
            objectives=objectives
        )
