#!/usr/bin/env python3
"""
Management command to add /catalog/ to image URLs
"""

from django.core.management.base import BaseCommand
from apps.products.models import Product


class Command(BaseCommand):
    help = 'Fix image URLs by adding /catalog/ in the path'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🔧 Fixing image URLs...'))

        products = Product.objects.all()
        updated_count = 0

        for product in products:
            updated = False

            # Fix main_image_url
            if product.main_image_url and '/catalog/' not in product.main_image_url:
                product.main_image_url = product.main_image_url.replace('/images/', '/images/catalog/')
                updated = True

            # Fix hover_image_url
            if product.hover_image_url and '/catalog/' not in product.hover_image_url:
                product.hover_image_url = product.hover_image_url.replace('/images/', '/images/catalog/')
                updated = True

            if updated:
                product.save()
                self.stdout.write(
                    self.style.SUCCESS(
                        f"✓ [{product.id}] {product.name}\n"
                        f"  Main:  {product.main_image_url}\n"
                        f"  Hover: {product.hover_image_url}\n"
                    )
                )
                updated_count += 1

        self.stdout.write('\n' + '=' * 80)
        self.stdout.write(
            self.style.SUCCESS(
                f"\n✅ URL fix completed!\n"
                f"   Updated: {updated_count} products\n"
            )
        )
