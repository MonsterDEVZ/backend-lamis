"""
Custom Pagination Classes for LAMIS API
"""
from rest_framework.pagination import PageNumberPagination


class CustomPageNumberPagination(PageNumberPagination):
    """
    Custom pagination that allows dynamic page size via 'limit' query parameter

    Usage:
    - GET /api/v1/products/?page=1&limit=48
    - GET /api/v1/products/?page=2&limit=12

    If limit is not provided, defaults to PAGE_SIZE from settings (20)
    """
    page_size = 20  # Default page size
    page_size_query_param = 'limit'  # Allow client to set page size via ?limit=X
    max_page_size = 100  # Maximum allowed page size
    page_query_param = 'page'  # Page number parameter
