"""
OpenRouter LLM client for AI service.

Handles communication with OpenRouter API using OpenAI SDK, including:
- Async API calls with OpenAI client
- Structured outputs (JSON Schema validation)
- Reasoning extraction (supports <think> tags from models like DeepSeek R1)
- Token usage tracking
- Cost calculation
- Error handling with Polish messages
"""

import json
import re
from typing import Dict, Any, Tuple, Optional
from openai import AsyncOpenAI

from ai_service.config import settings
from ai_service.utils.console import log_prompt, log_response, log_cost, log_error, log_warning, log_info
from ai_service.utils.cost_tracker import get_pricing_cache, calculate_cost


# JSON Schema for structured LLM output
# Ensures the model returns valid JSON with required fields
LLM_OUTPUT_JSON_SCHEMA = {
    "name": "educational_metadata",
    "strict": True,
    "schema": {
        "type": "object",
        "properties": {
            "modules": {
                "type": "array",
                "description": "List of educational module names in Polish (uppercase)",
                "items": {
                    "type": "string"
                },
                "minItems": 1,
                "maxItems": 3
            },
            "curriculum_refs": {
                "type": "array",
                "description": "List of curriculum reference codes (e.g., '4.15', '3.4')",
                "items": {
                    "type": "string"
                },
                "minItems": 1,
                "maxItems": 7
            },
            "objectives": {
                "type": "array",
                "description": "List of learning objectives in Polish",
                "items": {
                    "type": "string"
                },
                "minItems": 1,
                "maxItems": 5
            }
        },
        "required": ["modules", "curriculum_refs", "objectives"],
        "additionalProperties": False
    }
}


def extract_reasoning_and_json(response_content: str) -> Tuple[str, Dict[str, Any]]:
    """
    Extract reasoning and JSON from model response content.

    NOTE: This is a FALLBACK method for models that embed reasoning in content.
    The preferred approach is using OpenRouter's `include_reasoning: true` parameter,
    which returns reasoning in a separate API field.

    Handles responses that contain reasoning tags followed by JSON output.
    Supports multiple reasoning tag formats:
    - <think>...</think> (DeepSeek R1 style when reasoning is in content)
    - <thinking>...</thinking> (alternative format)

    Args:
        response_content: Raw response string from LLM

    Returns:
        (reasoning, json_dict) tuple where:
            - reasoning: Extracted reasoning text (empty if no reasoning tags found)
            - json_dict: Parsed JSON object

    Raises:
        ValueError: If JSON parsing fails
    """
    reasoning = ""
    json_str = response_content

    # Check for <think> tags (DeepSeek R1 style)
    if "<think>" in response_content and "</think>" in response_content:
        think_start = response_content.find("<think>") + len("<think>")
        think_end = response_content.find("</think>")
        reasoning = response_content[think_start:think_end].strip()
        json_str = response_content[think_end + len("</think>"):].strip()

    # Check for <thinking> tags (alternative format)
    elif "<thinking>" in response_content and "</thinking>" in response_content:
        think_start = response_content.find("<thinking>") + len("<thinking>")
        think_end = response_content.find("</thinking>")
        reasoning = response_content[think_start:think_end].strip()
        json_str = response_content[think_end + len("</thinking>"):].strip()

    # Clean JSON string (remove markdown code fences)
    json_str = json_str.replace('```json', '').replace('```', '').strip()

    # Parse JSON
    try:
        json_dict = json.loads(json_str)
    except json.JSONDecodeError:
        # If parsing fails, try to find JSON object in the string
        json_match = re.search(r'\{.*\}', json_str, re.DOTALL)
        if json_match:
            json_dict = json.loads(json_match.group())
        else:
            raise ValueError(f"Could not parse JSON from: {json_str}")

    return reasoning, json_dict


class OpenRouterClient:
    """
    Client for OpenRouter API using OpenAI SDK.

    Provides async methods for calling LLMs with automatic cost tracking
    and reasoning extraction support.
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

        if not self.api_key:
            raise ValueError("OpenRouter API key is required")

        # Initialize OpenAI client with OpenRouter base URL
        self.client = AsyncOpenAI(
            api_key=self.api_key,
            base_url="https://openrouter.ai/api/v1",
            timeout=float(self.timeout),
            default_headers={
                "HTTP-Referer": "https://github.com/teacher-assist",
                "X-Title": "Teacher Assist - Lesson Planner"
            }
        )

    async def generate(
        self,
        prompt: str,
        log_output: bool = True,
        http_client: Optional[Any] = None  # Ignored, kept for API compatibility
    ) -> Tuple[str, Dict[str, int]]:
        """
        Generate completion from LLM.

        Calls OpenRouter API via OpenAI SDK and tracks token usage and costs.

        Args:
            prompt: The complete prompt to send to the LLM.
            log_output: Whether to log prompt, response, and cost to console.
            http_client: Deprecated parameter, kept for backwards compatibility.
                        OpenAI SDK manages its own connection pooling.

        Returns:
            Tuple of (raw_response_text, usage_dict) where usage_dict contains:
                - input_tokens: Native input token count
                - output_tokens: Native output token count
                - total_tokens: Total token count
                - estimated_cost: Calculated cost in USD

        Raises:
            openai.APITimeoutError: If request exceeds timeout.
            openai.APIStatusError: If API returns error status.
            ValueError: If response format is invalid.
        """
        # Log prompt in GREEN
        if log_output:
            log_prompt(prompt)

        try:
            # Call OpenAI API (compatible with OpenRouter)
            # Enable structured outputs (JSON Schema validation) and reasoning tokens
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                response_format={
                    "type": "json_schema",
                    "json_schema": LLM_OUTPUT_JSON_SCHEMA
                },
                extra_body={
                    "include_reasoning": True  # OpenRouter parameter for reasoning tokens
                }
            )

        except Exception as e:
            # Handle various API errors
            error_type = type(e).__name__
            if "timeout" in error_type.lower():
                error_msg = f"Przekroczono limit czasu oczekiwania na odpowiedź LLM ({self.timeout}s)"
                log_error(error_msg, str(e))
            elif "status" in error_type.lower():
                error_msg = f"Błąd API OpenRouter: {str(e)}"
                log_error(error_msg, str(e))
            else:
                error_msg = "Nieoczekiwany błąd podczas wywołania LLM"
                log_error(error_msg, str(e))
            raise

        # Extract response text and reasoning
        try:
            raw_response: str = response.choices[0].message.content
            if raw_response is None:
                raise ValueError("Response content is None")

            # Extract reasoning from OpenRouter's reasoning field (if available)
            # This works with DeepSeek R1, Gemini Thinking, and other reasoning models
            reasoning = ""
            if hasattr(response.choices[0].message, 'reasoning') and response.choices[0].message.reasoning:
                reasoning = response.choices[0].message.reasoning

            # Log full response in BLUE (includes reasoning if present in content)
            # Note: If reasoning is in separate field, it won't appear in content
            if log_output:
                if reasoning:
                    # Log reasoning separately if extracted from reasoning field
                    log_response(f"[REASONING]\n{reasoning}\n\n[JSON OUTPUT]\n{raw_response}")
                else:
                    log_response(raw_response)

            # With structured outputs, response is guaranteed valid JSON matching schema
            # Verify JSON validity and extract if embedded in extra text
            try:
                json.loads(raw_response)  # Verify it's valid JSON (should always pass)
            except json.JSONDecodeError as e:
                # Fallback: Try to extract JSON object from response using regex
                # Look for single-level JSON object with expected fields
                log_error("Structured output parsing failed, attempting regex extraction", str(e))

                # Regex pattern explanation:
                # \{                 - Opening brace
                # [^{}]*             - Any characters except braces (ensures single-level)
                # "(?:modules|...)"  - Match any of our three required field names (must appear 3 times)
                # [^{}]*             - More characters without braces
                # \}                 - Closing brace
                # This ensures we extract a flat JSON object containing all three required fields
                pattern = r'\{[^{}]*"(?:modules|curriculum_refs|objectives)"[^{}]*"(?:modules|curriculum_refs|objectives)"[^{}]*"(?:modules|curriculum_refs|objectives)"[^{}]*\}'

                match = re.search(pattern, raw_response, re.DOTALL)
                if match:
                    json_str = match.group(0)
                    try:
                        json.loads(json_str)  # Verify extracted JSON is valid
                        raw_response = json_str  # Replace response with extracted JSON
                        log_info("Successfully extracted JSON from response", f"Original length: {len(raw_response)}, Extracted length: {len(json_str)}")
                    except json.JSONDecodeError as parse_err:
                        raise ValueError(f"Invalid JSON from structured output (extraction also failed): {str(e)}")
                else:
                    raise ValueError(f"Invalid JSON from structured output (no valid JSON found): {str(e)}")

        except (IndexError, AttributeError) as e:
            error_msg = "Nieprawidłowy format odpowiedzi z OpenRouter API"
            log_error(error_msg, f"Missing 'choices' or 'message' in response: {str(e)}")
            raise ValueError(error_msg)


        # Extract token usage
        usage = response.usage
        input_tokens: int = usage.prompt_tokens if usage else 0
        output_tokens: int = usage.completion_tokens if usage else 0
        total_tokens: int = usage.total_tokens if usage else (input_tokens + output_tokens)

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
            log_warning(
                f"Failed to fetch pricing from OpenRouter, using fallback prices: "
                f"${prompt_price:.8f}/token (input), ${completion_price:.8f}/token (output)"
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
