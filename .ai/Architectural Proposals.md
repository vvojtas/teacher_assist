# Architectural Proposals for MCP Integration

Based on the architecture of Teacher Assist (a Django backend serving a React frontend, with a separate LangGraph service) and the latest best practices for Model Context Protocol (MCP) integration, here are three architectural proposals to expose the Teacher Assist functionalities to AI agents.

---

## Proposal 1: Embedded MCP Endpoint within Django (using django-mcp-server)

### Short Description
Integrate the MCP server directly into the existing Django web server using a library like `django-mcp-server` or by wrapping a FastMCP instance. The server would be exposed as an HTTP-based Server-Sent Events (SSE) endpoint directly from Django (e.g., at `/mcp/sse`).

### Pros
- **Single Backend Service:** No need to manage, deploy, or monitor a third standalone service just for the MCP endpoint.
- **Direct Database Access:** The MCP tools can directly utilize the Django ORM to define tools (e.g., `lookup_curriculum_reference`) without HTTP overhead.
- **Shared Configuration:** Utilizes existing Django settings, environment variables, and connections.

### Cons
- **ASGI Requirement:** MCP over HTTP relies on Server-Sent Events (SSE) which requires asynchronous support. If the current Django app is heavily WSGI-based, you will need to switch to an ASGI server (like Daphne or Uvicorn).
- **Coupling:** Tightly couples the agent interface with the web application backend, potentially leading to monolith scaling issues in the future.

### Selection Advice
**Recommended if** you want to minimize the number of running services and are comfortable configuring Django with ASGI to support long-lived async connections.

---

## Proposal 2: Standalone FastMCP Service (API Gateway Approach)

### Short Description
Create a new, lightweight Python service using `FastMCP` that acts purely as an API gateway for agents. This service runs on its own port (e.g., 8002) and implements the MCP tools by making HTTP requests to the existing Django REST API endpoints (handling CSRF tokens and authentication as if it were a standard client).

### Pros
- **High Isolation (Microservices Pattern):** The core Django app remains untouched. The MCP service can be restarted, updated, or scaled independently.
- **Clear Boundaries:** Enforces strict usage of your well-defined REST API (`POST /api/fill-work-plan`, `GET /api/curriculum-refs`), ensuring all business logic and validations in Django are respected.
- **Framework Agnostic:** Easily built using FastMCP and standard HTTP clients (`httpx`), avoiding any complex Django configurations.

### Cons
- **Network Overhead:** Every tool call results in an extra internal HTTP hop (Agent -> MCP Service -> Django/LangGraph).
- **Operational Complexity:** Requires managing a third running process (alongside Django and LangGraph).
- **CSRF Workaround:** Needs to implement a mechanism to fetch and attach the Django `X-CSRFToken` before making POST requests.

### Selection Advice
**Highly Recommended** for this project. Since the MVP already separates the AI logic into LangGraph and the Web logic into Django, introducing a dedicated, isolated MCP gateway aligns perfectly with the current architecture and provides the cleanest separation of concerns.

---

## Proposal 3: Native Stdio CLI MCP Server (Integrated with Django ORM)

### Short Description
Instead of exposing MCP over a network port (SSE), build a Python CLI script that implements the MCP server communicating exclusively over standard input/output (`stdio`). The script will import `django.setup()` at startup to gain direct access to the database ORM, and use `requests` to call the LangGraph service directly for generation tools.

### Pros
- **Native Desktop Client Integration:** Standard `stdio` transport is the preferred method for many desktop AI tools (like Claude Desktop or Cursor). It avoids network port collisions entirely.
- **Performance:** Direct database access for reads (curriculum lookup) is extremely fast.
- **No Extra Server Management:** The server only runs when the agent invokes it. There is no long-running "server" process to monitor.

### Cons
- **Remote Access Limitations:** A `stdio` server must run locally on the same machine as the AI agent requesting it. It cannot easily be exposed over a network for remote agents without tunneling logic.
- **Startup Overhead:** Depending on the Django application size, booting `django.setup()` on every agent connection can introduce slight latency.

### Selection Advice
**Recommended if** the primary goal is allowing local agents (like Claude Desktop or an IDE assistant on the teacher's PC) to integrate with the Teacher Assist tools on the same machine. Not recommended if you plan to expose this system to remote or cloud-based AI agents.
