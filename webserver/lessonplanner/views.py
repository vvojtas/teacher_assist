"""
Views for the lesson planner application
"""

import json
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_http_methods

from .services.ai_client import generate_metadata, get_curriculum_text
from .forms import FillWorkPlanForm


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
        return JsonResponse({
            'error': 'Nie można połączyć z usługą AI. Wypełnij dane ręcznie.',
            'error_code': 'INTERNAL_ERROR'
        }, status=500)


@require_http_methods(["GET"])
def get_curriculum_tooltip_view(request, code):
    """
    Get full curriculum text for a reference code (for tooltips).

    URL parameter: code (e.g., "I.1.2", "4.15")

    Returns:
    {
        "code": "I.1.2",
        "text": "Full curriculum text in Polish"
    }
    """
    try:
        text = get_curriculum_text(code)

        return JsonResponse({
            'code': code,
            'text': text
        }, status=200)

    except Exception as e:
        return JsonResponse({
            'error_code': 'NOT_FOUND',
            'error': f'Nie znaleziono opisu dla kodu: {code}'
        }, status=404)
