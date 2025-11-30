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
    name = models.CharField(max_length=100, unique=True, db_index=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    title = models.CharField(max_length=255, blank=True, null=True, help_text="SEO заголовок для описания раздела")
    description = models.TextField(blank=True, null=True, help_text="Описание раздела (2-3 параграфа)")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'sections'
        verbose_name = 'Раздел'
        verbose_name_plural = 'Разделы'
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Brand(models.Model):
    name = models.CharField(max_length=100, unique=True, db_index=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    description = models.TextField(blank=True, null=True)
    image = models.URLField(max_length=500, blank=True, null=True, help_text="URL логотипа бренда")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'brands'
        verbose_name = 'Бренд'
        verbose_name_plural = 'Бренды'
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=150, db_index=True)
    slug = models.SlugField(max_length=180, blank=True)
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
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['section', 'brand', 'name']
        unique_together = ('section', 'brand', 'slug')

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.section.name}, {self.brand.name})"


class Collection(models.Model):
    name = models.CharField(max_length=150, db_index=True)
    slug = models.SlugField(max_length=180, blank=True)
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
        verbose_name = 'Коллекция'
        verbose_name_plural = 'Коллекции'
        ordering = ['brand', 'category', 'name']
        unique_together = ('brand', 'category', 'slug')

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.brand.name}-{self.category.name}-{self.name}")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.category.name}, {self.brand.name})"


class Type(models.Model):
    name = models.CharField(max_length=150, db_index=True)
    slug = models.SlugField(max_length=180, blank=True)
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
        verbose_name = 'Тип'
        verbose_name_plural = 'Типы'
        ordering = ['category', 'name']
        unique_together = ('category', 'slug')

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.category.name}-{self.name}")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.category.name})"


class Color(models.Model):
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
        verbose_name = 'Цвет'
        verbose_name_plural = 'Цвета'
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
        return bool(self.texture_image)


class Product(models.Model):
    name = models.CharField(max_length=255, db_index=True, verbose_name="Название")
    slug = models.SlugField(max_length=300, unique=True, blank=True, verbose_name="URL")
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name="Цена"
    )
    section = models.ForeignKey(
        Section,
        on_delete=models.CASCADE,
        related_name='products',
        verbose_name="Раздел",
        help_text="Раздел каталога"
    )
    brand = models.ForeignKey(
        Brand,
        on_delete=models.CASCADE,
        related_name='products',
        verbose_name="Бренд",
        help_text="Производитель (обязательно)"
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='products',
        verbose_name="Категория",
        help_text="Категория товаров"
    )
    collection = models.ForeignKey(
        Collection,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='products',
        verbose_name="Коллекция",
        help_text="Коллекция (опционально)"
    )
    type = models.ForeignKey(
        Type,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='products',
        verbose_name="Тип",
        help_text="Тип/Вид (опционально)"
    )
    main_image_url = models.URLField(max_length=500)
    hover_image_url = models.URLField(max_length=500, blank=True, null=True)
    images = models.JSONField(default=list, blank=True)
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
    colors = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Цвета (устаревшее)",
        help_text="DEPRECATED: Используйте поле 'color' и 'color_group' вместо этого"
    )
    is_new = models.BooleanField(default=False, db_index=True, verbose_name="Новинка")
    is_on_sale = models.BooleanField(default=False, db_index=True, verbose_name="Акция")
    is_featured = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Показать на главной",
        help_text="Отметьте, чтобы товар отображался в блоке 'Сантехника CAIZER' на главной странице"
    )
    description = RichTextField(
        blank=True,
        null=True,
        verbose_name="Описание товара",
        help_text="Полное описание товара с возможностью форматирования (жирный, курсив, списки и т.д.)"
    )
    characteristics = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Характеристики",
        help_text="Структурированные характеристики товара в формате [{\"key\": \"Ширина\", \"value\": \"60 см\"}, ...]"
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        db_table = 'products'
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'
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
        if not self.color_group:
            return Product.objects.none()
        return Product.objects.filter(
            color_group=self.color_group
        ).exclude(
            pk=self.pk
        ).select_related('color')

    def get_all_variations_including_self(self):
        if not self.color_group:
            return Product.objects.filter(pk=self.pk)
        return Product.objects.filter(
            color_group=self.color_group
        ).select_related('color')

    @classmethod
    def generate_color_group_id(cls):
        return uuid.uuid4()

    def get_main_image(self):
        image = self.gallery_images.filter(image_type='main').first()
        if image:
            return image.image_url
        return self.main_image_url

    def get_hover_image(self):
        image = self.gallery_images.filter(image_type='hover').first()
        if image:
            return image.image_url
        return self.hover_image_url

    def get_gallery_images(self):
        return self.gallery_images.all().order_by('sort_order', 'id')


class ProductImage(models.Model):
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
        verbose_name = 'Изображение товара'
        verbose_name_plural = 'Изображения товаров'
        ordering = ['sort_order', 'id']
        indexes = [
            models.Index(fields=['product', 'image_type']),
            models.Index(fields=['product', 'sort_order']),
        ]

    def __str__(self):
        return f"{self.product.name} - {self.get_image_type_display()}"

    def save(self, *args, **kwargs):
        if self.image_type in ['main', 'hover']:
            existing = ProductImage.objects.filter(
                product=self.product,
                image_type=self.image_type
            ).exclude(pk=self.pk)
            existing.update(image_type='gallery')
        super().save(*args, **kwargs)

    @property
    def is_main(self):
        return self.image_type == 'main'

    @property
    def is_hover(self):
        return self.image_type == 'hover'


class TutorialCategory(models.Model):
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
        verbose_name = 'Категория видеоуроков'
        verbose_name_plural = 'Категории видеоуроков'
        ordering = ['order', 'title']

    def __str__(self):
        return self.title


class TutorialVideo(models.Model):
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
        verbose_name = 'Видеоурок'
        verbose_name_plural = 'Видеоуроки'
        ordering = ['order', 'id']

    def __str__(self):
        return f"{self.title} ({self.category.title})"


class MaterialCategory(models.Model):
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
        verbose_name = 'Категория материалов'
        verbose_name_plural = 'Категории материалов'
        ordering = ['order', 'name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Material(models.Model):
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
        blank=True,
        default=''
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
        verbose_name = 'Материал'
        verbose_name_plural = 'Материалы'
        ordering = ['order', '-created_at']
        indexes = [
            models.Index(fields=['is_active', 'order']),
        ]

    def __str__(self):
        return self.title