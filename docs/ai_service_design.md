# AI Service Architecture Design

**Project:** Teacher Assist - LangGraph AI Service
**Version:** 1.1
**Last Updated:** 2025-11-23
**Status:** Design Phase

---

## 1. Overview

The AI Service is a LangGraph-based workflow that generates educational metadata (modules, curriculum references, and learning objectives) for kindergarten activities. The service uses a single LLM call with chain-of-thought reasoning and structured JSON output to produce coherent, context-aware results.

### Design Philosophy

- **Simplicity First:** Start with minimal complexity, add features based on real usage data
- **Progressive Enhancement:** Three-phase rollout to learn and validate each component
- **Cost-Effective:** Single LLM call for MVP, controlled cost increase in later phases
- **Self-Correcting:** Automated quality feedback loop in later phases

### Key Characteristics

- **Protocol:** HTTP REST API (FastAPI)
- **Orchestration:** LangGraph state machine
- **LLM Gateway:** OpenRouter (model-agnostic)
- **Language:** Polish (all AI-generated content)
- **Target Latency:** < 10 seconds
- **Budget:** ~$1/month (~1M tokens)

---

## 2. Architecture Phases

### Phase 0: MVP (Current - Mock Service)
- Mock service returns random data from database
- No LLM integration
- Purpose: Test Django ↔ AI Service integration

### Phase 1: MVP with Real LLM
- Single LLM call with structured output
- Rule-based validation (no retry)
- Return error on validation failure
- User manually regenerates if needed

### Phase 2: Quality Detection (Future)
- Add LLM-based quality checker
- Detect vague objectives, module mismatches
- Still return error (no auto-retry yet)
- Collect data on failure patterns

### Phase 3: Self-Correction (Future)
- Add retry loop with feedback
- Max 1-2 retry attempts
- LLM receives feedback from validator
- Graceful degradation after max retries

---

## 3. Phase 1 Architecture (MVP with Real LLM)

### 3.1 Workflow Graph

```
┌─────────────────────┐
│  Input Validator    │
│  - Validate input   │
│  - Initialize state │
└──────────┬──────────┘
           │
           ├──────────────┬──────────────┬──────────────┐
           ▼              ▼              ▼              ▼
    ┌───────────┐  ┌───────────┐  ┌───────────┐  ┌───────────┐
    │Load       │  │Load       │  │Load       │  │Load       │
    │Modules    │  │Curriculum │  │Examples   │  │Prompt     │
    │from DB    │  │Refs from  │  │from DB    │  │Template   │
    │           │  │DB         │  │           │  │from File  │
    └─────┬─────┘  └─────┬─────┘  └─────┬─────┘  └─────┬─────┘
          │              │              │              │
          └──────────────┴──────────────┴──────────────┘
                         │
                         ▼
              ┌──────────────────────┐
              │  Construct Prompt    │
              │  - Fill template     │
              │  - Add context       │
              └──────────┬───────────┘
                         │
                         ▼
              ┌──────────────────────┐
              │   LLM Generator      │
              │  - Single LLM call   │
              │  - JSON output       │
              │  - Reasoning step    │
              └──────────┬───────────┘
                         │
                         ▼
              ┌──────────────────────┐
              │  Output Validator    │
              │  (Rule-based)        │
              │  - Check JSON format │
              │  - Verify codes      │
              │  - Validate ranges   │
              └──────────┬───────────┘
                         │
                    ┌────┴────┐
                    ▼         ▼
            ┌─────────┐   ┌─────────┐
            │ Success │   │ Error   │
            │ Output  │   │ Output  │
            └─────────┘   └─────────┘
```

### 3.2 State Schema

The LangGraph state contains all data flowing through the workflow:

```python
class WorkflowState(TypedDict):
    # Input (from API request)
    activity: str              # Required, 1-500 chars
    theme: str                 # Optional, 0-200 chars

    # Database Context (loaded in parallel)
    available_modules: list[str]
    major_curriculum_refs: list[dict]
    curriculum_refs: list[dict]  # [{code: "4.15", text: "..."}, ...]
    example_entries: list[dict]

    # Prompt Engineering
    prompt_template: str
    constructed_prompt: str

    # LLM Generation
    llm_raw_response: str
    llm_parsed_output: dict    # { module, curriculum_refs, objectives}

    # Validation
    validation_passed: bool
    validation_errors: list[str]

    # Output
    final_response: FillWorkPlanResponse | ErrorResponse
```

### 3.3 Parallel Database Loading

**Purpose:** Learn LangGraph branching/joining mechanics

**Nodes:**
1. `load_modules` - Query `educational_modules` table
2. `load_curriculum_refs` - Query `curriculum_references` table (code + full_text + major_curriculum_id) & `load_major_curriculum_refs` (id + text)
3. `load_examples` - Query `work_plan_entries` where `is_example=true`
4. `load_prompt_template` - Read template file from `ai_service/templates/`

**Join Point:** All four branches must complete before prompt construction begins

**Note:** With SQLite and small dataset (~100 rows total), parallel loading provides minimal performance benefit. Primary purpose is learning LangGraph parallel execution patterns.

---

## 4. Prompt Engineering

### 4.1 Template Structure

Prompt templates are stored in `ai_service/templates/` as Jinja2-style templates with clear section markers.

**Template File:** `ai_service/templates/fill_work_plan_eng.txt`

**Placeholders:**
- `{activity}` - User-provided activity description
- `{theme}` - Optional weekly theme
- `{modules_list}` - All available educational modules
- `{curriculum_refs}` - All curriculum references with codes and full text (organised by major_curriculum_reffs)
- `{examples}` - 3-5 example work plan entries from database

**Template Sections:**
1. **System Role** - Define AI as kindergarten education expert
2. **Context** - Provide available modules, curriculum codes, examples
3. **Task** - Specify the activity and theme to process
4. **Output Format** - Define JSON schema with reasoning field
5. **Requirements** - Explicit constraints (use only provided codes, 2-3 objectives, etc.)

### 4.2 Prompt Requirements

The constructed prompt must:
- Include chain-of-thought reasoning step
- Provide 3-5 real examples from database (few-shot learning)
- List ALL curriculum reference codes explicitly
- Specify exact JSON output schema
- Emphasize using ONLY codes from provided list
- Request 2-3 specific, actionable objectives in Polish
- Keep total token count under 2000 tokens (input + output)

---

## 5. LLM Integration

**Implementation:** Uses OpenAI SDK (`openai` package) configured with OpenRouter's base URL. This provides compatibility with OpenRouter while using a mature, well-tested SDK.

### 5.1 Model Selection

**Gateway:** OpenRouter (https://openrouter.ai)

**Recommended Models (in priority order):**
1. `anthropic/claude-3.5-haiku` - Fast, good structured output, cost-effective
2. `openai/gpt-4o-mini` - Excellent structured output, slightly more expensive
3. `google/gemini-flash-1.5` - Very fast, budget-friendly

**Selection Criteria:**
- Structured JSON output support
- Polish language quality
- Cost (target: $0.0005 per request)
- Latency (target: < 5 seconds)

### 5.2 LLM Call Parameters

```yaml
model: "anthropic/claude-3.5-haiku"  # Configurable via environment
temperature: 0.7                     # Balance creativity and consistency
max_tokens: 500                      # Limit output size
response_format:                     # Structured output with JSON Schema
  type: json_schema
  json_schema: LLM_OUTPUT_JSON_SCHEMA  # Defines required fields and types
```

### 5.3 Expected Token Usage

**Input Tokens (per request):**
- Prompt template: ~200 tokens
- Activity + theme: ~50 tokens
- Modules list: ~30 tokens
- Curriculum refs (50 items): ~800 tokens
- Examples (3 items): ~300 tokens
- **Total Input:** ~1,400 tokens

**Output Tokens (per request):**
- Reasoning: ~50 tokens
- Module: ~5 tokens
- Curriculum refs: ~20 tokens
- Objectives: ~100 tokens
- **Total Output:** ~175 tokens

**Total per Request:** ~1,575 tokens
**Cost Estimate (Claude 3.5 Haiku):** ~$0.0003 per request

---

## 6. Validation Logic

### 6.1 Rule-Based Validator

The output validator performs fast, deterministic checks without LLM calls.

**Validation Rules:**

1. **JSON Format**
   - Output must be valid JSON
   - Required fields: `modules`, `curriculum_refs`, `objectives`

2. **Modules Validation**
   - All module names must exist in `available_modules` list
   - Count must be between 1-3
   - Case-sensitive match

3. **Curriculum References Validation**
   - All codes must exist in database `curriculum_references` table
   - Count must be between 1-10
   - No duplicate codes

4. **Objectives Validation**
   - Count must be between 1-5
   - Each objective must be non-empty string
   - Minimum 10 characters per objective (avoid trivial entries)

5. **Field Types**
   - `modules`: array of strings
   - `curriculum_refs`: array of strings
   - `objectives`: array of strings

### 6.2 Validation Failure Handling (Phase 1)

When validation fails:
1. Log the error with request context
2. Return `ErrorResponse` with:
   - `error_code`: "VALIDATION_ERROR"
   - `error`: Human-readable Polish message
   - `details`: Specific validation failures
3. User can click "Regenerate" to try again

**Partial Failure Strategy:**

If some curriculum codes are valid and some invalid:
- **Option A (Strict):** Reject entire response
- **Option B (Lenient):** Remove invalid codes, keep valid ones (if at least 1 valid)

**Recommendation:** Use Option B (lenient) for better UX, log removed codes for monitoring.

---

## 7. Phase 2: Quality Detection (Future)

### 7.1 LLM Quality Checker

Add an additional LLM call to evaluate output quality.

**Quality Checks:**
- Are objectives specific and actionable?
- Do objectives align with the activity?
- Is the module choice appropriate for the activity type?
- Is there logical coherence between module, curriculum refs, and objectives?

**Output:** Binary pass/fail + feedback text

**Integration Point:** After rule-based validator, before returning response

**Failure Behavior:** Return error with quality feedback (no retry yet)

### 7.2 Quality Checker Prompt

```
Jesteś ekspertem oceny jakości planów lekcji dla przedszkola.

Oceń następujące metadane:
Aktywność: {activity}
Moduł: {module}
Cele: {objectives}

Kryteria:
1. Czy cele są konkretne i mierzalne?
2. Czy cele pasują do aktywności?
3. Czy moduł jest odpowiedni?

Odpowiedź (JSON):
{
  "passed": true/false,
  "feedback": "Krótkie uzasadnienie"
}
```

---

## 8. Phase 3: Self-Correction Loop (Future)

### 8.1 Enhanced Workflow with Retry

```
Input → DB Load → Construct Prompt → LLM Generator → Rule Validator
                                          ↑                 ↓
                                          │          [Pass/Fail]
                                          │                 ↓
                                          │         Quality Checker (optional)
                                          │                 ↓
                                          │          [Pass/Fail + Feedback]
                                          │                 ↓
                                          └─────── Retry? (max 1-2 attempts)
                                                            ↓
                                                    Success or Error
```

### 8.2 Retry Logic

**State Additions:**
```python
attempt_number: int           # 0, 1, 2
previous_output: dict | None  # Save for retry prompt
feedback: str | None          # Validator feedback for LLM
```

**Retry Conditions:**
- Validation failed
- Error is retryable (invalid codes, vague objectives, module mismatch)
- `attempt_number < MAX_RETRIES` (default: 1)

**Non-Retryable Errors:**
- Malformed JSON (likely prompt issue)
- LLM timeout
- Empty or invalid input

**Retry Prompt Structure:**
```
Twoja poprzednia odpowiedź miała problemy:

PROBLEMY:
{feedback_details}

INSTRUKCJE:
{fix_instructions}

POPRZEDNIA ODPOWIEDŹ:
{previous_output}

ORYGINALNE ZADANIE:
Aktywność: {activity}
Temat: {theme}

Popraw odpowiedź zgodnie z instrukcjami.
```

### 8.3 Conditional Routing

After validation, route to one of three paths:
1. **"success"** - Validation passed → Format and return
2. **"retry"** - Validation failed, error is retryable, under retry limit → Loop to LLM
3. **"error"** - Validation failed, non-retryable or max retries exceeded → Return error

---

## 9. Performance Requirements

### 9.1 Latency Targets

| Component | Target | Maximum |
|-----------|--------|---------|
| Input validation | < 10ms | 50ms |
| DB loading (parallel) | < 100ms | 500ms |
| Prompt construction | < 50ms | 200ms |
| LLM call | < 5s | 30s |
| Output validation | < 10ms | 50ms |
| **Total (Phase 1)** | **< 6s** | **10s** |
| **Total (Phase 3, worst case)** | **< 15s** | **30s** |

### 9.2 Cost Targets

| Phase | LLM Calls | Cost per Request | Monthly Cost (1000 requests) |
|-------|-----------|------------------|------------------------------|
| Phase 1 | 1 | $0.0003 | $0.30 |
| Phase 2 | 2 | $0.0005 | $0.50 |
| Phase 3 (avg) | 1.5 | $0.0004 | $0.40 |
| Phase 3 (worst) | 3 | $0.0009 | $0.90 |

**Monthly Budget:** $1.00 (supports 1,000-3,000 requests depending on phase)

### 9.3 Success Metrics

**Accuracy:**
- ≥95% of curriculum codes are valid (exist in database)
- ≥80% of generated objectives deemed usable by teachers
- ≥85% of module selections appropriate for activity type

**Performance:**
- ≥95% of requests complete within 10 seconds
- ≥99% of requests complete within 30 seconds

**Quality (Phase 3):**
- ≤20% of requests require retry
- ≥70% of retries succeed on first attempt

---

## 10. Error Handling

### 10.1 Error Types

| Error Code | HTTP Status | Description | Retryable |
|------------|-------------|-------------|-----------|
| `VALIDATION_ERROR` | 400 | Invalid input or output validation failed | No (user retries manually) |
| `LLM_TIMEOUT` | 504 | LLM call exceeded timeout | No |
| `LLM_ERROR` | 500 | LLM API returned error | No |
| `INTERNAL_ERROR` | 500 | Unexpected server error | No |
| `DB_ERROR` | 500 | Database query failed | No |

### 10.2 Error Response Format

```json
{
  "error": "Nie można zweryfikować kodów podstawy programowej",
  "error_code": "VALIDATION_ERROR",
  "details": {
    "field": "curriculum_refs",
    "invalid_codes": ["4.99", "3.50"],
    "reason": "Kody nie istnieją w bazie danych"
  }
}
```

### 10.3 Logging Requirements

Log all requests with:
- Request ID (UUID)
- Input (activity, theme)
- Attempt number
- LLM model used
- Token usage
- Latency breakdown
- Validation result
- Error details (if any)

**Purpose:** Support debugging and inform Phase 2/3 decisions

---

## 11. Configuration

### 11.1 Environment Variables

```bash
# Service Mode
AI_SERVICE_MODE=real  # "mock" or "real"

# LLM Configuration
AI_SERVICE_OPENROUTER_API_KEY=sk-...
AI_SERVICE_LLM_MODEL=anthropic/claude-3.5-haiku
AI_SERVICE_LLM_TEMPERATURE=0.7
AI_SERVICE_LLM_MAX_TOKENS=500
AI_SERVICE_LLM_TIMEOUT_SECONDS=30

# Workflow Configuration
AI_SERVICE_MAX_RETRY_ATTEMPTS=0  # Phase 3+ (currently disabled)
AI_SERVICE_ENABLE_QUALITY_CHECKER=false  # Phase 2+
AI_SERVICE_ENABLE_AUTO_RETRY=false       # Phase 3+

# Database (path relative to repo root)
AI_SERVICE_DATABASE_PATH=db.sqlite3

# Prompt Templates
AI_SERVICE_PROMPT_TEMPLATE_DIR=ai_service/templates
```

### 11.2 Feature Flags

Use environment variables to enable/disable features:
- `ENABLE_QUALITY_CHECKER` - Toggle Phase 2 quality checking
- `ENABLE_AUTO_RETRY` - Toggle Phase 3 retry loop
- `MAX_RETRY_ATTEMPTS` - Configure retry limit (0 = disabled)

---

## 12. Testing Strategy

### 12.1 Unit Tests

- Input validator with various invalid inputs
- Database loaders (mock DB responses)
- Prompt template rendering
- Output validator with edge cases
- LLM response parser (malformed JSON)

### 12.2 Integration Tests

- Full workflow with mocked LLM
- Database integration (real SQLite queries)
- Error handling paths
- Retry logic (Phase 3)

### 12.3 LLM Evaluation

- Golden dataset of 20-30 activities
- Manual evaluation of output quality
- Track accuracy metrics (curriculum codes, module selection)
- Compare different models/prompts

---

## 13. Deployment & Monitoring

### 13.1 Startup Sequence

1. Load environment variables
2. Initialize database connection
3. Verify database tables exist
4. Load prompt templates from filesystem
5. Validate OpenRouter API key
6. Compile LangGraph workflow
7. Start FastAPI server on port 8001

### 13.2 Health Check Endpoint

`GET /health` should verify:
- Database connection
- Prompt templates loaded
- OpenRouter API key configured
- Return service version

### 13.3 Monitoring Metrics

**Application Metrics:**
- Requests per minute
- Average latency
- Error rate by error code
- LLM token usage
- Retry rate (Phase 3)

**Quality Metrics:**
- Validation failure rate
- Invalid curriculum code rate
- User regeneration rate (from Django logs)

---

## 16. Open Questions

1. **Prompt Template Format:** Jinja2, Python f-strings, or plain text with simple placeholders?
2. **Example Selection:** How to select best 3-5 examples from database? (Random, most recent, or topic-based?)
3. **Model Selection:** Should model be configurable per request, or global setting only?
4. **Curriculum Ref Limit:** Should we limit to top-N most relevant refs in prompt to save tokens?
5. **Reasoning Field:** Should reasoning be shown to user in UI, or only logged for debugging?

---

## Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-11-21 | AI Architect | Initial design document for Phase 1-3 |
| 1.1 | 2025-11-23 | VVojtas | Human corrections |

---

## Related Documents

- **PRD:** [docs/PRD.md](PRD.md) - Product requirements and user stories
- **API Specification:** [docs/ai_api.md](ai_api.md) - REST API contract
- **Database Schema:** [docs/db_schema.md](db_schema.md) - Database structure
- **Prompt Templates:** `ai_service/templates/` - Prompt engineering artifacts
