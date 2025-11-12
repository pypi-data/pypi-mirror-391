"""
ByteDocs Django - URL Configuration
URL patterns for documentation endpoints
"""

from django.urls import path
from . import views

app_name = 'bytedocs'

urlpatterns = [
    path('', views.docs_ui, name='docs_ui'),
    path('api-data.json', views.api_data, name='api_data'),
    path('openapi.json', views.openapi_json, name='openapi_json'),
    path('openapi.yaml', views.openapi_yaml, name='openapi_yaml'),
    path('chat', views.ai_chat, name='ai_chat'),
]
