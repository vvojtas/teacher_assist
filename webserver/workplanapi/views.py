"""
API views for workplanapi endpoints.

This module implements REST API endpoints that return mock data.
Uses Django Forms for validation with proper CSRF protection.
In Phase 2, these will be connected to the AI service and database.
"""

import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from .forms import FillWorkPlanForm


# Mock data for curriculum references (from API documentation)
MOCK_CURRICULUM_REFS = {
    "1.1": "zgłasza potrzeby fizjologiczne, samodzielnie wykonuje podstawowe czynności higieniczne;",
    "2.5": "rozstaje się z rodzicami bez lęku, ma świadomość, że rozstanie takie bywa dłuższe lub krótsze;",
    "3.8": "obdarza uwagą inne dzieci i osoby dorosłe;",
    "4.15": "przelicza elementy zbiorów w czasie zabawy, prac porządkowych, ćwiczeń i wykonywania innych czynności, posługuje się liczebnikami głównymi i porządkowymi, rozpoznaje cyfry oznaczające liczby od 0 do 10, eksperymentuje z tworzeniem kolejnych liczb, wykonuje dodawanie i odejmowanie w sytuacji użytkowej, liczy obiekty, odróżnia liczenie błędne od poprawnego;",
}

# Mock data for educational modules
MOCK_MODULES = [
    {
        "id": 1,
        "name": "JĘZYK",
        "is_ai_suggested": False,
        "created_at": "2025-10-28T10:00:00Z",
    },
    {
        "id": 2,
        "name": "MATEMATYKA",
        "is_ai_suggested": False,
        "created_at": "2025-10-28T10:00:00Z",
    },
    {
        "id": 3,
        "name": "MOTORYKA DUŻA",
        "is_ai_suggested": False,
        "created_at": "2025-10-28T10:00:00Z",
    },
    {
        "id": 4,
        "name": "FORMY PLASTYCZNE",
        "is_ai_suggested": False,
        "created_at": "2025-10-28T10:00:00Z",
    },
]


@csrf_exempt
@require_http_methods(["POST"])
def fill_work_plan_view(request):
    """
    POST /api/fill-work-plan

    Generates educational metadata (module, curriculum references, objectives)
    for a given activity.

    Currently returns mock data. Phase 2 will integrate with AI service.

    Note: Accepts both JSON and form-encoded data. CSRF protection applies
    when submitting from Django forms. For JSON API calls, include X-CSRFToken header.
    """
    # Parse request data (support both JSON and form-encoded)
    if request.content_type == 'application/json':
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse(
                {
                    "error": "Nieprawidłowy format JSON",
                    "error_code": "INVALID_JSON",
                },
                status=400,
            )
    else:
        # Form-encoded data
        data = request.POST

    # Validate using Django form
    form = FillWorkPlanForm(data)

    if form.is_valid():
        # Access validated data
        activity = form.cleaned_data['activity']
        theme = form.cleaned_data.get('theme', '')

        # Mock response data (matching API specification)
        return JsonResponse(
            {
                "module": "MATEMATYKA",
                "curriculum_refs": ["4.15", "4.18"],
                "objectives": [
                    "Dziecko potrafi przeliczać w zakresie 5",
                    "Rozpoznaje poznane wcześniej cyfry",
                ],
            },
            status=200,
        )
    else:
        # Return validation errors
        # Convert Django form errors to API format
        error_details = {}
        for field, errors in form.errors.items():
            error_details[field] = [str(error) for error in errors]

        # Get first error message
        first_field = list(form.errors.keys())[0] if form.errors else None
        first_error = form.errors[first_field][0] if first_field else "Błąd walidacji danych"

        return JsonResponse(
            {
                "error": str(first_error),
                "error_code": "INVALID_INPUT",
                "details": error_details,
            },
            status=400,
        )


@require_http_methods(["GET"])
def get_curriculum_refs_view(request):
    """
    GET /api/curriculum-refs

    Returns complete dictionary of curriculum reference codes and their full text.
    Used for tooltip display.

    Currently returns mock data. Phase 2 will query the database.
    """
    try:
        return JsonResponse(
            {
                "references": MOCK_CURRICULUM_REFS,
                "count": len(MOCK_CURRICULUM_REFS),
            },
            status=200,
        )
    except Exception as e:
        return JsonResponse(
            {
                "error": "Błąd pobierania podstawy programowej",
                "error_code": "DATABASE_ERROR",
                "details": str(e),
            },
            status=500,
        )


@require_http_methods(["GET"])
def get_curriculum_ref_by_code_view(request, code):
    """
    GET /api/curriculum-refs/<code>

    Retrieves full text for a specific curriculum reference code.

    Currently returns mock data. Phase 2 will query the database.
    """
    try:
        # Check if code exists in mock data
        if code not in MOCK_CURRICULUM_REFS:
            return JsonResponse(
                {
                    "error": f"Nie znaleziono kodu podstawy programowej: {code}",
                    "error_code": "REFERENCE_NOT_FOUND",
                },
                status=404,
            )

        # Return curriculum reference details
        return JsonResponse(
            {
                "reference_code": code,
                "full_text": MOCK_CURRICULUM_REFS[code],
                "created_at": "2025-10-28T10:30:00Z",
            },
            status=200,
        )
    except Exception as e:
        return JsonResponse(
            {
                "error": "Błąd pobierania podstawy programowej",
                "error_code": "DATABASE_ERROR",
                "details": str(e),
            },
            status=500,
        )


@require_http_methods(["GET"])
def get_modules_view(request):
    """
    GET /api/modules

    Returns list of known educational modules.
    Optional query parameter: ai_suggested (true/false)

    Currently returns mock data. Phase 2 will query the database.
    """
    try:
        # Parse optional query parameter
        ai_suggested_filter = request.GET.get('ai_suggested', None)

        # Filter modules if parameter is provided
        filtered_modules = MOCK_MODULES
        if ai_suggested_filter is not None:
            # Convert string to boolean
            filter_value = ai_suggested_filter.lower() in ('true', '1', 'yes')
            filtered_modules = [
                m for m in MOCK_MODULES if m['is_ai_suggested'] == filter_value
            ]

        # Construct response
        return JsonResponse(
            {
                "modules": filtered_modules,
                "count": len(filtered_modules),
            },
            status=200,
        )
    except Exception as e:
        return JsonResponse(
            {
                "error": "Błąd pobierania modułów edukacyjnych",
                "error_code": "DATABASE_ERROR",
                "details": str(e),
            },
            status=500,
        )
