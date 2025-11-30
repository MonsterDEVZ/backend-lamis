from django.apps import AppConfig


class ProductsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.products'
    verbose_name = 'Продукты'

    def ready(self):
        # Monkey-patch для исправления бага в django-jazzmin
        # https://github.com/farridav/django-jazzmin/issues/350
        # Ошибка: 'str' object has no attribute 'COOKIES'
        self._patch_jazzmin_sidebar_status()

    def _patch_jazzmin_sidebar_status(self):
        """
        Исправляет баг в django-jazzmin, когда sidebar_status получает
        строку вместо объекта HttpRequest.
        """
        try:
            from jazzmin.templatetags import jazzmin as jazzmin_tags
            from django.http import HttpRequest
            from django import template

            # Создаем новый simple_tag с проверкой типа
            @jazzmin_tags.register.simple_tag
            def sidebar_status(request: HttpRequest) -> str:
                """Безопасная версия sidebar_status с проверкой типа."""
                if not isinstance(request, HttpRequest):
                    return ""
                if request.COOKIES.get("jazzy_menu", "") == "closed":
                    return "sidebar-collapse"
                return ""

        except ImportError:
            pass  # jazzmin не установлен
