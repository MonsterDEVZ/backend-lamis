"""
DRF ViewSets for Products App
Implements Public Read API and Admin CRUD API
"""

from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django_filters.rest_framework import DjangoFilterBackend

from apps.products.models import Brand, Category, Collection, Product
from apps.products.serializers import (
    BrandSerializer,
    CategorySerializer,
    CollectionSerializer,
    ProductListSerializer,
    ProductDetailSerializer,
    ProductCreateUpdateSerializer
)
from apps.products.filters import ProductFilter
from apps.products.permissions import IsAdminOrReadOnly, IsAdmin


class BrandViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Brand model

    Public endpoints (GET):
    - list: GET /api/v1/brands/
    - retrieve: GET /api/v1/brands/{id}/
    - categories: GET /api/v1/brands/{id}/categories/

    Admin endpoints (POST/PUT/PATCH/DELETE):
    - create: POST /api/v1/admin/brands/
    - update: PUT /api/v1/admin/brands/{id}/
    - partial_update: PATCH /api/v1/admin/brands/{id}/
    - destroy: DELETE /api/v1/admin/brands/{id}/
    """
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']

    @action(detail=True, methods=['get'])
    def categories(self, request, pk=None):
        """Get all categories for a specific brand"""
        brand = self.get_object()
        categories = brand.categories.all()
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)


class CategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Category model

    Public endpoints (GET):
    - list: GET /api/v1/categories/
    - retrieve: GET /api/v1/categories/{id}/
    - brands: GET /api/v1/categories/{id}/brands/

    Admin endpoints (POST/PUT/PATCH/DELETE):
    - create: POST /api/v1/admin/categories/
    - update: PUT /api/v1/admin/categories/{id}/
    - partial_update: PATCH /api/v1/admin/categories/{id}/
    - destroy: DELETE /api/v1/admin/categories/{id}/
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']

    @action(detail=True, methods=['get'])
    def brands(self, request, pk=None):
        """Get all brands for a specific category"""
        category = self.get_object()
        brands = category.brands.all()
        serializer = BrandSerializer(brands, many=True)
        return Response(serializer.data)


class CollectionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Collection model

    Public endpoints (GET):
    - list: GET /api/v1/collections/
    - retrieve: GET /api/v1/collections/{id}/

    Filtering:
    - ?brand_id=1
    - ?category_id=2
    - ?brand_id=1&category_id=2

    Admin endpoints (POST/PUT/PATCH/DELETE):
    - create: POST /api/v1/admin/collections/
    - update: PUT /api/v1/admin/collections/{id}/
    - partial_update: PATCH /api/v1/admin/collections/{id}/
    - destroy: DELETE /api/v1/admin/collections/{id}/
    """
    queryset = Collection.objects.select_related('brand', 'category').all()
    serializer_class = CollectionSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['brand', 'category']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']


class ProductViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Product model

    Public endpoints (GET):
    - list: GET /api/v1/products/
    - retrieve: GET /api/v1/products/{slug}/

    Three-level filtering:
    - ?brand_id=1
    - ?brand_id=1&category_id=2
    - ?brand_id=1&category_id=2&collection_id=3
    - ?is_new=true
    - ?is_on_sale=true
    - ?min_price=1000&max_price=5000

    Search:
    - ?search=название

    Sorting:
    - ?ordering=price (ascending)
    - ?ordering=-price (descending)
    - ?ordering=-created_at (newest first)
    - ?ordering=name

    Pagination:
    - ?page=1&limit=20

    Admin endpoints (POST/PUT/PATCH/DELETE):
    - create: POST /api/v1/admin/products/
    - update: PUT /api/v1/admin/products/{id}/
    - partial_update: PATCH /api/v1/admin/products/{id}/
    - destroy: DELETE /api/v1/admin/products/{id}/
    """
    queryset = Product.objects.select_related('brand', 'category', 'collection').all()
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ProductFilter
    search_fields = ['name', 'description']
    ordering_fields = ['price', 'created_at', 'name', 'is_new']
    ordering = ['-created_at']
    lookup_field = 'slug'

    def get_serializer_class(self):
        """Return appropriate serializer class based on action"""
        if self.action == 'retrieve':
            return ProductDetailSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return ProductCreateUpdateSerializer
        return ProductListSerializer
