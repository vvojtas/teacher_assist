"""
Views for the lesson planner application
"""

import json
import logging

from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_http_methods

from .services.ai_client import generate_metadata, get_curriculum_text
from .forms import FillWorkPlanForm
from .fixtures.mock_data import MOCK_CURRICULUM_REFS, MOCK_EDUCATIONAL_MODULES

# Configure logger for this module
logger = logging.getLogger(__name__)


@ensure_csrf_cookie
def index(request):
    """
    Main lesson planning page with table interface.
    Ensures CSRF cookie is set for JavaScript requests.
    """
    return render(request, 'lessonplanner/index.html')


@require_http_methods(["POST"])
def fill_work_plan_view(request):
    """
    Generate metadata for a single activity (Fill Work Plan endpoint).

    Expected POST body:
    {
        "activity": "string (required, 1-500 chars)",
        "theme": "string (optional, max 200 chars)"
    }

    Returns:
    {
        "module": "string",
        "curriculum_refs": ["string", ...],
        "objectives": ["string", ...]
    }

    Error responses follow django_api.md specification:
    - 400 INVALID_INPUT - Empty or invalid activity field
    - 503 AI_SERVICE_UNAVAILABLE - LangGraph service unreachable
    - 504 AI_SERVICE_TIMEOUT - Request exceeds timeout
    - 500 INTERNAL_ERROR - Unexpected server errors
    """
    try:
        # Parse request body
        data = json.loads(request.body)

        # Validate using Django form
        form = FillWorkPlanForm(data)

        if not form.is_valid():
            # Get first error message
            errors = form.errors.as_data()
            first_error = None
            for field, error_list in errors.items():
                if error_list:
                    first_error = error_list[0].message
                    break

            return JsonResponse({
                'error': first_error or 'Nieprawidłowe dane wejściowe',
                'error_code': 'INVALID_INPUT'
            }, status=400)

        # Get cleaned data
        activity = form.cleaned_data['activity']
        theme = form.cleaned_data.get('theme', '')

        # Call AI client service
        result = generate_metadata(activity, theme)

        return JsonResponse(result, status=200)

    except json.JSONDecodeError:
        return JsonResponse({
            'error': 'Nieprawidłowy format danych JSON',
            'error_code': 'INVALID_INPUT'
        }, status=400)

    except ValueError as e:
        # ValueError can be raised by AI client for invalid input
        return JsonResponse({
            'error': str(e) if str(e) else 'Nieprawidłowe dane wejściowe',
            'error_code': 'INVALID_INPUT'
        }, status=400)

    except ConnectionError:
        return JsonResponse({
            'error': 'Nie można połączyć z usługą AI. Wypełnij dane ręcznie.',
            'error_code': 'AI_SERVICE_UNAVAILABLE'
        }, status=503)

    except TimeoutError:
        return JsonResponse({
            'error': 'Żądanie przekroczyło limit czasu. Spróbuj ponownie.',
            'error_code': 'AI_SERVICE_TIMEOUT'
        }, status=504)

    except Exception as e:
        # Log unexpected errors for debugging
        logger.error(
            "Unexpected error in fill_work_plan_view: %s",
            e,
            exc_info=True  # Include full stack trace
        )
        return JsonResponse({
            'error': 'Wystąpił nieoczekiwany błąd serwera. Spróbuj ponownie lub wypełnij dane ręcznie.',
            'error_code': 'INTERNAL_ERROR'
        }, status=500)


@require_http_methods(["GET"])
def get_all_curriculum_refs_view(request):
    """
    Get all curriculum references (for tooltips and caching).

    MOCK IMPLEMENTATION: Returns sample curriculum reference data.

    Returns:
    {
        "references": {
            "1.1": "Full Polish text...",
            "2.5": "Full Polish text...",
            ...
        },
        "count": 123
    }

    Error responses follow django_api.md specification:
    - 500 DATABASE_ERROR - Database query failure
    """
    try:
        return JsonResponse({
            'references': MOCK_CURRICULUM_REFS,
            'count': len(MOCK_CURRICULUM_REFS)
        }, status=200)

    except Exception as e:
        logger.error(
            "Unexpected error in get_all_curriculum_refs_view: %s",
            e,
            exc_info=True
        )
        return JsonResponse({
            'error': 'Błąd bazy danych przy pobieraniu odniesień',
            'error_code': 'DATABASE_ERROR'
        }, status=500)


@require_http_methods(["GET"])
def get_curriculum_ref_by_code_view(request, code):
    """
    Lookup curriculum reference by code.

    MOCK IMPLEMENTATION: Returns sample curriculum reference data.

    URL parameter: code (e.g., "3.8", "4.15")

    Returns:
    {
        "reference_code": "3.8",
        "full_text": "Full curriculum text in Polish",
        "created_at": "2025-10-28T10:30:00Z"
    }

    Error responses follow django_api.md specification:
    - 404 REFERENCE_NOT_FOUND - Curriculum reference code doesn't exist
    - 400 INVALID_CODE_FORMAT - Invalid code format
    """
    try:
        # Validate code format (basic check)
        if not code or len(code) > 20:
            return JsonResponse({
                'error': 'Nieprawidłowy format kodu odniesienia',
                'error_code': 'INVALID_CODE_FORMAT'
            }, status=400)

        # Lookup curriculum reference
        if code not in MOCK_CURRICULUM_REFS:
            return JsonResponse({
                'error': f'Nie znaleziono odniesienia dla kodu: {code}',
                'error_code': 'REFERENCE_NOT_FOUND'
            }, status=404)

        return JsonResponse({
            'reference_code': code,
            'full_text': MOCK_CURRICULUM_REFS[code],
            'created_at': '2025-10-28T10:30:00Z'
        }, status=200)

    except Exception as e:
        logger.error(
            "Unexpected error in get_curriculum_ref_by_code_view: %s",
            e,
            exc_info=True
        )
        return JsonResponse({
            'error': 'Błąd bazy danych',
            'error_code': 'DATABASE_ERROR'
        }, status=500)


@require_http_methods(["GET"])
def get_modules_view(request):
    """
    Get all educational modules with optional filtering.

    MOCK IMPLEMENTATION: Returns sample educational module data.

    Query Parameters:
    - ai_suggested (optional): Filter by AI-suggested flag (true/false)

    Returns:
    {
        "modules": [
            {
                "id": 1,
                "name": "JĘZYK",
                "is_ai_suggested": false,
                "created_at": "2025-10-28T10:00:00Z"
            },
            ...
        ],
        "count": 4
    }

    Error responses follow django_api.md specification:
    - 500 DATABASE_ERROR - Database query failure
    """
    try:
        # Get optional filter parameter
        ai_suggested_param = request.GET.get('ai_suggested', None)

        # Apply filtering if requested
        if ai_suggested_param is not None:
            # Convert string to boolean
            ai_suggested = ai_suggested_param.lower() in ('true', '1', 'yes')
            modules_data = [m for m in MOCK_EDUCATIONAL_MODULES if m['is_ai_suggested'] == ai_suggested]
        else:
            modules_data = MOCK_EDUCATIONAL_MODULES

        return JsonResponse({
            'modules': modules_data,
            'count': len(modules_data)
        }, status=200)

    except Exception as e:
        logger.error(
            "Unexpected error in get_modules_view: %s",
            e,
            exc_info=True
        )
        return JsonResponse({
            'error': 'Błąd bazy danych przy pobieraniu modułów',
            'error_code': 'DATABASE_ERROR'
        }, status=500)
