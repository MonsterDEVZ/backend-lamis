from django.apps import AppConfig


class ProductsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.products'
    verbose_name = 'Products'

    def ready(self):
        pass  # import apps.products.signals  # noqa - disabled due to missing apps.logs
