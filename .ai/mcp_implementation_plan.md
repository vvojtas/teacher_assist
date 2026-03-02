# Implementation Plan: Standalone FastMCP Service

This document outlines the implementation strategy for creating a standalone FastMCP service (API Gateway) that exposes the Teacher Assist Django REST API to AI agents. 

We will start with the foundational setup and the simple `GET /api/curriculum-refs` endpoint, and then progressively add support for the remaining APIs.

---

## 🏗️ Phase 1: Foundation and Initial Endpoint (`/api/curriculum-refs`)

This phase focuses on the fundamental project setup and reading simple data from the Django API.

### 1. Project Initialization & Structure
- **Create Directory:** Create a new folder at the project root named `mcp_service/`.
- **Dependencies:** Use the existing `.venv` in the project root. Add `mcp`, `httpx`, `python-dotenv`, `pytest`, and `pytest-asyncio` to the root `requirements.txt`.
- **File Structure:** Set up the basic module structure:
  - `mcp_service/main.py`: The entry point and FastMCP instance definition.
  - `mcp_service/config.py`: Environment configuration (e.g., parsing `DJANGO_API_URL`).
  - `mcp_service/api_client.py`: A reusable, asynchronous HTTP client to communicate with Django.

### 2. Core Modules Implementation
- **`config.py`**: Add configurations for the base URL (defaulting to `http://localhost:8000`), timeouts, and other operational parameters.
- **`api_client.py`**: Create an asynchronous class (`DjangoAPIClient`) that initializes an `httpx.AsyncClient`. Implement basic error handling and logging for outgoing requests.

### 3. Implementing the Curriculum Interfaces
Based on `.ai/api_info.md`, we will expose curriculum references in two ways. For Phase 1, we focus on fetching all references:
- **As an MCP Resource (All References):**
  - **Client Method:** Implement `get_all_curriculum_references()` in `api_client.py` that calls `GET /api/curriculum-refs`.
  - **MCP Definition:** In `main.py`, define a FastMCP Resource (e.g., `curriculum://references/all`) that fetches and formats the entire curriculum JSON as readable text.

### 4. Unit Testing Setup
- **Create Tests Directory:** Set up a `tests/` directory within `mcp_service/`.
- **Initial Tests:** Write unit tests for `config.py` parsing and basic `api_client.py` functionality.

### 5. Initial Documentation Update
- **`mcp_service/README.md`**: Create a README file detailing how to run the MCP service.
- **Root `README.md`**: Add a high-level note about the `mcp_service` API gateway.

---

## 🔍 Verification (Post Phase 1)

**Manual Verification:**
1. Boot the `webserver` and `ai_service` locally.
2. Boot the `mcp_service`.
3. Using an MCP inspector or curl, test the `curriculum://references/all` resource to ensure data is retrieved from Django.
4. Run unit tests to verify local functionality.

---

## 🚀 Phase 2: Advancing to Complex Endpoints

Once the foundation is solid and verified, we will introduce the remaining features.

### 1. Specific Curriculum Reference Tool (`GET /api/curriculum-refs/{code}`)
- **Client Method:** Implement `lookup_curriculum_reference(code: str)` in `api_client.py` that calls `GET /api/curriculum-refs/{code}`.
- **MCP Definition:** In `main.py`, define a FastMCP Tool named `lookup_curriculum_reference` that accepts a `code` argument and returns the specific text.
- **Tests**: Add unit tests for this specific lookup.

### 2. Educational Modules Tool (`GET /api/modules`)
- **Client Method:** Add `get_educational_modules(ai_suggested: bool = None)` to `api_client.py`.
- **MCP Definition:** Define an MCP Tool in `main.py` that allows the agent to retrieve available educational modules from the database, optionally filtering by the `ai_suggested` flag.
- **Tests**: Add unit tests for the modules API client function.

### 3. Generative Metadata Tool (`POST /api/fill-work-plan`)
This is the most complex endpoint because it requires CSRF token exchange and handles long-running AI generation.
- **CSRF Exchange Module:**
  - Update `api_client.py` to maintain a session state.
  - Implement an initialization method that performs a basic `GET /` to the Django server to extract the `csrftoken` cookie.
  - Ensure subsequent `POST` requests include the `X-CSRFToken` header.
- **Client Method:** Implement `generate_lesson_metadata(activity: str, theme: str)` which performs the POST request. Ensure robust handling of timeouts (as the Django endpoint has a 120s timeout limit).
- **MCP Definition:** Define an MCP Tool `generate_lesson_metadata` in `main.py` that accepts the `activity` (required) and `theme` (optional) arguments.
- **Tests**: Add unit tests simulating the CSRF token exchange and metadata generation.

---

## 📚 Phase 3: Error Handling & Final Documentation

### 1. Resilient Error Handling
- Ensure that network failures (Django down, LangGraph down) are caught and returned as clean, informative MCP Tool errors, preventing the FastMCP service from crashing.
- Map Django's REST API error codes (e.g., `503 AI_SERVICE_UNAVAILABLE`) to user-friendly Polish responses where applicable.
- Add unit tests for all expected error pathways.

### 2. Comprehensive Documentation
- **Create `docs/mcp_api.md`**: Write a dedicated document explaining the full API surface that the FastMCP service exposes (Resources and Tools).
- **Update `docs/PRD.md`**: Annotate the document indicating the successful integration of the MCP API Gateway architecture.
