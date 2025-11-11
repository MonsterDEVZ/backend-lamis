"""
Management command to populate collections
Usage: python manage.py populate_collections
"""

from django.core.management.base import BaseCommand
from apps.products.models import Brand, Category, Collection


class Command(BaseCommand):
    help = 'Populate database with product collections'

    def handle(self, *args, **kwargs):
        # Get brands and categories
        brands = {brand.name: brand for brand in Brand.objects.all()}
        categories = {cat.name: cat for cat in Category.objects.all()}

        if not brands or not categories:
            self.stdout.write(self.style.ERROR('❌ Brands or categories not found. Run populate_brands and populate_categories first.'))
            return

        collections_data = [
            # Lamis - Мебель для ванн
            {
                'name': 'Solo',
                'brand': 'Lamis',
                'category': 'Мебель для ванн',
                'description': 'Минималистичная коллекция мебели для ванной'
            },
            {
                'name': 'Harmony',
                'brand': 'Lamis',
                'category': 'Мебель для ванн',
                'description': 'Гармоничное сочетание функциональности и дизайна'
            },
            {
                'name': 'Lux',
                'brand': 'Lamis',
                'category': 'Мебель для ванн',
                'description': 'Премиум коллекция мебели для ванной'
            },
            # Lamis - Зеркала
            {
                'name': 'Classic',
                'brand': 'Lamis',
                'category': 'Зеркала',
                'description': 'Классические зеркала без подсветки'
            },
            {
                'name': 'LED',
                'brand': 'Lamis',
                'category': 'Зеркала',
                'description': 'Современные зеркала с LED подсветкой'
            },
            # Caizer - Сантехника
            {
                'name': 'Premium',
                'brand': 'Caizer',
                'category': 'Сантехника',
                'description': 'Премиальная сантехника для ванной'
            },
            {
                'name': 'Eco',
                'brand': 'Caizer',
                'category': 'Сантехника',
                'description': 'Экономичная сантехника с функцией экономии воды'
            },
            # Lamis & Blesk - Водонагреватели
            {
                'name': 'Compact',
                'brand': 'Lamis',
                'category': 'Водонагреватели',
                'description': 'Компактные водонагреватели для небольших помещений'
            },
            {
                'name': 'Standard',
                'brand': 'Blesk',
                'category': 'Водонагреватели',
                'description': 'Стандартные водонагреватели для дома'
            },
        ]

        created_count = 0
        updated_count = 0

        for col_data in collections_data:
            brand = brands.get(col_data['brand'])
            category = categories.get(col_data['category'])

            if not brand or not category:
                self.stdout.write(self.style.ERROR(f'❌ Brand or category not found for: {col_data["name"]}'))
                continue

            collection, created = Collection.objects.update_or_create(
                name=col_data['name'],
                brand=brand,
                category=category,
                defaults={'description': col_data['description']}
            )

            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'✓ Created collection: {collection.name} ({brand.name} - {category.name})'))
            else:
                updated_count += 1
                self.stdout.write(self.style.WARNING(f'↻ Updated collection: {collection.name}'))

        self.stdout.write(self.style.SUCCESS(f'\n✅ Collections populated: {created_count} created, {updated_count} updated'))
