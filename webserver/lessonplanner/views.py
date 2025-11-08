"""
Views for the lesson planner application
"""

import json
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_http_methods

from .services.ai_client import generate_metadata, get_curriculum_text


# Constants for validation
MAX_ACTIVITY_LENGTH = 500
MAX_THEME_LENGTH = 200


@ensure_csrf_cookie
def index(request):
    """
    Main lesson planning page with table interface.
    Ensures CSRF cookie is set for JavaScript requests.
    """
    return render(request, 'lessonplanner/index.html')


@require_http_methods(["POST"])
def generate_metadata_view(request):
    """
    Generate metadata for a single activity.

    Expected POST body:
    {
        "activity": "string (required)",
        "theme": "string (optional)"
    }

    Returns:
    {
        "module": "string",
        "curriculum_refs": ["string", ...],
        "objectives": ["string", ...]
    }
    """
    try:
        # Parse request body
        data = json.loads(request.body)
        activity = data.get('activity', '').strip()
        theme = data.get('theme', '').strip()

        # Validate activity
        if not activity:
            return JsonResponse({
                'error_code': 'VALIDATION_ERROR',
                'error': 'Pole "Aktywność" nie może być puste.'
            }, status=400)

        # Validate activity length (1-500 chars as per PRD)
        if len(activity) > MAX_ACTIVITY_LENGTH:
            return JsonResponse({
                'error_code': 'VALIDATION_ERROR',
                'error': f'Opis aktywności jest zbyt długi (max {MAX_ACTIVITY_LENGTH} znaków).'
            }, status=400)

        # Validate theme length (0-200 chars as per PRD)
        if len(theme) > MAX_THEME_LENGTH:
            return JsonResponse({
                'error_code': 'VALIDATION_ERROR',
                'error': f'Temat tygodnia jest zbyt długi (max {MAX_THEME_LENGTH} znaków).'
            }, status=400)

        # Call AI client service
        result = generate_metadata(activity, theme)

        return JsonResponse(result, status=200)

    except json.JSONDecodeError:
        return JsonResponse({
            'error_code': 'INVALID_JSON',
            'error': 'Nieprawidłowy format danych.'
        }, status=400)

    except ValueError as e:
        return JsonResponse({
            'error_code': 'VALIDATION_ERROR',
            'error': str(e)
        }, status=400)

    except Exception as e:
        return JsonResponse({
            'error_code': 'SERVER_ERROR',
            'error': 'Nie można połączyć z usługą AI. Wypełnij dane ręcznie.'
        }, status=500)


@require_http_methods(["POST"])
def generate_bulk_view(request):
    """
    Generate metadata for multiple activities in bulk.

    Expected POST body:
    {
        "theme": "string (optional)",
        "activities": [
            {"id": "row_id", "activity": "string"},
            ...
        ]
    }

    Returns:
    {
        "results": [
            {
                "id": "row_id",
                "success": true,
                "data": {
                    "module": "string",
                    "curriculum_refs": ["string", ...],
                    "objectives": ["string", ...]
                }
            },
            ...
        ]
    }
    """
    try:
        # Parse request body
        data = json.loads(request.body)
        theme = data.get('theme', '').strip()
        activities = data.get('activities', [])

        if not activities:
            return JsonResponse({
                'error_code': 'VALIDATION_ERROR',
                'error': 'Brak aktywności do przetworzenia.'
            }, status=400)

        # Validate theme length
        if len(theme) > MAX_THEME_LENGTH:
            return JsonResponse({
                'error_code': 'VALIDATION_ERROR',
                'error': f'Temat tygodnia jest zbyt długi (max {MAX_THEME_LENGTH} znaków).'
            }, status=400)

        # Process each activity
        results = []
        for item in activities:
            row_id = item.get('id')
            activity = item.get('activity', '').strip()

            if not activity:
                # Skip empty activities
                results.append({
                    'id': row_id,
                    'success': False,
                    'error': 'Aktywność jest pusta'
                })
                continue

            # Validate activity length
            if len(activity) > MAX_ACTIVITY_LENGTH:
                results.append({
                    'id': row_id,
                    'success': False,
                    'error': f'Aktywność zbyt długa (max {MAX_ACTIVITY_LENGTH} znaków)'
                })
                continue

            try:
                # Generate metadata
                metadata = generate_metadata(activity, theme)
                results.append({
                    'id': row_id,
                    'success': True,
                    'data': metadata
                })
            except Exception as e:
                # Individual row error
                results.append({
                    'id': row_id,
                    'success': False,
                    'error': 'Błąd generowania danych'
                })

        return JsonResponse({'results': results}, status=200)

    except json.JSONDecodeError:
        return JsonResponse({
            'error_code': 'INVALID_JSON',
            'error': 'Nieprawidłowy format danych.'
        }, status=400)

    except Exception as e:
        return JsonResponse({
            'error_code': 'SERVER_ERROR',
            'error': 'Nie można połączyć z usługą AI. Wypełnij dane ręcznie.'
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
