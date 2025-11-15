"""
Django Admin Configuration for Products App
"""

from django.contrib import admin
from django.db.models import Count
from django.utils.html import format_html
from apps.products.models import Section, Brand, Category, Collection, Type, Product, TutorialCategory, TutorialVideo


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'slug', 'created_at']
    search_fields = ['name', 'description', 'title']
    list_filter = ['created_at']
    readonly_fields = ['slug', 'created_at']
    ordering = ['name']

    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'slug')
        }),
        ('SEO и описание', {
            'fields': ('title', 'description'),
            'classes': ('collapse',),
            'description': 'Заголовок и описание раздела для отображения на странице каталога'
        }),
        ('Даты', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'slug', 'created_at']
    search_fields = ['name', 'description']
    list_filter = ['created_at']
    readonly_fields = ['slug', 'created_at']
    ordering = ['name']
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'slug', 'description')
        }),
        ('Медиа', {
            'fields': ('image',),
            'classes': ('collapse',)
        }),
        ('Даты', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'section', 'brand', 'slug', 'created_at']
    search_fields = ['name', 'description', 'section__name', 'brand__name']
    list_filter = ['section', 'brand', 'created_at']
    readonly_fields = ['slug', 'created_at']
    ordering = ['section', 'brand', 'name']
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'slug', 'description')
        }),
        ('Классификация', {
            'fields': ('section', 'brand'),
            'description': 'Категория привязана к Section и Brand'
        }),
        ('Даты', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


class ProductInline(admin.TabularInline):
    """Inline редактирование продуктов для Collection и Type"""
    model = Product
    extra = 0
    fields = ['name', 'price', 'is_new', 'is_on_sale', 'slug']
    readonly_fields = ['slug']
    show_change_link = True
    can_delete = False


@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'brand', 'category', 'product_count', 'created_at']
    list_filter = ['brand', 'category', 'created_at']
    search_fields = ['name', 'description', 'brand__name', 'category__name']
    readonly_fields = ['slug', 'created_at', 'product_count']
    ordering = ['brand', 'category', 'name']
    inlines = [ProductInline]

    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'slug', 'description')
        }),
        ('Классификация', {
            'fields': ('brand', 'category'),
            'description': 'Collection привязана к Brand и Category'
        }),
        ('Медиа', {
            'fields': ('image',),
            'classes': ('collapse',)
        }),
        ('Статистика', {
            'fields': ('product_count', 'created_at'),
            'classes': ('collapse',)
        }),
    )

    def product_count(self, obj):
        """Показать количество продуктов в коллекции"""
        count = obj.products.count()
        return format_html(
            '<a href="/admin/products/product/?collection__id__exact={}">{} товаров</a>',
            obj.id, count
        )
    product_count.short_description = 'Товары'

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(
            _product_count=Count('products', distinct=True)
        )
        return queryset

    actions = ['duplicate_collection']

    def duplicate_collection(self, request, queryset):
        """Bulk action: дублировать коллекции"""
        for collection in queryset:
            collection.pk = None
            collection.name = f"{collection.name} (копия)"
            collection.slug = ""
            collection.save()
        self.message_user(request, f"Успешно создано {queryset.count()} копий коллекций")
    duplicate_collection.short_description = "Дублировать выбранные коллекции"


@admin.register(Type)
class TypeAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'category', 'product_count', 'slug_display', 'created_at']
    list_filter = ['category', 'created_at']
    search_fields = ['name', 'description', 'category__name', 'slug']
    readonly_fields = ['slug', 'created_at', 'product_count']
    ordering = ['category', 'name']
    list_per_page = 50
    inlines = [ProductInline]

    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'slug', 'description'),
            'description': 'Базовая информация о типе продукта'
        }),
        ('Классификация', {
            'fields': ('category',),
            'description': 'Type привязан ТОЛЬКО к Category (section и brand знаем через category)'
        }),
        ('Статистика', {
            'fields': ('product_count', 'created_at'),
            'classes': ('collapse',),
            'description': 'Статистика и даты'
        }),
    )

    def product_count(self, obj):
        """Показать количество продуктов этого типа с ссылкой"""
        count = obj.products.count()
        if count > 0:
            return format_html(
                '<a href="/admin/products/product/?type__id__exact={}" style="color: #417690; font-weight: bold;">{} товаров</a>',
                obj.id, count
            )
        return format_html('<span style="color: #999;">0 товаров</span>')
    product_count.short_description = 'Товары'

    def slug_display(self, obj):
        """Красиво отображать slug"""
        return format_html(
            '<code style="background: #f0f0f0; padding: 2px 6px; border-radius: 3px;">{}</code>',
            obj.slug
        )
    slug_display.short_description = 'URL Slug'

    def get_queryset(self, request):
        """Оптимизированный queryset с аннотациями"""
        queryset = super().get_queryset(request)
        queryset = queryset.select_related('category')
        queryset = queryset.annotate(
            _product_count=Count('products', distinct=True)
        )
        return queryset

    # Custom bulk actions
    actions = ['duplicate_type', 'export_as_csv']

    def duplicate_type(self, request, queryset):
        """Bulk action: дублировать типы"""
        duplicated_count = 0
        for type_obj in queryset:
            type_obj.pk = None
            type_obj.name = f"{type_obj.name} (копия)"
            type_obj.slug = ""  # Will be auto-generated
            type_obj.save()
            duplicated_count += 1

        self.message_user(request, f"Успешно создано {duplicated_count} копий типов")
    duplicate_type.short_description = "Дублировать выбранные типы"

    def export_as_csv(self, request, queryset):
        """Bulk action: экспорт в CSV"""
        import csv
        from django.http import HttpResponse

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="types.csv"'

        writer = csv.writer(response)
        writer.writerow(['ID', 'Название', 'Slug', 'Категория', 'Товаров', 'Дата создания'])

        for type_obj in queryset:
            writer.writerow([
                type_obj.id,
                type_obj.name,
                type_obj.slug,
                type_obj.category.name,
                type_obj.products.count(),
                type_obj.created_at.strftime('%Y-%m-%d')
            ])

        return response
    export_as_csv.short_description = "Экспортировать в CSV"


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'price', 'section', 'brand', 'category', 'collection', 'type', 'is_new', 'is_on_sale', 'created_at']
    list_filter = ['section', 'brand', 'category', 'collection', 'type', 'is_new', 'is_on_sale', 'created_at']
    search_fields = ['name', 'description', 'slug', 'brand__name']
    readonly_fields = ['slug', 'created_at', 'updated_at']
    list_editable = ['price', 'is_new', 'is_on_sale']
    ordering = ['-created_at']
    list_per_page = 50


# ========================
# Tutorial Admin Classes
# ========================

class TutorialVideoInline(admin.TabularInline):
    """Inline редактирование видео для TutorialCategory"""
    model = TutorialVideo
    extra = 1
    fields = ['title', 'youtube_video_id', 'order']
    ordering = ['order']


@admin.register(TutorialCategory)
class TutorialCategoryAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug', 'order', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['title', 'slug']
    prepopulated_fields = {'slug': ('title',)}
    ordering = ['order', '-created_at']

    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'slug', 'banner_image_url', 'order', 'is_active')
        }),
        ('Даты', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ['created_at', 'updated_at']
    inlines = [TutorialVideoInline]


@admin.register(TutorialVideo)
class TutorialVideoAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'youtube_video_id', 'order', 'created_at']
    list_filter = ['category', 'created_at']
    search_fields = ['title', 'youtube_video_id']
    ordering = ['category', 'order', '-created_at']

    fieldsets = (
        ('Основная информация', {
            'fields': ('category', 'title', 'youtube_video_id', 'order')
        }),
        ('Даты', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ['created_at']
