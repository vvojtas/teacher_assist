# AI Service REST API Documentation

**Project:** Teacher Assist - LangGraph AI Service
**Version:** 1.0 (MVP)
**Base URL:** `http://localhost:8001`
**Last Updated:** 2025-11-10

---

## Overview

The LangGraph AI service generates educational metadata (modules, curriculum references, objectives) based on activity descriptions. Django server proxies requests to this service.

**Key Characteristics:**
- Protocol: HTTP/REST
- Format: JSON
- Language: Polish (all AI-generated content)
- Timeout: 120 seconds maximum
- Authentication: None (localhost-only)

---

## Architecture Context

```
Django Backend (localhost:8000)
       ↓
LangGraph AI Service (localhost:8001) ← YOU ARE HERE
   ├── API Endpoints (this document)
   ├── LangGraph Workflow
   └── OpenRouter LLM Gateway
```

---

## API Endpoints

### 1. Fill Work Plan (AI Metadata Generation)

Generates educational metadata for a given activity description.

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
| `activity` | string | Yes | 1-500 chars | Teacher's activity description (Polish) |
| `theme` | string | No | 0-200 chars | Weekly theme for context |

**Success Response (200 OK):**
```json
{
  "activity": "Zabawa w sklep z owocami",
  "modules": ["MATEMATYKA"],
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
| `activity` | string | Activity description (echoed from request) |
| `modules` | array[string] | Educational module names (Polish, uppercase, 1-4 items) |
| `curriculum_refs` | array[string] | Podstawa Programowa codes (1-10 items) |
| `objectives` | array[string] | Learning objectives (typically 2-3) |

**Error Responses:**
- `400 VALIDATION_ERROR` - Empty or invalid activity field
- `500 INTERNAL_ERROR` - LLM API call failed
- `503 SERVICE_UNAVAILABLE` - OpenRouter API unreachable
- `504 LLM_TIMEOUT` - Request exceeded 120s timeout

*See [Error Handling](#error-handling) for full error response format.*

**Implementation Notes:**
- Processes via LangGraph workflow (activity classification → module mapping → curriculum lookup → objective generation)
- Calls OpenRouter LLM for natural Polish text generation
- Target response: < 10 seconds
- Token budget: ~200-500 tokens per request

---

### 2. Health Check (Optional)

**Endpoint:** `GET /health`

**Success Response (200 OK):**
```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

**Error Response (503 Service Unavailable):**
```json
{
  "status": "unhealthy",
  "error": "OpenRouter API key not configured"
}
```

**Implementation Notes:**
- Optional for MVP
- Can be used for diagnostics or startup checks

---

## Error Handling

### Error Response Format

All error responses follow this structure:
```json
{
  "error": "Human-readable error description",
  "error_code": "MACHINE_READABLE_CODE",
  "details": {}  // Optional
}
```

### Error Codes

| Error Code | HTTP Status | Description |
|------------|-------------|-------------|
| `VALIDATION_ERROR` | 400 | Invalid request data |
| `INTERNAL_ERROR` | 500 | AI service internal error |
| `SERVICE_UNAVAILABLE` | 503 | OpenRouter API unavailable |
| `LLM_TIMEOUT` | 504 | LLM request timeout |

---

## Examples

### Example 1: Math Activity

**Request:**
```json
{
  "activity": "Sortowanie kasztanów według wielkości",
  "theme": "Jesień - zbiory"
}
```

**Response (200 OK):**
```json
{
  "activity": "Sortowanie kasztanów według wielkości",
  "modules": ["MATEMATYKA"],
  "curriculum_refs": ["4.15", "4.16"],
  "objectives": [
    "Dziecko potrafi sortować obiekty według jednej cechy",
    "Rozróżnia pojęcia wielkości: duży, mały, średni"
  ]
}
```

### Example 2: Art Activity

**Request:**
```json
{
  "activity": "Malowanie liści farbami",
  "theme": "Jesień - zbiory"
}
```

**Response (200 OK):**
```json
{
  "activity": "Malowanie liści farbami",
  "modules": ["FORMY PLASTYCZNE"],
  "curriculum_refs": ["3.2", "3.5"],
  "objectives": [
    "Dziecko rozwija koordynację wzrokowo-ruchową",
    "Potrafi posługiwać się farbami i pędzlem",
    "Zapoznaje się z jesiennymi kolorami"
  ]
}
```

### Example 3: Validation Error

**Request:**
```json
{
  "activity": "",
  "theme": "Jesień"
}
```

**Response (400 Bad Request):**
```json
{
  "error_code": "VALIDATION_ERROR",
  "error": "Activity field cannot be empty",
  "details": {
    "field": "activity",
    "reason": "Field length must be between 1-500 characters"
  }
}
```

---

## Related Documents

- [PRD.md](PRD.md) - Product Requirements Document
