"""
Constants for AI service validation and configuration.

Centralized location for magic numbers and validation limits.
"""

# Input validation limits
MAX_ACTIVITY_LENGTH = 500  # Maximum characters for activity field
MAX_THEME_LENGTH = 200  # Maximum characters for theme field
MIN_ACTIVITY_LENGTH = 1  # Minimum characters for activity field

# Output validation limits
MIN_MODULES = 1  # Minimum number of modules required
MAX_MODULES = 3  # Maximum number of modules allowed
MIN_CURRICULUM_REFS = 1  # Minimum number of curriculum references required
MAX_CURRICULUM_REFS = 10  # Maximum number of curriculum references allowed
MIN_OBJECTIVES = 1  # Minimum number of objectives required
MAX_OBJECTIVES = 5  # Maximum number of objectives allowed
MIN_OBJECTIVE_LENGTH = 10  # Minimum characters per objective

# LLM Configuration defaults (can be overridden by settings)
DEFAULT_TEMPERATURE = 0.7
DEFAULT_MAX_TOKENS = 500
DEFAULT_TIMEOUT_SECONDS = 30

# Pricing cache defaults
DEFAULT_PRICING_CACHE_TTL = 3600  # 1 hour in seconds
