"""
Django Management Command для заполнения базы данных тестовыми данными
Использование: python manage.py seed_data
"""

from django.core.management.base import BaseCommand
from decimal import Decimal
from apps.products.models import Section, Brand, Category, Collection, Type, Product


class Command(BaseCommand):
    help = 'Загрузка тестовых данных для всех 6 секций'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🚀 Начинаем загрузку тестовых данных...\n'))

        # Base URL для изображений
        BASE_IMAGE_URL = 'https://pub-abbe62b0e52d438ea38505b6a2c733d7.r2.dev/images/catalog/'

        # ========== ЭТАП 1: СОЗДАНИЕ BRANDS ==========
        self.stdout.write(self.style.WARNING('📦 ЭТАП 1: Создание брендов...'))

        lamis, _ = Brand.objects.get_or_create(
            slug='lamis',
            defaults={
                'name': 'Lamis',
                'description': 'Мебель и сантехника премиум класса'
            }
        )

        caizer, _ = Brand.objects.get_or_create(
            slug='caizer',
            defaults={
                'name': 'Caizer',
                'description': 'Сантехника и керамика'
            }
        )

        blesk, _ = Brand.objects.get_or_create(
            slug='blesk',
            defaults={
                'name': 'Blesk',
                'description': 'Водонагреватели и системы'
            }
        )

        self.stdout.write(self.style.SUCCESS(f'✅ Создано 3 бренда: {lamis.name}, {caizer.name}, {blesk.name}\n'))

        # Получаем все секции
        section_1 = Section.objects.get(id=1)  # Мебель для ванной
        section_2 = Section.objects.get(id=2)  # Санфарфор
        section_3 = Section.objects.get(id=3)  # Смесители
        section_4 = Section.objects.get(id=4)  # Инсталяции
        section_5 = Section.objects.get(id=5)  # Водонагреватели
        section_6 = Section.objects.get(id=6)  # Дизайнерские и умные зеркала

        # ========== ЭТАП 2: SECTION 1 - МЕБЕЛЬ ДЛЯ ВАННОЙ ==========
        self.stdout.write(self.style.WARNING('🛁 ЭТАП 2: Section 1 - Мебель для ванной (Lamis)...'))

        # Categories
        cat_vanny, _ = Category.objects.get_or_create(
            slug='vanny',
            section=section_1,
            brand=lamis,
            defaults={
                'name': 'Ванны',
                'description': 'Ванны для ванной комнаты'
            }
        )

        cat_zerkala, _ = Category.objects.get_or_create(
            slug='zerkala',
            section=section_1,
            brand=lamis,
            defaults={
                'name': 'Зеркала',
                'description': 'Зеркала для ванной'
            }
        )

        cat_umyvalki, _ = Category.objects.get_or_create(
            slug='umyvalkii',
            section=section_1,
            brand=lamis,
            defaults={
                'name': 'Умывалки',
                'description': 'Раковины и умывальники'
            }
        )

        # Types для Ванны
        type_vstraivaemye_vanny, _ = Type.objects.get_or_create(
            slug='vstraivaemye',
            category=cat_vanny,
            defaults={'name': 'Встраиваемые'}
        )

        type_podvesnye_vanny, _ = Type.objects.get_or_create(
            slug='podvesnye',
            category=cat_vanny,
            defaults={'name': 'Подвесные'}
        )

        type_napolnye_vanny, _ = Type.objects.get_or_create(
            slug='napolnye',
            category=cat_vanny,
            defaults={'name': 'Напольные'}
        )

        # Types для Зеркала
        type_s_podsvetkoj, _ = Type.objects.get_or_create(
            slug='s-podsvetkoj',
            category=cat_zerkala,
            defaults={'name': 'С подсветкой'}
        )

        type_bez_podsvetki, _ = Type.objects.get_or_create(
            slug='bez-podsvetki',
            category=cat_zerkala,
            defaults={'name': 'Без подсветки'}
        )

        # Types для Умывалки
        type_vstraivaemye_umyvalki, _ = Type.objects.get_or_create(
            slug='vstraivaemye-umyvalki',
            category=cat_umyvalki,
            defaults={'name': 'Встраиваемые'}
        )

        type_nakladnye, _ = Type.objects.get_or_create(
            slug='nakladnye',
            category=cat_umyvalki,
            defaults={'name': 'Накладные'}
        )

        # Collections для Ванны
        col_akcent, _ = Collection.objects.get_or_create(
            slug='akcent',
            brand=lamis,
            category=cat_vanny,
            defaults={
                'name': 'Akcent',
                'description': 'Коллекция Akcent - классический дизайн'
            }
        )

        col_omega, _ = Collection.objects.get_or_create(
            slug='omega',
            brand=lamis,
            category=cat_vanny,
            defaults={
                'name': 'Omega',
                'description': 'Коллекция Omega - современный стиль'
            }
        )

        col_sanremo, _ = Collection.objects.get_or_create(
            slug='sanremo',
            brand=lamis,
            category=cat_vanny,
            defaults={
                'name': 'Sanremo',
                'description': 'Коллекция Sanremo - премиум качество'
            }
        )

        self.stdout.write(self.style.SUCCESS('✅ Созданы категории, типы и коллекции для Мебели'))

        # Products для ВАННЫ + Akcent
        Product.objects.get_or_create(
            slug='vanna-akcent-vstraivaemaya-150',
            defaults={
                'name': 'Ванна Akcent встраиваемая 150см',
                'section': section_1,
                'brand': lamis,
                'category': cat_vanny,
                'collection': col_akcent,
                'type': type_vstraivaemye_vanny,
                'price': Decimal('45000'),
                'main_image_url': f'{BASE_IMAGE_URL}lamis-akcent-1-main.webp',
                'hover_image_url': f'{BASE_IMAGE_URL}lamis-akcent-1-render.webp',
                'description': 'Встраиваемая ванна из коллекции Akcent'
            }
        )

        Product.objects.get_or_create(
            slug='vanna-akcent-podvesnaya-140',
            defaults={
                'name': 'Ванна Akcent подвесная 140см',
                'section': section_1,
                'brand': lamis,
                'category': cat_vanny,
                'collection': col_akcent,
                'type': type_podvesnye_vanny,
                'price': Decimal('52000'),
                'main_image_url': f'{BASE_IMAGE_URL}lamis-akcent-2-main.webp',
                'hover_image_url': f'{BASE_IMAGE_URL}lamis-akcent-2-render.webp',
                'description': 'Подвесная ванна Akcent'
            }
        )

        Product.objects.get_or_create(
            slug='vanna-akcent-napolnaya-160',
            defaults={
                'name': 'Ванна Akcent напольная 160см',
                'section': section_1,
                'brand': lamis,
                'category': cat_vanny,
                'collection': col_akcent,
                'type': type_napolnye_vanny,
                'price': Decimal('38000'),
                'main_image_url': f'{BASE_IMAGE_URL}lamis-akcent-3-main.webp',
                'description': 'Напольная ванна классического дизайна'
            }
        )

        # Products для ВАННЫ + Omega
        Product.objects.get_or_create(
            slug='vanna-omega-vstraivaemaya-150',
            defaults={
                'name': 'Ванна Omega встраиваемая 150см',
                'section': section_1,
                'brand': lamis,
                'category': cat_vanny,
                'collection': col_omega,
                'type': type_vstraivaemye_vanny,
                'price': Decimal('48000'),
                'main_image_url': f'{BASE_IMAGE_URL}lamis-omega-1-main.webp',
                'description': 'Встраиваемая ванна Omega'
            }
        )

        Product.objects.get_or_create(
            slug='vanna-omega-podvesnaya-140',
            defaults={
                'name': 'Ванна Omega подвесная 140см',
                'section': section_1,
                'brand': lamis,
                'category': cat_vanny,
                'collection': col_omega,
                'type': type_podvesnye_vanny,
                'price': Decimal('55000'),
                'main_image_url': f'{BASE_IMAGE_URL}lamis-amsterdam-1-main.webp',
                'hover_image_url': f'{BASE_IMAGE_URL}lamis-amsterdam-1-render.webp',
                'description': 'Подвесная ванна серии Omega'
            }
        )

        Product.objects.get_or_create(
            slug='vanna-omega-napolnaya-160',
            defaults={
                'name': 'Ванна Omega напольная 160см',
                'section': section_1,
                'brand': lamis,
                'category': cat_vanny,
                'collection': col_omega,
                'type': type_napolnye_vanny,
                'price': Decimal('41000'),
                'main_image_url': f'{BASE_IMAGE_URL}lamis-andalusia-1-main.webp',
                'description': 'Напольная ванна современного дизайна'
            }
        )

        # Products для ВАННЫ + Sanremo
        Product.objects.get_or_create(
            slug='vanna-sanremo-vstraivaemaya-150',
            defaults={
                'name': 'Ванна Sanremo встраиваемая 150см',
                'section': section_1,
                'brand': lamis,
                'category': cat_vanny,
                'collection': col_sanremo,
                'type': type_vstraivaemye_vanny,
                'price': Decimal('50000'),
                'main_image_url': f'{BASE_IMAGE_URL}lamis-sanremo-1-main.webp',
                'description': 'Премиум ванна серии Sanremo'
            }
        )

        # Products для ЗЕРКАЛА (без коллекции)
        Product.objects.get_or_create(
            slug='zerkalo-led-80',
            defaults={
                'name': 'Зеркало с LED подсветкой 80см',
                'section': section_1,
                'brand': lamis,
                'category': cat_zerkala,
                'type': type_s_podsvetkoj,
                'price': Decimal('12000'),
                'main_image_url': f'{BASE_IMAGE_URL}lamis-led-1-main.webp',
                'hover_image_url': f'{BASE_IMAGE_URL}lamis-led-1-render.webp',
                'description': 'Зеркало с теплой LED подсветкой'
            }
        )

        Product.objects.get_or_create(
            slug='zerkalo-bez-80',
            defaults={
                'name': 'Зеркало без подсветки 80см',
                'section': section_1,
                'brand': lamis,
                'category': cat_zerkala,
                'type': type_bez_podsvetki,
                'price': Decimal('6000'),
                'main_image_url': f'{BASE_IMAGE_URL}lamis-nora-1-main.webp',
                'description': 'Простое зеркало классического дизайна'
            }
        )

        # Products для УМЫВАЛКИ (без коллекции)
        Product.objects.get_or_create(
            slug='umyvalka-vstraivaemaya-60',
            defaults={
                'name': 'Умывалка встраиваемая 60см',
                'section': section_1,
                'brand': lamis,
                'category': cat_umyvalki,
                'type': type_vstraivaemye_umyvalki,
                'price': Decimal('8500'),
                'main_image_url': f'{BASE_IMAGE_URL}lamis-compact-1-main.webp',
                'hover_image_url': f'{BASE_IMAGE_URL}lamis-compact-1-render.webp',
                'description': 'Встраиваемая керамическая раковина'
            }
        )

        Product.objects.get_or_create(
            slug='umyvalka-nakladnaya-50',
            defaults={
                'name': 'Умывалка накладная 50см',
                'section': section_1,
                'brand': lamis,
                'category': cat_umyvalki,
                'type': type_nakladnye,
                'price': Decimal('5500'),
                'main_image_url': f'{BASE_IMAGE_URL}lamis-compact-2-main.webp',
                'description': 'Накладная раковина на столешницу'
            }
        )

        self.stdout.write(self.style.SUCCESS('✅ Создано 11 товаров для Мебели для ванной\n'))

        # ========== ЭТАП 3: SECTION 2 - САНФАРФОР ==========
        self.stdout.write(self.style.WARNING('🚽 ЭТАП 3: Section 2 - Санфарфор (Caizer)...'))

        # Categories
        cat_unitazy, _ = Category.objects.get_or_create(
            slug='unitazy',
            section=section_2,
            brand=caizer,
            defaults={
                'name': 'Унитазы',
                'description': 'Унитазы и сиденья'
            }
        )

        cat_rakoviny, _ = Category.objects.get_or_create(
            slug='rakoviny',
            section=section_2,
            brand=caizer,
            defaults={
                'name': 'Раковины',
                'description': 'Раковины для ванной'
            }
        )

        cat_bide, _ = Category.objects.get_or_create(
            slug='bide',
            section=section_2,
            brand=caizer,
            defaults={
                'name': 'Биде',
                'description': 'Биде различных типов'
            }
        )

        # Types
        type_napolnye_unitazy, _ = Type.objects.get_or_create(
            slug='napolnye-unitazy',
            category=cat_unitazy,
            defaults={'name': 'Напольные'}
        )

        type_podvesnye_unitazy, _ = Type.objects.get_or_create(
            slug='podvesnye-unitazy',
            category=cat_unitazy,
            defaults={'name': 'Подвесные'}
        )

        type_vstraivaemye_rakoviny, _ = Type.objects.get_or_create(
            slug='vstraivaemye-rakoviny',
            category=cat_rakoviny,
            defaults={'name': 'Встраиваемые'}
        )

        type_nakladnye_rakoviny, _ = Type.objects.get_or_create(
            slug='nakladnye-rakoviny',
            category=cat_rakoviny,
            defaults={'name': 'Накладные'}
        )

        type_napolnye_bide, _ = Type.objects.get_or_create(
            slug='napolnye-bide',
            category=cat_bide,
            defaults={'name': 'Напольные'}
        )

        # Products (БЕЗ коллекций!)
        Product.objects.get_or_create(
            slug='unitaz-caizer-standard',
            defaults={
                'name': 'Унитаз напольный Caizer Standard',
                'section': section_2,
                'brand': caizer,
                'category': cat_unitazy,
                'type': type_napolnye_unitazy,
                'price': Decimal('15000'),
                'main_image_url': f'{BASE_IMAGE_URL}caizer-premium-1-main.webp',
                'hover_image_url': f'{BASE_IMAGE_URL}caizer-premium-1-render.webp',
                'description': 'Надежный напольный унитаз'
            }
        )

        Product.objects.get_or_create(
            slug='unitaz-caizer-premium-podvesnoj',
            defaults={
                'name': 'Унитаз подвесной Caizer Premium',
                'section': section_2,
                'brand': caizer,
                'category': cat_unitazy,
                'type': type_podvesnye_unitazy,
                'price': Decimal('22000'),
                'main_image_url': f'{BASE_IMAGE_URL}caizer-premium-2-main.webp',
                'hover_image_url': f'{BASE_IMAGE_URL}caizer-premium-2-render.webp',
                'description': 'Подвесной унитаз премиум серии'
            }
        )

        Product.objects.get_or_create(
            slug='rakoviny-caizer-vstraivaemaya',
            defaults={
                'name': 'Раковина встраиваемая Caizer',
                'section': section_2,
                'brand': caizer,
                'category': cat_rakoviny,
                'type': type_vstraivaemye_rakoviny,
                'price': Decimal('8000'),
                'main_image_url': f'{BASE_IMAGE_URL}caizer-premium-1-main.webp',
                'description': 'Встраиваемая раковина'
            }
        )

        Product.objects.get_or_create(
            slug='rakoviny-caizer-nakladnaya',
            defaults={
                'name': 'Раковина накладная Caizer',
                'section': section_2,
                'brand': caizer,
                'category': cat_rakoviny,
                'type': type_nakladnye_rakoviny,
                'price': Decimal('5500'),
                'main_image_url': f'{BASE_IMAGE_URL}caizer-premium-2-main.webp',
                'description': 'Накладная раковина на стол'
            }
        )

        Product.objects.get_or_create(
            slug='bide-caizer-napolnoe',
            defaults={
                'name': 'Биде напольное Caizer',
                'section': section_2,
                'brand': caizer,
                'category': cat_bide,
                'type': type_napolnye_bide,
                'price': Decimal('12000'),
                'main_image_url': f'{BASE_IMAGE_URL}caizer-premium-1-main.webp',
                'description': 'Керамическое биде'
            }
        )

        self.stdout.write(self.style.SUCCESS('✅ Создано 5 товаров для Санфарфора\n'))

        # ========== ЭТАП 4: SECTION 3 - СМЕСИТЕЛИ ==========
        self.stdout.write(self.style.WARNING('🚿 ЭТАП 4: Section 3 - Смесители (Blesk)...'))

        # Categories
        cat_smesiteli_vanna, _ = Category.objects.get_or_create(
            slug='dlya-vanny-smesiteli',
            section=section_3,
            brand=blesk,
            defaults={
                'name': 'Для ванны',
                'description': 'Смесители для ванны'
            }
        )

        cat_smesiteli_kuhnya, _ = Category.objects.get_or_create(
            slug='dlya-kuhni',
            section=section_3,
            brand=blesk,
            defaults={
                'name': 'Для кухни',
                'description': 'Смесители для кухни'
            }
        )

        # Types
        type_odnorychazhnye, _ = Type.objects.get_or_create(
            slug='odnorychazhnye-smesiteli',
            category=cat_smesiteli_vanna,
            defaults={'name': 'Однорычажные'}
        )

        type_dvuhventilnye, _ = Type.objects.get_or_create(
            slug='dvuhventilnye-smesiteli',
            category=cat_smesiteli_vanna,
            defaults={'name': 'Двухвентильные'}
        )

        # Products
        Product.objects.get_or_create(
            slug='smesitel-odnorychazhnyj-vanna',
            defaults={
                'name': 'Смеситель однорычажный для ванны',
                'section': section_3,
                'brand': blesk,
                'category': cat_smesiteli_vanna,
                'type': type_odnorychazhnye,
                'price': Decimal('3500'),
                'main_image_url': f'{BASE_IMAGE_URL}blesk-standard-1-main.webp',
                'hover_image_url': f'{BASE_IMAGE_URL}blesk-standard-1-render.webp',
                'description': 'Надежный однорычажный смеситель'
            }
        )

        Product.objects.get_or_create(
            slug='smesitel-dvuhventilnyj-vanna',
            defaults={
                'name': 'Смеситель двухвентильный для ванны',
                'section': section_3,
                'brand': blesk,
                'category': cat_smesiteli_vanna,
                'type': type_dvuhventilnye,
                'price': Decimal('2800'),
                'main_image_url': f'{BASE_IMAGE_URL}blesk-standard-1-main.webp',
                'description': 'Классический двухвентильный смеситель'
            }
        )

        Product.objects.get_or_create(
            slug='smesitel-odnorychazhnyj-kuhnya',
            defaults={
                'name': 'Смеситель однорычажный для кухни',
                'section': section_3,
                'brand': blesk,
                'category': cat_smesiteli_kuhnya,
                'type': type_odnorychazhnye,
                'price': Decimal('4200'),
                'main_image_url': f'{BASE_IMAGE_URL}blesk-standard-1-main.webp',
                'hover_image_url': f'{BASE_IMAGE_URL}blesk-standard-1-render.webp',
                'description': 'Смеситель для кухни с выдвижным шлангом'
            }
        )

        self.stdout.write(self.style.SUCCESS('✅ Создано 3 товара для Смесителей\n'))

        # ========== ЭТАП 5: SECTION 4 - ИНСТАЛЯЦИИ ==========
        self.stdout.write(self.style.WARNING('🔧 ЭТАП 5: Section 4 - Инсталяции (Blesk)...'))

        # Categories
        cat_instalyacii, _ = Category.objects.get_or_create(
            slug='dlya-unitaza-instalyacii',
            section=section_4,
            brand=blesk,
            defaults={
                'name': 'Для унитаза',
                'description': 'Инсталляции для унитаза'
            }
        )

        # Types
        type_podvesnaya_inst, _ = Type.objects.get_or_create(
            slug='podvesnaya-instalyaciya',
            category=cat_instalyacii,
            defaults={'name': 'Подвесная'}
        )

        # Products
        Product.objects.get_or_create(
            slug='instalyaciya-unitaz-podvesnaya',
            defaults={
                'name': 'Инсталляция подвесная для унитаза',
                'section': section_4,
                'brand': blesk,
                'category': cat_instalyacii,
                'type': type_podvesnaya_inst,
                'price': Decimal('8500'),
                'main_image_url': f'{BASE_IMAGE_URL}blesk-standard-1-main.webp',
                'description': 'Встроенная инсталляция'
            }
        )

        self.stdout.write(self.style.SUCCESS('✅ Создан 1 товар для Инсталяций\n'))

        # ========== ЭТАП 6: SECTION 5 - ВОДОНАГРЕВАТЕЛИ ==========
        self.stdout.write(self.style.WARNING('🔥 ЭТАП 6: Section 5 - Водонагреватели (Blesk)...'))

        # Categories
        cat_vodonagrev, _ = Category.objects.get_or_create(
            slug='nakopitelnye',
            section=section_5,
            brand=blesk,
            defaults={
                'name': 'Накопительные',
                'description': 'Накопительные водонагреватели'
            }
        )

        # Types
        type_50l, _ = Type.objects.get_or_create(
            slug='50l',
            category=cat_vodonagrev,
            defaults={'name': '50л'}
        )

        type_100l, _ = Type.objects.get_or_create(
            slug='100l',
            category=cat_vodonagrev,
            defaults={'name': '100л'}
        )

        # Products
        Product.objects.get_or_create(
            slug='vodonagrevatel-50l-blesk',
            defaults={
                'name': 'Водонагреватель 50л Blesk',
                'section': section_5,
                'brand': blesk,
                'category': cat_vodonagrev,
                'type': type_50l,
                'price': Decimal('6500'),
                'main_image_url': f'{BASE_IMAGE_URL}blesk-standard-1-main.webp',
                'hover_image_url': f'{BASE_IMAGE_URL}blesk-standard-1-render.webp',
                'description': 'Экономичный водонагреватель'
            }
        )

        Product.objects.get_or_create(
            slug='vodonagrevatel-100l-blesk',
            defaults={
                'name': 'Водонагреватель 100л Blesk',
                'section': section_5,
                'brand': blesk,
                'category': cat_vodonagrev,
                'type': type_100l,
                'price': Decimal('9500'),
                'main_image_url': f'{BASE_IMAGE_URL}blesk-standard-1-main.webp',
                'description': 'Мощный водонагреватель'
            }
        )

        self.stdout.write(self.style.SUCCESS('✅ Создано 2 товара для Водонагревателей\n'))

        # ========== ЭТАП 7: SECTION 6 - ДИЗАЙНЕРСКИЕ И УМНЫЕ ЗЕРКАЛА ==========
        self.stdout.write(self.style.WARNING('💡 ЭТАП 7: Section 6 - Дизайнерские и умные зеркала (Lamis)...'))

        # Categories
        cat_zerkala_led, _ = Category.objects.get_or_create(
            slug='s-podsvetkoj-zerkala',
            section=section_6,
            brand=lamis,
            defaults={
                'name': 'С подсветкой',
                'description': 'Зеркала с LED подсветкой'
            }
        )

        cat_umnye_zerkala, _ = Category.objects.get_or_create(
            slug='umnye-zerkala',
            section=section_6,
            brand=lamis,
            defaults={
                'name': 'Умные зеркала',
                'description': 'Зеркала с сенсором и функциями'
            }
        )

        # Types
        type_led_teploe, _ = Type.objects.get_or_create(
            slug='led-teploe',
            category=cat_zerkala_led,
            defaults={'name': 'LED теплое'}
        )

        type_datchik, _ = Type.objects.get_or_create(
            slug='s-datchikom-dvizheniya',
            category=cat_umnye_zerkala,
            defaults={'name': 'С датчиком движения'}
        )

        # Products
        Product.objects.get_or_create(
            slug='zerkalo-led-100-dizajnerskoe',
            defaults={
                'name': 'Зеркало с LED подсветкой 100см',
                'section': section_6,
                'brand': lamis,
                'category': cat_zerkala_led,
                'type': type_led_teploe,
                'price': Decimal('18000'),
                'main_image_url': f'{BASE_IMAGE_URL}lamis-led-1-main.webp',
                'hover_image_url': f'{BASE_IMAGE_URL}lamis-led-1-render.webp',
                'description': 'Премиум зеркало с теплой подсветкой'
            }
        )

        Product.objects.get_or_create(
            slug='umnoe-zerkalo-datchik',
            defaults={
                'name': 'Умное зеркало с датчиком',
                'section': section_6,
                'brand': lamis,
                'category': cat_umnye_zerkala,
                'type': type_datchik,
                'price': Decimal('25000'),
                'main_image_url': f'{BASE_IMAGE_URL}lamis-led-2-main.webp',
                'description': 'Зеркало включается при приближении'
            }
        )

        self.stdout.write(self.style.SUCCESS('✅ Создано 2 товара для Дизайнерских зеркал\n'))

        # ========== ИТОГО ==========
        self.stdout.write(self.style.SUCCESS('\n' + '='*60))
        self.stdout.write(self.style.SUCCESS('🎉 ЗАГРУЗКА ЗАВЕРШЕНА!'))
        self.stdout.write(self.style.SUCCESS('='*60))

        total_brands = Brand.objects.count()
        total_categories = Category.objects.count()
        total_types = Type.objects.count()
        total_collections = Collection.objects.count()
        total_products = Product.objects.count()

        self.stdout.write(self.style.SUCCESS(f'\n📊 СТАТИСТИКА:'))
        self.stdout.write(self.style.SUCCESS(f'✅ Brands: {total_brands}'))
        self.stdout.write(self.style.SUCCESS(f'✅ Categories: {total_categories}'))
        self.stdout.write(self.style.SUCCESS(f'✅ Types: {total_types}'))
        self.stdout.write(self.style.SUCCESS(f'✅ Collections: {total_collections}'))
        self.stdout.write(self.style.SUCCESS(f'✅ Products: {total_products}'))

        self.stdout.write(self.style.SUCCESS(f'\n🔗 ПРОВЕРКА:'))
        self.stdout.write(self.style.SUCCESS(f'Admin: http://127.0.0.1:8000/admin/products/'))
        self.stdout.write(self.style.SUCCESS(f'API Brands: http://127.0.0.1:8000/api/v1/brands/'))
        self.stdout.write(self.style.SUCCESS(f'API Products: http://127.0.0.1:8000/api/v1/products/'))
