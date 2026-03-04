import httpx
from typing import Optional
from mcp_service import config


class DjangoAPIClient:
    def __init__(self, base_url: str = config.DJANGO_API_BASE_URL):
        self.base_url = base_url.rstrip('/')
        self.timeout = config.API_TIMEOUT_SECONDS
        self.ai_timeout = config.AI_GENERATION_TIMEOUT_SECONDS

    # ── Phase 1: Curriculum references (all) ──────────────────────

    async def get_all_curriculum_references(self) -> dict:
        """
        Fetches all curriculum references from the Django API.

        Returns:
            dict: {"references": {"1.1": "text...", ...}, "count": N}
            On error: {"error": "..."}
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

    # ── Phase 2: Curriculum reference lookup ──────────────────────

    async def lookup_curriculum_reference(self, code: str) -> dict:
        """
        Looks up a single curriculum reference by its code.

        Args:
            code: Reference code, e.g. "3.8", "4.15"

        Returns:
            dict: {"reference_code": "3.8", "full_text": "...", "created_at": "..."}
            On 404: {"error": "...", "error_code": "REFERENCE_NOT_FOUND"}
            On error: {"error": "..."}
        """
        async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
            try:
                response = await client.get(f"{self.base_url}/api/curriculum-refs/{code}/")
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                # Preserve Django's error response body
                try:
                    return e.response.json()
                except Exception:
                    return {"error": f"HTTP {e.response.status_code}: {str(e)}"}
            except httpx.HTTPError as e:
                return {"error": f"HTTP error: {str(e)}"}
            except Exception as e:
                return {"error": str(e)}

    # ── Phase 2: Educational modules ─────────────────────────────

    async def get_educational_modules(self, ai_suggested: Optional[bool] = None) -> dict:
        """
        Fetches educational modules, optionally filtering by ai_suggested flag.

        Args:
            ai_suggested: If provided, filter modules by this flag.

        Returns:
            dict: {"modules": [...], "count": N}
            On error: {"error": "..."}
        """
        params = {}
        if ai_suggested is not None:
            params["ai_suggested"] = "true" if ai_suggested else "false"

        async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
            try:
                response = await client.get(f"{self.base_url}/api/modules/", params=params)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                return {"error": f"HTTP error: {str(e)}"}
            except Exception as e:
                return {"error": str(e)}

    # ── Phase 2: Fill work plan (AI generation with CSRF) ────────

    async def _get_csrf_token(self, client: httpx.AsyncClient) -> str:
        """
        Fetches a CSRF token from Django by hitting the root page.

        Returns:
            str: The CSRF token value.

        Raises:
            RuntimeError: If CSRF token cannot be obtained.
        """
        response = await client.get(f"{self.base_url}/")
        csrf_token = response.cookies.get("csrftoken")
        if not csrf_token:
            raise RuntimeError("Could not obtain CSRF token from Django")
        return csrf_token

    async def generate_lesson_metadata(self, activity: str, theme: Optional[str] = None) -> dict:
        """
        Calls the fill-work-plan endpoint to generate lesson metadata via AI.

        Handles CSRF token exchange automatically.

        Args:
            activity: Activity description (required, 1-500 chars).
            theme: Optional theme string (max 200 chars).

        Returns:
            dict: {"module": "...", "curriculum_refs": [...], "objectives": [...]}
            On error: {"error": "...", "error_code": "..."}
        """
        async with httpx.AsyncClient(timeout=self.ai_timeout, follow_redirects=True) as client:
            try:
                # Step 1: Get CSRF token
                csrf_token = await self._get_csrf_token(client)

                # Step 2: POST with CSRF header and cookie
                payload = {"activity": activity}
                if theme:
                    payload["theme"] = theme

                response = await client.post(
                    f"{self.base_url}/api/fill-work-plan/",
                    json=payload,
                    headers={"X-CSRFToken": csrf_token},
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                # Preserve Django's structured error response
                try:
                    return e.response.json()
                except Exception:
                    return {"error": f"HTTP {e.response.status_code}: {str(e)}"}
            except RuntimeError as e:
                return {"error": str(e), "error_code": "CSRF_ERROR"}
            except httpx.TimeoutException:
                return {
                    "error": "AI generation timed out. Try again or fill data manually.",
                    "error_code": "AI_SERVICE_TIMEOUT",
                }
            except httpx.HTTPError as e:
                return {"error": f"HTTP error: {str(e)}"}
            except Exception as e:
                return {"error": str(e)}
