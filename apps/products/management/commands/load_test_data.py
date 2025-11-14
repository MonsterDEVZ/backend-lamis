"""
Management command to load comprehensive test data for LAMIS
Usage: python manage.py load_test_data

Loads in order:
1. Brands (Lamis, Blesk, Caizer)
2. Sections (6 sections with descriptions)
3. Categories (for each section + brand)
4. Collections (10 for Мебель для ванной)
5. Products (25-30 with real image URLs)
"""

from django.core.management.base import BaseCommand
from apps.products.models import Brand, Section, Category, Collection, Type, Product
from decimal import Decimal
import random


class Command(BaseCommand):
    help = 'Load comprehensive test data into the database'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.HTTP_INFO('\n' + '='*60))
        self.stdout.write(self.style.HTTP_INFO('  ЗАГРУЗКА ТЕСТОВЫХ ДАННЫХ В БД'))
        self.stdout.write(self.style.HTTP_INFO('='*60 + '\n'))

        # Step 1: Create Brands
        self.stdout.write(self.style.HTTP_INFO('ШАГ 1: Создание брендов...'))
        brands = self.create_brands()

        # Step 2: Create Sections
        self.stdout.write(self.style.HTTP_INFO('\nШАГ 2: Создание разделов...'))
        sections = self.create_sections()

        # Step 3: Create Categories
        self.stdout.write(self.style.HTTP_INFO('\nШАГ 3: Создание категорий...'))
        categories = self.create_categories(sections, brands)

        # Step 4: Create Collections
        self.stdout.write(self.style.HTTP_INFO('\nШАГ 4: Создание коллекций...'))
        collections = self.create_collections(sections, brands, categories)

        # Step 5: Create Products
        self.stdout.write(self.style.HTTP_INFO('\nШАГ 5: Создание товаров...'))
        products = self.create_products(sections, brands, categories, collections)

        # Summary
        self.stdout.write(self.style.SUCCESS('\n' + '='*60))
        self.stdout.write(self.style.SUCCESS('  ✅ ЗАГРУЗКА ЗАВЕРШЕНА!'))
        self.stdout.write(self.style.SUCCESS('='*60))
        self.stdout.write(self.style.SUCCESS(f'Брендов: {len(brands)}'))
        self.stdout.write(self.style.SUCCESS(f'Разделов: {len(sections)}'))
        self.stdout.write(self.style.SUCCESS(f'Категорий: {len(categories)}'))
        self.stdout.write(self.style.SUCCESS(f'Коллекций: {len(collections)}'))
        self.stdout.write(self.style.SUCCESS(f'Товаров: {len(products)}'))
        self.stdout.write(self.style.SUCCESS('='*60 + '\n'))

    def create_brands(self):
        """Create 3 brands: Lamis, Blesk, Caizer"""
        brands_data = [
            {
                'name': 'Lamis',
                'description': 'Мебель для ванных комнат, зеркала и водонагреватели премиум класса'
            },
            {
                'name': 'Blesk',
                'description': 'Водонагреватели и отопительное оборудование высокого качества'
            },
            {
                'name': 'Caizer',
                'description': 'Современная сантехника и аксессуары для ванной'
            },
        ]

        brands = {}
        for brand_data in brands_data:
            brand, created = Brand.objects.update_or_create(
                name=brand_data['name'],
                defaults={'description': brand_data['description']}
            )
            brands[brand.name] = brand
            status = '✓ Создан' if created else '↻ Обновлён'
            self.stdout.write(f'  {status}: {brand.name}')

        return brands

    def create_sections(self):
        """Create 6 sections with detailed descriptions"""
        sections_data = [
            {
                'name': 'Мебель для ванной',
                'title': 'Мебель для ванной комнаты - функциональность и стиль',
                'description': '''Мебель для ванной комнаты играет ключевую роль в создании комфортного и функционального пространства. Она не только обеспечивает удобное хранение необходимых принадлежностей, но и задает стиль всего помещения. Современная мебель сочетает практичность с эстетикой, предлагая решения для ванных комнат любых размеров.

При выборе мебели важно учитывать материалы, устойчивые к влаге и перепадам температур. Качественная фурнитура и покрытия обеспечивают долговечность и сохранение внешнего вида на долгие годы. Грамотно подобранная мебель способна визуально расширить пространство и создать уютную атмосферу.'''
            },
            {
                'name': 'Санфарфор',
                'title': 'Санфарфор - качественная сантехника для вашего дома',
                'description': '''Санитарный фарфор является основой комфорта в ванной комнате и туалете. Высококачественный санфарфор отличается прочностью, гигиеничностью и долговечностью. Современные технологии производства позволяют создавать изделия с идеально гладкой поверхностью, которая легко очищается и противостоит образованию налета.

При выборе санфарфора важно обращать внимание на качество глазури, равномерность покрытия и отсутствие дефектов. Правильно подобранная сантехника не только служит долгие годы, но и способствует экономии воды благодаря современным системам слива.'''
            },
            {
                'name': 'Смесители',
                'title': 'Смесители - функциональность и дизайн для вашей ванной',
                'description': '''Смесители являются одним из важнейших элементов оснащения ванной комнаты и кухни. Современные смесители сочетают надежность, экономичность и стильный дизайн. Качественная арматура обеспечивает комфортное использование и долгий срок службы без протечек и поломок.

Выбор смесителя зависит от типа установки, дизайна интерьера и функциональных требований. Хромированные покрытия защищают от коррозии и сохраняют блеск, а керамические картриджи обеспечивают плавное регулирование температуры и напора воды.'''
            },
            {
                'name': 'Душевые кабины',
                'title': 'Душевые кабины - современное решение для ванной комнаты',
                'description': '''Душевые кабины стали популярным решением для современных ванных комнат благодаря своей практичности и компактности. Они позволяют эффективно использовать пространство, особенно в небольших помещениях, при этом обеспечивая комфорт и функциональность.

Современные душевые кабины изготавливаются из качественных материалов, устойчивых к влаге и температурным перепадам. Закаленное стекло, надежная фурнитура и продуманная система водоотведения обеспечивают долгий срок службы и удобство эксплуатации.'''
            },
            {
                'name': 'Водонагреватели',
                'title': 'Водонагреватели - надежное обеспечение горячей водой',
                'description': '''Водонагреватели обеспечивают независимость от централизованного горячего водоснабжения и позволяют иметь горячую воду круглый год. Современные модели отличаются энергоэффективностью, надежностью и длительным сроком службы.

Выбор водонагревателя зависит от потребностей семьи, доступного пространства и источника энергии. Накопительные модели обеспечивают запас горячей воды, а проточные нагревают воду мгновенно, экономя пространство и электроэнергию.'''
            },
            {
                'name': 'Зеркала',
                'title': 'Зеркала для ванной - функциональность и декор',
                'description': '''Зеркала в ванной комнате выполняют не только практическую функцию, но и играют важную роль в дизайне интерьера. Правильно подобранное зеркало способно визуально расширить пространство, добавить света и стать стильным акцентом помещения.

Современные зеркала для ванных комнат часто оснащаются подсветкой, системой подогрева против запотевания и даже сенсорными элементами управления. Качественное покрытие защищает от влаги и обеспечивает долгий срок службы без потери отражающих свойств.'''
            },
        ]

        sections = {}
        for section_data in sections_data:
            section, created = Section.objects.update_or_create(
                name=section_data['name'],
                defaults={
                    'title': section_data['title'],
                    'description': section_data['description']
                }
            )
            sections[section.name] = section
            status = '✓ Создан' if created else '↻ Обновлён'
            self.stdout.write(f'  {status}: {section.name}')

        return sections

    def create_categories(self, sections, brands):
        """Create categories for each section + brand combination"""
        categories_data = {
            'Мебель для ванной': ['Мебель', 'Тумбы', 'Пеналы', 'Шкафы'],
            'Санфарфор': ['Раковины', 'Унитазы', 'Биде', 'Писсуары'],
            'Смесители': ['Смесители для раковины', 'Смесители для ванны', 'Смесители для душа', 'Смесители для кухни'],
            'Душевые кабины': ['Душевые кабины', 'Душевые уголки', 'Душевые двери', 'Поддоны'],
            'Водонагреватели': ['Накопительные', 'Проточные', 'Бойлеры', 'Косвенного нагрева'],
            'Зеркала': ['Зеркала с подсветкой', 'Зеркала без подсветки', 'Зеркальные шкафы', 'Зеркала с полкой'],
        }

        categories = []
        for section_name, category_names in categories_data.items():
            section = sections[section_name]
            for brand_name, brand in brands.items():
                for category_name in category_names:
                    category, created = Category.objects.update_or_create(
                        name=category_name,
                        section=section,
                        brand=brand,
                        defaults={
                            'description': f'{category_name} от производителя {brand_name}'
                        }
                    )
                    categories.append(category)
                    status = '✓' if created else '↻'
                    self.stdout.write(f'  {status} {section.name} → {brand.name} → {category.name}')

        return categories

    def create_collections(self, sections, brands, categories):
        """Create 10 collections for 'Мебель для ванной' section across ALL categories"""
        collections_data = [
            'Akcent',
            'Omega',
            'Sanremo',
            'Palermo',
            'Deluxe',
            'Andalusia',
            'Premium',
            'Solo',
            'Harmony',
            'Lux',
        ]

        section_furniture = sections['Мебель для ванной']
        collections = []

        # Create collections for each brand + category combination in Мебель для ванной
        for brand_name, brand in brands.items():
            # Get ALL categories for this section + brand
            section_categories = Category.objects.filter(
                section=section_furniture,
                brand=brand
            )

            # Create collections for EACH category (not just first one!)
            for category in section_categories:
                for collection_name in collections_data:
                    collection, created = Collection.objects.update_or_create(
                        name=collection_name,
                        brand=brand,
                        category=category,
                        defaults={
                            'description': f'Коллекция {collection_name} от {brand_name} для {category.name}'
                        }
                    )
                    collections.append(collection)
                    status = '✓' if created else '↻'
                    self.stdout.write(f'  {status} {collection.name} ({brand.name} → {category.name})')

        return collections

    def get_images_for_product(self, product_name, collection_name, brand_name):
        """Get appropriate images for a product based on name/collection/brand"""

        # Base URL for all images
        base_url = 'https://pub-abbe62b0e52d438ea38505b6a2c733d7.r2.dev/images/catalog/'

        # Mapping collections/names to image prefixes
        image_mapping = {
            'solo': 'lamis-solo',
            'harmony': 'lamis-harmony',
            'lux': 'lamis-lux',
            'premium': 'caizer-premium' if brand_name == 'Caizer' else 'lamis-lux',
            'deluxe': 'lamis-led',
            'akcent': 'lamis-akcent',
            'omega': 'lamis-omega',
            'sanremo': 'lamis-sanremo',
            'palermo': 'lamis-palermo',
            'andalusia': 'lamis-andalusia',
            'amsterdam': 'lamis-amsterdam',
            'appalon': 'lamis-appalon',
            'nora': 'lamis-nora',
            'sevilya': 'lamis-sevilya',
            'compact': 'lamis-compact',
            'led': 'lamis-led',
            'standard': 'blesk-standard',
        }

        # All available images
        all_images = [
            ('blesk-standard', 1, True),
            ('caizer-premium', 1, True),
            ('caizer-premium', 2, True),
            ('lamis-akcent', 1, True),
            ('lamis-akcent', 2, True),
            ('lamis-akcent', 3, True),
            ('lamis-amsterdam', 1, True),
            ('lamis-andalusia', 1, True),
            ('lamis-appalon', 1, True),
            ('lamis-compact', 1, True),
            ('lamis-compact', 2, True),
            ('lamis-harmony', 1, True),
            ('lamis-lamis', 1, True),
            ('lamis-lamis', 2, True),
            ('lamis-led', 1, True),
            ('lamis-led', 2, True),
            ('lamis-lux', 1, True),
            ('lamis-lux', 2, True),
            ('lamis-nora', 1, False),
            ('lamis-omega', 1, False),
            ('lamis-palermo', 1, False),
            ('lamis-sanremo', 1, False),
            ('lamis-sevilya', 1, False),
            ('lamis-solo', 1, True),
            ('lamis-solo', 2, True),
        ]

        # Try to find matching image by collection or product name
        search_term = None
        if collection_name:
            search_term = collection_name.lower()
        else:
            # Try to find keyword in product name
            product_lower = product_name.lower()
            for keyword in image_mapping.keys():
                if keyword in product_lower:
                    search_term = keyword
                    break

        # Get image prefix
        if search_term and search_term in image_mapping:
            image_prefix = image_mapping[search_term]
        else:
            # Random fallback
            image_prefix = random.choice([img[0] for img in all_images])

        # Find images with this prefix
        matching_images = [img for img in all_images if img[0] == image_prefix]

        if not matching_images:
            # Fallback to first available
            matching_images = all_images[:1]

        # Pick a random variant (1 or 2) if multiple exist
        selected = random.choice(matching_images)
        prefix, number, has_render = selected

        main_image = f'{base_url}{prefix}-{number}-main.webp'
        hover_image = f'{base_url}{prefix}-{number}-render.webp' if has_render else main_image

        # Additional images - try to get other variants
        additional = []
        for img in all_images:
            if img[0] == prefix and img[1] != number:
                additional.append(f'{base_url}{img[0]}-{img[1]}-main.webp')
                if img[2]:  # has render
                    additional.append(f'{base_url}{img[0]}-{img[1]}-render.webp')

        # Limit to 2 additional images
        additional = additional[:2]

        return main_image, hover_image, additional

    def create_products(self, sections, brands, categories, collections):
        """Create 25-30 products with real image URLs from Cloudflare R2"""

        products_data = [
            # Мебель для ванной - Lamis
            {'name': 'Тумба Solo 60 подвесная с раковиной', 'section': 'Мебель для ванной', 'brand': 'Lamis', 'category': 'Тумбы', 'collection': 'Solo', 'price': 25990},
            {'name': 'Тумба Harmony 80 напольная белый глянец', 'section': 'Мебель для ванной', 'brand': 'Lamis', 'category': 'Тумбы', 'collection': 'Harmony', 'price': 32500},
            {'name': 'Пенал Lux подвесной с корзиной', 'section': 'Мебель для ванной', 'brand': 'Lamis', 'category': 'Пеналы', 'collection': 'Lux', 'price': 18900},
            {'name': 'Зеркало Premium 100 с LED подсветкой', 'section': 'Зеркала', 'brand': 'Lamis', 'category': 'Зеркала с подсветкой', 'collection': None, 'price': 15600},
            {'name': 'Шкаф зеркальный Modern 80 двухдверный', 'section': 'Зеркала', 'brand': 'Lamis', 'category': 'Зеркальные шкафы', 'collection': None, 'price': 22300},

            # Санфарфор - Caizer
            {'name': 'Раковина подвесная 60 см белая', 'section': 'Санфарфор', 'brand': 'Caizer', 'category': 'Раковины', 'collection': None, 'price': 8900},
            {'name': 'Унитаз подвесной с инсталляцией', 'section': 'Санфарфор', 'brand': 'Caizer', 'category': 'Унитазы', 'collection': None, 'price': 28500},
            {'name': 'Биде подвесное белое', 'section': 'Санфарфор', 'brand': 'Caizer', 'category': 'Биде', 'collection': None, 'price': 12400},
            {'name': 'Раковина накладная круглая 42 см', 'section': 'Санфарфор', 'brand': 'Caizer', 'category': 'Раковины', 'collection': None, 'price': 6700},
            {'name': 'Унитаз напольный компакт с микролифтом', 'section': 'Санфарфор', 'brand': 'Caizer', 'category': 'Унитазы', 'collection': None, 'price': 19900},

            # Смесители - Lamis
            {'name': 'Смеситель для раковины однорычажный хром', 'section': 'Смесители', 'brand': 'Lamis', 'category': 'Смесители для раковины', 'collection': None, 'price': 4590},
            {'name': 'Смеситель для ванны с душем хром', 'section': 'Смесители', 'brand': 'Lamis', 'category': 'Смесители для ванны', 'collection': None, 'price': 5890},
            {'name': 'Смеситель для кухни с выдвижным изливом', 'section': 'Смесители', 'brand': 'Lamis', 'category': 'Смесители для кухни', 'collection': None, 'price': 7200},
            {'name': 'Смеситель термостатический для душа', 'section': 'Смесители', 'brand': 'Lamis', 'category': 'Смесители для душа', 'collection': None, 'price': 12800},

            # Душевые кабины - Caizer
            {'name': 'Душевой уголок 90x90 прозрачное стекло', 'section': 'Душевые кабины', 'brand': 'Caizer', 'category': 'Душевые уголки', 'collection': None, 'price': 24900},
            {'name': 'Душевая дверь распашная 80 см', 'section': 'Душевые кабины', 'brand': 'Caizer', 'category': 'Душевые двери', 'collection': None, 'price': 16500},
            {'name': 'Поддон акриловый 90x90 белый', 'section': 'Душевые кабины', 'brand': 'Caizer', 'category': 'Поддоны', 'collection': None, 'price': 8900},
            {'name': 'Душевой уголок 100x100 раздвижной', 'section': 'Душевые кабины', 'brand': 'Caizer', 'category': 'Душевые уголки', 'collection': None, 'price': 28700},

            # Водонагреватели - Blesk
            {'name': 'Водонагреватель накопительный 50л вертикальный', 'section': 'Водонагреватели', 'brand': 'Blesk', 'category': 'Накопительные', 'collection': None, 'price': 12900},
            {'name': 'Водонагреватель накопительный 80л', 'section': 'Водонагреватели', 'brand': 'Blesk', 'category': 'Накопительные', 'collection': None, 'price': 16500},
            {'name': 'Водонагреватель проточный 3.5 кВт', 'section': 'Водонагреватели', 'brand': 'Blesk', 'category': 'Проточные', 'collection': None, 'price': 5890},
            {'name': 'Бойлер косвенного нагрева 100л', 'section': 'Водонагреватели', 'brand': 'Blesk', 'category': 'Косвенного нагрева', 'collection': None, 'price': 28900},
            {'name': 'Водонагреватель накопительный 100л горизонтальный', 'section': 'Водонагреватели', 'brand': 'Blesk', 'category': 'Накопительные', 'collection': None, 'price': 18900},

            # Дополнительные товары
            {'name': 'Тумба Akcent 50 с раковиной венге', 'section': 'Мебель для ванной', 'brand': 'Lamis', 'category': 'Тумбы', 'collection': 'Akcent', 'price': 21900},
            {'name': 'Пенал Omega высокий двухдверный', 'section': 'Мебель для ванной', 'brand': 'Lamis', 'category': 'Пеналы', 'collection': 'Omega', 'price': 16700},
            {'name': 'Зеркало Deluxe 120 с подсветкой и подогревом', 'section': 'Зеркала', 'brand': 'Lamis', 'category': 'Зеркала с подсветкой', 'collection': None, 'price': 24500},
            {'name': 'Раковина двойная 120 см керамика', 'section': 'Санфарфор', 'brand': 'Caizer', 'category': 'Раковины', 'collection': None, 'price': 18900},
            {'name': 'Душевая кабина 120x80 с поддоном', 'section': 'Душевые кабины', 'brand': 'Caizer', 'category': 'Душевые кабины', 'collection': None, 'price': 45900},
            {'name': 'Водонагреватель проточный 5.5 кВт с душем', 'section': 'Водонагреватели', 'brand': 'Blesk', 'category': 'Проточные', 'collection': None, 'price': 7890},
            {'name': 'Тумба Palermo 70 напольная с ящиками', 'section': 'Мебель для ванной', 'brand': 'Lamis', 'category': 'Тумбы', 'collection': 'Palermo', 'price': 28900},
        ]

        products = []
        colors_options = [
            [{'name': 'Белый', 'hex': '#FFFFFF'}],
            [{'name': 'Хром', 'hex': '#C0C0C0'}],
            [{'name': 'Венге', 'hex': '#4A4A4A'}],
            [{'name': 'Белый глянец', 'hex': '#FAFAFA'}],
        ]

        for idx, product_data in enumerate(products_data):
            section = sections[product_data['section']]
            brand = brands[product_data['brand']]

            # Find matching category
            category = Category.objects.filter(
                name=product_data['category'],
                section=section,
                brand=brand
            ).first()

            if not category:
                self.stdout.write(self.style.WARNING(f'  ⚠ Category not found: {product_data["category"]} for {brand.name}'))
                continue

            # Find collection if specified
            collection = None
            collection_name = None
            if product_data.get('collection'):
                collection = Collection.objects.filter(
                    name=product_data['collection'],
                    brand=brand,
                    category__section=section
                ).first()
                collection_name = product_data['collection'] if collection else None

            # Get appropriate images based on product name/collection
            main_image, hover_image, additional_images = self.get_images_for_product(
                product_data['name'],
                collection_name,
                brand.name
            )

            # Random colors
            colors = random.choice(colors_options)

            # Random flags
            is_new = random.random() < 0.3  # 30% chance
            is_on_sale = random.random() < 0.2  # 20% chance

            product, created = Product.objects.update_or_create(
                name=product_data['name'],
                section=section,
                brand=brand,
                defaults={
                    'category': category,
                    'collection': collection,
                    'price': Decimal(str(product_data['price'])),
                    'main_image_url': main_image,
                    'hover_image_url': hover_image,
                    'images': additional_images,
                    'colors': colors,
                    'is_new': is_new,
                    'is_on_sale': is_on_sale,
                    'description': f'{product_data["name"]} от производителя {brand.name}. Высокое качество и надежность.'
                }
            )
            products.append(product)
            status = '✓ Создан' if created else '↻ Обновлён'
            flags = []
            if is_new:
                flags.append('🆕')
            if is_on_sale:
                flags.append('🔥')
            flags_str = ' '.join(flags) if flags else ''
            self.stdout.write(f'  {status}: {product.name} {flags_str}')

        return products
