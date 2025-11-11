"""
Custom Permissions for Products App
"""

from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Custom permission:
    - Allow read-only access (GET, HEAD, OPTIONS) for anyone
    - Allow write access (POST, PUT, PATCH, DELETE) only for admin users
    """

    def has_permission(self, request, view):
        # Read permissions are allowed for any request (GET, HEAD, OPTIONS)
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions only for authenticated admin users
        return request.user and request.user.is_authenticated and request.user.is_admin


class IsAdmin(permissions.BasePermission):
    """
    Custom permission to only allow admin users
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_admin
