"""
DRF Serializers for Products App
"""

from rest_framework import serializers
from apps.products.models import Brand, Category, Collection, Product, BrandCategory


class BrandSerializer(serializers.ModelSerializer):
    """Serializer for Brand model"""

    class Meta:
        model = Brand
        fields = ['id', 'name', 'slug', 'description', 'created_at']
        read_only_fields = ['id', 'slug', 'created_at']


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for Category model"""
    brand_ids = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'created_at', 'brand_ids']
        read_only_fields = ['id', 'slug', 'created_at']

    def get_brand_ids(self, obj):
        """Get list of brand IDs associated with this category"""
        return list(obj.brands.values_list('id', flat=True))


class CollectionSerializer(serializers.ModelSerializer):
    """Serializer for Collection model"""
    brand_name = serializers.CharField(source='brand.name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Collection
        fields = [
            'id', 'name', 'slug', 'brand', 'brand_name',
            'category', 'category_name', 'description', 'created_at'
        ]
        read_only_fields = ['id', 'slug', 'created_at']


class ProductListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for Product list views
    Used in catalog listings with pagination
    """
    brand_name = serializers.CharField(source='brand.name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    collection_name = serializers.CharField(source='collection.name', read_only=True, allow_null=True)

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'price',
            'brand', 'brand_name',
            'category', 'category_name',
            'collection', 'collection_name',
            'main_image_url', 'colors',
            'is_new', 'is_on_sale',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at']


class ProductDetailSerializer(serializers.ModelSerializer):
    """
    Full serializer for Product detail views
    Includes all product information
    """
    brand_name = serializers.CharField(source='brand.name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    collection_name = serializers.CharField(source='collection.name', read_only=True, allow_null=True)

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'price',
            'brand', 'brand_name',
            'category', 'category_name',
            'collection', 'collection_name',
            'main_image_url', 'images', 'colors',
            'is_new', 'is_on_sale',
            'description',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at']


class ProductCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating products (admin only)"""

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'price',
            'brand', 'category', 'collection',
            'main_image_url', 'images', 'colors',
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
        """Validate that collection belongs to the selected brand and category"""
        if 'collection' in data and data['collection']:
            collection = data['collection']
            brand = data.get('brand')
            category = data.get('category')

            if collection.brand != brand:
                raise serializers.ValidationError(
                    {"collection": "Collection must belong to the selected brand"}
                )
            if collection.category != category:
                raise serializers.ValidationError(
                    {"collection": "Collection must belong to the selected category"}
                )

        return data
