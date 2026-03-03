import sys
import os

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

@mcp.resource("curriculum://references/all", mime_type="application/json")
async def get_curriculum_references_resource() -> dict:
    """
    Returns the complete list of available Polish kindergarten curriculum (Podstawa Programowa) references
    as a JSON dictionary mapping reference codes (e.g., '1.1', '4.15') to their full text.
    """
    return await django_client.get_all_curriculum_references()

if __name__ == "__main__":
    mcp.run(transport="streamable-http")
