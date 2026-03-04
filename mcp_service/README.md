# Teacher Assist - MCP Service

This is the standalone FastMCP service (API Gateway) for the **Teacher Assist** project. It exposes the Django REST API functionalities to AI agents using the [Model Context Protocol (MCP)](https://modelcontextprotocol.io/).

## Architecture

The MCP Gateway sits between AI agents and the Django backend:

```
AI Agent (Claude, Cursor, etc.)
         │
         │  MCP (Streamable HTTP)
         ▼
   MCP Gateway (port 8002)
         │
         │  HTTP (REST API)
         ▼
   Django Backend (port 8000)
```

## Transport

The server uses **Streamable HTTP** transport (not stdio), running on `http://127.0.0.1:8002`.
The MCP endpoint is at `http://127.0.0.1:8002/mcp`.

## Setup & Running

This service shares the root project Virtual Environment (`.venv`) and dependencies (`requirements.txt`).

### Start manually
```bash
# From the project root
python mcp_service/main.py
```

### Start with the unified startup scripts
```bash
# Windows
start.bat

# Linux/Mac
./start.sh
```

### Connect via MCP Inspector
1. Start the MCP server: `python mcp_service/main.py`
2. Launch the Inspector: `npx @modelcontextprotocol/inspector`
3. In the Inspector UI, set transport to **Streamable HTTP** and URL to `http://localhost:8002/mcp`

### Connect from Claude Desktop / Cursor
Add to your MCP client config:
```json
{
  "mcpServers": {
    "teacher-assist": {
      "url": "http://localhost:8002/mcp"
    }
  }
}
```

## Features (Phase 1)

### Resources
| URI | Description |
|-----|-------------|
| `curriculum://references/all` | Returns all Polish kindergarten curriculum (Podstawa Programowa) references as JSON |

**Response format** (`application/json`):
```json
{
  "references": {
    "1.1": "zgłasza potrzeby fizjologiczne...",
    "2.5": "rozstaje się z rodzicami..."
  },
  "count": 52
}
```

## Configuration

Environment variables (can be set in `.env` at project root):

| Variable | Default | Description |
|----------|---------|-------------|
| `DJANGO_API_URL` | `http://localhost:8000` | Base URL for the Django REST API |
| `MCP_API_TIMEOUT_SECONDS` | `30` | HTTP request timeout |

## Testing

```bash
pytest mcp_service/tests/ -v
```
