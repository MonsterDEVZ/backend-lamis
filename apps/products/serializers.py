"""
DRF Serializers for Products App
"""

from rest_framework import serializers
from apps.products import models
from apps.products.models import Section, Brand, Category, Collection, Type, Product, TutorialCategory, TutorialVideo


class SectionSerializer(serializers.ModelSerializer):
    """Serializer for Section model"""

    class Meta:
        model = Section
        fields = ['id', 'name', 'slug', 'title', 'description', 'created_at']
        read_only_fields = ['id', 'slug', 'created_at']


class BrandSerializer(serializers.ModelSerializer):
    """Serializer for Brand model"""

    class Meta:
        model = Brand
        fields = ['id', 'name', 'slug', 'description', 'image', 'created_at']
        read_only_fields = ['id', 'slug', 'created_at']


class CategorySerializer(serializers.ModelSerializer):
    """
    Serializer for Category model
    НОВАЯ АРХИТЕКТУРА: Category привязана к Section + Brand
    """
    section_name = serializers.CharField(source='section.name', read_only=True)
    brand_name = serializers.CharField(source='brand.name', read_only=True)

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'section', 'section_name', 'brand', 'brand_name', 'created_at']
        read_only_fields = ['id', 'slug', 'created_at']


class CollectionSerializer(serializers.ModelSerializer):
    """
    Serializer for Collection model
    НОВАЯ АРХИТЕКТУРА: Collection привязана к Brand + Category
    """
    brand_name = serializers.CharField(source='brand.name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    section = serializers.IntegerField(source='category.section.id', read_only=True)
    section_name = serializers.CharField(source='category.section.name', read_only=True)

    class Meta:
        model = Collection
        fields = [
            'id', 'name', 'slug', 'brand', 'brand_name',
            'category', 'category_name', 'section', 'section_name',
            'image', 'description', 'created_at'
        ]
        read_only_fields = ['id', 'slug', 'created_at']


class TypeSerializer(serializers.ModelSerializer):
    """
    Serializer for Type model
    НОВАЯ АРХИТЕКТУРА: Type привязан ТОЛЬКО к Category
    """
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Type
        fields = [
            'id', 'name', 'slug',
            'category', 'category_name', 'description', 'created_at'
        ]
        read_only_fields = ['id', 'slug', 'created_at']


class ProductListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for Product list views
    Used in catalog listings with pagination
    НОВАЯ АРХИТЕКТУРА: Product имеет обязательный brand
    """
    section_name = serializers.CharField(source='section.name', read_only=True)
    brand_name = serializers.CharField(source='brand.name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    collection_name = serializers.CharField(source='collection.name', read_only=True, allow_null=True)
    type_name = serializers.CharField(source='type.name', read_only=True, allow_null=True)

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'price',
            'section', 'section_name',
            'brand', 'brand_name',
            'category', 'category_name',
            'collection', 'collection_name',
            'type', 'type_name',
            'main_image_url', 'hover_image_url', 'colors',
            'is_new', 'is_on_sale',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at']


class ProductDetailSerializer(serializers.ModelSerializer):
    """
    Full serializer for Product detail views
    Includes all product information
    НОВАЯ АРХИТЕКТУРА: Product имеет обязательный brand
    """
    section_name = serializers.CharField(source='section.name', read_only=True)
    brand_name = serializers.CharField(source='brand.name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    collection_name = serializers.CharField(source='collection.name', read_only=True, allow_null=True)
    type_name = serializers.CharField(source='type.name', read_only=True, allow_null=True)

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'price',
            'section', 'section_name',
            'brand', 'brand_name',
            'category', 'category_name',
            'collection', 'collection_name',
            'type', 'type_name',
            'main_image_url', 'hover_image_url', 'images', 'colors',
            'is_new', 'is_on_sale',
            'description',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at']


class ProductCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating/updating products (admin only)
    НОВАЯ АРХИТЕКТУРА: brand обязателен!
    """

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'price',
            'section', 'brand', 'category', 'collection', 'type',
            'main_image_url', 'hover_image_url', 'images', 'colors',
            'is_new', 'is_on_sale',
            'description'
        ]
        read_only_fields = ['id', 'slug']

    def validate_price(self, value):
        """Validate that price is positive"""
        if value < 0:
            raise serializers.ValidationError("Price must be positive")
        return value

    def validate(self, data):
        """
        Validate that collection and type belong to the selected brand and category
        НОВАЯ АРХИТЕКТУРА:
        - Collection привязана к brand + category
        - Type привязан только к category
        """
        brand = data.get('brand')
        category = data.get('category')

        # Validate collection
        if 'collection' in data and data['collection']:
            collection = data['collection']
            if collection.brand != brand:
                raise serializers.ValidationError(
                    {"collection": "Collection must belong to the selected brand"}
                )
            if collection.category != category:
                raise serializers.ValidationError(
                    {"collection": "Collection must belong to the selected category"}
                )

        # Validate type
        if 'type' in data and data['type']:
            product_type = data['type']
            if product_type.category != category:
                raise serializers.ValidationError(
                    {"type": "Type must belong to the selected category"}
                )

        return data


class SearchResultSerializer(serializers.Serializer):
    """
    Universal serializer for search results
    Унифицированный формат для всех типов результатов поиска:
    - Products
    - Collections
    - Categories
    - Brands
    """
    id = serializers.IntegerField()
    name = serializers.CharField()
    type = serializers.CharField()  # 'product', 'collection', 'category', 'brand'
    breadcrumb = serializers.CharField()  # e.g. "Мебель для ванной > Lamis > Omega"

    # Filter IDs for catalog navigation
    section_id = serializers.IntegerField(required=False, allow_null=True)
    brand_id = serializers.IntegerField(required=False, allow_null=True)
    category_id = serializers.IntegerField(required=False, allow_null=True)
    collection_id = serializers.IntegerField(required=False, allow_null=True)
    type_id = serializers.IntegerField(required=False, allow_null=True)

    # Additional fields
    slug = serializers.CharField(required=False, allow_null=True)
    image = serializers.CharField(required=False, allow_null=True)


class TutorialVideoSerializer(serializers.ModelSerializer):
    """
    Serializer for Tutorial Video

    Returns video data in format compatible with frontend EmbeddedVideoPlayer component:
    {
        "id": 1,
        "title": "Сборка шкафа-купе",
        "videoId": "dQw4w9WgXcQ"
    }
    """
    videoId = serializers.CharField(source='youtube_video_id', read_only=True)

    class Meta:
        model = models.TutorialVideo
        fields = [
            'id',
            'title',
            'videoId',  # Frontend expects 'videoId', not 'youtube_video_id'
        ]


class TutorialCategorySerializer(serializers.ModelSerializer):
    """
    Serializer for Tutorial Category

    Returns category data with nested videos in format compatible with frontend:
    {
        "id": 1,
        "title": "Установка мебели",
        "slug": "furniture-installation",
        "banner_image_url": "https://...",
        "videos": [
            {"id": 1, "title": "Сборка шкафа-купе", "videoId": "dQw4w9WgXcQ"},
            ...
        ]
    }
    """
    videos = TutorialVideoSerializer(many=True, read_only=True)
    # Alias for frontend compatibility
    pageTitle = serializers.CharField(source='title', read_only=True)
    pageBannerUrl = serializers.CharField(source='banner_image_url', read_only=True)

    class Meta:
        model = models.TutorialCategory
        fields = [
            'id',
            'title',
            'slug',
            'banner_image_url',
            'videos',
            # Frontend compatibility aliases
            'pageTitle',
            'pageBannerUrl',
        ]
