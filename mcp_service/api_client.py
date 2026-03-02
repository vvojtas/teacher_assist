import httpx
from typing import Dict, Any
from . import config

class DjangoAPIClient:
    def __init__(self, base_url: str = config.DJANGO_API_BASE_URL):
        self.base_url = base_url.rstrip('/')
        self.timeout = config.API_TIMEOUT_SECONDS
    
    async def get_all_curriculum_references(self) -> str:
        """
        Fetches all curriculum references and formats them as a readable string.
        """
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.get(f"{self.base_url}/api/curriculum-refs")
                response.raise_for_status()
                data = response.json()
                
                references = data.get("references", {})
                if not references:
                    return "No curriculum references found."
                
                formatted_refs = ["Curriculum References:\n", "="*20]
                for code, text in references.items():
                    formatted_refs.append(f"[{code}] {text}")
                
                return "\n".join(formatted_refs)
            except httpx.HTTPError as e:
                return f"HTTP error occurred while fetching curriculum references: {str(e)}"
            except Exception as e:
                return f"An error occurred: {str(e)}"
