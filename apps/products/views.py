"""
DRF ViewSets for Products App
НОВАЯ АРХИТЕКТУРА: Section → Brand → Category → Collection/Type → Product
Implements Public Read API and Admin CRUD API
"""

from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django_filters.rest_framework import DjangoFilterBackend

from apps.products.models import (
    Section, Brand, Category, Collection, Type, Product, Color,
    TutorialCategory, TutorialVideo,
    MaterialCategory, Material
)
from apps.products.serializers import (
    SectionSerializer,
    BrandSerializer,
    CategorySerializer,
    CollectionSerializer,
    TypeSerializer,
    ProductListSerializer,
    ProductDetailSerializer,
    ProductCreateUpdateSerializer,
    ColorSerializer,
    TutorialCategorySerializer,
    PlumbingProductSerializer,
    MaterialCategorySerializer,
    MaterialSerializer,
)
from apps.products.filters import ProductFilter, BrandFilter, CategoryFilter, CollectionFilter, TypeFilter
from apps.products.permissions import IsAdminOrReadOnly, IsAdmin


class SectionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Section model

    Public endpoints (GET):
    - list: GET /api/v1/sections/
    - retrieve: GET /api/v1/sections/{id}/
    - categories: GET /api/v1/sections/{id}/categories/

    Admin endpoints (POST/PUT/PATCH/DELETE):
    - create: POST /api/v1/admin/sections/
    - update: PUT /api/v1/admin/sections/{id}/
    - partial_update: PATCH /api/v1/admin/sections/{id}/
    - destroy: DELETE /api/v1/admin/sections/{id}/
    """
    queryset = Section.objects.all()
    serializer_class = SectionSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']

    @action(detail=True, methods=['get'])
    def categories(self, request, pk=None):
        """Get all categories for a specific section"""
        section = self.get_object()
        categories = section.categories.all()
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)


class BrandViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Brand model
    НОВАЯ АРХИТЕКТУРА: Brand - второй уровень после Section

    Public endpoints (GET):
    - list: GET /api/v1/brands/
    - retrieve: GET /api/v1/brands/{id}/

    Filtering:
    - ?section_id=1 (get brands that have categories in this section)
    - ?section_slug=mebel-dlya-vannoy

    Admin endpoints (POST/PUT/PATCH/DELETE):
    - create: POST /api/v1/admin/brands/
    - update: PUT /api/v1/admin/brands/{id}/
    - partial_update: PATCH /api/v1/admin/brands/{id}/
    - destroy: DELETE /api/v1/admin/brands/{id}/
    """
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = BrandFilter
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
    НОВАЯ АРХИТЕКТУРА: Category зависит от Section + Brand

    Public endpoints (GET):
    - list: GET /api/v1/categories/
    - retrieve: GET /api/v1/categories/{id}/
    - first_brand: GET /api/v1/categories/{id}/first-brand/ (для автовыбора фильтров)

    Filtering:
    - ?section_id=1 (get categories for specific section)
    - ?section_slug=mebel-dlya-vannoy
    - ?brand_id=1 (get categories for specific brand)
    - ?brand_slug=lamis
    - ?section_id=1&brand_id=1 (most common use case)

    Admin endpoints (POST/PUT/PATCH/DELETE):
    - create: POST /api/v1/admin/categories/
    - update: PUT /api/v1/admin/categories/{id}/
    - partial_update: PATCH /api/v1/admin/categories/{id}/
    - destroy: DELETE /api/v1/admin/categories/{id}/
    """
    queryset = Category.objects.select_related('section', 'brand').all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = CategoryFilter
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']

    def list(self, request, *args, **kwargs):
        """
        Override list to return unique categories by name when filtering by section
        This removes duplicates when same category exists for multiple brands
        """
        queryset = self.filter_queryset(self.get_queryset())

        # Check if filtering by section (for navigation menu)
        section_id = request.query_params.get('section_id')
        section_slug = request.query_params.get('section_slug')
        brand_id = request.query_params.get('brand_id')
        brand_slug = request.query_params.get('brand_slug')

        # If filtering by section without brand - return unique category names
        if (section_id or section_slug) and not (brand_id or brand_slug):
            # Get unique categories by name
            seen_names = set()
            unique_categories = []
            for category in queryset:
                if category.name not in seen_names:
                    seen_names.add(category.name)
                    unique_categories.append(category)

            serializer = self.get_serializer(unique_categories, many=True)
            # Return in DRF paginated format for consistency
            return Response({
                'count': len(unique_categories),
                'next': None,
                'previous': None,
                'results': serializer.data
            })

        # Default behavior for other cases
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'count': len(queryset),
            'next': None,
            'previous': None,
            'results': serializer.data
        })

    @action(detail=True, methods=['get'])
    def first_brand(self, request, pk=None):
        """
        GET /api/v1/categories/{id}/first-brand/

        Возвращает бренд для этой категории (для автоматического выбора фильтров)
        """
        category = self.get_object()
        brand = category.brand

        if not brand:
            return Response({'error': 'No brand found for this category'}, status=404)

        return Response({
            'id': brand.id,
            'name': brand.name,
            'slug': brand.slug
        })


class CollectionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Collection model
    НОВАЯ АРХИТЕКТУРА: Collection зависит от Brand + Category

    Public endpoints (GET):
    - list: GET /api/v1/collections/
    - retrieve: GET /api/v1/collections/{id}/
    - first_brand: GET /api/v1/collections/{id}/first-brand/ (для автовыбора фильтров)
    - first_category: GET /api/v1/collections/{id}/first-category/ (для автовыбора фильтров)

    Filtering:
    - ?section_id=1 (get collections for specific section - for header navigation)
    - ?section_slug=mebel-dlya-vannoy
    - ?brand_id=1 (get collections for specific brand)
    - ?brand_slug=lamis
    - ?category_id=2
    - ?category_slug=furniture
    - ?brand_id=1&category_id=2 (most common use case)

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
    filterset_class = CollectionFilter
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']

    def list(self, request, *args, **kwargs):
        """
        Override list to return unique collections by name when filtering by section
        This removes duplicates when same collection exists for multiple categories/brands
        """
        queryset = self.filter_queryset(self.get_queryset())

        # Check if filtering by section only (for navigation menu)
        section_id = request.query_params.get('section_id')
        section_slug = request.query_params.get('section_slug')
        brand_id = request.query_params.get('brand_id')
        brand_slug = request.query_params.get('brand_slug')
        category_id = request.query_params.get('category_id')
        category_slug = request.query_params.get('category_slug')

        # If filtering by section without brand/category - return unique collection names
        if (section_id or section_slug) and not (brand_id or brand_slug or category_id or category_slug):
            # Get unique collections by name
            seen_names = set()
            unique_collections = []
            for collection in queryset:
                if collection.name not in seen_names:
                    seen_names.add(collection.name)
                    unique_collections.append(collection)

            serializer = self.get_serializer(unique_collections, many=True)
            # Return in DRF paginated format for consistency
            return Response({
                'count': len(unique_collections),
                'next': None,
                'previous': None,
                'results': serializer.data
            })

        # Default behavior for other cases
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'count': len(queryset),
            'next': None,
            'previous': None,
            'results': serializer.data
        })

    @action(detail=True, methods=['get'])
    def first_brand(self, request, pk=None):
        """
        GET /api/v1/collections/{id}/first-brand/

        Возвращает бренд для этой коллекции (для автоматического выбора фильтров)
        """
        collection = self.get_object()
        brand = collection.brand

        if not brand:
            return Response({'error': 'No brand found for this collection'}, status=404)

        return Response({
            'id': brand.id,
            'name': brand.name,
            'slug': brand.slug
        })

    @action(detail=True, methods=['get'])
    def first_category(self, request, pk=None):
        """
        GET /api/v1/collections/{id}/first-category/

        Возвращает категорию для этой коллекции (для автоматического выбора фильтров)
        """
        collection = self.get_object()
        category = collection.category

        if not category:
            return Response({'error': 'No category found for this collection'}, status=404)

        return Response({
            'id': category.id,
            'name': category.name,
            'slug': category.slug
        })


class TypeViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Type model
    НОВАЯ АРХИТЕКТУРА: Type зависит ТОЛЬКО от Category

    Public endpoints (GET):
    - list: GET /api/v1/types/
    - retrieve: GET /api/v1/types/{id}/

    Filtering:
    - ?category_id=1 (get types for specific category)
    - ?category_slug=sanfarfor

    Admin endpoints (POST/PUT/PATCH/DELETE):
    - create: POST /api/v1/admin/types/
    - update: PUT /api/v1/admin/types/{id}/
    - partial_update: PATCH /api/v1/admin/types/{id}/
    - destroy: DELETE /api/v1/admin/types/{id}/
    """
    queryset = Type.objects.select_related('category').all()
    serializer_class = TypeSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = TypeFilter
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']


class ColorViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Color model (Справочник цветов)

    Централизованное управление палитрой цветов для всех продуктов.

    Public endpoints (GET):
    - list: GET /api/v1/colors/
      Returns all colors in the catalog

    - retrieve: GET /api/v1/colors/{id}/
      Returns specific color details

    Admin endpoints (POST/PUT/PATCH/DELETE):
    - create: POST /api/v1/colors/
      Create new color in catalog

    - update: PUT /api/v1/colors/{id}/
      Full update of color

    - partial_update: PATCH /api/v1/colors/{id}/
      Partial update of color

    - destroy: DELETE /api/v1/colors/{id}/
      Delete color from catalog

    Example usage:
    ```
    # Get all colors
    GET /api/v1/colors/

    # Create new color
    POST /api/v1/colors/
    {
        "name": "Белый глянец",
        "hex_code": "#FFFFFF"
    }

    # Create texture color
    POST /api/v1/colors/
    {
        "name": "Дуб венге",
        "texture_image": "https://storage.example.com/textures/oak-wenge.jpg"
    }
    ```
    """
    queryset = Color.objects.all()
    serializer_class = ColorSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']


class ProductViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Product model
    SIMPLIFIED ARCHITECTURE: Backend filters only by section, frontend handles the rest

    NEW STRATEGY:
    - Backend returns ALL products for a section (e.g., all Санфарфор products)
    - Frontend filters by category/collection/type in memory
    - Benefits: No double-firing, instant filtering, better UX

    Public endpoints (GET):
    - list: GET /api/v1/products/
    - retrieve: GET /api/v1/products/{slug}/

    Section filtering (ONLY backend filter):
    - ?section_id=1  → Returns ALL products for section 1
    - ?section_slug=mebel-dlia-vannoi  → Returns ALL products for section

    Flag filters (lightweight, done on backend):
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
    - ?page=1&limit=100  (larger limit since filtering done on frontend)

    Admin endpoints (POST/PUT/PATCH/DELETE):
    - create: POST /api/v1/admin/products/
    - update: PUT /api/v1/admin/products/{id}/
    - partial_update: PATCH /api/v1/admin/products/{id}/
    - destroy: DELETE /api/v1/admin/products/{id}/
    """
    queryset = Product.objects.select_related('section', 'brand', 'category', 'collection', 'type', 'color').all()
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


class TutorialCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for Tutorial Categories (Read-Only)

    Public endpoints (GET):
    - list: GET /api/v1/tutorials/
      Returns all active tutorial categories

    - retrieve: GET /api/v1/tutorials/{slug}/
      Returns specific category with all its videos

    Example response for retrieve:
    {
        "id": 1,
        "title": "Установка мебели",
        "slug": "furniture-installation",
        "banner_image_url": "https://...",
        "pageTitle": "Установка мебели",
        "pageBannerUrl": "https://...",
        "videos": [
            {
                "id": 1,
                "title": "Сборка шкафа-купе",
                "videoId": "dQw4w9WgXcQ"
            },
            ...
        ]
    }

    Admin operations (POST/PUT/DELETE) should be done through Django Admin panel.
    """
    queryset = TutorialCategory.objects.filter(is_active=True).prefetch_related('videos')
    serializer_class = TutorialCategorySerializer
    permission_classes = [AllowAny]  # Public access
    lookup_field = 'slug'  # Use slug instead of id for URLs


class PlumbingSectionViewSet(viewsets.ViewSet):
    """
    ViewSet for PlumbingSection (CAIZER brand products)

    Public endpoint (GET):
    - GET /api/v1/plumbing-section/
      Returns all CAIZER products grouped by categories

    Example response:
    {
        "rakoviny": [
            {
                "id": 1,
                "name": "Раковина встраиваемая белая",
                "brand": "Caizer",
                "brand_id": 3,
                "category": "Раковины",
                "category_id": 5,
                "section": "Санфарфор",
                "section_id": 2,
                "image_url": "https://..."
            },
            ...
        ],
        "unitazy": [...],
        "bidet": [...],
        "pissuari": [...],
        "smesiteli": [...],
        "dushevye": [...],
        "vanny": [...]
    }

    Categories:
    - rakoviny: Раковины (ID=5)
    - unitazy: Унитазы (ID=4)
    - bidet: Биде (ID=6)
    - pissuari: Писсуары (ID=25)
    - smesiteli: Смесители (IDs=26,27,28,29)
    - dushevye: Душевые (IDs=30,31,32,33)
    - vanny: Ванны (ID=1)
    """
    permission_classes = [AllowAny]

    def list(self, request):
        """
        GET /api/v1/plumbing-section/
        Returns CAIZER products grouped by categories

        Uses category names instead of IDs to work across different databases
        """
        from django.db.models import Q

        # Find CAIZER brand dynamically
        try:
            caizer_brand = Brand.objects.get(name__iexact='Caizer')
        except Brand.DoesNotExist:
            return Response({
                'rakoviny': [],
                'unitazy': [],
                'bidet': [],
                'pissuari': [],
                'smesiteli': [],
                'dushevye': [],
                'vanny': [],
            })

        # Category name mapping (works across different databases)
        CATEGORY_NAME_MAPPING = {
            'rakoviny': ['Раковины'],
            'unitazy': ['Унитазы'],
            'bidet': ['Биде'],
            'pissuari': ['Писсуары'],
            'smesiteli': ['Смесители для раковины', 'Смесители для ванны', 'Смесители для душа', 'Смесители для кухни'],
            'dushevye': ['Душевые кабины', 'Душевые уголки', 'Душевые двери', 'Поддоны'],
            'vanny': ['Ванны'],
        }

        # Fetch all CAIZER products
        caizer_products = Product.objects.filter(
            brand=caizer_brand
        ).select_related('section', 'brand', 'category')

        # Group products by category
        result = {}
        for key, category_names in CATEGORY_NAME_MAPPING.items():
            # Build Q filter for category names
            category_filter = Q()
            for cat_name in category_names:
                category_filter |= Q(category__name__iexact=cat_name)

            products = caizer_products.filter(category_filter)
            serializer = PlumbingProductSerializer(products, many=True)
            result[key] = serializer.data

        return Response(result)


# ========================
# Materials for Download
# ========================

class MaterialCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    MaterialCategory ViewSet (Read-Only for Public)

    Endpoints:
        GET /api/v1/material-categories/          - List all categories
        GET /api/v1/material-categories/{id}/     - Get category details

    Features:
        - Public read access
        - Returns categories ordered by order field
        - Includes material count for each category
    """
    queryset = MaterialCategory.objects.all().order_by('order', 'name')
    serializer_class = MaterialCategorySerializer
    permission_classes = [AllowAny]
    pagination_class = None  # No pagination for categories


class MaterialViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Material ViewSet (Read-Only for Public)

    Endpoints:
        GET /api/v1/materials/?page=1&limit=10            - List materials (paginated)
        GET /api/v1/materials/{id}/                       - Get material details

    Features:
        - Public read access
        - Pagination with customizable limit (default: 10, max: 100)
        - Only returns all materials
        - Ordered by order field, then by created_at (newest first)

    Query Parameters:
        - page: Page number (default: 1)
        - limit: Items per page (default: 10, max: 100)

    Response Format:
        {
            "count": 25,
            "total_pages": 3,
            "current_page": 1,
            "page_size": 10,
            "next": "http://api.example.com/materials/?page=2",
            "previous": null,
            "results": [...]
        }
    """
    serializer_class = MaterialSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        """
        Return all materials.
        """
        queryset = Material.objects.select_related('category').all()
        return queryset

    def list(self, request, *args, **kwargs):
        """
        Custom list method with enhanced pagination info.
        Adds total_pages, current_page, and page_size to response.
        """
        queryset = self.filter_queryset(self.get_queryset())

        # Get page size from query params (default: 10, max: 100)
        try:
            page_size = int(request.query_params.get('limit', 10))
            page_size = min(page_size, 100)  # Max 100 items per page
            page_size = max(page_size, 1)    # Min 1 item per page
        except (ValueError, TypeError):
            page_size = 10

        # Paginate queryset
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response = self.get_paginated_response(serializer.data)

            # Add custom pagination metadata
            total_count = queryset.count()
            total_pages = (total_count + page_size - 1) // page_size  # Ceiling division
            current_page = int(request.query_params.get('page', 1))

            response.data['total_pages'] = total_pages
            response.data['current_page'] = current_page
            response.data['page_size'] = page_size

            return response

        # Fallback if pagination is disabled
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
