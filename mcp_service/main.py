from mcp.server.fastmcp import FastMCP
from .api_client import DjangoAPIClient

# Initialize FastMCP Server
mcp = FastMCP("TeacherAssist", description="MCP Server providing access to Teacher Assist Backend API")

# Initialize our Django API client
django_client = DjangoAPIClient()

@mcp.resource("curriculum://references/all")
async def get_curriculum_references_resource() -> str:
    """
    Returns the complete list of available Polish kindergarten curriculum (Podstawa Programowa) references.
    Provides paragraph numbers (e.g., '1.1', '4.15') and their full text.
    """
    return await django_client.get_all_curriculum_references()

if __name__ == "__main__":
    mcp.run()
