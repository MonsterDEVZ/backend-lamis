"""
Management command to populate categories
Usage: python manage.py populate_categories
"""

from django.core.management.base import BaseCommand
from apps.products.models import Brand, Category, BrandCategory


class Command(BaseCommand):
    help = 'Populate database with product categories and link them to brands'

    def handle(self, *args, **kwargs):
        # Ensure brands exist
        lamis = Brand.objects.filter(name='Lamis').first()
        caizer = Brand.objects.filter(name='Caizer').first()
        blesk = Brand.objects.filter(name='Blesk').first()

        if not all([lamis, caizer, blesk]):
            self.stdout.write(self.style.ERROR('❌ Brands not found. Run populate_brands first.'))
            return

        categories_data = [
            {
                'name': 'Мебель для ванн',
                'description': 'Тумбы, пеналы и другая мебель для ванных комнат',
                'brands': [lamis]
            },
            {
                'name': 'Зеркала',
                'description': 'Зеркала с подсветкой и без для ванных комнат',
                'brands': [lamis]
            },
            {
                'name': 'Водонагреватели',
                'description': 'Электрические и газовые водонагреватели',
                'brands': [lamis, blesk]
            },
            {
                'name': 'Сантехника',
                'description': 'Смесители, душевые системы и аксессуары',
                'brands': [caizer]
            },
        ]

        created_count = 0
        updated_count = 0

        for cat_data in categories_data:
            brands = cat_data.pop('brands')
            category, created = Category.objects.update_or_create(
                name=cat_data['name'],
                defaults={'description': cat_data['description']}
            )

            # Link to brands
            for brand in brands:
                BrandCategory.objects.get_or_create(brand=brand, category=category)

            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'✓ Created category: {category.name}'))
            else:
                updated_count += 1
                self.stdout.write(self.style.WARNING(f'↻ Updated category: {category.name}'))

        self.stdout.write(self.style.SUCCESS(f'\n✅ Categories populated: {created_count} created, {updated_count} updated'))
