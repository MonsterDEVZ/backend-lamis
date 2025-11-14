"""
Django Filters for Products App
НОВАЯ АРХИТЕКТУРА: Section → Brand → Category → Collection/Type → Product
"""

from django_filters import rest_framework as filters
from apps.products.models import Product, Brand, Category, Collection, Type


class ProductFilter(filters.FilterSet):
    """
    FilterSet for Product model
    Supports filtering by section, category, collection, type, and flags
    Supports both ID (number) and slug (string) filtering
    """
    # Support both ID and slug for section
    section_id = filters.NumberFilter(field_name='section__id')
    section_slug = filters.CharFilter(field_name='section__slug')

    # Support both ID and slug for category
    category_id = filters.CharFilter(method='filter_category')
    category_slug = filters.CharFilter(field_name='category__slug')

    # Support both ID and slug for collection
    collection_id = filters.CharFilter(method='filter_collection')
    collection_slug = filters.CharFilter(field_name='collection__slug')

    # Support both ID and slug for type
    type_id = filters.CharFilter(method='filter_type')
    type_slug = filters.CharFilter(field_name='type__slug')

    is_new = filters.BooleanFilter(field_name='is_new')
    is_on_sale = filters.BooleanFilter(field_name='is_on_sale')
    min_price = filters.NumberFilter(field_name='price', lookup_expr='gte')
    max_price = filters.NumberFilter(field_name='price', lookup_expr='lte')

    class Meta:
        model = Product
        fields = [
            'section_id', 'section_slug',
            'category_id', 'category_slug',
            'collection_id', 'collection_slug',
            'type_id', 'type_slug',
            'is_new', 'is_on_sale',
            'min_price', 'max_price'
        ]

    def filter_category(self, queryset, name, value):
        """Filter by category ID or slug"""
        if value.isdigit():
            return queryset.filter(category__id=int(value))
        return queryset.filter(category__slug=value)

    def filter_collection(self, queryset, name, value):
        """Filter by collection ID or slug"""
        if value.isdigit():
            return queryset.filter(collection__id=int(value))
        return queryset.filter(collection__slug=value)

    def filter_type(self, queryset, name, value):
        """Filter by type ID or slug"""
        if value.isdigit():
            return queryset.filter(type__id=int(value))
        return queryset.filter(type__slug=value)


class BrandFilter(filters.FilterSet):
    """
    FilterSet for Brand model
    НОВАЯ АРХИТЕКТУРА: Brand - второй уровень после Section
    Brands are independent but can be shown for specific sections through their categories
    """
    section_id = filters.NumberFilter(method='filter_by_section')
    section_slug = filters.CharFilter(method='filter_by_section_slug')

    class Meta:
        model = Brand
        fields = ['section_id', 'section_slug']

    def filter_by_section(self, queryset, name, value):
        """Filter brands that have categories in this section"""
        return queryset.filter(categories__section__id=value).distinct()

    def filter_by_section_slug(self, queryset, name, value):
        """Filter brands that have categories in this section (by slug)"""
        return queryset.filter(categories__section__slug=value).distinct()


class CategoryFilter(filters.FilterSet):
    """
    FilterSet for Category model
    НОВАЯ АРХИТЕКТУРА: Category зависит от Section + Brand (оба обязательны)
    """
    section_id = filters.NumberFilter(method='filter_by_section')
    section_slug = filters.CharFilter(method='filter_by_section_slug')
    brand_id = filters.NumberFilter(field_name='brand__id')
    brand_slug = filters.CharFilter(field_name='brand__slug')

    class Meta:
        model = Category
        fields = ['section_id', 'section_slug', 'brand_id', 'brand_slug']

    def filter_by_section(self, queryset, name, value):
        """Filter categories by section - returns distinct category names"""
        return queryset.filter(section__id=value).distinct()

    def filter_by_section_slug(self, queryset, name, value):
        """Filter categories by section slug - returns distinct category names"""
        return queryset.filter(section__slug=value).distinct()


class CollectionFilter(filters.FilterSet):
    """
    FilterSet for Collection model
    НОВАЯ АРХИТЕКТУРА: Collection зависит от Brand + Category
    Добавлена поддержка фильтрации по section_id для header navigation
    """
    section_id = filters.NumberFilter(method='filter_by_section')
    section_slug = filters.CharFilter(method='filter_by_section_slug')
    brand_id = filters.NumberFilter(field_name='brand__id')
    brand_slug = filters.CharFilter(field_name='brand__slug')
    category_id = filters.CharFilter(method='filter_category')
    category_slug = filters.CharFilter(field_name='category__slug')

    class Meta:
        model = Collection
        fields = ['section_id', 'section_slug', 'brand_id', 'brand_slug', 'category_id', 'category_slug']

    def filter_by_section(self, queryset, name, value):
        """Filter collections that belong to categories in this section"""
        return queryset.filter(category__section__id=value).distinct()

    def filter_by_section_slug(self, queryset, name, value):
        """Filter collections that belong to categories in this section (by slug)"""
        return queryset.filter(category__section__slug=value).distinct()

    def filter_category(self, queryset, name, value):
        """Filter by category ID or slug"""
        if value.isdigit():
            return queryset.filter(category__id=int(value))
        return queryset.filter(category__slug=value)


class TypeFilter(filters.FilterSet):
    """
    FilterSet for Type model
    НОВАЯ АРХИТЕКТУРА: Type зависит ТОЛЬКО от Category (section убрали!)
    """
    category_id = filters.CharFilter(method='filter_category')
    category_slug = filters.CharFilter(field_name='category__slug')

    class Meta:
        model = Type
        fields = ['category_id', 'category_slug']

    def filter_category(self, queryset, name, value):
        """Filter by category ID or slug"""
        if value.isdigit():
            return queryset.filter(category__id=int(value))
        return queryset.filter(category__slug=value)
