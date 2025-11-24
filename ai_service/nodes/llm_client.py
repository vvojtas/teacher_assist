"""
OpenRouter LLM client for AI service.

Handles communication with OpenRouter API, including:
- Async HTTP requests
- Token usage tracking
- Cost calculation
- Error handling with Polish messages
"""

import httpx
from typing import Dict, Any, Tuple, Optional

from ai_service.config import settings
from ai_service.utils.console import log_prompt, log_response, log_cost, log_error
from ai_service.utils.cost_tracker import get_pricing_cache, calculate_cost


class OpenRouterClient:
    """
    Client for OpenRouter API.

    Provides async methods for calling LLMs with automatic cost tracking.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        timeout: Optional[int] = None
    ):
        """
        Initialize OpenRouter client.

        Args:
            api_key: OpenRouter API key (defaults to settings.openrouter_api_key).
            model: Model identifier (defaults to settings.llm_model).
            temperature: Temperature 0.0-1.0 (defaults to settings.llm_temperature).
            max_tokens: Max output tokens (defaults to settings.llm_max_tokens).
            timeout: Request timeout in seconds (defaults to settings.llm_timeout_seconds).
        """
        self.api_key = api_key or settings.ai_service_openrouter_api_key
        self.model = model or settings.ai_service_llm_model
        self.temperature = temperature or settings.ai_service_llm_temperature
        self.max_tokens = max_tokens or settings.ai_service_llm_max_tokens
        self.timeout = timeout or settings.ai_service_llm_timeout_seconds
        self.base_url = "https://openrouter.ai/api/v1"

        if not self.api_key:
            raise ValueError("OpenRouter API key is required")

    async def generate(
        self,
        prompt: str,
        log_output: bool = True,
        http_client: Optional[httpx.AsyncClient] = None
    ) -> Tuple[str, Dict[str, int]]:
        """
        Generate completion from LLM.

        Calls OpenRouter API and tracks token usage and costs.

        Args:
            prompt: The complete prompt to send to the LLM.
            log_output: Whether to log prompt, response, and cost to console.
            http_client: Optional shared HTTP client (recommended for connection pooling).
                        If None, creates a new client for this request.

        Returns:
            Tuple of (raw_response_text, usage_dict) where usage_dict contains:
                - input_tokens: Native input token count
                - output_tokens: Native output token count
                - total_tokens: Total token count
                - estimated_cost: Calculated cost in USD

        Raises:
            httpx.TimeoutException: If request exceeds timeout.
            httpx.HTTPStatusError: If API returns error status.
            ValueError: If response format is invalid.
        """
        # Log prompt in GREEN
        if log_output:
            log_prompt(prompt)

        # Prepare request payload
        payload: Dict[str, Any] = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            # Enable usage tracking for token counts
            "usage": {"include": True}
        }

        headers: Dict[str, str] = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/teacher-assist",  # Optional: helps with rate limits
            "X-Title": "Teacher Assist - Lesson Planner"  # Optional: shown in OpenRouter dashboard
        }

        try:
            # Use shared client if provided, otherwise create a new one
            if http_client is not None:
                # Use shared client (recommended for connection pooling)
                response = await http_client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=self.timeout
                )
                response.raise_for_status()
                data: Dict[str, Any] = response.json()
            else:
                # Create temporary client (fallback for testing)
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        f"{self.base_url}/chat/completions",
                        headers=headers,
                        json=payload,
                        timeout=self.timeout
                    )
                    response.raise_for_status()
                    data: Dict[str, Any] = response.json()

        except httpx.TimeoutException as e:
            error_msg = f"Przekroczono limit czasu oczekiwania na odpowiedź LLM ({self.timeout}s)"
            log_error(error_msg, str(e))
            raise

        except httpx.HTTPStatusError as e:
            error_msg = f"Błąd API OpenRouter: {e.response.status_code}"
            error_details = e.response.text
            log_error(error_msg, error_details)
            raise

        except Exception as e:
            error_msg = "Nieoczekiwany błąd podczas wywołania LLM"
            log_error(error_msg, str(e))
            raise

        # Extract response text
        try:
            raw_response: str = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError) as e:
            error_msg = "Nieprawidłowy format odpowiedzi z OpenRouter API"
            log_error(error_msg, f"Missing 'choices' or 'message' in response: {str(e)}")
            raise ValueError(error_msg)

        # Log raw response in BLUE
        if log_output:
            log_response(raw_response)

        # Extract token usage
        usage: Dict[str, Any] = data.get("usage", {})
        input_tokens: int = usage.get("prompt_tokens", 0)
        output_tokens: int = usage.get("completion_tokens", 0)
        total_tokens: int = usage.get("total_tokens", input_tokens + output_tokens)

        # Calculate cost using pricing cache
        estimated_cost: float
        try:
            pricing_cache = get_pricing_cache(settings.ai_service_pricing_cache_ttl_seconds)
            prompt_price, completion_price = await pricing_cache.fetch_pricing(
                self.api_key,
                self.model
            )
            estimated_cost = calculate_cost(
                input_tokens,
                output_tokens,
                prompt_price,
                completion_price
            )
        except Exception as e:
            # Fallback cost estimation if pricing fetch fails
            # Use configurable fallback prices from settings
            prompt_price = settings.ai_service_fallback_prompt_price
            completion_price = settings.ai_service_fallback_completion_price
            estimated_cost = (input_tokens * prompt_price) + (output_tokens * completion_price)

            # Log warning about fallback pricing
            log_error(
                "Nie można pobrać cen z OpenRouter, używam szacunkowych cen",
                f"Błąd: {str(e)} | "
                f"Używam: ${prompt_price:.8f}/token (input), ${completion_price:.8f}/token (output)"
            )

        # Log token usage and cost in YELLOW
        if log_output:
            log_cost(input_tokens, output_tokens, estimated_cost, self.model)

        usage_dict: Dict[str, Any] = {
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": total_tokens,
            "estimated_cost": estimated_cost
        }

        return raw_response, usage_dict


def get_llm_client(
    api_key: Optional[str] = None,
    model: Optional[str] = None
) -> OpenRouterClient:
    """
    Get OpenRouter client instance.

    Args:
        api_key: Optional API key override.
        model: Optional model override.

    Returns:
        Configured OpenRouterClient instance.
    """
    return OpenRouterClient(api_key=api_key, model=model)
