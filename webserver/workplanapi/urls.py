"""
URL configuration for workplanapi endpoints.

Maps URL patterns to view functions.
"""

from django.urls import path
from . import views

urlpatterns = [
    # POST /api/fill-work-plan
    path('fill-work-plan', views.fill_work_plan_view, name='fill_work_plan'),

    # GET /api/curriculum-refs
    path('curriculum-refs', views.get_curriculum_refs_view, name='get_curriculum_refs'),

    # GET /api/curriculum-refs/<code>
    path('curriculum-refs/<str:code>', views.get_curriculum_ref_by_code_view, name='get_curriculum_ref_by_code'),

    # GET /api/modules
    path('modules', views.get_modules_view, name='get_modules'),
]
