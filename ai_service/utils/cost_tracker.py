"""
Cost tracking and calculation utilities.

Handles fetching pricing data from OpenRouter and calculating request costs.
Pricing is cached to minimize API calls.
"""

import asyncio
import httpx
from typing import Dict, Optional, Tuple
from datetime import datetime, timedelta
from .console import log_warning, log_error


class PricingCache:
    """
    Cache for OpenRouter model pricing data.

    Pricing is fetched from /api/v1/models endpoint and cached for a configurable TTL.
    Thread-safe with async lock to prevent concurrent API calls.
    """

    def __init__(self, ttl_seconds: int = 3600):
        """
        Initialize pricing cache.

        Args:
            ttl_seconds: Time-to-live for cached pricing in seconds (default: 1 hour).
        """
        self.ttl_seconds = ttl_seconds
        self._cache: Dict[str, Tuple[float, float]] = {}  # model -> (prompt_price, completion_price)
        self._cache_time: Optional[datetime] = None
        self._lock = asyncio.Lock()  # Ensure thread-safe access

    def _is_cache_valid(self) -> bool:
        """Check if cache is still valid based on TTL."""
        if self._cache_time is None:
            return False
        return datetime.now() - self._cache_time < timedelta(seconds=self.ttl_seconds)

    async def fetch_pricing(
        self,
        api_key: str,
        model: str
    ) -> Tuple[float, float]:
        """
        Fetch pricing for a specific model from OpenRouter.

        Uses cached data if available and valid, otherwise fetches fresh data.
        Thread-safe with async lock to prevent concurrent API calls.

        Args:
            api_key: OpenRouter API key.
            model: Model identifier (e.g., "anthropic/claude-3.5-haiku").

        Returns:
            Tuple of (prompt_price_per_token, completion_price_per_token).

        Raises:
            httpx.HTTPError: If API request fails.
        """
        # Use async lock to prevent concurrent fetches
        async with self._lock:
            # Check cache again after acquiring lock (double-checked locking)
            if self._is_cache_valid() and model in self._cache:
                return self._cache[model]

            # Fetch fresh pricing data
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(
                        "https://openrouter.ai/api/v1/models",
                        headers={"Authorization": f"Bearer {api_key}"},
                        timeout=10.0
                    )
                    response.raise_for_status()
                    data = response.json()

                # Find pricing for requested model
                for model_data in data.get("data", []):
                    if model_data.get("id") == model:
                        pricing = model_data.get("pricing", {})
                        # Prices are strings to avoid float precision issues
                        prompt_price = float(pricing.get("prompt", "0"))
                        completion_price = float(pricing.get("completion", "0"))

                        # Cache the result
                        self._cache[model] = (prompt_price, completion_price)
                        self._cache_time = datetime.now()

                        return (prompt_price, completion_price)

                # Model not found, use fallback pricing
                log_warning(f"Pricing not found for model {model}, using fallback estimate")
                return self._get_fallback_pricing()

            except Exception as e:
                log_error(f"Failed to fetch pricing from OpenRouter: {str(e)}")
                log_warning("Using fallback pricing estimates")
                return self._get_fallback_pricing()

    def _get_fallback_pricing(self) -> Tuple[float, float]:
        """
        Return fallback pricing estimates if API fetch fails.

        Based on typical Claude 3.5 Haiku pricing as of late 2024.

        Returns:
            Tuple of (prompt_price_per_token, completion_price_per_token).
        """
        # Fallback: Claude 3.5 Haiku approximate pricing
        # $0.25 per 1M input tokens = $0.00000025 per token
        # $1.25 per 1M output tokens = $0.00000125 per token
        return (0.00000025, 0.00000125)

    def reset(self) -> None:
        """
        Reset the cache.

        Clears all cached pricing data and timestamps.
        Useful for testing or when pricing data needs to be refreshed.
        """
        self._cache.clear()
        self._cache_time = None


def calculate_cost(
    input_tokens: int,
    output_tokens: int,
    prompt_price: float,
    completion_price: float
) -> float:
    """
    Calculate the cost of an LLM request.

    Formula: cost = (input_tokens × prompt_price) + (output_tokens × completion_price)

    Args:
        input_tokens: Number of native input/prompt tokens.
        output_tokens: Number of native output/completion tokens.
        prompt_price: Price per input token (from OpenRouter pricing).
        completion_price: Price per output token (from OpenRouter pricing).

    Returns:
        Total cost in USD.
    """
    return (input_tokens * prompt_price) + (output_tokens * completion_price)


# Global pricing cache instance
_pricing_cache: Optional[PricingCache] = None


def get_pricing_cache(ttl_seconds: int = 3600) -> PricingCache:
    """
    Get or create the global pricing cache instance.

    Args:
        ttl_seconds: Time-to-live for cached pricing (default: 1 hour).

    Returns:
        Global PricingCache instance.
    """
    global _pricing_cache
    if _pricing_cache is None:
        _pricing_cache = PricingCache(ttl_seconds=ttl_seconds)
    return _pricing_cache


def reset_pricing_cache() -> None:
    """
    Reset the global pricing cache instance.

    Useful for testing or when pricing data needs to be refreshed.
    Should be called in test teardown to avoid cross-test contamination.
    """
    global _pricing_cache
    if _pricing_cache is not None:
        _pricing_cache.reset()
    _pricing_cache = None
