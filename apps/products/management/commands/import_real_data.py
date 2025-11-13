"""
Management command to import real product data from frontend
"""

from django.core.management.base import BaseCommand
from apps.products.models import Brand, Category, Collection, Product, BrandCategory
from decimal import Decimal


class Command(BaseCommand):
    help = 'Import real collections and products data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Starting real data import...\n')

        # Get brands
        lamis = Brand.objects.get(slug='lamis')
        caizer = Brand.objects.get(slug='caizer')
        blesk = Brand.objects.get(slug='blesk')

        # Get or create categories
        furniture_cat, _ = Category.objects.get_or_create(
            slug='mebel-dlia-vann',
            defaults={
                'name': 'Мебель для ванн',
                'description': 'Тумбы, пеналы и другая мебель для ванных комнат'
            }
        )

        mirrors_cat, _ = Category.objects.get_or_create(
            slug='zerkala',
            defaults={
                'name': 'Зеркала',
                'description': 'Зеркала с подсветкой и без для ванных комнат'
            }
        )

        santech_cat, _ = Category.objects.get_or_create(
            slug='santekhnika',
            defaults={
                'name': 'Сантехника',
                'description': 'Смесители, душевые системы и аксессуары'
            }
        )

        heaters_cat, _ = Category.objects.get_or_create(
            slug='vodonagrevateli',
            defaults={
                'name': 'Водонагреватели',
                'description': 'Электрические и газовые водонагреватели'
            }
        )

        # Link brands to categories
        BrandCategory.objects.get_or_create(brand=lamis, category=furniture_cat)
        BrandCategory.objects.get_or_create(brand=lamis, category=mirrors_cat)
        BrandCategory.objects.get_or_create(brand=lamis, category=heaters_cat)
        BrandCategory.objects.get_or_create(brand=caizer, category=santech_cat)
        BrandCategory.objects.get_or_create(brand=blesk, category=heaters_cat)

        # Create real collections from frontend
        collections_data = [
            # Lamis Furniture Collections
            {'name': 'Akcent', 'slug': 'akcent', 'brand': lamis, 'category': furniture_cat, 'description': 'Коллекция Akcent'},
            {'name': 'Amsterdam', 'slug': 'amsterdam', 'brand': lamis, 'category': furniture_cat, 'description': 'Коллекция Amsterdam'},
            {'name': 'Andalusia', 'slug': 'andalusia', 'brand': lamis, 'category': furniture_cat, 'description': 'Коллекция Andalusia'},
            {'name': 'Appalon', 'slug': 'appalon', 'brand': lamis, 'category': furniture_cat, 'description': 'Коллекция Appalon'},
            {'name': 'Capetown', 'slug': 'capetown', 'brand': lamis, 'category': furniture_cat, 'description': 'Коллекция Capetown'},
            {'name': 'Deluxe', 'slug': 'deluxe', 'brand': lamis, 'category': furniture_cat, 'description': 'Коллекция Deluxe'},
            {'name': 'Lamis', 'slug': 'lamis', 'brand': lamis, 'category': furniture_cat, 'description': 'Коллекция Lamis'},
            {'name': 'Nora', 'slug': 'nora', 'brand': lamis, 'category': furniture_cat, 'description': 'Коллекция Nora'},
            {'name': 'Omega', 'slug': 'omega', 'brand': lamis, 'category': furniture_cat, 'description': 'Коллекция Omega'},
            {'name': 'Palermo', 'slug': 'palermo', 'brand': lamis, 'category': furniture_cat, 'description': 'Коллекция Palermo'},
            {'name': 'Sanremo', 'slug': 'sanremo', 'brand': lamis, 'category': furniture_cat, 'description': 'Коллекция Sanremo'},
            {'name': 'Sevilya', 'slug': 'sevilya', 'brand': lamis, 'category': furniture_cat, 'description': 'Коллекция Sevilya'},
        ]

        for coll_data in collections_data:
            coll, created = Collection.objects.get_or_create(
                slug=coll_data['slug'],
                brand=coll_data['brand'],
                category=coll_data['category'],
                defaults={
                    'name': coll_data['name'],
                    'description': coll_data['description']
                }
            )
            status = '✓ Created' if created else '• Updated'
            self.stdout.write(f"{status} collection: {coll.name} ({coll.brand.name} - {coll.category.name})")

        self.stdout.write(self.style.SUCCESS(f'\n✅ Collections imported: {len(collections_data)} total'))

        # Create sample products from Akcent collection
        base_url = 'https://pub-abbe62b0e52d438ea38505b6a2c733d7.r2.dev/images/'
        akcent_coll = Collection.objects.get(slug='akcent')

        products_data = [
            {
                'name': 'Accent Black Closet 400x300x1750',
                'slug': 'accent-black-closet',
                'price': Decimal('45990.00'),
                'brand': lamis,
                'category': furniture_cat,
                'collection': akcent_coll,
                'main_image_url': f'{base_url}Lamis/Accent/AKTSENT-Closet-Black-400x300x1750.webp',
                'images': [
                    f'{base_url}Lamis/Accent/AKTSENT-Closet-Black-400x300x1750.webp',
                    f'{base_url}Lamis/Accent/1/example_for_2_image.webp',
                ],
                'is_new': True,
                'description': 'Элегантный шкаф-пенал Accent в черном цвете. Идеально подходит для хранения банных принадлежностей.'
            },
            {
                'name': 'Accent White Closet 400x300x1750',
                'slug': 'accent-white-closet',
                'price': Decimal('45990.00'),
                'brand': lamis,
                'category': furniture_cat,
                'collection': akcent_coll,
                'main_image_url': f'{base_url}Lamis/Accent/AKTSENT-Closet-White-400x300x1750.webp',
                'images': [
                    f'{base_url}Lamis/Accent/AKTSENT-Closet-White-400x300x1750.webp',
                    f'{base_url}Lamis/Accent/2/example_for_2_image.webp',
                ],
                'is_new': False,
                'description': 'Элегантный шкаф-пенал Accent в белом цвете. Универсальное решение для любой ванной.'
            },
            {
                'name': 'Accent Grey Closet 400x300x1750',
                'slug': 'accent-grey-closet',
                'price': Decimal('45990.00'),
                'brand': lamis,
                'category': furniture_cat,
                'collection': akcent_coll,
                'main_image_url': f'{base_url}Lamis/Accent/AKTSENT-Grey-400x300x1750.webp',
                'images': [
                    f'{base_url}Lamis/Accent/AKTSENT-Grey-400x300x1750.webp',
                    f'{base_url}Lamis/Accent/1/example_for_2_image.webp',
                ],
                'is_new': False,
                'description': 'Элегантный шкаф-пенал Accent в сером цвете. Стильное дополнение к современному интерьеру.'
            },
        ]

        for prod_data in products_data:
            prod, created = Product.objects.get_or_create(
                slug=prod_data['slug'],
                defaults=prod_data
            )
            status = '✓ Created' if created else '• Updated'
            self.stdout.write(f"{status}: {prod.name}")

        self.stdout.write(self.style.SUCCESS(f'\n✅ Sample products: {len(products_data)} created'))
        self.stdout.write(self.style.SUCCESS('\n🎉 Real data import completed!'))
