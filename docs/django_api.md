# Django Backend API Documentation

**Project:** Teacher Assist - AI-Powered Lesson Planning Tool
**Version:** 1.0 (MVP)
**Base URL:** `http://localhost:8000`
**Last Updated:** 2025-10-30

---

## Overview

The Django backend serves as the intermediary between the frontend UI and the LangGraph AI service. It provides REST API endpoints for:
1. AI-powered metadata generation (proxying to LangGraph service)
2. Curriculum reference data access
3. Educational module information

All responses are in JSON format. The UI and all user-facing content is in Polish.

---

## Architecture Context

```
Frontend (JavaScript)
       ↓
Django Backend (localhost:8000) ← YOU ARE HERE
   ├── API Endpoints (this document)
   ├── SQLite Database (curriculum_references, educational_modules)
   └── HTTP Client (requests to LangGraph)
       ↓
LangGraph AI Service (localhost:8001)
```

---


## API Endpoints

### 1. Fill Work Plan (AI Metadata Generation)

Generates educational metadata (module, curriculum references, objectives) for a given activity.

**Endpoint:** `POST /api/fill-work-plan`

**Request Headers:**
```
Content-Type: application/json
```

**Request Body:**
```json
{
  "activity": "Zabawa w sklep z owocami",
  "theme": "Jesień - zbiory"
}
```

**Request Schema:**
| Field | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| `activity` | string | Yes | 1-500 chars | Teacher's activity description |
| `theme` | string | No | 0-200 chars | Weekly theme (optional context) |

**Success Response (200 OK):**
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

**Response Schema:**
| Field | Type | Description |
|-------|------|-------------|
| `module` | string | Educational module name |
| `curriculum_refs` | array[string] | Curriculum reference codes |
| `objectives` | array[string] | Educational objectives (typically 2-3) |

**Error Responses:**
- `400 INVALID_INPUT` - Empty or invalid activity field
- `503 AI_SERVICE_UNAVAILABLE` - LangGraph service unreachable
- `504 AI_SERVICE_TIMEOUT` - Request exceeds 120s timeout
- `500 INTERNAL_ERROR` - Unexpected server errors

*See [Error Handling Guidelines](#error-handling-guidelines) for full error response format.*

**Implementation Notes:**
- Proxies to LangGraph service at `http://localhost:8001/api/fill-work-plan` with 120s timeout
- Validates: `activity` (1-500 chars, non-empty), `theme` (optional, max 200 chars)

---

### 2. Get All Curriculum References

Returns complete dictionary of curriculum reference codes and their full Polish text. Used for tooltip display.

**Endpoint:** `GET /api/curriculum-refs`

**Request Headers:** None required

**Query Parameters:** None

**Success Response (200 OK):**
```json
{
  "references": {
    "1.1": "zgłasza potrzeby fizjologiczne, samodzielnie wykonuje podstawowe czynności higieniczne;",
    "2.5": "rozstaje się z rodzicami bez lęku, ma świadomość, że rozstanie takie bywa dłuższe lub krótsze;",
    "3.8": "obdarza uwagą inne dzieci i osoby dorosłe;",
    "4.15": "przelicza elementy zbiorów w czasie zabawy, prac porządkowych, ćwiczeń i wykonywania innych czynności, posługuje się liczebnikami głównymi i porządkowymi, rozpoznaje cyfry oznaczające liczby od 0 do 10, eksperymentuje z tworzeniem kolejnych liczb, wykonuje dodawanie i odejmowanie w sytuacji użytkowej, liczy obiekty, odróżnia liczenie błędne od poprawnego;"
  },
  "count": 4
}
```

**Response Schema:**
| Field | Type | Description |
|-------|------|-------------|
| `references` | object | Dictionary mapping curriculum codes to full text |
| `count` | integer | Total number of curriculum references |

**Error Responses:**
- `500 DATABASE_ERROR` - Database query failure

*See [Error Handling Guidelines](#error-handling-guidelines) for full error response format.*

**Implementation Notes:**
- Queries all records from `curriculum_references` table
- Frontend should cache response (data rarely changes)
- Expected payload: ~50-100 references (5-10KB), <500ms response time

---

### 3. Lookup Curriculum Reference by Code

Retrieves full text for a specific curriculum reference code. Alternative to bulk loading.

**Endpoint:** `GET /api/curriculum-refs/<code>`

**Path Parameters:**
| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `code` | string | Curriculum reference code | `3.8` |

**Example Request:**
```
GET /api/curriculum-refs/3.8
```

**Success Response (200 OK):**
```json
{
  "reference_code": "3.8",
  "full_text": "obdarza uwagą inne dzieci i osoby dorosłe;",
  "created_at": "2025-10-28T10:30:00Z"
}
```

**Response Schema:**
| Field | Type | Description |
|-------|------|-------------|
| `reference_code` | string | The curriculum reference code |
| `full_text` | string | Complete Polish text of the curriculum requirement |
| `created_at` | string (ISO 8601) | When this reference was added to database |

**Error Responses:**
- `404 REFERENCE_NOT_FOUND` - Curriculum reference code doesn't exist
- `400 INVALID_CODE_FORMAT` - Invalid code format

*See [Error Handling Guidelines](#error-handling-guidelines) for full error response format.*

**Implementation Notes:**
- Single record lookup from `curriculum_references` table by code
- Use case: On-demand tooltip loading or debugging

---

### 4. Get Educational Modules (Optional)

Returns list of known educational modules. Can be used for autocomplete or validation.

**Endpoint:** `GET /api/modules`

**Request Headers:** None required

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `ai_suggested` | boolean | No | Filter by whether module was AI-suggested (`true`/`false`) |

**Example Requests:**
```
GET /api/modules
GET /api/modules?ai_suggested=false
```

**Success Response (200 OK):**
```json
{
  "modules": [
    {
      "id": 1,
      "name": "JĘZYK",
      "is_ai_suggested": false,
      "created_at": "2025-10-28T10:00:00Z"
    },
    {
      "id": 2,
      "name": "MATEMATYKA",
      "is_ai_suggested": false,
      "created_at": "2025-10-28T10:00:00Z"
    },
    {
      "id": 3,
      "name": "MOTORYKA DUŻA",
      "is_ai_suggested": false,
      "created_at": "2025-10-28T10:00:00Z"
    },
    {
      "id": 4,
      "name": "FORMY PLASTYCZNE",
      "is_ai_suggested": false,
      "created_at": "2025-10-28T10:00:00Z"
    }
  ],
  "count": 4
}
```

**Response Schema:**
| Field | Type | Description |
|-------|------|-------------|
| `modules` | array[object] | List of educational modules |
| `modules[].id` | integer | Unique module ID |
| `modules[].name` | string | Module name in Polish |
| `modules[].is_ai_suggested` | boolean | Whether module was suggested by AI (not predefined) |
| `modules[].created_at` | string (ISO 8601) | When module was added |
| `count` | integer | Total number of modules returned |

**Error Responses:**
- `500 DATABASE_ERROR` - Database query failure

*See [Error Handling Guidelines](#error-handling-guidelines) for full error response format.*

**Implementation Notes:**
- Queries `educational_modules` table, ordered alphabetically
- Optional filtering by `is_ai_suggested` flag
- **MVP Status:** Optional endpoint (may be deferred to Phase 2)

---

## Error Handling Guidelines

### Error Response Format (Standard)

All error responses follow this structure:
```json
{
  "error": "Human-readable error message in Polish",
  "error_code": "MACHINE_READABLE_CODE",
  "details": {}  // Optional additional context
}
```

### Error Code Categories

| Code Prefix | Category | HTTP Status | Description |
|-------------|----------|-------------|-------------|
| `INVALID_*` | Validation | 400 | Client sent invalid data |
| `NOT_FOUND_*` | Resource | 404 | Requested resource doesn't exist |
| `AI_SERVICE_*` | External | 503/504 | LangGraph service issues |
| `DATABASE_*` | Internal | 500 | Database connection/query errors |
| `INTERNAL_*` | Internal | 500 | Unexpected server errors |

### Error Messages (Polish)

All error messages must be in Polish, user-friendly, and actionable:

**Good:**
- "Nie można połączyć z usługą AI. Wypełnij dane ręcznie."
- "Pole 'activity' jest wymagane"

**Bad:**
- "500 Internal Server Error"
- "Connection refused to 127.0.0.1:8001"

### Timeout Handling

- **AI Service Timeout:** 120 seconds (as per PRD 6.2)
- Use `requests.timeout` parameter when calling LangGraph
- Return 504 Gateway Timeout with user-friendly Polish message


## CORS and Security

**MVP:** Local deployment only - no authentication, HTTPS, or CORS required. Django backend holds OpenRouter API key (environment variable); never exposed to frontend. LangGraph service only accepts localhost connections.

