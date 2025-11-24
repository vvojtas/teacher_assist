"""
LLM generation node for LangGraph workflow.

Calls OpenRouter API to generate educational metadata.
"""

from typing import Dict, Any

from ai_service.nodes.llm_client import get_llm_client
from ai_service.config import settings
from ai_service.utils.console import log_error


async def generate_with_llm(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate LLM response from constructed prompt.

    LangGraph node that:
    1. Calls OpenRouter API with constructed prompt
    2. Tracks token usage and cost
    3. Logs prompt (green), response (blue), and cost (yellow)

    Args:
        state: Workflow state containing:
            - constructed_prompt: The complete prompt to send to LLM

    Returns:
        Updated state with:
            - llm_raw_response: Raw text response from LLM
            - input_tokens: Number of input tokens
            - output_tokens: Number of output tokens
            - estimated_cost: Estimated cost in USD
    """
    prompt: str = state.get("constructed_prompt", "")

    if not prompt:
        error_msg = "Brak skonstruowanego promptu"
        log_error("Błąd generowania LLM", "Prompt jest pusty")
        return {
            **state,
            "llm_raw_response": "",
            "validation_errors": state.get("validation_errors", []) + [error_msg],
            "validation_passed": False
        }

    try:
        # Get LLM client
        llm_client = get_llm_client()

        # Generate response (logs are handled inside the client)
        raw_response: str
        usage: Dict[str, Any]
        raw_response, usage = await llm_client.generate(
            prompt=prompt,
            log_output=True  # Enable colored console logging
        )

        return {
            **state,
            "llm_raw_response": raw_response,
            "input_tokens": usage["input_tokens"],
            "output_tokens": usage["output_tokens"],
            "estimated_cost": usage["estimated_cost"]
        }

    except Exception as e:
        error_msg = f"Błąd podczas generowania odpowiedzi LLM: {str(e)}"
        log_error("Błąd generowania LLM", str(e))

        return {
            **state,
            "llm_raw_response": "",
            "validation_errors": state.get("validation_errors", []) + [error_msg],
            "validation_passed": False
        }
