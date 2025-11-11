"""
Product-related Models for LAMIS E-commerce
Implements Brand → Category → Collection → Product hierarchy
"""

from django.db import models
from slugify import slugify  # python-slugify для транслитерации русских символов
from django.core.validators import MinValueValidator
from decimal import Decimal


class Brand(models.Model):
    """
    Brand Model (Lamis, Caizer, Blesk)

    Fields:
        id: Primary Key
        name: Brand name (unique)
        slug: URL-friendly slug (auto-generated from name)
        description: Optional brand description
        created_at: Timestamp when brand was created
    """

    name = models.CharField(max_length=100, unique=True, db_index=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    description = models.TextField(blank=True, null=True)
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

    Fields:
        id: Primary Key
        name: Category name (unique)
        slug: URL-friendly slug (auto-generated from name)
        brands: Many-to-Many relationship with Brand
        description: Optional category description
        created_at: Timestamp when category was created
    """

    name = models.CharField(max_length=150, unique=True, db_index=True)
    slug = models.SlugField(max_length=180, unique=True, blank=True)
    brands = models.ManyToManyField(Brand, through='BrandCategory', related_name='categories')
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'categories'
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class BrandCategory(models.Model):
    """
    Many-to-Many through table for Brand and Category
    Allows a category to belong to multiple brands
    """

    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    class Meta:
        db_table = 'brand_categories'
        unique_together = ('brand', 'category')
        verbose_name = 'Brand Category'
        verbose_name_plural = 'Brand Categories'

    def __str__(self):
        return f"{self.brand.name} - {self.category.name}"


class Collection(models.Model):
    """
    Collection Model (Solo, Harmony, Lux, Premium, Eco, etc.)
    Collections belong to a specific Brand and Category

    Fields:
        id: Primary Key
        name: Collection name
        slug: URL-friendly slug (auto-generated from name)
        brand: Foreign Key to Brand
        category: Foreign Key to Category
        description: Optional collection description
        created_at: Timestamp when collection was created
    """

    name = models.CharField(max_length=150, db_index=True)
    slug = models.SlugField(max_length=180, blank=True)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name='collections')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='collections')
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'collections'
        verbose_name = 'Collection'
        verbose_name_plural = 'Collections'
        ordering = ['brand', 'category', 'name']
        unique_together = ('brand', 'category', 'name')

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.brand.name}-{self.category.name}-{self.name}")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.brand.name} - {self.category.name} - {self.name}"


class Product(models.Model):
    """
    Product Model

    Fields:
        id: Primary Key
        name: Product name
        slug: URL-friendly slug (unique, auto-generated from name)
        price: Product price (Decimal for precise currency handling)
        brand: Foreign Key to Brand
        category: Foreign Key to Category
        collection: Foreign Key to Collection (optional)
        main_image_url: Main product image URL
        images: JSON array of additional image URLs
        colors: JSON array of color options [{name, hex}, ...]
        is_new: Flag for "Новинка" badge
        is_on_sale: Flag for "Акция" badge
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
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name='products')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    collection = models.ForeignKey(
        Collection,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='products'
    )
    main_image_url = models.URLField(max_length=500)
    images = models.JSONField(default=list, blank=True)
    colors = models.JSONField(default=list, blank=True)
    is_new = models.BooleanField(default=False, db_index=True)
    is_on_sale = models.BooleanField(default=False, db_index=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'products'
        verbose_name = 'Product'
        verbose_name_plural = 'Products'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['brand', 'category']),
            models.Index(fields=['brand', 'category', 'collection']),
            models.Index(fields=['is_new', 'is_on_sale']),
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
        return self.name
