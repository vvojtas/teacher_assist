import sys
import os
from typing import Optional

# Ensure the project root is on sys.path so absolute imports work
# when this file is executed standalone via `mcp run`
_project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from mcp.server.fastmcp import FastMCP
from mcp_service.api_client import DjangoAPIClient

# Initialize FastMCP Server
mcp = FastMCP(
    "TeacherAssist",
    instructions="MCP Server providing access to Teacher Assist Backend API",
    host="127.0.0.1",
    port=8002,
)

# Initialize our Django API client
django_client = DjangoAPIClient()


# ── Resources ────────────────────────────────────────────────────

@mcp.resource("curriculum://references/all", mime_type="application/json")
async def get_curriculum_references_resource() -> dict:
    """
    Returns the complete list of available Polish kindergarten curriculum (Podstawa Programowa) references
    as a JSON dictionary mapping reference codes (e.g., '1.1', '4.15') to their full text.
    """
    return await django_client.get_all_curriculum_references()


# ── Tools ────────────────────────────────────────────────────────

@mcp.tool()
async def lookup_curriculum_reference(code: str) -> dict:
    """
    Look up a specific curriculum reference by its code.

    Use this to get the exact wording of a specific Podstawa Programowa paragraph
    when you already know the code (e.g., from the fill-work-plan results).

    Args:
        code: The curriculum reference code, e.g. "3.8" or "4.15".

    Returns:
        Dictionary with reference_code, full_text, and created_at.
        On error: Dictionary with error message.
    """
    return await django_client.lookup_curriculum_reference(code)


@mcp.tool()
async def get_educational_modules(ai_suggested: Optional[bool] = None) -> dict:
    """
    Get a list of available educational modules from the database.

    Modules represent broad educational areas (e.g., "JĘZYK", "MATEMATYKA").
    Optionally filter to only show modules that are suggested for AI-assisted planning.

    Args:
        ai_suggested: If True, return only AI-suggested modules.
                      If False, return only non-AI-suggested modules.
                      If not provided, return all modules.

    Returns:
        Dictionary with modules list and count.
        On error: Dictionary with error message.
    """
    return await django_client.get_educational_modules(ai_suggested=ai_suggested)


@mcp.tool()
async def generate_lesson_metadata(activity: str, theme: Optional[str] = None) -> dict:
    """
    Generate educational metadata for a kindergarten activity using AI.

    Given an informal activity description, this tool uses a LangGraph AI workflow
    to suggest the appropriate educational module, relevant curriculum references
    (Podstawa Programowa codes), and learning objectives.

    This is a long-running operation (may take 30-120 seconds).

    Args:
        activity: Description of the planned activity (1-500 characters).
                  Example: "Dzieci będą malować obrazki inspirowane wiosną"
        theme: Optional theme or topic for context (max 200 characters).
               Example: "Wiosna"

    Returns:
        Dictionary with module, curriculum_refs list, and objectives list.
        On error: Dictionary with error message and error_code.
    """
    return await django_client.generate_lesson_metadata(activity=activity, theme=theme)


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
