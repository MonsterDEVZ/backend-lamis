#!/usr/bin/env python3
"""
Management command to prepare images for R2 upload
Maps available images from r2-ready-images/ to products in database
Copies and renames images following the naming scheme: {brand}-{collection}-{n}-main/render.webp
"""

from django.core.management.base import BaseCommand
from apps.products.models import Product
from slugify import slugify
import os
import shutil
from pathlib import Path
from collections import defaultdict


class Command(BaseCommand):
    help = 'Prepare images for R2 upload - copy and rename from r2-ready-images/ to catalog-for-r2/'

    def add_arguments(self, parser):
        parser.add_argument(
            '--source-dir',
            type=str,
            default='r2-ready-images',
            help='Source directory with images (default: r2-ready-images)',
        )
        parser.add_argument(
            '--output-dir',
            type=str,
            default='catalog-for-r2',
            help='Output directory for renamed images (default: catalog-for-r2)',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Preview operations without copying files',
        )

    def handle(self, *args, **options):
        source_dir = options['source_dir']
        output_dir = options['output_dir']
        dry_run = options['dry_run']

        self.stdout.write(self.style.SUCCESS('🖼️  Preparing images for R2 upload...\n'))

        if dry_run:
            self.stdout.write(self.style.WARNING('🔍 DRY RUN MODE - No files will be copied\n'))

        # Create output directory if it doesn't exist
        output_path = Path(output_dir)
        if not dry_run:
            output_path.mkdir(exist_ok=True)
            self.stdout.write(f'✓ Output directory: {output_dir}\n')

        # Check if source directory exists
        source_path = Path(source_dir)
        if not source_path.exists():
            self.stdout.write(self.style.ERROR(f'❌ Source directory not found: {source_dir}'))
            self.stdout.write('   Please create this directory and add images to it.')
            return

        # Build a mapping of images organized by brand/collection
        # Key: (brand_name, collection_name), Value: list of image paths
        images_by_brand_collection = defaultdict(list)

        for ext in ['*.webp', '*.jpg', '*.jpeg', '*.png']:
            for img_path in source_path.rglob(ext):
                # Skip README, example, and backup files
                if any(skip in img_path.stem.lower() for skip in ['readme', 'example', 'копия']):
                    continue

                # Try to determine brand and collection from path
                parts = img_path.parts
                brand_name = None
                collection_name = None

                # Look for brand in path (Lamis, Caizer, Blesk)
                for part in parts:
                    if part in ['Lamis', 'Caizer', 'Blesk']:
                        brand_name = part
                        break

                # Collection is usually the subdirectory after brand
                if brand_name:
                    try:
                        brand_idx = parts.index(brand_name)
                        if brand_idx + 1 < len(parts) - 1:  # -1 because last is filename
                            collection_name = parts[brand_idx + 1]
                    except (ValueError, IndexError):
                        pass

                # If no collection from path, try from filename
                if not collection_name:
                    # Try to extract from filename (e.g., "DELUXE-Grey-800...")
                    filename_lower = img_path.stem.lower()
                    for word in img_path.stem.split('-'):
                        if len(word) > 2:  # Avoid short words
                            collection_name = word
                            break

                if brand_name:
                    key = (brand_name.lower(), collection_name.lower() if collection_name else 'unknown')
                    images_by_brand_collection[key].append(img_path)

        # Also build a flat list for fallback matching
        all_images = []
        for ext in ['*.webp', '*.jpg', '*.jpeg', '*.png']:
            for img_path in source_path.rglob(ext):
                if any(skip in img_path.stem.lower() for skip in ['readme', 'example', 'копия']):
                    continue
                all_images.append(img_path)

        self.stdout.write(f'📁 Found {len(all_images)} images in {source_dir} (recursive)')
        self.stdout.write(f'📦 Organized into {len(images_by_brand_collection)} brand/collection groups\n')

        # Statistics
        stats = {
            'products_processed': 0,
            'images_copied': 0,
            'images_missing': 0,
            'images_skipped': 0,
        }

        # Track which images have been used
        used_images = set()

        # Group products by brand and collection
        products_by_brand_collection = {}
        for product in Product.objects.select_related('brand', 'collection').all():
            key = (product.brand.id, product.collection.id)
            if key not in products_by_brand_collection:
                products_by_brand_collection[key] = []
            products_by_brand_collection[key].append(product)

        # Process each brand+collection group
        for (brand_id, collection_id), products in products_by_brand_collection.items():
            if not products:
                continue

            brand = products[0].brand
            collection = products[0].collection
            brand_slug = slugify(brand.name)
            collection_slug = slugify(collection.name)

            self.stdout.write(f'\n📦 {brand.name} - {collection.name}')
            self.stdout.write(f'   Products: {len(products)}')

            # Find available images for this brand/collection
            lookup_key = (brand.name.lower(), collection.name.lower())
            available_images = images_by_brand_collection.get(lookup_key, [])

            # Fallback: try different collection name variations
            if not available_images:
                for key, imgs in images_by_brand_collection.items():
                    brand_key, coll_key = key
                    # Match if brand matches and collection name is similar
                    if brand_key == brand.name.lower():
                        if (collection.name.lower() in coll_key or
                            coll_key in collection.name.lower() or
                            collection_slug in coll_key or
                            coll_key in collection_slug):
                            available_images = imgs
                            break

            self.stdout.write(f'   Available images: {len(available_images)}')

            # Process each product in this group
            for idx, product in enumerate(products, 1):
                stats['products_processed'] += 1

                # Expected filenames (as will be stored)
                main_filename = f"{brand_slug}-{collection_slug}-{idx}-main"
                render_filename = f"{brand_slug}-{collection_slug}-{idx}-render"

                # Determine which source images to use
                main_source = None
                render_source = None

                if available_images:
                    # Use images sequentially from available pool
                    unused_images = [img for img in available_images if img not in used_images]

                    if unused_images:
                        # Use first unused image as main
                        main_source = unused_images[0]
                        used_images.add(main_source)

                        # Try to find a second image for render/hover
                        if len(unused_images) > 1:
                            # Look for images with similar names (might be different views)
                            main_stem = main_source.stem.lower()
                            for img in unused_images[1:]:
                                # Simple heuristic: if names are very similar, likely same product
                                if self._similarity_score(main_stem, img.stem.lower()) > 0.5:
                                    render_source = img
                                    used_images.add(render_source)
                                    break

                            # If no similar image found, use the same image for both
                            if not render_source:
                                render_source = main_source

                # Copy images
                dest_main = output_path / f"{main_filename}.webp"
                dest_render = output_path / f"{render_filename}.webp"

                if main_source:
                    if dest_main.exists():
                        self.stdout.write(f'   ⏩ Skipped: {dest_main.name} (already exists)')
                        stats['images_skipped'] += 1
                    else:
                        if not dry_run:
                            shutil.copy2(main_source, dest_main)
                        self.stdout.write(f'   ✓ Main: {main_source.name} → {dest_main.name}')
                        stats['images_copied'] += 1
                else:
                    self.stdout.write(f'   ⚠️  Missing main image for: {product.name}')
                    stats['images_missing'] += 1

                if render_source and main_source:
                    if dest_render.exists():
                        stats['images_skipped'] += 1
                    else:
                        if not dry_run:
                            shutil.copy2(render_source, dest_render)
                        if render_source != main_source:
                            self.stdout.write(f'   ✓ Hover: {render_source.name} → {dest_render.name}')
                        else:
                            self.stdout.write(f'   ℹ️  Hover: Using same as main')
                        stats['images_copied'] += 1

        # Print summary
        self.stdout.write('\n' + '=' * 80)
        self.stdout.write(self.style.SUCCESS('\n✅ Image preparation completed!'))
        self.stdout.write(f'\n📊 Statistics:')
        self.stdout.write(f'   Products processed: {stats["products_processed"]}')
        self.stdout.write(f'   Images copied: {stats["images_copied"]}')
        self.stdout.write(f'   Images skipped (already exist): {stats["images_skipped"]}')
        self.stdout.write(f'   Images missing: {stats["images_missing"]}')

        if not dry_run:
            self.stdout.write(f'\n📁 Output directory: {output_dir}/')
            self.stdout.write('\n⚠️  NEXT STEPS:')
            self.stdout.write(f'   1. Review images in {output_dir}/')
            self.stdout.write('   2. Upload images to R2 storage')
            self.stdout.write('   3. Verify images are accessible at the URLs in database\n')
        else:
            self.stdout.write(self.style.WARNING('\n💡 This was a dry run. Run without --dry-run to copy files.\n'))

    def _similarity_score(self, str1, str2):
        """Calculate simple similarity score between two strings"""
        # Remove common parts
        str1_clean = str1.lower().replace('-', '').replace('_', '')
        str2_clean = str2.lower().replace('-', '').replace('_', '')

        # Count common characters
        common = sum(1 for c in str1_clean if c in str2_clean)
        total = max(len(str1_clean), len(str2_clean))

        return common / total if total > 0 else 0
