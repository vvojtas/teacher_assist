"""
Colored console output utilities.

Uses colorama for cross-platform colored terminal output.
Color scheme:
- Green: Prompts sent to LLM
- Blue: LLM responses
- Yellow: Token counts and costs
- Red: Errors and warnings
"""

from colorama import Fore, Style, init

# Initialize colorama for cross-platform support
init(autoreset=True)


def log_prompt(prompt: str) -> None:
    """
    Log the formatted prompt sent to LLM in GREEN.

    Args:
        prompt: The complete prompt string sent to the LLM.
    """
    print(f"\n{Fore.GREEN}{'=' * 80}")
    print(f"{Fore.GREEN}[PROMPT SENT TO LLM]")
    print(f"{Fore.GREEN}{'=' * 80}")
    print(f"{Fore.GREEN}{prompt}")
    print(f"{Fore.GREEN}{'=' * 80}{Style.RESET_ALL}\n")


def log_response(response: str) -> None:
    """
    Log the raw LLM response in BLUE.

    Args:
        response: The raw response string from the LLM.
    """
    print(f"\n{Fore.BLUE}{'=' * 80}")
    print(f"{Fore.BLUE}[LLM RESPONSE]")
    print(f"{Fore.BLUE}{'=' * 80}")
    print(f"{Fore.BLUE}{response}")
    print(f"{Fore.BLUE}{'=' * 80}{Style.RESET_ALL}\n")


def log_cost(
    input_tokens: int,
    output_tokens: int,
    cost: float,
    model: str = ""
) -> None:
    """
    Log token counts and estimated cost in YELLOW.

    Args:
        input_tokens: Number of input/prompt tokens.
        output_tokens: Number of output/completion tokens.
        cost: Estimated cost in USD.
        model: Optional model name for reference.
    """
    total_tokens = input_tokens + output_tokens
    model_info = f" ({model})" if model else ""

    print(f"\n{Fore.YELLOW}{'=' * 80}")
    print(f"{Fore.YELLOW}[TOKEN USAGE & COST]{model_info}")
    print(f"{Fore.YELLOW}{'=' * 80}")
    print(f"{Fore.YELLOW}  Input tokens:      {input_tokens:,}")
    print(f"{Fore.YELLOW}  Output tokens:     {output_tokens:,}")
    print(f"{Fore.YELLOW}  Total tokens:      {total_tokens:,}")
    print(f"{Fore.YELLOW}  Estimated cost:    ${cost:.6f}")
    print(f"{Fore.YELLOW}{'=' * 80}{Style.RESET_ALL}\n")


def log_error(message: str, details: str = "") -> None:
    """
    Log error message in RED.

    Args:
        message: The error message.
        details: Optional detailed error information.
    """
    print(f"\n{Fore.RED}{'=' * 80}")
    print(f"{Fore.RED}[ERROR]")
    print(f"{Fore.RED}{'=' * 80}")
    print(f"{Fore.RED}{message}")
    if details:
        print(f"{Fore.RED}\nDetails:")
        print(f"{Fore.RED}{details}")
    print(f"{Fore.RED}{'=' * 80}{Style.RESET_ALL}\n")


def log_warning(message: str) -> None:
    """
    Log warning message in RED.

    Used for lenient validation warnings (e.g., filtered invalid curriculum codes).

    Args:
        message: The warning message.
    """
    print(f"{Fore.RED}[WARNING] {message}{Style.RESET_ALL}")


def log_info(message: str) -> None:
    """
    Log informational message (no color).

    Args:
        message: The informational message.
    """
    print(f"[INFO] {message}")
