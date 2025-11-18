"""
DRF Serializers for Products App
"""

from rest_framework import serializers
from apps.products import models
from apps.products.models import Section, Brand, Category, Collection, Type, Product, TutorialCategory, TutorialVideo, Color, ProductImage


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


class ColorSerializer(serializers.ModelSerializer):
    """
    Serializer for Color model (справочник цветов)

    Возвращает данные цвета в формате:
    {
        "id": 1,
        "name": "Белый глянец",
        "slug": "belyj-glyanec",
        "hex_code": "#FFFFFF",
        "texture_image": null,
        "is_texture": false,
        "created_at": "2025-11-18T10:00:00Z"
    }
    """
    is_texture = serializers.BooleanField(read_only=True)

    class Meta:
        model = Color
        fields = [
            'id', 'name', 'slug', 'hex_code', 'texture_image',
            'is_texture', 'created_at'
        ]
        read_only_fields = ['id', 'slug', 'created_at', 'is_texture']


class ColorVariationSerializer(serializers.ModelSerializer):
    """
    Сериализатор для отображения цветовой вариации продукта.

    Используется в ProductDetailSerializer для показа связанных вариаций.
    Возвращает минимум информации, необходимый фронтенду для переключателя цветов:
    {
        "id": 2,
        "slug": "unitaz-model-x-belyj",
        "name": "Унитаз Model X белый",
        "main_image_url": "https://...",
        "color": {
            "id": 1,
            "name": "Белый глянец",
            "hex_code": "#FFFFFF",
            "texture_image": null
        }
    }
    """
    color = ColorSerializer(read_only=True)
    main_image_url = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'slug', 'name', 'main_image_url', 'color']
        read_only_fields = ['id', 'slug', 'name', 'main_image_url', 'color']

    def get_main_image_url(self, obj):
        """Получить главное изображение из галереи или fallback"""
        return obj.get_main_image()


class ProductImageSerializer(serializers.ModelSerializer):
    """
    Serializer for ProductImage model (галерея изображений продукта)

    Возвращает данные изображения в формате:
    {
        "id": 1,
        "image_url": "https://...",
        "image_type": "main",
        "image_type_display": "Главное изображение",
        "is_main": true,
        "is_hover": false,
        "sort_order": 0,
        "alt_text": "Унитаз Model X вид спереди"
    }
    """
    image_type_display = serializers.CharField(source='get_image_type_display', read_only=True)
    is_main = serializers.BooleanField(read_only=True)
    is_hover = serializers.BooleanField(read_only=True)

    class Meta:
        model = ProductImage
        fields = [
            'id', 'image_url', 'image_type', 'image_type_display',
            'is_main', 'is_hover', 'sort_order', 'alt_text'
        ]
        read_only_fields = ['id', 'image_type_display', 'is_main', 'is_hover']


class ProductImageCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating/updating ProductImage (admin only)
    """

    class Meta:
        model = ProductImage
        fields = [
            'id', 'product', 'image_url', 'image_type', 'sort_order', 'alt_text'
        ]
        read_only_fields = ['id']


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

    Возвращает только main и hover изображения из галереи для производительности.
    """
    section_name = serializers.CharField(source='section.name', read_only=True)
    brand_name = serializers.CharField(source='brand.name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    collection_name = serializers.CharField(source='collection.name', read_only=True, allow_null=True)
    type_name = serializers.CharField(source='type.name', read_only=True, allow_null=True)
    color = ColorSerializer(read_only=True)
    has_variations = serializers.SerializerMethodField()

    # Изображения из новой галереи
    main_image_url = serializers.SerializerMethodField()
    hover_image_url = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'price',
            'section', 'section_name',
            'brand', 'brand_name',
            'category', 'category_name',
            'collection', 'collection_name',
            'type', 'type_name',
            'main_image_url', 'hover_image_url',
            'color', 'color_group', 'has_variations',
            'colors',  # deprecated, kept for backward compatibility
            'is_new', 'is_on_sale',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at']

    def get_main_image_url(self, obj):
        """Получить главное изображение из галереи или fallback на старое поле"""
        return obj.get_main_image()

    def get_hover_image_url(self, obj):
        """Получить hover изображение из галереи или fallback на старое поле"""
        return obj.get_hover_image()

    def get_has_variations(self, obj):
        """Проверяет, есть ли у продукта цветовые вариации"""
        if not obj.color_group:
            return False
        return Product.objects.filter(color_group=obj.color_group).exclude(pk=obj.pk).exists()


class ProductDetailSerializer(serializers.ModelSerializer):
    """
    Full serializer for Product detail views
    Includes all product information, gallery and color variations
    НОВАЯ АРХИТЕКТУРА: Product имеет обязательный brand

    Возвращает полную галерею изображений с указанием типа (main/hover/gallery)
    """
    section_name = serializers.CharField(source='section.name', read_only=True)
    brand_name = serializers.CharField(source='brand.name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    collection_name = serializers.CharField(source='collection.name', read_only=True, allow_null=True)
    type_name = serializers.CharField(source='type.name', read_only=True, allow_null=True)
    color = ColorSerializer(read_only=True)
    color_variations = serializers.SerializerMethodField()

    # Изображения из новой галереи
    main_image_url = serializers.SerializerMethodField()
    hover_image_url = serializers.SerializerMethodField()
    gallery = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'price',
            'section', 'section_name',
            'brand', 'brand_name',
            'category', 'category_name',
            'collection', 'collection_name',
            'type', 'type_name',
            'main_image_url', 'hover_image_url', 'gallery',
            'images',  # deprecated, kept for backward compatibility
            'color', 'color_group', 'color_variations',
            'colors',  # deprecated, kept for backward compatibility
            'is_new', 'is_on_sale',
            'description',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at']

    def get_main_image_url(self, obj):
        """Получить главное изображение из галереи или fallback на старое поле"""
        return obj.get_main_image()

    def get_hover_image_url(self, obj):
        """Получить hover изображение из галереи или fallback на старое поле"""
        return obj.get_hover_image()

    def get_gallery(self, obj):
        """
        Возвращает полный отсортированный список всех изображений продукта.

        Returns:
            list: Список изображений с указанием типа (main/hover/gallery)
        """
        images = obj.get_gallery_images()
        return ProductImageSerializer(images, many=True).data

    def get_color_variations(self, obj):
        """
        Возвращает список всех цветовых вариаций продукта.

        Включает сам продукт в список, чтобы фронтенд мог отобразить
        все доступные цвета, включая текущий выбранный.

        Returns:
            list: Список вариаций с slug, name, main_image_url и color
        """
        if not obj.color_group:
            # Если нет группы вариаций, возвращаем только текущий продукт
            return [ColorVariationSerializer(obj).data]

        # Получаем все продукты в группе, включая текущий
        variations = Product.objects.filter(
            color_group=obj.color_group
        ).select_related('color').order_by('name')

        return ColorVariationSerializer(variations, many=True).data


class ProductCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating/updating products (admin only)
    НОВАЯ АРХИТЕКТУРА: brand обязателен!

    Поддерживает работу с:
    - color: ID цвета из справочника
    - color_group: UUID группы вариаций (для связи с другими цветовыми вариантами)
    """
    # Для удобства можно передать generate_color_group=true чтобы создать новую группу
    generate_color_group = serializers.BooleanField(write_only=True, required=False, default=False)

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'price',
            'section', 'brand', 'category', 'collection', 'type',
            'main_image_url', 'hover_image_url', 'images',
            'color', 'color_group', 'generate_color_group',
            'colors',  # deprecated, kept for backward compatibility
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

    def create(self, validated_data):
        """Создание продукта с поддержкой генерации color_group"""
        generate_group = validated_data.pop('generate_color_group', False)

        if generate_group and not validated_data.get('color_group'):
            validated_data['color_group'] = Product.generate_color_group_id()

        return super().create(validated_data)

    def update(self, instance, validated_data):
        """Обновление продукта с поддержкой генерации color_group"""
        generate_group = validated_data.pop('generate_color_group', False)

        if generate_group and not validated_data.get('color_group') and not instance.color_group:
            validated_data['color_group'] = Product.generate_color_group_id()

        return super().update(instance, validated_data)


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


class PlumbingProductSerializer(serializers.ModelSerializer):
    """
    Serializer for PlumbingSection products (CAIZER brand)

    Returns product data in format:
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
    }
    """
    brand = serializers.CharField(source='brand.name', read_only=True)
    category = serializers.CharField(source='category.name', read_only=True)
    section = serializers.CharField(source='section.name', read_only=True)
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id',
            'name',
            'brand',
            'brand_id',
            'category',
            'category_id',
            'section',
            'section_id',
            'image_url'
        ]

    def get_image_url(self, obj):
        """Return main image URL or None"""
        return obj.main_image_url if obj.main_image_url else None


class MaterialCategorySerializer(serializers.ModelSerializer):
    """
    Serializer for MaterialCategory model

    Returns category data in format:
    {
        "id": 1,
        "name": "Каталоги",
        "slug": "katalogi",
        "description": "Каталоги продукции",
        "order": 0,
        "material_count": 5
    }
    """
    material_count = serializers.SerializerMethodField()

    class Meta:
        model = models.MaterialCategory
        fields = [
            'id',
            'name',
            'slug',
            'description',
            'order',
            'material_count'
        ]

    def get_material_count(self, obj):
        """Return count of active materials in this category"""
        return obj.materials.filter(is_active=True).count()


class MaterialSerializer(serializers.ModelSerializer):
    """
    Serializer for Material model

    Returns material data in format:
    {
        "id": 1,
        "title": "Каталог продукции 2024",
        "description": "Полный каталог всех товаров",
        "file_url": "https://example.com/catalog.pdf",
        "category": "Каталоги",
        "category_id": 1,
        "order": 0,
        "created_at": "2024-01-15T10:30:00Z",
        "updated_at": "2024-01-15T10:30:00Z"
    }
    """
    category = serializers.CharField(source='category.name', read_only=True)
    category_id = serializers.IntegerField(source='category.id', read_only=True)

    class Meta:
        model = models.Material
        fields = [
            'id',
            'title',
            'description',
            'file_url',
            'category',
            'category_id',
            'order',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
