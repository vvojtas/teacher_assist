import httpx
from typing import Dict, Any
from mcp_service import config

class DjangoAPIClient:
    def __init__(self, base_url: str = config.DJANGO_API_BASE_URL):
        self.base_url = base_url.rstrip('/')
        self.timeout = config.API_TIMEOUT_SECONDS
    
    async def get_all_curriculum_references(self) -> dict:
        """
        Fetches all curriculum references from the Django API.

        Returns:
            dict: The JSON response from Django, e.g.:
                {"references": {"1.1": "text...", ...}, "count": 49}
            On error, returns: {"error": "..."}
        """
        async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
            try:
                response = await client.get(f"{self.base_url}/api/curriculum-refs/")
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                return {"error": f"HTTP error: {str(e)}"}
            except Exception as e:
                return {"error": str(e)}
