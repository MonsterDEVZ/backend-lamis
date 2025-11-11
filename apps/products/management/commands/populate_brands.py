"""
Management command to populate brands
Usage: python manage.py populate_brands
"""

from django.core.management.base import BaseCommand
from apps.products.models import Brand


class Command(BaseCommand):
    help = 'Populate database with LAMIS brands (Lamis, Caizer, Blesk)'

    def handle(self, *args, **kwargs):
        brands_data = [
            {
                'name': 'Lamis',
                'description': 'Мебель для ванных комнат, зеркала и водонагреватели премиум класса'
            },
            {
                'name': 'Caizer',
                'description': 'Современная сантехника и аксессуары для ванной'
            },
            {
                'name': 'Blesk',
                'description': 'Водонагреватели и отопительное оборудование'
            },
        ]

        created_count = 0
        updated_count = 0

        for brand_data in brands_data:
            brand, created = Brand.objects.update_or_create(
                name=brand_data['name'],
                defaults={'description': brand_data['description']}
            )
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'✓ Created brand: {brand.name}'))
            else:
                updated_count += 1
                self.stdout.write(self.style.WARNING(f'↻ Updated brand: {brand.name}'))

        self.stdout.write(self.style.SUCCESS(f'\n✅ Brands populated: {created_count} created, {updated_count} updated'))
