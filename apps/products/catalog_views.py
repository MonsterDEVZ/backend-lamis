"""
SEO-Friendly Catalog Navigation Views

Implements URL structure:
- /catalog/{section_slug}/ → categories for section
- /catalog/{section_slug}/{category_slug}/ → collections/types for category
- /catalog/{section_slug}/{category_slug}/{collection_or_type_slug}/ → products
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.shortcuts import get_object_or_404
from django.db.models import Q

from apps.products.models import Section, Category, Collection, Type, Product
from apps.products.serializers import (
    SectionSerializer,
    CategorySerializer,
    CollectionSerializer,
    TypeSerializer,
    ProductListSerializer
)


class CatalogSectionView(APIView):
    """
    GET /catalog/{section_slug}/

    Returns:
    - Section details
    - List of categories available in this section
    """
    permission_classes = [AllowAny]

    def get(self, request, section_slug):
        section = get_object_or_404(Section, slug=section_slug)
        categories = section.categories.all()

        return Response({
            'section': SectionSerializer(section).data,
            'categories': CategorySerializer(categories, many=True).data
        })


class CatalogCategoryView(APIView):
    """
    GET /catalog/{section_slug}/{category_slug}/

    Returns:
    - Section details
    - Category details
    - List of collections for this section+category
    - List of types for this section+category
    """
    permission_classes = [AllowAny]

    def get(self, request, section_slug, category_slug):
        section = get_object_or_404(Section, slug=section_slug)
        category = get_object_or_404(Category, slug=category_slug)

        # Get collections and types for this section+category
        collections = Collection.objects.filter(
            section=section,
            category=category
        )
        types = Type.objects.filter(
            section=section,
            category=category
        )

        # Verify that this section+category combination exists
        # (i.e., has at least one collection or type)
        if not collections.exists() and not types.exists():
            return Response(
                {'error': 'No collections or types found for this section and category'},
                status=status.HTTP_404_NOT_FOUND
            )

        return Response({
            'section': SectionSerializer(section).data,
            'category': CategorySerializer(category).data,
            'collections': CollectionSerializer(collections, many=True).data,
            'types': TypeSerializer(types, many=True).data
        })


class CatalogProductsView(APIView):
    """
    GET /catalog/{section_slug}/{category_slug}/{collection_or_type_slug}/

    Returns:
    - Section details
    - Category details
    - Collection OR Type details
    - List of products

    Algorithm:
    1. Try to find Collection with this slug in section+category
    2. If not found, try to find Type with this slug
    3. If neither found, return 404
    """
    permission_classes = [AllowAny]

    def get(self, request, section_slug, category_slug, item_slug):
        section = get_object_or_404(Section, slug=section_slug)
        category = get_object_or_404(Category, slug=category_slug)

        # Try to find Collection first
        try:
            collection = Collection.objects.get(
                section=section,
                category=category,
                slug=item_slug
            )
            products = Product.objects.filter(
                section=section,
                category=category,
                collection=collection
            ).select_related('section', 'category', 'collection', 'type')

            return Response({
                'section': SectionSerializer(section).data,
                'category': CategorySerializer(category).data,
                'collection': CollectionSerializer(collection).data,
                'type': None,
                'products': ProductListSerializer(products, many=True).data
            })
        except Collection.DoesNotExist:
            pass

        # Try to find Type
        try:
            product_type = Type.objects.get(
                section=section,
                category=category,
                slug=item_slug
            )
            products = Product.objects.filter(
                section=section,
                category=category,
                type=product_type
            ).select_related('section', 'category', 'collection', 'type')

            return Response({
                'section': SectionSerializer(section).data,
                'category': CategorySerializer(category).data,
                'collection': None,
                'type': TypeSerializer(product_type).data,
                'products': ProductListSerializer(products, many=True).data
            })
        except Type.DoesNotExist:
            pass

        # Neither collection nor type found
        return Response(
            {'error': 'Collection or Type not found'},
            status=status.HTTP_404_NOT_FOUND
        )


class CatalogBrowseView(APIView):
    """
    GET /catalog/browse/

    Returns complete catalog structure for navigation:
    - All sections with their categories, collections, and types

    This endpoint is useful for building navigation menus and sitemaps
    """
    permission_classes = [AllowAny]

    def get(self, request):
        sections = Section.objects.all()
        catalog_structure = []

        for section in sections:
            section_data = {
                'section': SectionSerializer(section).data,
                'categories': []
            }

            # Get all unique categories for this section by checking collections and types
            collection_categories = Collection.objects.filter(section=section).values_list('category', flat=True).distinct()
            type_categories = Type.objects.filter(section=section).values_list('category', flat=True).distinct()

            # Combine and get unique category IDs
            category_ids = set(list(collection_categories) + list(type_categories))

            # Get Category objects
            categories = Category.objects.filter(id__in=category_ids)

            for category in categories:
                category_data = {
                    'category': CategorySerializer(category).data,
                    'collections': CollectionSerializer(
                        Collection.objects.filter(section=section, category=category),
                        many=True
                    ).data,
                    'types': TypeSerializer(
                        Type.objects.filter(section=section, category=category),
                        many=True
                    ).data
                }
                section_data['categories'].append(category_data)

            catalog_structure.append(section_data)

        return Response({
            'catalog': catalog_structure
        })
