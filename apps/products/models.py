"""
Product-related Models for LAMIS E-commerce
Implements Section → Category → Collection → Product hierarchy
"""

import uuid
from django.db import models
from slugify import slugify  # python-slugify для транслитерации русских символов
from django.core.validators import MinValueValidator
from decimal import Decimal
from ckeditor.fields import RichTextField  # WYSIWYG редактор для админки


class Section(models.Model):
    """
    Section Model (Мебель для ванной, Санфарфор, Смесители, etc.)

    Fields:
        id: Primary Key
        name: Section name (unique)
        slug: URL-friendly slug (auto-generated from name)
        title: SEO title for section description
        description: Optional section description
        created_at: Timestamp when section was created
    """

    name = models.CharField(max_length=100, unique=True, db_index=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    title = models.CharField(max_length=255, blank=True, null=True, help_text="SEO заголовок для описания раздела")
    description = models.TextField(blank=True, null=True, help_text="Описание раздела (2-3 параграфа)")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'sections'
        verbose_name = 'Section'
        verbose_name_plural = 'Sections'
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Brand(models.Model):
    """
    Brand Model (Производитель - Lamis, Caizer, Blesk, etc.)

    КЛЮЧЕВОЙ УРОВЕНЬ после Section:
    Section → Brand → Category → Collection/Type → Product

    Fields:
        id: Primary Key
        name: Brand name (unique)
        slug: URL-friendly slug (auto-generated from name)
        description: Optional brand description
        image: Optional brand logo/image URL
        created_at: Timestamp when brand was created
    """

    name = models.CharField(max_length=100, unique=True, db_index=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    description = models.TextField(blank=True, null=True)
    image = models.URLField(max_length=500, blank=True, null=True, help_text="URL логотипа бренда")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'brands'
        verbose_name = 'Brand'
        verbose_name_plural = 'Brands'
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Category(models.Model):
    """
    Category Model (Мебель, Зеркала, Сантехника, Водонагреватели)

    НОВАЯ АРХИТЕКТУРА: Category зависит от Section + Brand
    Section → Brand → Category

    Fields:
        id: Primary Key
        name: Category name
        slug: URL-friendly slug (auto-generated from name)
        section: Foreign Key to Section (обязательно)
        brand: Foreign Key to Brand (обязательно)
        description: Optional category description
        created_at: Timestamp when category was created
    """

    name = models.CharField(max_length=150, db_index=True)
    slug = models.SlugField(max_length=180, blank=True)

    # НОВЫЕ связи: Section + Brand
    section = models.ForeignKey(
        Section,
        on_delete=models.CASCADE,
        related_name='categories',
        help_text="Раздел каталога (Мебель для ванной, Санфарфор, etc.)"
    )
    brand = models.ForeignKey(
        Brand,
        on_delete=models.CASCADE,
        related_name='categories',
        help_text="Производитель (Lamis, Caizer, Blesk, etc.)"
    )

    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'categories'
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ['section', 'brand', 'name']
        unique_together = ('section', 'brand', 'slug')

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        # Показываем контекст в админке!
        return f"{self.name} ({self.section.name}, {self.brand.name})"


class Collection(models.Model):
    """
    Collection Model (Solo, Harmony, Lux, Premium, Eco, etc.)

    НОВАЯ АРХИТЕКТУРА: Collection зависит от Brand + Category
    Section → Brand → Category → Collection

    Fields:
        id: Primary Key
        name: Collection name
        slug: URL-friendly slug (auto-generated from name)
        brand: Foreign Key to Brand (обязательно)
        category: Foreign Key to Category (обязательно)
        image: URL of collection image (from R2 storage)
        description: Optional collection description
        created_at: Timestamp when collection was created
    """

    name = models.CharField(max_length=150, db_index=True)
    slug = models.SlugField(max_length=180, blank=True)

    # НОВЫЕ связи: Brand + Category (section знаем через Category)
    brand = models.ForeignKey(
        Brand,
        on_delete=models.CASCADE,
        related_name='collections',
        help_text="Производитель"
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='collections',
        help_text="Категория товаров"
    )

    image = models.URLField(
        max_length=500,
        null=True,
        blank=True,
        help_text="URL изображения коллекции (картинка с R2)"
    )
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'collections'
        verbose_name = 'Collection'
        verbose_name_plural = 'Collections'
        ordering = ['brand', 'category', 'name']
        unique_together = ('brand', 'category', 'slug')

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.brand.name}-{self.category.name}-{self.name}")
        super().save(*args, **kwargs)

    def __str__(self):
        # Показываем контекст!
        return f"{self.name} ({self.category.name}, {self.brand.name})"


class Type(models.Model):
    """
    Type Model (Вид) - Product type classification

    НОВАЯ АРХИТЕКТУРА: Type зависит ТОЛЬКО от Category
    Section → Brand → Category → Type
    (section и brand знаем через Category)

    Examples: Раковины, Унитазы, Писсуары, Биде

    Fields:
        id: Primary Key
        name: Type name (Вид)
        slug: URL-friendly slug (auto-generated from name)
        category: Foreign Key to Category (обязательно)
        description: Optional type description
        created_at: Timestamp when type was created
    """

    name = models.CharField(max_length=150, db_index=True)
    slug = models.SlugField(max_length=180, blank=True)

    # ТОЛЬКО Category (section и brand знаем через category)
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='types',
        help_text="Категория товаров"
    )

    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'types'
        verbose_name = 'Type'
        verbose_name_plural = 'Types'
        ordering = ['category', 'name']
        unique_together = ('category', 'slug')

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.category.name}-{self.name}")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.category.name})"


class Color(models.Model):
    """
    Color Model - Централизованный справочник цветов

    Используется для:
    - Унификации цветов во всех продуктах
    - Возможности выбора цвета из справочника при создании продукта
    - Поддержки как простых цветов (HEX), так и текстур (изображения)

    Fields:
        name: Название цвета (уникальное)
        slug: URL-friendly slug (auto-generated)
        hex_code: HEX код цвета (для простых цветов)
        texture_image: URL изображения текстуры (для текстурных цветов)
        created_at: Timestamp
    """

    name = models.CharField(
        max_length=100,
        unique=True,
        db_index=True,
        verbose_name="Название цвета",
        help_text="Например: Белый глянец, Дуб венге, Хром"
    )
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    hex_code = models.CharField(
        max_length=7,
        blank=True,
        null=True,
        verbose_name="HEX код",
        help_text="Код цвета в формате #FFFFFF (для простых цветов)"
    )
    texture_image = models.URLField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name="URL текстуры",
        help_text="URL изображения текстуры (для материалов типа дерево, камень и т.д.)"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'colors'
        verbose_name = 'Color'
        verbose_name_plural = 'Colors'
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        if self.hex_code:
            return f"{self.name} ({self.hex_code})"
        return self.name

    @property
    def is_texture(self):
        """Проверяет, является ли цвет текстурой"""
        return bool(self.texture_image)


class Product(models.Model):
    """
    Product Model

    НОВАЯ АРХИТЕКТУРА: Product ОБЯЗАТЕЛЬНО имеет brand
    Section → Brand → Category → Collection/Type → Product

    Fields:
        id: Primary Key
        name: Product name
        slug: URL-friendly slug (unique, auto-generated from name)
        price: Product price (Decimal for precise currency handling)
        section: Foreign Key to Section (обязательно)
        brand: Foreign Key to Brand (обязательно) ← НОВОЕ!
        category: Foreign Key to Category (обязательно)
        collection: Foreign Key to Collection (optional)
        type: Foreign Key to Type (optional)
        main_image_url: Main product image URL (shown by default)
        hover_image_url: Hover/render image URL (shown on hover)
        images: JSON array of additional image URLs
        colors: JSON array of color options [{name, hex}, ...]
        is_new: Flag for "Новинка" badge
        is_on_sale: Flag for "Акция" badge
        is_featured: Flag for showing product on homepage (CAIZER section)
        description: Product description
        created_at: Timestamp when product was created
        updated_at: Timestamp when product was last updated
    """

    name = models.CharField(max_length=255, db_index=True)
    slug = models.SlugField(max_length=300, unique=True, blank=True)
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )

    # Основные связи
    section = models.ForeignKey(
        Section,
        on_delete=models.CASCADE,
        related_name='products',
        help_text="Раздел каталога"
    )
    brand = models.ForeignKey(
        Brand,
        on_delete=models.CASCADE,
        related_name='products',
        help_text="Производитель (обязательно)"
    )  # ← НОВОЕ! ОБЯЗАТЕЛЬНЫЙ БРЕНД!
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='products',
        help_text="Категория товаров"
    )

    # Опциональные связи
    collection = models.ForeignKey(
        Collection,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='products',
        help_text="Коллекция (опционально)"
    )
    type = models.ForeignKey(
        Type,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='products',
        help_text="Тип/Вид (опционально)"
    )

    main_image_url = models.URLField(max_length=500)
    hover_image_url = models.URLField(max_length=500, blank=True, null=True)
    images = models.JSONField(default=list, blank=True)

    # Новая система цветов
    color = models.ForeignKey(
        Color,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='products',
        verbose_name="Цвет",
        help_text="Цвет продукта из справочника"
    )
    color_group = models.UUIDField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Группа цветовых вариаций",
        help_text="UUID для связывания продуктов-вариаций одной модели. Продукты с одинаковым color_group являются цветовыми вариациями друг друга."
    )

    # Старое поле colors оставляем для обратной совместимости (deprecated)
    colors = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Цвета (устаревшее)",
        help_text="DEPRECATED: Используйте поле 'color' и 'color_group' вместо этого"
    )

    is_new = models.BooleanField(default=False, db_index=True)
    is_on_sale = models.BooleanField(default=False, db_index=True)
    is_featured = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Показать на главной",
        help_text="Отметьте, чтобы товар отображался в блоке 'Сантехника CAIZER' на главной странице"
    )

    # Описание с поддержкой HTML форматирования (WYSIWYG редактор)
    description = RichTextField(
        blank=True,
        null=True,
        verbose_name="Описание товара",
        help_text="Полное описание товара с возможностью форматирования (жирный, курсив, списки и т.д.)"
    )

    # Структурированные характеристики товара
    characteristics = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Характеристики",
        help_text="Структурированные характеристики товара в формате [{\"key\": \"Ширина\", \"value\": \"60 см\"}, ...]"
    )

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'products'
        verbose_name = 'Product'
        verbose_name_plural = 'Products'
        ordering = ['-created_at']
        unique_together = ('section', 'brand', 'slug')
        indexes = [
            models.Index(fields=['section', 'brand']),
            models.Index(fields=['section', 'brand', 'category']),
            models.Index(fields=['section', 'brand', 'category', 'collection']),
            models.Index(fields=['section', 'brand', 'category', 'type']),
            models.Index(fields=['is_new', 'is_on_sale', 'is_featured']),
            models.Index(fields=['color_group']),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while Product.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.brand.name})"

    def get_color_variations(self):
        """
        Получить все цветовые вариации этого продукта.

        Returns:
            QuerySet продуктов с тем же color_group (исключая текущий продукт).
            Пустой QuerySet если color_group не установлен.
        """
        if not self.color_group:
            return Product.objects.none()

        return Product.objects.filter(
            color_group=self.color_group
        ).exclude(
            pk=self.pk
        ).select_related('color')

    def get_all_variations_including_self(self):
        """
        Получить все продукты в группе вариаций, включая текущий.

        Returns:
            QuerySet всех продуктов с тем же color_group.
        """
        if not self.color_group:
            return Product.objects.filter(pk=self.pk)

        return Product.objects.filter(
            color_group=self.color_group
        ).select_related('color')

    @classmethod
    def generate_color_group_id(cls):
        """
        Генерирует новый UUID для группы цветовых вариаций.

        Использование:
            product.color_group = Product.generate_color_group_id()
        """
        return uuid.uuid4()

    def get_main_image(self):
        """Получить главное изображение из галереи"""
        image = self.gallery_images.filter(image_type='main').first()
        if image:
            return image.image_url
        # Fallback на старое поле для обратной совместимости
        return self.main_image_url

    def get_hover_image(self):
        """Получить hover изображение из галереи"""
        image = self.gallery_images.filter(image_type='hover').first()
        if image:
            return image.image_url
        # Fallback на старое поле для обратной совместимости
        return self.hover_image_url

    def get_gallery_images(self):
        """Получить все изображения галереи отсортированные по порядку"""
        return self.gallery_images.all().order_by('sort_order', 'id')


class ProductImage(models.Model):
    """
    ProductImage Model - Изображения продукта (галерея)

    Централизованное управление всеми изображениями продукта.
    Заменяет старые поля main_image_url, hover_image_url и images.

    Fields:
        product: ForeignKey к Product
        image_url: URL изображения
        image_type: Тип изображения (main, hover, gallery)
        sort_order: Порядок сортировки в галерее
        alt_text: Alt текст для SEO
        created_at: Timestamp

    Примечание:
        - У продукта может быть только одно main и одно hover изображение
        - gallery изображений может быть сколько угодно
        - Архитектура готова к будущей загрузке файлов (можно добавить FileField)
    """

    class ImageType(models.TextChoices):
        MAIN = 'main', 'Главное изображение'
        HOVER = 'hover', 'Изображение при наведении'
        GALLERY = 'gallery', 'Галерея'

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='gallery_images',
        verbose_name="Продукт"
    )
    image_url = models.URLField(
        max_length=500,
        verbose_name="URL изображения",
        help_text="Ссылка на изображение"
    )
    # Поле для будущей поддержки загрузки файлов
    # image_file = models.ImageField(upload_to='products/', blank=True, null=True)

    image_type = models.CharField(
        max_length=10,
        choices=ImageType.choices,
        default=ImageType.GALLERY,
        verbose_name="Тип изображения",
        help_text="main - главное, hover - при наведении, gallery - дополнительные"
    )
    sort_order = models.PositiveIntegerField(
        default=0,
        verbose_name="Порядок сортировки",
        help_text="Меньшее число = выше в списке"
    )
    alt_text = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Alt текст",
        help_text="Альтернативный текст для SEO и доступности"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'product_images'
        verbose_name = 'Product Image'
        verbose_name_plural = 'Product Images'
        ordering = ['sort_order', 'id']
        indexes = [
            models.Index(fields=['product', 'image_type']),
            models.Index(fields=['product', 'sort_order']),
        ]

    def __str__(self):
        return f"{self.product.name} - {self.get_image_type_display()}"

    def save(self, *args, **kwargs):
        """
        Обеспечивает уникальность main и hover изображений для продукта.
        Если добавляется новое main/hover, старое становится gallery.
        """
        if self.image_type in ['main', 'hover']:
            # Найти существующее изображение этого типа
            existing = ProductImage.objects.filter(
                product=self.product,
                image_type=self.image_type
            ).exclude(pk=self.pk)

            # Перевести старое в gallery
            existing.update(image_type='gallery')

        super().save(*args, **kwargs)

    @property
    def is_main(self):
        return self.image_type == 'main'

    @property
    def is_hover(self):
        return self.image_type == 'hover'


class TutorialCategory(models.Model):
    """
    Tutorial Category Model (Категория видео уроков)

    Examples: "Установка мебели", "Установка раковины", etc.
    Each category has a hero banner and multiple tutorial videos.

    Fields:
        title: Category name (e.g. "Установка мебели")
        slug: URL-friendly slug (e.g. "furniture-installation")
        banner_image_url: Hero section background image URL
        order: Display order (lower number = higher priority)
        is_active: Whether category is visible on frontend
    """

    title = models.CharField(
        max_length=200,
        verbose_name="Название категории",
        help_text="Например: Установка мебели"
    )
    slug = models.SlugField(
        max_length=250,
        unique=True,
        verbose_name="URL slug",
        help_text="Например: furniture-installation"
    )
    banner_image_url = models.URLField(
        verbose_name="URL фото для hero section",
        help_text="Фоновое изображение для hero section"
    )
    order = models.IntegerField(
        default=0,
        verbose_name="Порядок сортировки",
        help_text="Меньшее число = выше в списке"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Активна",
        help_text="Показывать на фронтенде"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'tutorial_categories'
        verbose_name = 'Tutorial Category'
        verbose_name_plural = 'Tutorial Categories'
        ordering = ['order', 'title']

    def __str__(self):
        return self.title


class TutorialVideo(models.Model):
    """
    Tutorial Video Model (Видео урок в категории)

    Each video belongs to a TutorialCategory and contains a YouTube video.

    Fields:
        category: Parent category (ForeignKey)
        title: Video title (e.g. "Сборка шкафа-купе")
        youtube_video_id: YouTube video ID (e.g. "dQw4w9WgXcQ")
        order: Display order within category
    """

    category = models.ForeignKey(
        TutorialCategory,
        on_delete=models.CASCADE,
        related_name='videos',
        verbose_name="Категория"
    )
    title = models.CharField(
        max_length=200,
        verbose_name="Название видео",
        help_text="Например: Сборка шкафа-купе"
    )
    youtube_video_id = models.CharField(
        max_length=20,
        verbose_name="YouTube Video ID",
        help_text="ID видео на YouTube (например: dQw4w9WgXcQ)"
    )
    order = models.IntegerField(
        default=0,
        verbose_name="Порядок сортировки",
        help_text="Меньшее число = выше в списке"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'tutorial_videos'
        verbose_name = 'Tutorial Video'
        verbose_name_plural = 'Tutorial Videos'
        ordering = ['order', 'id']

    def __str__(self):
        return f"{self.title} ({self.category.title})"


# ========================
# Materials for Download
# ========================

class MaterialCategory(models.Model):
    """
    Material Category Model (Категория материалов для скачивания)

    Examples: Каталоги, Сертификаты, Логотипы, Инструкции

    Fields:
        name: Category name (unique)
        slug: URL-friendly slug
        description: Optional category description
        order: Display order
        created_at: Timestamp
    """

    name = models.CharField(
        max_length=100,
        unique=True,
        db_index=True,
        verbose_name="Название категории",
        help_text="Например: Каталоги, Сертификаты, Логотипы"
    )
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name="Описание",
        help_text="Описание категории материалов"
    )
    order = models.IntegerField(
        default=0,
        verbose_name="Порядок сортировки",
        help_text="Меньшее число = выше в списке"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'material_categories'
        verbose_name = 'Material Category'
        verbose_name_plural = 'Material Categories'
        ordering = ['order', 'name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Material(models.Model):
    """
    Material Model (Материал для скачивания - PDF, картинки, архивы, etc.)

    Materials that can be downloaded from the website.

    Fields:
        title: Material title (required, max 255 chars)
        description: Optional long text description
        file_url: URL to the file (required)
        image_url: URL to the image for material display (required)
        category: Foreign Key to MaterialCategory (required)
        order: Manual sort order (number)
        is_active: Checkbox for enabling/disabling (default True)
        created_at: Auto timestamp
        updated_at: Auto timestamp
    """

    title = models.CharField(
        max_length=255,
        verbose_name="Название материала",
        help_text="Например: Каталог продукции 2024"
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name="Описание",
        help_text="Подробное описание материала"
    )
    file_url = models.URLField(
        max_length=500,
        verbose_name="Ссылка на файл",
        help_text="URL для скачивания файла (может быть внешняя ссылка или путь на сервере)"
    )
    image_url = models.URLField(
        max_length=500,
        verbose_name="Ссылка на картинку",
        help_text="URL картинки для отображения материала",
        default='https://via.placeholder.com/400x300?text=Material+Image'
    )
    order = models.IntegerField(
        default=0,
        verbose_name="Порядок сортировки",
        help_text="Меньшее число = выше в списке. Используется для ручной сортировки."
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Активен",
        help_text="Отключите, если материал устарел и не должен показываться на сайте"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'materials'
        verbose_name = 'Material'
        verbose_name_plural = 'Materials'
        ordering = ['order', '-created_at']
        indexes = [
            models.Index(fields=['is_active', 'order']),
        ]

    def __str__(self):
        return self.title
