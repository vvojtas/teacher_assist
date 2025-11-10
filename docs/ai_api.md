# AI Service REST API Specification

**Version:** 1.0
**Date:** 2025-11-10
**Status:** Design Specification
**Project:** Teacher Assist - AI Service Integration

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [API Endpoints](#api-endpoints)
4. [Error Handling](#error-handling)
5. [Integration Patterns](#integration-patterns)
6. [Examples](#examples)

---

## Overview

This document defines the REST API interface between the Django web server and the LangGraph AI service. The AI service is responsible for generating educational metadata (modules, curriculum references, and objectives) based on activity descriptions provided by the teacher.

### Key Characteristics

- **Protocol:** HTTP/REST
- **Format:** JSON
- **Language:** Polish (all AI-generated content)
- **Timeout:** 120 seconds maximum per request
- **Rate Limiting:** Not implemented in MVP (single user, local deployment)
- **Authentication:** None (localhost-only deployment)

### Design Principles

1. **Simple and Focused:** Single primary endpoint for metadata generation
2. **Fail-Safe:** Graceful error handling allows manual fallback
3. **Stateless:** No session management; each request is independent
4. **Synchronous:** Request-response pattern (no async/webhooks in MVP)

---

## Architecture

```
┌─────────────────┐         HTTP POST          ┌─────────────────┐
│                 │ ───────────────────────────>│                 │
│  Django Server  │                             │  AI Service     │
│  (port 8000)    │                             │  (port 8001)    │
│                 │<─────────────────────────── │                 │
└─────────────────┘      JSON Response          └─────────────────┘
        │                                               │
        │                                               │
        ├─ Serves UI                                   ├─ LangGraph Workflow
        ├─ Manages session data                        ├─ OpenRouter LLM calls
        ├─ Stores curriculum refs (SQLite)             └─ JSON formatting
        └─ Orchestrates bulk operations
```

### Process Flow

1. **User triggers autofill** in Django UI (single row or bulk)
2. **Django validates** activity description exists
3. **Django sends POST request** to AI service with activity + theme
4. **AI service processes** via LangGraph workflow:
   - Activity classification
   - Module mapping
   - Curriculum reference selection
   - Objective generation (Polish)
5. **AI service returns** structured JSON response
6. **Django populates** table fields with received data
7. **User can edit** any generated content manually

---

## API Endpoints

### Base URL

```
http://localhost:8001
```

---

### 1. Generate Metadata

**Endpoint:** `/api/generate-metadata`
**Method:** `POST`
**Description:** Generates educational metadata (module, curriculum references, objectives) based on a planned activity description.

#### Request

**Headers:**
```http
Content-Type: application/json
Accept: application/json
```

**Body Schema:**
```json
{
  "activity": "string",    // Required: 1-500 characters
  "theme": "string"        // Optional: 0-200 characters
}
```

**Field Descriptions:**

| Field | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| `activity` | string | Yes | 1-500 chars | Teacher's description of planned activity (Polish) |
| `theme` | string | No | 0-200 chars | Weekly theme for context (Polish) |

**Validation Rules:**
- `activity` cannot be empty string
- `activity` length: 1-500 characters
- `theme` is optional; if provided, max 200 characters
- Both fields should be UTF-8 encoded Polish text

**Example Request:**
```json
{
  "activity": "Zabawa w sklep z owocami",
  "theme": "Jesień - zbiory"
}
```

#### Success Response

**Status Code:** `200 OK`

**Body Schema:**
```json
{
  "module": "string",
  "curriculum_refs": ["string"],
  "objectives": ["string"]
}
```

**Field Descriptions:**

| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| `module` | string | Educational module name (Polish) | 1-100 chars, uppercase recommended |
| `curriculum_refs` | array[string] | Podstawa Programowa paragraph codes | 1-10 items, valid reference format |
| `objectives` | array[string] | Learning objectives (Polish) | 2-4 items, 20-200 chars each |

**Validation Rules:**
- `module` must be non-empty, valid Polish educational module
- `curriculum_refs` must contain valid reference codes (e.g., "4.15", "3.8")
- `curriculum_refs` should have 1-10 items
- `objectives` should contain 2-3 objectives (4 maximum)
- All text must be in natural Polish (no translation artifacts)

**Example Response:**
```json
{
  "module": "MATEMATYKA",
  "curriculum_refs": ["4.15", "4.18"],
  "objectives": [
    "Dziecko potrafi przeliczać w zakresie 5",
    "Rozpoznaje poznane wcześniej cyfry"
  ]
}
```

#### Error Responses

**Status Code:** `400 Bad Request`

**Description:** Invalid request data

**Body Schema:**
```json
{
  "error_code": "VALIDATION_ERROR",
  "error": "string",
  "details": {
    "field": "string",
    "reason": "string"
  }
}
```

**Example:**
```json
{
  "error_code": "VALIDATION_ERROR",
  "error": "Activity field is required",
  "details": {
    "field": "activity",
    "reason": "Field is empty or missing"
  }
}
```

**Status Code:** `500 Internal Server Error`

**Description:** AI service internal error

**Body Schema:**
```json
{
  "error_code": "INTERNAL_ERROR",
  "error": "string"
}
```

**Example:**
```json
{
  "error_code": "INTERNAL_ERROR",
  "error": "LLM API call failed"
}
```

**Status Code:** `503 Service Unavailable`

**Description:** AI service or dependency unavailable

**Body Schema:**
```json
{
  "error_code": "SERVICE_UNAVAILABLE",
  "error": "string"
}
```

**Example:**
```json
{
  "error_code": "SERVICE_UNAVAILABLE",
  "error": "OpenRouter API is unreachable"
}
```

**Status Code:** `504 Gateway Timeout`

**Description:** LLM request exceeded timeout

**Body Schema:**
```json
{
  "error_code": "LLM_TIMEOUT",
  "error": "string"
}
```

**Example:**
```json
{
  "error_code": "LLM_TIMEOUT",
  "error": "LLM request exceeded 120 second timeout"
}
```

#### Performance Expectations

- **Target Response Time:** < 10 seconds (user experience goal)
- **Maximum Timeout:** 120 seconds (Django client should enforce)
- **Expected Token Usage:** ~200-500 tokens per request (input + output)

---

### 2. Health Check

**Endpoint:** `/health`
**Method:** `GET`
**Description:** Checks if the AI service is running and ready to accept requests.

#### Request

**Headers:**
```http
Accept: application/json
```

**Body:** None

#### Success Response

**Status Code:** `200 OK`

**Body Schema:**
```json
{
  "status": "healthy",
  "version": "string",
  "timestamp": "string"
}
```

**Example Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2025-11-10T14:30:00Z"
}
```

#### Error Responses

**Status Code:** `503 Service Unavailable`

**Description:** Service is starting up or dependencies unavailable

**Body Schema:**
```json
{
  "status": "unhealthy",
  "error": "string"
}
```

**Example:**
```json
{
  "status": "unhealthy",
  "error": "OpenRouter API key not configured"
}
```

#### Usage Pattern

Django should call this endpoint:
- On application startup (optional - for diagnostic purposes)
- Before bulk operations (optional - to show user-friendly error early)
- For debugging/diagnostics

**Note:** Health check is optional for MVP. Django can rely on catching errors from the main endpoint.

---

## Error Handling

### Error Code Reference

| Error Code | HTTP Status | Description | Django Action |
|------------|-------------|-------------|---------------|
| `VALIDATION_ERROR` | 400 | Invalid request data | Show validation error to user |
| `INTERNAL_ERROR` | 500 | AI service internal error | Show generic error, allow manual entry |
| `SERVICE_UNAVAILABLE` | 503 | AI service or LLM unavailable | Show "service unavailable" message |
| `LLM_TIMEOUT` | 504 | LLM request timeout | Show timeout message, allow retry |
| `LLM_ERROR` | 500 | LLM returned invalid response | Show "AI error" message, allow retry |

### Error Messages (Polish)

Django should translate error codes to user-friendly Polish messages:

```python
ERROR_MESSAGES = {
    "VALIDATION_ERROR": "Nieprawidłowe dane wejściowe. Sprawdź opis aktywności.",
    "INTERNAL_ERROR": "Błąd usługi AI. Wypełnij dane ręcznie lub spróbuj ponownie.",
    "SERVICE_UNAVAILABLE": "Nie można połączyć z usługą AI. Wypełnij dane ręcznie.",
    "LLM_TIMEOUT": "Przekroczono limit czasu. Spróbuj ponownie z krótszym opisem.",
    "LLM_ERROR": "Otrzymano nieprawidłową odpowiedź. Spróbuj ponownie.",
    "NETWORK_ERROR": "Błąd połączenia. Sprawdź czy usługa AI jest uruchomiona.",
}
```

### Timeout Handling

**Django client configuration:**
```python
import requests

TIMEOUT = 120  # seconds (matches PRD requirement)

try:
    response = requests.post(
        "http://localhost:8001/api/generate-metadata",
        json={"activity": activity, "theme": theme},
        timeout=TIMEOUT
    )
except requests.exceptions.Timeout:
    # Show timeout error message to user
    return handle_timeout_error()
except requests.exceptions.ConnectionError:
    # Show connection error message
    return handle_connection_error()
```

### Response Validation

Django must validate AI service responses before displaying to user:

**Required validations:**
1. Response is valid JSON
2. All required fields present (`module`, `curriculum_refs`, `objectives`)
3. `curriculum_refs` are valid codes (exist in Django's SQLite database)
4. `objectives` array has 2-4 items
5. All text fields are non-empty strings

**Example validation:**
```python
def validate_ai_response(data):
    """Validate AI service response structure and content."""
    if not isinstance(data, dict):
        raise ValidationError("Response is not a JSON object")

    # Check required fields
    required_fields = ["module", "curriculum_refs", "objectives"]
    for field in required_fields:
        if field not in data:
            raise ValidationError(f"Missing required field: {field}")

    # Validate curriculum refs exist in database
    for ref_code in data["curriculum_refs"]:
        if not CurriculumReference.objects.filter(code=ref_code).exists():
            # Log warning but don't fail - AI might suggest valid but unknown refs
            logger.warning(f"Unknown curriculum reference: {ref_code}")

    # Validate objectives count
    if not (2 <= len(data["objectives"]) <= 4):
        logger.warning(f"Unexpected objectives count: {len(data['objectives'])}")

    return data
```

---

## Integration Patterns

### Single Row Autofill

**User Flow:**
1. User enters activity in row
2. User clicks "Wypełnij AI" button
3. Django shows loading spinner on row
4. Django calls `/api/generate-metadata`
5. Django receives response and populates fields
6. User can edit any field manually

**Django Implementation:**
```python
def autofill_row(activity, theme=None):
    """Generate metadata for a single activity."""
    try:
        response = requests.post(
            "http://localhost:8001/api/generate-metadata",
            json={"activity": activity, "theme": theme},
            timeout=120
        )
        response.raise_for_status()
        data = response.json()

        # Validate response
        validated_data = validate_ai_response(data)

        return {
            "success": True,
            "data": validated_data
        }

    except requests.exceptions.Timeout:
        return {
            "success": False,
            "error_code": "TIMEOUT",
            "message": ERROR_MESSAGES["LLM_TIMEOUT"]
        }

    except requests.exceptions.ConnectionError:
        return {
            "success": False,
            "error_code": "CONNECTION",
            "message": ERROR_MESSAGES["NETWORK_ERROR"]
        }

    except requests.exceptions.HTTPError as e:
        error_data = e.response.json() if e.response else {}
        error_code = error_data.get("error_code", "INTERNAL_ERROR")
        return {
            "success": False,
            "error_code": error_code,
            "message": ERROR_MESSAGES.get(error_code, "Nieznany błąd")
        }
```

### Bulk Autofill

**User Flow:**
1. User enters activities in multiple rows
2. User clicks "Wypełnij wszystko AI" button
3. Django shows progress bar "Przetwarzanie... (1/5)"
4. Django calls `/api/generate-metadata` sequentially for each row
5. Django updates progress after each row
6. Individual row failures don't stop bulk operation

**Django Implementation:**
```python
def autofill_bulk(activities, theme=None):
    """Generate metadata for multiple activities sequentially."""
    results = []
    total = len(activities)

    for index, activity in enumerate(activities):
        # Update progress (via WebSocket or polling)
        update_progress(index + 1, total)

        # Call AI service for this row
        result = autofill_row(activity, theme)
        results.append(result)

        # Optional: short delay between requests to be nice to API
        # time.sleep(0.5)

    return {
        "total": total,
        "successful": sum(1 for r in results if r["success"]),
        "failed": sum(1 for r in results if not r["success"]),
        "results": results
    }
```

### Regenerate Flow

**User Flow:**
1. User is not satisfied with AI-generated content
2. User clicks "Generuj ponownie" button
3. Django shows confirmation if user edited the row
4. Django calls `/api/generate-metadata` with same inputs
5. Django replaces fields with new response

**Implementation:**
- Uses same `autofill_row()` function
- Django tracks if fields were user-edited
- Shows confirmation dialog before overwriting user edits

---

## Examples

### Example 1: Autumn Theme Activity

**Request:**
```http
POST /api/generate-metadata HTTP/1.1
Host: localhost:8001
Content-Type: application/json

{
  "activity": "Sortowanie kasztanów według wielkości",
  "theme": "Jesień - zbiory"
}
```

**Response:**
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "module": "MATEMATYKA",
  "curriculum_refs": ["4.15", "4.16"],
  "objectives": [
    "Dziecko potrafi sortować obiekty według jednej cechy",
    "Rozróżnia pojęcia wielkości: duży, mały, średni"
  ]
}
```

### Example 2: Art Activity

**Request:**
```http
POST /api/generate-metadata HTTP/1.1
Host: localhost:8001
Content-Type: application/json

{
  "activity": "Malowanie liści farbami",
  "theme": "Jesień - zbiory"
}
```

**Response:**
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "module": "FORMY PLASTYCZNE",
  "curriculum_refs": ["3.2", "3.5"],
  "objectives": [
    "Dziecko rozwija koordynację wzrokowo-ruchową",
    "Potrafi posługiwać się farbami i pędzlem",
    "Zapoznaje się z jesiennymi kolorami"
  ]
}
```

### Example 3: Movement Activity (No Theme)

**Request:**
```http
POST /api/generate-metadata HTTP/1.1
Host: localhost:8001
Content-Type: application/json

{
  "activity": "Zabawa ruchowa przy piosence Biegnę do przedszkola"
}
```

**Response:**
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "module": "MOTORYKA DUŻA",
  "curriculum_refs": ["2.3", "2.8"],
  "objectives": [
    "Dziecko rozwija sprawność ruchową",
    "Ćwiczy koordynację ruchów do rytmu muzyki"
  ]
}
```

### Example 4: Validation Error

**Request:**
```http
POST /api/generate-metadata HTTP/1.1
Host: localhost:8001
Content-Type: application/json

{
  "activity": "",
  "theme": "Jesień"
}
```

**Response:**
```http
HTTP/1.1 400 Bad Request
Content-Type: application/json

{
  "error_code": "VALIDATION_ERROR",
  "error": "Activity field cannot be empty",
  "details": {
    "field": "activity",
    "reason": "Field length must be between 1-500 characters"
  }
}
```

### Example 5: Service Unavailable

**Request:**
```http
POST /api/generate-metadata HTTP/1.1
Host: localhost:8001
Content-Type: application/json

{
  "activity": "Zabawa w sklep z owocami"
}
```

**Response:**
```http
HTTP/1.1 503 Service Unavailable
Content-Type: application/json

{
  "error_code": "SERVICE_UNAVAILABLE",
  "error": "OpenRouter API is currently unavailable"
}
```

---

## Implementation Checklist

### AI Service (LangGraph/FastAPI) Responsibilities

- [ ] Implement POST `/api/generate-metadata` endpoint
- [ ] Implement GET `/health` endpoint
- [ ] Validate request body schema
- [ ] Enforce character limits (activity: 500, theme: 200)
- [ ] Call OpenRouter LLM via LangGraph workflow
- [ ] Generate Polish educational metadata
- [ ] Validate curriculum references
- [ ] Format response as JSON
- [ ] Handle LLM errors gracefully
- [ ] Implement 120-second timeout
- [ ] Return appropriate HTTP status codes
- [ ] Log errors for debugging

### Django Server Responsibilities

- [ ] Create HTTP client with 120-second timeout
- [ ] Build request JSON from user input
- [ ] Handle network errors (connection, timeout)
- [ ] Validate AI service response structure
- [ ] Cross-check curriculum references with SQLite database
- [ ] Translate error codes to Polish messages
- [ ] Implement single row autofill view
- [ ] Implement bulk autofill with progress tracking
- [ ] Show loading states in UI
- [ ] Allow manual override of all fields
- [ ] Implement regenerate functionality
- [ ] Log AI service interactions for debugging

---

## Future Enhancements (Post-MVP)

**Not included in MVP but may be considered:**

1. **Batch Endpoint:** Single API call with array of activities (more efficient than sequential calls)
2. **Streaming Response:** Server-sent events for real-time progress on long generations
3. **Caching:** Cache responses for identical activity+theme combinations
4. **Feedback API:** Allow teachers to rate AI suggestions for model improvement
5. **Module Suggestions:** Endpoint to get list of suggested modules based on activity keywords
6. **Authentication:** API key or token-based auth if deployed beyond localhost

---

## Related Documents

- [PRD.md](PRD.md) - Product Requirements Document
- [db_schema.md](db_schema.md) - Database schema for curriculum references
- [CLAUDE.md](../CLAUDE.md) - Development guidelines

---

**Document Version History**

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-11-10 | Architecture Team | Initial API specification |
