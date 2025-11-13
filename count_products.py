#!/usr/bin/env python3
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.products.models import Product

products = Product.objects.select_related('brand', 'category', 'collection').all()

print(f"Total products: {products.count()}\n")
print("Product List:")
print("=" * 80)

for p in products:
    collection_name = p.collection.name if p.collection else "No-Collection"
    print(f"{p.id} | {p.brand.name} | {collection_name} | {p.name}")
