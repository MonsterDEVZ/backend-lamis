#!/usr/bin/env python3
"""
Management command to populate database with test products
Creates minimum 2 products for each combination of (brand + category + collection)
"""

from django.core.management.base import BaseCommand
from apps.products.models import Brand, Category, Collection, Product
from decimal import Decimal
from slugify import slugify
import random


class Command(BaseCommand):
    help = 'Populate database with test products (min 2 per brand+category+collection)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear all test products before populating (products with "Test" in name)',
        )
        parser.add_argument(
            '--products-per-collection',
            type=int,
            default=2,
            help='Number of products to create per collection (default: 2)',
        )

    def handle(self, *args, **options):
        BASE_URL = "https://pub-abbe62b0e52d438ea38505b6a2c733d7.r2.dev/images/catalog/"

        products_per_collection = options['products_per_collection']

        self.stdout.write(self.style.SUCCESS('🔄 Populating database with test data...'))
        self.stdout.write(f'Products per collection: {products_per_collection}\n')

        # Clear test products if requested
        if options['clear']:
            test_products = Product.objects.filter(name__icontains='Test')
            count = test_products.count()
            test_products.delete()
            self.stdout.write(self.style.WARNING(f'🗑️  Cleared {count} test products\n'))

        # Track statistics
        stats = {
            'brands': 0,
            'categories': 0,
            'collections': 0,
            'products_created': 0,
            'products_skipped': 0,
        }

        # Iterate through all brands
        for brand in Brand.objects.all():
            stats['brands'] += 1
            self.stdout.write(self.style.SUCCESS(f'\n📦 Brand: {brand.name}'))

            # Get categories for this brand (using M2M relationship)
            categories = Category.objects.filter(brands=brand)

            if not categories.exists():
                self.stdout.write(self.style.WARNING(f'  ⚠️  No categories for brand {brand.name}'))
                continue

            for category in categories:
                stats['categories'] += 1
                self.stdout.write(f'  📂 Category: {category.name}')

                # Get collections for this brand+category
                collections = Collection.objects.filter(brand=brand, category=category)

                if not collections.exists():
                    self.stdout.write(self.style.WARNING(f'    ⚠️  No collections for {brand.name} + {category.name}'))
                    continue

                for collection in collections:
                    stats['collections'] += 1
                    self.stdout.write(f'    📁 Collection: {collection.name}')

                    # Check how many products already exist for this combination
                    existing_count = Product.objects.filter(
                        brand=brand,
                        category=category,
                        collection=collection
                    ).count()

                    # Calculate how many products to create
                    to_create = max(0, products_per_collection - existing_count)

                    if to_create == 0:
                        self.stdout.write(f'      ✓ Already has {existing_count} products, skipping')
                        stats['products_skipped'] += existing_count
                        continue

                    # Create products
                    for i in range(to_create):
                        product_number = existing_count + i + 1

                        # Generate product data
                        product_name = f"{brand.name} {collection.name} {category.name} #{product_number}"
                        price = Decimal(random.randint(5000, 100000))
                        is_new = random.choice([True, False])
                        is_on_sale = random.choice([True, False])

                        # Generate image URLs
                        brand_slug = slugify(brand.name)
                        collection_slug = slugify(collection.name)
                        main_image_url = f"{BASE_URL}{brand_slug}-{collection_slug}-{product_number}-main.webp"
                        hover_image_url = f"{BASE_URL}{brand_slug}-{collection_slug}-{product_number}-render.webp"

                        # Create product
                        try:
                            product = Product.objects.create(
                                name=product_name,
                                price=price,
                                brand=brand,
                                category=category,
                                collection=collection,
                                main_image_url=main_image_url,
                                hover_image_url=hover_image_url,
                                is_new=is_new,
                                is_on_sale=is_on_sale,
                                description=f"Test product for {brand.name} - {collection.name} collection"
                            )

                            self.stdout.write(
                                f'      ✓ Created: {product.name} '
                                f'(ID: {product.id}, Price: {price}, New: {is_new}, Sale: {is_on_sale})'
                            )
                            stats['products_created'] += 1

                        except Exception as e:
                            self.stdout.write(
                                self.style.ERROR(f'      ❌ Error creating product: {str(e)}')
                            )

        # Print summary
        self.stdout.write('\n' + '=' * 80)
        self.stdout.write(self.style.SUCCESS('\n✅ Population completed!'))
        self.stdout.write(f'\n📊 Statistics:')
        self.stdout.write(f'   Brands processed: {stats["brands"]}')
        self.stdout.write(f'   Categories processed: {stats["categories"]}')
        self.stdout.write(f'   Collections processed: {stats["collections"]}')
        self.stdout.write(f'   Products created: {stats["products_created"]}')
        self.stdout.write(f'   Products skipped (already exist): {stats["products_skipped"]}')
        self.stdout.write(f'\n   Total products in DB: {Product.objects.count()}')

        self.stdout.write('\n⚠️  NEXT STEPS:')
        self.stdout.write('   1. Run: python manage.py prepare_images_for_r2')
        self.stdout.write('   2. This will prepare images for all products')
        self.stdout.write('   3. Upload images from catalog-for-r2/ to R2\n')
