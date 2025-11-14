"""
Custom Pagination Classes for LAMIS API
"""
from rest_framework.pagination import PageNumberPagination


class CustomPageNumberPagination(PageNumberPagination):
    """
    Custom pagination that allows dynamic page size via 'limit' query parameter

    NEW ARCHITECTURE:
    - Frontend does filtering in memory
    - Backend returns ALL products for section (up to 500)
    - Larger page_size to support client-side filtering

    Usage:
    - GET /api/v1/products/?section_id=2  (returns all products for section)
    - GET /api/v1/products/?page=1&limit=200  (custom limit)
    """
    page_size = 100  # Increased default to return all section products
    page_size_query_param = 'limit'  # Allow client to set page size via ?limit=X
    max_page_size = 500  # Increased max to support large catalogs
    page_query_param = 'page'  # Page number parameter
