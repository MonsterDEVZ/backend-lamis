"""
Search ViewSet for Products App
Provides unified search across Products, Collections, Categories, and Brands
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.db.models import Q, Case, When, IntegerField

from apps.products.models import Section, Brand, Category, Collection, Type, Product
from apps.products.serializers import SearchResultSerializer


class SearchViewSet(viewsets.ViewSet):
    """
    ViewSet for unified search across all product-related models

    Endpoint:
    GET /api/v1/search/?q=omega

    Returns unified search results from:
    - Products
    - Collections
    - Categories
    - Brands
    """
    permission_classes = [AllowAny]

    def list(self, request):
        """
        GET /api/v1/search/?q=query

        Search across all models and return unified results
        """
        query = request.query_params.get('q', '').strip()

        if not query:
            return Response({
                'results': [],
                'total': 0,
                'message': 'Please provide a search query using ?q=your_query'
            })

        if len(query) < 2:
            return Response({
                'results': [],
                'total': 0,
                'message': 'Search query must be at least 2 characters'
            })

        # Collect all results
        results = []

        # 1. Search Collections
        collections = self._search_collections(query)
        results.extend(collections)

        # 2. Search Products
        products = self._search_products(query)
        results.extend(products)

        # 3. Search Categories
        categories = self._search_categories(query)
        results.extend(categories)

        # 4. Search Brands
        brands = self._search_brands(query)
        results.extend(brands)

        # Serialize results
        serializer = SearchResultSerializer(results, many=True)

        return Response({
            'results': serializer.data,
            'total': len(serializer.data)
        })

    def _search_collections(self, query):
        """Search in Collections with priority ordering"""
        query_lower = query.lower()

        collections = Collection.objects.select_related('brand', 'category', 'category__section').annotate(
            priority=Case(
                When(name__iexact=query, then=1),  # Exact match
                When(name__istartswith=query, then=2),  # Starts with
                When(name__icontains=query, then=3),  # Contains
                default=4,
                output_field=IntegerField()
            )
        ).filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        ).order_by('priority', 'name')[:10]

        results = []
        for collection in collections:
            # Breadcrumb: "Section > Brand > Collection"
            breadcrumb = f"{collection.category.section.name} > {collection.brand.name} > {collection.name}"

            results.append({
                'id': collection.id,
                'name': collection.name,
                'type': 'collection',
                'breadcrumb': breadcrumb,
                'section_id': collection.category.section.id,
                'brand_id': collection.brand.id,
                'category_id': collection.category.id,
                'collection_id': collection.id,
                'type_id': None,
                'slug': collection.slug,
                'image': collection.image if collection.image else None
            })

        return results

    def _search_products(self, query):
        """Search in Products with priority ordering"""
        query_lower = query.lower()

        products = Product.objects.select_related(
            'section', 'brand', 'category', 'collection', 'type'
        ).annotate(
            priority=Case(
                When(name__iexact=query, then=1),  # Exact match
                When(name__istartswith=query, then=2),  # Starts with
                When(name__icontains=query, then=3),  # Contains
                default=4,
                output_field=IntegerField()
            )
        ).filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        ).order_by('priority', 'name')[:10]

        results = []
        for product in products:
            # Breadcrumb: "Section > Category > Product"
            # or "Section > Category > Collection > Product" if collection exists
            if product.collection:
                breadcrumb = f"{product.section.name} > {product.category.name} > {product.collection.name} > {product.name}"
            else:
                breadcrumb = f"{product.section.name} > {product.category.name} > {product.name}"

            results.append({
                'id': product.id,
                'name': product.name,
                'type': 'product',
                'breadcrumb': breadcrumb,
                'section_id': product.section.id,
                'brand_id': product.brand.id,
                'category_id': product.category.id,
                'collection_id': product.collection.id if product.collection else None,
                'type_id': product.type.id if product.type else None,
                'slug': product.slug,
                'image': product.main_image_url
            })

        return results

    def _search_categories(self, query):
        """Search in Categories with priority ordering"""
        query_lower = query.lower()

        categories = Category.objects.select_related('section', 'brand').annotate(
            priority=Case(
                When(name__iexact=query, then=1),  # Exact match
                When(name__istartswith=query, then=2),  # Starts with
                When(name__icontains=query, then=3),  # Contains
                default=4,
                output_field=IntegerField()
            )
        ).filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        ).order_by('priority', 'name')[:10]

        results = []
        for category in categories:
            # Breadcrumb: "Section > Brand > Category"
            breadcrumb = f"{category.section.name} > {category.brand.name} > {category.name}"

            results.append({
                'id': category.id,
                'name': category.name,
                'type': 'category',
                'breadcrumb': breadcrumb,
                'section_id': category.section.id,
                'brand_id': category.brand.id,
                'category_id': category.id,
                'collection_id': None,
                'type_id': None,
                'slug': category.slug,
                'image': None
            })

        return results

    def _search_brands(self, query):
        """Search in Brands with priority ordering"""
        query_lower = query.lower()

        brands = Brand.objects.annotate(
            priority=Case(
                When(name__iexact=query, then=1),  # Exact match
                When(name__istartswith=query, then=2),  # Starts with
                When(name__icontains=query, then=3),  # Contains
                default=4,
                output_field=IntegerField()
            )
        ).filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        ).order_by('priority', 'name')[:10]

        results = []
        for brand in brands:
            # Breadcrumb: "Бренды > Brand Name"
            breadcrumb = f"Бренды > {brand.name}"

            results.append({
                'id': brand.id,
                'name': brand.name,
                'type': 'brand',
                'breadcrumb': breadcrumb,
                'section_id': None,
                'brand_id': brand.id,
                'category_id': None,
                'collection_id': None,
                'type_id': None,
                'slug': brand.slug,
                'image': brand.image if brand.image else None
            })

        return results
