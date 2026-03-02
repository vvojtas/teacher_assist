# Teacher Assist API - MCP Server Planning

This document describes the existing Django REST API endpoints and outlines how they can be exposed through a Model Context Protocol (MCP) server. This facilitates interaction between AI agents and the Teacher Assist system.

## Context & Database Usage

From our analysis of the `lessonplanner/views.py` and `lessonplanner/urls.py`, the backend interacts with the database in specific ways:
- **Database Fetching**: The `GET` endpoints for references and modules query the SQLite database directly (via `db_service`).
- **AI Proxying**: The `POST` endpoint delegates heavy lifting to a LangGraph service, meaning it doesn't query the database schema for the returned metadata but rather passes the AI's output.

---

## Endpoints Overview & MCP Exposure Strategy

### 1. Fill Work Plan (AI Metadata Generation)
- **HTTP/Path**: `POST /api/fill-work-plan`
- **Input**: `{"activity": "string", "theme": "string (optional)"}`
- **Response**: `{"modules": ["..."], "curriculum_refs": ["..."], "objectives": ["..."]}`
- **Source**: LangGraph AI Service wrapper.

**MCP Exposure Plan**:
- **MCP Concept**: **Tool** (e.g., `generate_lesson_metadata`)
- **Arguments**: `activity` (string, required), `theme` (string, optional)
- **Purpose**: A generative action tool allowing the agent to submit an informal activity description and receive formal educational metadata, objectives, and curriculum mapping.

### 2. Get All Curriculum References
- **HTTP/Path**: `GET /api/curriculum-refs`
- **Response**: Dictionary mapping reference codes (e.g., `"1.1"`) to full Polish text.
- **Source**: Local Database (`curriculum_references` table).

**MCP Exposure Plan**:
- **MCP Concept**: **Resource**
- **URI Pattern**: `curriculum://references/all`
- **Purpose**: Exposes the entire curriculum database as a read-only document. Since it is relatively small (estimated 50-100 references), the LLM can read the entire context at once to make holistic lesson planning decisions.

### 3. Lookup Curriculum Reference by Code
- **HTTP/Path**: `GET /api/curriculum-refs/<code>`
- **Response**: Object containing `reference_code` and `full_text`.
- **Source**: Local Database (`curriculum_references` table).

**MCP Exposure Plan**:
- **MCP Concept**: **Tool** (e.g., `lookup_curriculum_reference`)
- **Arguments**: `code` (string, required, e.g., `"3.8"`)
- **Purpose**: A precise lookup mechanism. If the agent only needs the exact wording of specific codes (e.g., returned from the `fill-work-plan` tool), it can fetch them selectively to save context space.

### 4. Get Educational Modules
- **HTTP/Path**: `GET /api/modules`
- **Query Params**: `ai_suggested` (boolean, optional)
- **Response**: Array of available module objects.
- **Source**: Local Database (`educational_modules` table).

**MCP Exposure Plan**:
- **MCP Concept**: **Tool** (e.g., `get_educational_modules`)
- **Arguments**: `ai_suggested` (boolean, optional)
- **Purpose**: Provides a dynamic list of valid educational modules. Exposing it as a tool allows the agent to filter the database directly.

## Implementation Considerations for MCP

1. **Authentication / CSRF Requirements**: 
   The `POST /api/fill-work-plan` requires an `X-CSRFToken` header. When implementing the MCP server, it will act as an API client. It must either perform a preliminary `GET /` request to extract the `csrftoken` cookie or the Django app must be configured to bypass CSRF for local trust-zone requests coming from the MCP server.

2. **Error Translation**:
   The API has standard Polish error responses and defined codes (e.g., `INVALID_INPUT`, `AI_SERVICE_UNAVAILABLE`). The MCP tools should gracefully catch HTTP errors, returning them as user-facing tool errors rather than crashing the server.
