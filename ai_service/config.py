"""
Configuration management for AI Service.

Uses Pydantic Settings to load configuration from environment variables.
Supports both mock and real mode for testing and production.
"""

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Literal


class Settings(BaseSettings):
    """
    AI Service configuration loaded from environment variables.

    Environment variables should be defined in .env file or system environment.
    See ai_service/README.md for detailed documentation.
    """

    # Service Mode (keep without prefix as it's the main service identifier)
    ai_service_mode: Literal["mock", "real"] = "mock"

    # LLM Configuration (OpenRouter) - All with ai_service_ prefix for consistency
    ai_service_openrouter_api_key: str = ""
    ai_service_llm_model: str = "anthropic/claude-3.5-haiku"
    ai_service_llm_temperature: float = 0.7
    ai_service_llm_max_tokens: int = 500
    ai_service_llm_timeout_seconds: int = 30

    # Database - With ai_service_ prefix
    ai_service_database_path: str = "db.sqlite3"
    ai_service_database_timeout_seconds: float = 10.0  # SQLite connection timeout

    # Prompt Templates - With ai_service_ prefix
    ai_service_prompt_template_dir: str = "ai_service/templates"

    # Workflow Configuration - With ai_service_ prefix
    ai_service_max_retry_attempts: int = 0  # Phase 1: No retry, Phase 3: 1-2

    # Feature Flags (Phase 2/3) - With ai_service_ prefix
    ai_service_enable_quality_checker: bool = False  # Phase 2+
    ai_service_enable_auto_retry: bool = False       # Phase 3+

    # Cost Tracking - With ai_service_ prefix
    ai_service_pricing_cache_ttl_seconds: int = 3600  # 1 hour
    ai_service_fallback_prompt_price: float = 0.00000025  # Fallback $0.25 per 1M input tokens
    ai_service_fallback_completion_price: float = 0.00000125  # Fallback $1.25 per 1M output tokens

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    def validate_real_mode(self) -> None:
        """
        Validate that required configuration is present for real mode.

        Raises:
            ValueError: If OpenRouter API key is missing in real mode.
        """
        if self.ai_service_mode == "real" and not self.ai_service_openrouter_api_key:
            raise ValueError(
                "AI_SERVICE_OPENROUTER_API_KEY is required when AI_SERVICE_MODE=real. "
                "Please set it in your .env file or environment variables."
            )


@lru_cache
def get_settings() -> Settings:
    """
    Get cached settings instance.

    Uses @lru_cache for efficient singleton pattern without mutable globals.
    Cache can be cleared with get_settings.cache_clear() for testing.

    Returns:
        Settings: The cached settings instance.
    """
    return Settings()


# Convenience alias for backwards compatibility
settings = get_settings()
