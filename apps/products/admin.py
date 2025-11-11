"""
Django Admin Configuration for Products App
"""

from django.contrib import admin
from apps.products.models import Brand, Category, BrandCategory, Collection, Product


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'slug', 'created_at']
    search_fields = ['name', 'description']
    list_filter = ['created_at']
    readonly_fields = ['slug', 'created_at']
    ordering = ['name']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'slug', 'created_at']
    search_fields = ['name', 'description']
    list_filter = ['created_at']
    readonly_fields = ['slug', 'created_at']
    ordering = ['name']


@admin.register(BrandCategory)
class BrandCategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'brand', 'category']
    list_filter = ['brand', 'category']
    search_fields = ['brand__name', 'category__name']


@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'brand', 'category', 'created_at']
    list_filter = ['brand', 'category', 'created_at']
    search_fields = ['name', 'description', 'brand__name', 'category__name']
    readonly_fields = ['slug', 'created_at']
    ordering = ['brand', 'category', 'name']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'price', 'brand', 'category', 'collection', 'is_new', 'is_on_sale', 'created_at']
    list_filter = ['brand', 'category', 'collection', 'is_new', 'is_on_sale', 'created_at']
    search_fields = ['name', 'description', 'slug']
    readonly_fields = ['slug', 'created_at', 'updated_at']
    list_editable = ['price', 'is_new', 'is_on_sale']
    ordering = ['-created_at']
    list_per_page = 50
