"""
Configuration management for AI Service.

Uses Pydantic Settings to load configuration from environment variables.
Supports both mock and real mode for testing and production.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Literal


class Settings(BaseSettings):
    """
    AI Service configuration loaded from environment variables.

    Environment variables should be defined in .env file or system environment.
    See ai_service/README.md for detailed documentation.
    """

    # Service Mode
    ai_service_mode: Literal["mock", "real"] = "mock"

    # LLM Configuration (OpenRouter)
    openrouter_api_key: str = ""
    llm_model: str = "anthropic/claude-3.5-haiku"
    llm_temperature: float = 0.7
    llm_max_tokens: int = 500
    llm_timeout_seconds: int = 30

    # Database
    database_path: str = "../db.sqlite3"
    database_timeout_seconds: float = 10.0  # SQLite connection timeout

    # Prompt Templates
    prompt_template_dir: str = "ai_service/templates"

    # Workflow Configuration
    max_retry_attempts: int = 0  # Phase 1: No retry, Phase 3: 1-2

    # Feature Flags (Phase 2/3)
    enable_quality_checker: bool = False  # Phase 2+
    enable_auto_retry: bool = False       # Phase 3+

    # Cost Tracking
    pricing_cache_ttl_seconds: int = 3600  # 1 hour

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
        if self.ai_service_mode == "real" and not self.openrouter_api_key:
            raise ValueError(
                "OPENROUTER_API_KEY is required when AI_SERVICE_MODE=real. "
                "Please set it in your .env file or environment variables."
            )


# Global settings instance
settings = Settings()
