import os
from dotenv import load_dotenv

# Load environment variables (from the root .env file)
load_dotenv()

DJANGO_API_BASE_URL = os.environ.get("DJANGO_API_URL", "http://localhost:8000")
API_TIMEOUT_SECONDS = int(os.environ.get("MCP_API_TIMEOUT_SECONDS", "30"))
