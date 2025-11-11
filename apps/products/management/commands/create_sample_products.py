"""
Management command to create sample products
Usage: python manage.py create_sample_products
"""

from django.core.management.base import BaseCommand
from apps.products.models import Brand, Category, Collection, Product
from decimal import Decimal


class Command(BaseCommand):
    help = 'Create sample products for testing'

    def handle(self, *args, **kwargs):
        # Get brands
        lamis = Brand.objects.get(name='Lamis')
        caizer = Brand.objects.get(name='Caizer')
        blesk = Brand.objects.get(name='Blesk')

        # Get categories
        mebel = Category.objects.get(name='Мебель для ванн')
        zerkala = Category.objects.get(name='Зеркала')
        vodonagrevateli = Category.objects.get(name='Водонагреватели')
        santekhnika = Category.objects.get(name='Сантехника')

        # Get collections
        solo = Collection.objects.get(name='Solo', brand=lamis, category=mebel)
        harmony = Collection.objects.get(name='Harmony', brand=lamis, category=mebel)
        led = Collection.objects.get(name='LED', brand=lamis, category=zerkala)
        premium = Collection.objects.get(name='Premium', brand=caizer, category=santekhnika)
        compact = Collection.objects.get(name='Compact', brand=lamis, category=vodonagrevateli)

        products_data = [
            # Мебель Lamis Solo
            {
                'name': 'Тумба для ванной Solo 60',
                'price': Decimal('15000.00'),
                'brand': lamis,
                'category': mebel,
                'collection': solo,
                'main_image_url': 'https://via.placeholder.com/600x400?text=Solo+60',
                'images': ['https://via.placeholder.com/600x400?text=Solo+60+1', 'https://via.placeholder.com/600x400?text=Solo+60+2'],
                'colors': [{'name': 'Белый', 'hex': '#FFFFFF'}, {'name': 'Дуб', 'hex': '#A0826D'}],
                'is_new': True,
                'is_on_sale': False,
                'description': 'Современная тумба для ванной комнаты из коллекции Solo. Влагостойкие материалы, плавное закрывание.'
            },
            {
                'name': 'Тумба для ванной Solo 80',
                'price': Decimal('18500.00'),
                'brand': lamis,
                'category': mebel,
                'collection': solo,
                'main_image_url': 'https://via.placeholder.com/600x400?text=Solo+80',
                'images': ['https://via.placeholder.com/600x400?text=Solo+80+1'],
                'colors': [{'name': 'Белый', 'hex': '#FFFFFF'}, {'name': 'Графит', 'hex': '#2F4F4F'}],
                'is_new': True,
                'is_on_sale': False,
                'description': 'Просторная тумба для ванной 80 см из коллекции Solo.'
            },
            # Мебель Lamis Harmony
            {
                'name': 'Комплект Harmony 100',
                'price': Decimal('28000.00'),
                'brand': lamis,
                'category': mebel,
                'collection': harmony,
                'main_image_url': 'https://via.placeholder.com/600x400?text=Harmony+100',
                'images': [],
                'colors': [{'name': 'Венге', 'hex': '#4A3728'}],
                'is_new': False,
                'is_on_sale': True,
                'description': 'Полный комплект мебели Harmony: тумба с раковиной, зеркало и пенал.'
            },
            # Зеркала Lamis LED
            {
                'name': 'Зеркало LED 60x80',
                'price': Decimal('12500.00'),
                'brand': lamis,
                'category': zerkala,
                'collection': led,
                'main_image_url': 'https://via.placeholder.com/400x600?text=LED+Mirror',
                'images': [],
                'colors': [],
                'is_new': True,
                'is_on_sale': False,
                'description': 'Зеркало с LED подсветкой, сенсорный выключатель, защита от запотевания.'
            },
            {
                'name': 'Зеркало LED 80x100',
                'price': Decimal('16900.00'),
                'brand': lamis,
                'category': zerkala,
                'collection': led,
                'main_image_url': 'https://via.placeholder.com/400x600?text=LED+Mirror+Large',
                'images': [],
                'colors': [],
                'is_new': False,
                'is_on_sale': True,
                'description': 'Большое зеркало с LED подсветкой и часами.'
            },
            # Сантехника Caizer Premium
            {
                'name': 'Смеситель для раковины Caizer Premium',
                'price': Decimal('8900.00'),
                'brand': caizer,
                'category': santekhnika,
                'collection': premium,
                'main_image_url': 'https://via.placeholder.com/600x400?text=Caizer+Mixer',
                'images': [],
                'colors': [{'name': 'Хром', 'hex': '#C0C0C0'}, {'name': 'Черный матовый', 'hex': '#1C1C1C'}],
                'is_new': True,
                'is_on_sale': False,
                'description': 'Однорычажный смеситель премиум класса с керамическим картриджем.'
            },
            {
                'name': 'Душевая система Caizer Premium',
                'price': Decimal('24500.00'),
                'brand': caizer,
                'category': santekhnika,
                'collection': premium,
                'main_image_url': 'https://via.placeholder.com/400x600?text=Shower+System',
                'images': [],
                'colors': [{'name': 'Хром', 'hex': '#C0C0C0'}],
                'is_new': False,
                'is_on_sale': False,
                'description': 'Душевая система с верхним душем, термостатом и ручной лейкой.'
            },
            # Водонагреватели Lamis Compact
            {
                'name': 'Водонагреватель Compact 30L',
                'price': Decimal('11200.00'),
                'brand': lamis,
                'category': vodonagrevateli,
                'collection': compact,
                'main_image_url': 'https://via.placeholder.com/400x600?text=Heater+30L',
                'images': [],
                'colors': [{'name': 'Белый', 'hex': '#FFFFFF'}],
                'is_new': True,
                'is_on_sale': False,
                'description': 'Компактный электрический водонагреватель 30 литров.'
            },
            {
                'name': 'Водонагреватель Compact 50L',
                'price': Decimal('13800.00'),
                'brand': lamis,
                'category': vodonagrevateli,
                'collection': compact,
                'main_image_url': 'https://via.placeholder.com/400x600?text=Heater+50L',
                'images': [],
                'colors': [{'name': 'Белый', 'hex': '#FFFFFF'}],
                'is_new': False,
                'is_on_sale': True,
                'description': 'Электрический водонагреватель 50 литров с ускоренным нагревом.'
            },
            # Водонагреватели Blesk Standard
            {
                'name': 'Водонагреватель Blesk Standard 80L',
                'price': Decimal('16500.00'),
                'brand': blesk,
                'category': vodonagrevateli,
                'collection': Collection.objects.get(name='Standard', brand=blesk),
                'main_image_url': 'https://via.placeholder.com/400x600?text=Blesk+80L',
                'images': [],
                'colors': [{'name': 'Белый', 'hex': '#FFFFFF'}, {'name': 'Серебристый', 'hex': '#E5E5E5'}],
                'is_new': False,
                'is_on_sale': False,
                'description': 'Надежный водонагреватель Blesk на 80 литров.'
            },
        ]

        created_count = 0
        for product_data in products_data:
            product, created = Product.objects.get_or_create(
                name=product_data['name'],
                defaults=product_data
            )
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'✓ Created: {product.name}'))
            else:
                self.stdout.write(self.style.WARNING(f'↻ Already exists: {product.name}'))

        self.stdout.write(self.style.SUCCESS(f'\n✅ Sample products: {created_count} created'))
