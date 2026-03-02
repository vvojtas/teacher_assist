# Teacher Assist - MCP Service

This is the standalone FastMCP service (API Gateway) for the **Teacher Assist** project. It exposes the Django REST API functionalities to AI agents using the Model Context Protocol (MCP).

## Setup & Running

This service shares the root project Virtual Environment (`.venv`) and dependencies. Ensure you have installed the root requirements.

To run the MCP server:
```bash
# Activation of the environment (Windows)
..venv\Scripts\activate

# Run the MCP server
mcp run mcp_service/main.py
```

## Features (Phase 1)
- Exposes `curriculum://references/all` resource to fetch all Polish kindergarten curriculum paragraphs from the database.

## Testing
To run the automated tests for the MCP API client:
```bash
pytest mcp_service/tests/
```
