#!/usr/bin/env python3
"""
Management command to populate main_image_url and hover_image_url for all products
Based on the naming scheme: {brand}-{collection}-{n}-main.webp / render.webp
"""

from django.core.management.base import BaseCommand
from apps.products.models import Product
from slugify import slugify


class Command(BaseCommand):
    help = 'Populate image URLs for all products based on R2 naming scheme'

    def handle(self, *args, **options):
        BASE_URL = "https://pub-abbe62b0e52d438ea38505b6a2c733d7.r2.dev/images/catalog/"

        self.stdout.write(self.style.SUCCESS('🖼️  Populating image URLs...'))
        self.stdout.write(f'Base URL: {BASE_URL}\n')

        # Get all products ordered by brand, collection, and id
        products = Product.objects.select_related('brand', 'collection').all().order_by('brand', 'collection', 'id')

        # Track collection counters per brand-collection combination
        collection_counters = {}

        updated_count = 0
        error_count = 0

        for product in products:
            brand_slug = slugify(product.brand.name)
            collection_slug = slugify(product.collection.name if product.collection else 'no-collection')

            # Get counter for this collection
            key = f"{brand_slug}-{collection_slug}"
            if key not in collection_counters:
                collection_counters[key] = 1
            else:
                collection_counters[key] += 1

            n = collection_counters[key]

            # Construct image URLs
            main_image_url = f"{BASE_URL}{brand_slug}-{collection_slug}-{n}-main.webp"
            hover_image_url = f"{BASE_URL}{brand_slug}-{collection_slug}-{n}-render.webp"

            try:
                product.main_image_url = main_image_url
                product.hover_image_url = hover_image_url
                product.save()

                self.stdout.write(
                    self.style.SUCCESS(
                        f"✓ [{product.id}] {product.name}\n"
                        f"  Main:  {main_image_url}\n"
                        f"  Hover: {hover_image_url}\n"
                    )
                )
                updated_count += 1

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"❌ [{product.id}] {product.name}: {str(e)}\n")
                )
                error_count += 1

        self.stdout.write('\n' + '=' * 80)
        self.stdout.write(
            self.style.SUCCESS(
                f"\n✅ Image URL population completed!\n"
                f"   Updated: {updated_count} products\n"
                f"   Errors: {error_count}\n"
            )
        )

        self.stdout.write(
            self.style.WARNING(
                "\n⚠️  IMPORTANT: Make sure to upload the images to R2!\n"
                f"   Images location: /Users/daniel/Desktop/Daniel_Projects/LAMIS/catalog-for-r2/\n"
                f"   R2 destination: images/\n"
            )
        )
