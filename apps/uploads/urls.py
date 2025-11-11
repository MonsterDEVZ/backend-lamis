"""
URL Configuration for Uploads App
"""

from django.urls import path
from apps.uploads.views import ImageUploadView

urlpatterns = [
    path('upload/', ImageUploadView.as_view(), name='image-upload'),
]
