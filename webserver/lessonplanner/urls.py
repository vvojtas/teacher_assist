"""
URL configuration for lessonplanner app
"""

from django.urls import path
from . import views

app_name = 'lessonplanner'

urlpatterns = [
    # Main page
    path('', views.index, name='index'),

    # API endpoints (following django_api.md specification)
    path('api/fill-work-plan', views.fill_work_plan_view, name='fill_work_plan'),
    path('api/curriculum-refs', views.get_all_curriculum_refs_view, name='curriculum_refs_all'),
    path('api/curriculum-refs/<str:code>', views.get_curriculum_ref_by_code_view, name='curriculum_ref_by_code'),
    path('api/modules', views.get_modules_view, name='modules'),
]
