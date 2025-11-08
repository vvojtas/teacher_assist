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
    path('api/generate-metadata/', views.generate_metadata_view, name='generate_metadata'),
    path('api/generate-bulk/', views.generate_bulk_view, name='generate_bulk'),
    path('api/curriculum/<str:code>/', views.get_curriculum_tooltip_view, name='curriculum_tooltip'),
]
