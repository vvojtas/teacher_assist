from typing import Any, Dict, List, Optional
from ..models import CurriculumReference, EducationalModule


def get_all_curriculum_refs() -> Dict[str, str]:
    """
    Retrieve all curriculum references from database.

    Returns:
        Dict[str, str]: Dictionary mapping reference codes to full text
                       Example: {"4.15": "Full text...", "3.8": "Full text..."}

    Raises:
        Exception: Database query errors propagate to caller
    """
    # Query all curriculum references, ordered by code
    refs = CurriculumReference.objects.all().order_by('reference_code')

    # Convert to dictionary format {code: full_text}
    return {ref.reference_code: ref.full_text for ref in refs}


def get_curriculum_ref_by_code(code: str) -> Optional[CurriculumReference]:
    """
    Retrieve a single curriculum reference by code.

    Args:
        code: Curriculum reference code (e.g., "4.15", "3.8")

    Returns:
        CurriculumReference object if found, None otherwise

    Raises:
        Exception: Database query errors propagate to caller
    """
    try:
        return CurriculumReference.objects.get(reference_code=code)
    except CurriculumReference.DoesNotExist:
        return None


def get_all_modules(ai_suggested: Optional[bool] = None) -> List[Dict[str, Any]]:
    """
    Retrieve all educational modules from database.

    Args:
        ai_suggested: Optional filter - True for AI-suggested modules only,
                     False for predefined modules only, None for all modules

    Returns:
        List[Dict]: List of module dictionaries with keys:
                   - id: Module ID
                   - name: Module name (e.g., "MATEMATYKA")
                   - is_ai_suggested: Boolean flag
                   - created_at: ISO timestamp string

    Raises:
        Exception: Database query errors propagate to caller
    """
    # Build query with optional filter
    query = EducationalModule.objects.all()

    if ai_suggested is not None:
        query = query.filter(is_ai_suggested=ai_suggested)

    # Order by module name for consistent results
    query = query.order_by('module_name')

    # Convert to list of dictionaries
    return [
        {
            'id': module.id,
            'name': module.module_name,
            'is_ai_suggested': module.is_ai_suggested,
            'created_at': module.created_at.isoformat()
        }
        for module in query
    ]


def get_all_module_names() -> List[str]:
    """
    Retrieve just the module names from database (for AI service).

    Returns:
        List[str]: List of module names (e.g., ["JĘZYK", "MATEMATYKA", ...])

    Raises:
        Exception: Database query errors propagate to caller
    """
    return list(
        EducationalModule.objects.all()
        .order_by('module_name')
        .values_list('module_name', flat=True)
    )


def get_all_curriculum_ref_codes() -> List[str]:
    """
    Retrieve just the curriculum reference codes from database (for AI service).

    Returns:
        List[str]: List of reference codes (e.g., ["1.1", "2.5", "4.15", ...])

    Raises:
        Exception: Database query errors propagate to caller
    """
    return list(
        CurriculumReference.objects.all()
        .order_by('reference_code')
        .values_list('reference_code', flat=True)
    )
