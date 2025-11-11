"""
URL Configuration for Authentication App
"""

from django.urls import path
from apps.authentication.views import (
    UserRegisterView,
    UserLoginView,
    UserLogoutView,
    UserMeView,
    CustomTokenRefreshView
)

urlpatterns = [
    path('register/', UserRegisterView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    path('me/', UserMeView.as_view(), name='me'),
    path('refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
]
