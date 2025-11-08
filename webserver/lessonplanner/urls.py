"""
URL configuration for lessonplanner app
"""

from django.urls import path
from . import views

app_name = 'lessonplanner'

urlpatterns = [
    # Main page
    path('', views.index, name='index'),

    # API endpoints
    path('api/fill-work-plan', views.fill_work_plan_view, name='fill_work_plan'),
    path('api/curriculum/<str:code>/', views.get_curriculum_tooltip_view, name='curriculum_tooltip'),
]
