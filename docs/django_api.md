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

## Use Cases

### UC1: Single Row AI Autofill
**User Story 3:** Teacher enters activity, clicks "Wypełnij AI" button
**Flow:** Frontend → Django `/api/fill-work-plan` → LangGraph → Django → Frontend

### UC2: Bulk AI Autofill
**User Story 4:** Teacher clicks "Wypełnij wszystko AI" for multiple rows
**Flow:** Frontend makes multiple sequential calls to `/api/fill-work-plan`

### UC3: Regenerate Metadata
**User Story 10:** Teacher unsatisfied with AI output, clicks "Generuj ponownie"
**Flow:** Same as UC1, called again with same input

### UC4: Curriculum Reference Tooltips
**User Story 6:** Teacher hovers over curriculum reference code (e.g., "I.1.2")
**Flow:** Frontend uses data from `/api/curriculum-references` (loaded on page load)

### UC5: Page Load Initialization
**User Story 1:** Teacher opens application
**Flow:** Frontend loads curriculum references and optionally modules list

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
  "modul": "Zabawy matematyczne",
  "podstawa_programowa": ["I.1.2", "II.3.1"],
  "cele": [
    "Rozwijanie umiejętności liczenia",
    "Poznawanie nazw owoców sezonowych"
  ]
}
```

**Response Schema:**
| Field | Type | Description |
|-------|------|-------------|
| `modul` | string | Educational module name |
| `podstawa_programowa` | array[string] | Curriculum reference codes |
| `cele` | array[string] | Educational objectives (typically 2-3) |

**Error Responses:**

**400 Bad Request** - Invalid input
```json
{
  "error": "Pole 'activity' nie może być puste",
  "error_code": "INVALID_INPUT"
}
```

**503 Service Unavailable** - LangGraph service down
```json
{
  "error": "Nie można połączyć z usługą AI. Wypełnij dane ręcznie.",
  "error_code": "AI_SERVICE_UNAVAILABLE"
}
```

**504 Gateway Timeout** - LangGraph response timeout (>120s)
```json
{
  "error": "Przekroczono limit czasu oczekiwania. Spróbuj ponownie.",
  "error_code": "AI_SERVICE_TIMEOUT"
}
```

**500 Internal Server Error** - Other errors
```json
{
  "error": "Wystąpił nieoczekiwany błąd. Spróbuj ponownie.",
  "error_code": "INTERNAL_ERROR"
}
```

**Implementation Notes:**
- Django proxies request to LangGraph service at `http://localhost:8001/api/fill-work-plan`
- Timeout: 120 seconds (as per PRD section 6.2)
- Validates input before forwarding to LangGraph
- Transforms/validates response from LangGraph before returning to frontend
- Logs all requests and responses for debugging

**Validation Rules:**
- `activity` must not be empty or whitespace-only
- `activity` length: 1-500 characters
- `theme` is optional; if provided, max 200 characters
- Response `podstawa_programowa` codes should match format: `Roman.Arabic.Arabic`

---

### 2. Get All Curriculum References

Returns complete dictionary of curriculum reference codes and their full Polish text. Used for tooltip display.

**Endpoint:** `GET /api/curriculum-references`

**Request Headers:** None required

**Query Parameters:** None

**Success Response (200 OK):**
```json
{
  "references": {
    "I.1.1": "Dziecko rozumie pojęcie ilości i potrafi liczyć do 10",
    "I.1.2": "Dziecko rozpoznaje cyfry i umie je zapisać",
    "II.3.1": "Dziecko zna nazwy owoców i warzyw sezonowych",
    "II.3.2": "Dziecko rozumie podstawowe pojęcia matematyczne"
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

**500 Internal Server Error** - Database error
```json
{
  "error": "Nie można pobrać danych z bazy",
  "error_code": "DATABASE_ERROR"
}
```

**Implementation Notes:**
- Queries `curriculum_references` table
- Returns all records as key-value pairs
- Response should be cached on frontend (data rarely changes)
- Consider adding `Last-Modified` header for caching
- Data loaded on page initialization

**Performance:**
- Target response time: <500ms
- Expected payload size: ~50-100 references (estimated 5-10KB)
- Can be cached indefinitely on frontend

---

### 3. Lookup Curriculum Reference by Code

Retrieves full text for a specific curriculum reference code. Alternative to bulk loading.

**Endpoint:** `GET /api/curriculum-references/<code>`

**Path Parameters:**
| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `code` | string | Curriculum reference code | `I.1.2` |

**Example Request:**
```
GET /api/curriculum-references/I.1.2
```

**Success Response (200 OK):**
```json
{
  "reference_code": "I.1.2",
  "full_text": "Dziecko rozpoznaje cyfry i umie je zapisać",
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

**404 Not Found** - Curriculum reference does not exist
```json
{
  "error": "Nie znaleziono odniesienia do podstawy programowej",
  "error_code": "REFERENCE_NOT_FOUND",
  "requested_code": "I.1.2"
}
```

**400 Bad Request** - Invalid code format
```json
{
  "error": "Nieprawidłowy format kodu podstawy programowej",
  "error_code": "INVALID_CODE_FORMAT"
}
```

**Implementation Notes:**
- Queries `curriculum_references` table by `reference_code`
- Returns 404 if reference not found (not an error, just missing data)
- Code format validation: Should match pattern `[IVX]+\.\d+\.\d+` (Roman.Number.Number)
- Consider URL encoding for special characters (though unlikely in curriculum codes)

**Use Cases:**
- On-demand tooltip loading (if not using bulk load)
- Validation of AI-generated curriculum codes
- Debugging/verification during development

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
      "name": "Zabawy matematyczne",
      "is_ai_suggested": false,
      "created_at": "2025-10-28T10:00:00Z"
    },
    {
      "id": 2,
      "name": "Rozwój społeczny",
      "is_ai_suggested": false,
      "created_at": "2025-10-28T10:00:00Z"
    },
    {
      "id": 3,
      "name": "Eksperymenty naukowe",
      "is_ai_suggested": true,
      "created_at": "2025-10-29T14:30:00Z"
    }
  ],
  "count": 3
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

**500 Internal Server Error** - Database error
```json
{
  "error": "Nie można pobrać listy modułów",
  "error_code": "DATABASE_ERROR"
}
```

**Implementation Notes:**
- Queries `educational_modules` table
- Supports filtering by `is_ai_suggested` flag
- Ordered alphabetically by `name`
- Can be used for frontend autocomplete/suggestions
- New modules may be added by AI during operation

**MVP Status:** Optional endpoint - not critical for core workflow. May be deferred to Phase 2.

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

---

## Database Models Reference

### Curriculum References Table
```python
# Model: CurriculumReference
# Table: curriculum_references

Fields:
- id: AutoField (primary key)
- reference_code: CharField(max_length=20, unique=True)
  Example: "I.1.2"
- full_text: TextField
  Example: "Dziecko rozpoznaje cyfry i umie je zapisać"
- created_at: DateTimeField(auto_now_add=True)
```

### Educational Modules Table
```python
# Model: EducationalModule
# Table: educational_modules

Fields:
- id: AutoField (primary key)
- module_name: CharField(max_length=200, unique=True)
  Example: "Zabawy matematyczne"
- is_ai_suggested: BooleanField(default=True)
- created_at: DateTimeField(auto_now_add=True)
```

**Note:** Session data (themes, activities, generated metadata) is NOT persisted in MVP.

---

## CORS and Security

### MVP Security Profile
- **Authentication:** None (local deployment only)
- **HTTPS:** Not required (localhost only)
- **CORS:** Not needed (same origin)
- **API Key:** Not required for Django endpoints

### LangGraph Service Communication
- Django backend holds OpenRouter API key (environment variable)
- API key NEVER exposed to frontend
- LangGraph service only accepts connections from localhost

### Future Considerations (Post-MVP)
- Add authentication when moving to multi-user deployment
- Implement rate limiting for AI calls
- Add CSRF protection for state-changing operations
- Use HTTPS in production

---

## Performance Requirements

Based on PRD Section 7.6:

| Endpoint | Target Response Time | Notes |
|----------|---------------------|-------|
| `POST /api/fill-work-plan` | < 30s | Includes LangGraph call; 120s timeout |
| `GET /api/curriculum-references` | < 500ms | Database query, ~50-100 records |
| `GET /api/curriculum-references/<code>` | < 200ms | Single record lookup |
| `GET /api/modules` | < 500ms | Database query |

**Frontend Experience:**
- Show loading indicators immediately
- Display progress for bulk operations
- Allow user to continue working (non-blocking where possible)

---

## Testing Endpoints

### Manual Testing with cURL

**Test Fill Work Plan:**
```bash
curl -X POST http://localhost:8000/api/fill-work-plan \
  -H "Content-Type: application/json" \
  -d '{
    "activity": "Zabawa w sklep z owocami",
    "theme": "Jesień - zbiory"
  }'
```

**Test Get All Curriculum References:**
```bash
curl http://localhost:8000/api/curriculum-references
```

**Test Lookup Specific Reference:**
```bash
curl http://localhost:8000/api/curriculum-references/I.1.2
```

**Test Get Modules:**
```bash
curl http://localhost:8000/api/modules
```

### Test Data Requirements

For testing, seed database with:
- At least 10-20 curriculum references
- At least 5-8 predefined educational modules
- Mix of predefined and AI-suggested modules

---

## Implementation Checklist

### Phase 1: Core Endpoints
- [ ] Implement `POST /api/fill-work-plan`
  - [ ] Input validation
  - [ ] LangGraph HTTP client integration
  - [ ] Timeout handling (120s)
  - [ ] Error transformation to Polish
  - [ ] Response validation
- [ ] Implement `GET /api/curriculum-references`
  - [ ] Query all curriculum references
  - [ ] Return as dictionary
  - [ ] Handle empty database gracefully
- [ ] Implement `GET /api/curriculum-references/<code>`
  - [ ] Single record lookup
  - [ ] Return 404 for missing codes
  - [ ] Code format validation

### Phase 2: Optional Endpoints
- [ ] Implement `GET /api/modules`
  - [ ] Query educational modules
  - [ ] Support filtering
  - [ ] Alphabetical ordering

### Phase 3: Testing & Polish
- [ ] Write unit tests for all endpoints
- [ ] Test error scenarios
- [ ] Verify all error messages in Polish
- [ ] Load testing (especially bulk operations)
- [ ] Integration testing with LangGraph service

---

## Related Documentation

- [PRD.md](./PRD.md) - Product Requirements Document
- [CLAUDE.md](../CLAUDE.md) - Development guidelines and git workflow
- LangGraph API specification (see PRD.md Section 7.3)

---

## Changelog

| Date | Version | Changes |
|------|---------|---------|
| 2025-10-30 | 1.0 | Initial Django API specification for MVP |
