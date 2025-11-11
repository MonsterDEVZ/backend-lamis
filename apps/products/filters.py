"""
Django Filters for Products App
Implements three-level filtering: Brand → Category → Collection → Product
"""

from django_filters import rest_framework as filters
from apps.products.models import Product


class ProductFilter(filters.FilterSet):
    """
    FilterSet for Product model
    Supports filtering by brand, category, collection, and flags
    """
    brand_id = filters.NumberFilter(field_name='brand__id')
    category_id = filters.NumberFilter(field_name='category__id')
    collection_id = filters.NumberFilter(field_name='collection__id')
    is_new = filters.BooleanFilter(field_name='is_new')
    is_on_sale = filters.BooleanFilter(field_name='is_on_sale')
    min_price = filters.NumberFilter(field_name='price', lookup_expr='gte')
    max_price = filters.NumberFilter(field_name='price', lookup_expr='lte')

    class Meta:
        model = Product
        fields = [
            'brand_id', 'category_id', 'collection_id',
            'is_new', 'is_on_sale',
            'min_price', 'max_price'
        ]
