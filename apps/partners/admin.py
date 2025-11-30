from django.contrib import admin
from django.utils.html import format_html
from .models import Partner

@admin.register(Partner)
class PartnerAdmin(admin.ModelAdmin):
    # Поля, которые будут видны в списке
    list_display = ('id', 'format_logo_preview', 'name')
    # Делает имя кликабельным для перехода к редактированию
    list_display_links = ('id', 'name')
    # Добавляет поиск по названию
    search_fields = ('name',)
    # Порядок сортировки
    ordering = ('id',)

    # Функция для предпросмотра логотипа в списке
    def format_logo_preview(self, obj):
        if obj.logo:
            return format_html('<img src="{}" width="100" />', obj.logo.url)
        return "Нет логотипа"
    
    # Название колонки с предпросмотром
    format_logo_preview.short_description = 'Логотип'