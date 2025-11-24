# AI Service - LangGraph-based Lesson Plan Metadata Generator

FastAPI service that generates educational metadata (modules, curriculum references, objectives) for kindergarten activities using LangGraph workflow and OpenRouter LLM gateway.

## Features

- **Two Modes**: Mock mode (testing) and Real mode (LLM integration)
- **LangGraph Workflow**: Parallel data loading, prompt construction, LLM generation, validation
- **OpenRouter Integration**: Model-agnostic LLM gateway
- **Cost Tracking**: Automatic token counting and cost calculation
- **Colored Console**: Visual output for prompts, responses, costs, and errors
- **Lenient Validation**: Filters invalid curriculum codes with warnings

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create a `.env` file in the project root (or set environment variables):

```bash
# Service Mode (mock or real)
AI_SERVICE_MODE=mock

# OpenRouter Configuration (required for real mode)
# Get your key from https://openrouter.ai/keys
OPENROUTER_API_KEY=your-key-here

# LLM Model Selection
LLM_MODEL=anthropic/claude-3.5-haiku
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=500
LLM_TIMEOUT_SECONDS=30

# Database Path (relative to project root)
DATABASE_PATH=../db.sqlite3

# Prompt Templates Directory
PROMPT_TEMPLATE_DIR=ai_service/templates

# Feature Flags (Phase 2/3)
ENABLE_QUALITY_CHECKER=false
ENABLE_AUTO_RETRY=false
MAX_RETRY_ATTEMPTS=0

# Cost Tracking
PRICING_CACHE_TTL_SECONDS=3600
```

### 3. Run the Service

```bash
# From project root
python ai_service/main.py
```

The service will start on `http://localhost:8001`.

## Environment Variables Reference

### Service Configuration

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `AI_SERVICE_MODE` | No | `mock` | Service mode: `mock` (testing) or `real` (LLM integration) |

### OpenRouter Configuration

| Variable | Conditional | Default | Description |
|----------|-------------|---------|-------------|
| `OPENROUTER_API_KEY` | Yes (real mode) | - | Your OpenRouter key from https://openrouter.ai/keys |
| `LLM_MODEL` | No | `anthropic/claude-3.5-haiku` | Model identifier from OpenRouter |
| `LLM_TEMPERATURE` | No | `0.7` | Temperature for LLM (0.0-1.0) |
| `LLM_MAX_TOKENS` | No | `500` | Maximum output tokens |
| `LLM_TIMEOUT_SECONDS` | No | `30` | Request timeout in seconds |

### Database Configuration

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DATABASE_PATH` | No | `../db.sqlite3` | Path to SQLite database (relative to ai_service) |

### Workflow Configuration

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `PROMPT_TEMPLATE_DIR` | No | `ai_service/templates` | Directory containing prompt templates |
| `MAX_RETRY_ATTEMPTS` | No | `0` | Max retries for validation failures (Phase 3) |
| `ENABLE_QUALITY_CHECKER` | No | `false` | Enable LLM quality checking (Phase 2) |
| `ENABLE_AUTO_RETRY` | No | `false` | Enable automatic retry on failure (Phase 3) |
| `PRICING_CACHE_TTL_SECONDS` | No | `3600` | Cache TTL for OpenRouter pricing (seconds) |

## Mode Toggle

### Mock Mode (Default)

Returns random data from the database. No LLM calls, no API key required.

```bash
AI_SERVICE_MODE=mock
```

**Use Cases:**
- Testing the Django ↔ AI Service integration
- Development without API costs
- CI/CD pipeline testing

### Real Mode

Uses LangGraph workflow with real LLM calls via OpenRouter.

```bash
AI_SERVICE_MODE=real
OPENROUTER_API_KEY=your-actual-key-here
```

**Requirements:**
- Valid OpenRouter API key
- Database populated with curriculum data
- Prompt template file exists

## API Endpoints

### POST /api/fill-work-plan

Generate metadata for an activity.

**Request:**
```json
{
  "activity": "Zabawa w sklep z owocami",
  "theme": "Jesień - zbiory"
}
```

**Response (Success):**
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

**Response (Error):**
```json
{
  "error": "Nieprawidłowe dane wejściowe",
  "error_code": "VALIDATION_ERROR",
  "details": {
    "field": "activity",
    "reason": "Field cannot be empty"
  }
}
```

### GET /health

Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "mode": "mock",
  "version": "1.0.0"
}
```

### GET /api/mode

Get current service mode.

**Response:**
```json
{
  "mode": "mock",
  "llm_model": "anthropic/claude-3.5-haiku"
}
```

## Colored Console Output

When running in real mode, the console displays:

- 🟢 **Green**: Final formatted prompt sent to LLM
- 🔵 **Blue**: Raw LLM response
- 🟡 **Yellow**: Token counts and estimated cost
- 🔴 **Red**: Errors and validation warnings

Example output:
```
================================================================================
[PROMPT SENT TO LLM]
================================================================================
Jesteś ekspertem edukacji przedszkolnej w Polsce.
...
================================================================================

================================================================================
[LLM RESPONSE]
================================================================================
{
  "reasoning": "...",
  "modules": ["MATEMATYKA"],
  ...
}
================================================================================

================================================================================
[TOKEN USAGE & COST] (anthropic/claude-3.5-haiku)
================================================================================
  Input tokens:      1,423
  Output tokens:     187
  Total tokens:      1,610
  Estimated cost:    $0.000589
================================================================================
```

## Cost Tracking

The service automatically tracks and logs costs for each request:

1. Fetches pricing from OpenRouter `/api/v1/models` endpoint
2. Caches pricing for 1 hour (configurable)
3. Calculates cost using native token counts
4. Displays detailed breakdown in yellow console output

**Typical Cost (Claude 3.5 Haiku):**
- Input: ~1,400 tokens @ ~$0.00000025/token
- Output: ~180 tokens @ ~$0.00000125/token
- **Total: ~$0.0006 per request**

**Budget: $1 supports ~1,600 requests**

## Validation Behavior

### Lenient Mode (Default)

When the LLM returns invalid curriculum codes:

1. Valid codes are kept
2. Invalid codes are filtered out
3. Warning logged in **RED** console output
4. At least 1 valid code required

Example warning:
```
[WARNING] Filtered out invalid curriculum codes: 4.99, 3.50
```

### Strict Mode (Future)

Rejects entire response if any code is invalid.

## Testing

```bash
# Run all tests
pytest ai_service/tests/

# Run with coverage
pytest ai_service/tests/ --cov=ai_service --cov-report=html

# Run specific test file
pytest ai_service/tests/test_workflow.py
```

## Getting OpenRouter API Key

1. Go to https://openrouter.ai
2. Sign up or log in
3. Navigate to https://openrouter.ai/keys
4. Create a new API key
5. Add credits to your account (minimum $5 recommended)
6. Copy the key and add to `.env` file

**Important:** Keep your API key secure. Never commit it to git.

## Troubleshooting

### "OPENROUTER_API_KEY is required when AI_SERVICE_MODE=real"

**Solution:** Add your OpenRouter key to the `.env` file or set environment variable.

### "Database not found" error

**Solution:** Verify `DATABASE_PATH` points to correct SQLite file. Default is `../db.sqlite3` (relative to ai_service directory).

### "Template file not found" error

**Solution:** Ensure `ai_service/templates/fill_work_plan.txt` exists.

### High costs

**Solution:**
- Use cheaper models (e.g., `google/gemini-flash-1.5`)
- Reduce `LLM_MAX_TOKENS` setting
- Switch to `AI_SERVICE_MODE=mock` for testing

### Slow responses

**Solution:**
- Check network latency to OpenRouter
- Try faster models (e.g., `anthropic/claude-3.5-haiku`)
- Increase `LLM_TIMEOUT_SECONDS` if needed

## Development

### Project Structure

```
ai_service/
├── __init__.py
├── main.py                  # FastAPI entry point
├── config.py                # Configuration management
├── workflow.py              # LangGraph state machine
├── mock_service.py          # Mock service (Phase 0)
├── db_client.py            # Database client
├── db_models.py            # Database Pydantic models
├── utils/                   # Utility modules
│   ├── console.py          # Colored output
│   ├── cost_tracker.py     # Cost calculation
│   ├── formatters.py       # Data formatting
│   └── response_schema.py  # LLM response TypedDict
├── nodes/                   # LangGraph workflow nodes
│   ├── validators.py       # Input/output validation
│   ├── loaders.py          # Database loaders
│   ├── prompt_builder.py   # Prompt construction
│   ├── llm_client.py       # OpenRouter integration
│   └── formatters.py       # Response formatters
├── templates/               # Prompt templates
│   └── fill_work_plan.txt  # Main prompt template
└── tests/                   # Test suite
    ├── test_api.py
    ├── test_workflow.py
    ├── test_validators.py
    └── test_llm_client.py
```

### Adding New Models

To use a different LLM model:

1. Find model identifier at https://openrouter.ai/models
2. Update `LLM_MODEL` in `.env`:
   ```bash
   LLM_MODEL=openai/gpt-4o-mini
   ```
3. Restart the service

## Phase Roadmap

- **Phase 0 (Current)**: Mock service with random data
- **Phase 1 (In Progress)**: Real LLM integration with rule-based validation
- **Phase 2 (Future)**: LLM-based quality checker
- **Phase 3 (Future)**: Self-correction with retry loop

## Support

For issues or questions:
- Check troubleshooting section above
- Review error logs in red console output
- Verify all environment variables are set correctly
- Test with `AI_SERVICE_MODE=mock` to isolate LLM issues

---

**Version:** 1.0.0
**Last Updated:** 2025-11-24
**License:** MIT
