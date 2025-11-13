#!/usr/bin/env python
"""
Скрипт для заполнения URLs картинок коллекций из R2 storage
"""
import os
import django

# Настройка Django окружения
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.products.models import Collection

# Базовый URL для картинок коллекций на R2
BASE_R2_URL = "https://pub-abbe62b0e52d438ea38505b6a2c733d7.r2.dev/images"

# Mapping: имя коллекции -> имя файла на R2 (коллекции относятся к секции "Мебель для ванной")
COLLECTION_IMAGES = {
    'Akcent': 'NvCl-Accent.webp',
    'Amsterdam': 'NvCl-Amsterdam.webp',
    'Andalusia': 'NvCl-Andalusia.webp',
    'Appalon': 'NvCl-Appalon.webp',
    'Capetown': 'NvCl-Kapetown.webp',
    'Classic': 'NvCl-Classic.webp',
    'Compact': 'NvCl-Compact.webp',
    'Deluxe': 'NvCl-Deluxe.webp',
    'Harmony': 'NvCl-Harmony.webp',
    'Lamis': 'NvCl-Lamis.webp',
    'LED': 'NvCl-LED.webp',
    'Lux': 'NvCl-Lux.webp',
    'Nora': 'NvCl-Nora.webp',
    'Omega': 'NvCl-Omega.webp',
    'Palermo': 'NvCl-Palermo.webp',
    'Sanremo': 'NvCl-Sanremo.webp',
    'Sevilya': 'NvCl-Seviliya.webp',  # Note: Sevilya -> Seviliya на R2
    'Solo': 'NvCl-Solo.webp',
}

def populate_collection_images():
    """Заполняет URLs картинок для всех коллекций"""
    updated_count = 0
    not_found_count = 0

    collections = Collection.objects.all()

    for collection in collections:
        if collection.name in COLLECTION_IMAGES:
            image_filename = COLLECTION_IMAGES[collection.name]
            image_url = f"{BASE_R2_URL}/{image_filename}"

            collection.image = image_url
            collection.save()

            print(f"✅ {collection.name}: {image_url}")
            updated_count += 1
        else:
            print(f"⚠️  {collection.name}: картинка не найдена в маппинге")
            not_found_count += 1

    print(f"\n📊 Итого:")
    print(f"   Обновлено: {updated_count}")
    print(f"   Не найдено: {not_found_count}")
    print(f"   Всего коллекций: {collections.count()}")

if __name__ == '__main__':
    populate_collection_images()
