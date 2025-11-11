"""
Seed script to populate database with test data for products and categories
"""

import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import AsyncSessionLocal
from app.models.category import Category
from app.models.product import Product


async def seed_database():
    """Seed the database with sample categories and products"""
    async with AsyncSessionLocal() as db:
        try:
            # Create categories
            categories_data = [
                {
                    "name": "Смесители для ванной",
                    "slug": "smesiteli-dlya-vannoy",
                    "description": "Высококачественные смесители для ванной комнаты",
                },
                {
                    "name": "Душевые системы",
                    "slug": "dushevye-sistemy",
                    "description": "Современные душевые системы и гарнитуры",
                },
                {
                    "name": "Раковины",
                    "slug": "rakoviny",
                    "description": "Раковины различных форм и размеров",
                },
                {
                    "name": "Аксессуары для ванной",
                    "slug": "aksessuary-dlya-vannoy",
                    "description": "Держатели, полки и другие аксессуары",
                },
            ]

            categories = []
            for cat_data in categories_data:
                category = Category(**cat_data)
                db.add(category)
                categories.append(category)

            await db.commit()

            # Refresh to get IDs
            for cat in categories:
                await db.refresh(cat)

            # Create products
            products_data = [
                {
                    "name": "Смеситель для ванной GROHE Eurosmart",
                    "price": 12500.00,
                    "is_new": True,
                    "main_image_url": "https://example.com/images/grohe-eurosmart.jpg",
                    "category_id": categories[0].id,
                    "description": "Современный однорычажный смеситель с хромированным покрытием",
                },
                {
                    "name": "Смеситель Hansgrohe Logis",
                    "price": 15800.00,
                    "is_new": False,
                    "main_image_url": "https://example.com/images/hansgrohe-logis.jpg",
                    "category_id": categories[0].id,
                    "description": "Немецкое качество и минималистичный дизайн",
                },
                {
                    "name": "Душевая система Raindance Select",
                    "price": 45000.00,
                    "is_new": True,
                    "main_image_url": "https://example.com/images/raindance-select.jpg",
                    "category_id": categories[1].id,
                    "description": "Душевая система с верхним душем и термостатом",
                },
                {
                    "name": "Душевая панель Hansgrohe Crometta",
                    "price": 28000.00,
                    "is_new": False,
                    "main_image_url": "https://example.com/images/crometta.jpg",
                    "category_id": categories[1].id,
                    "description": "Многофункциональная душевая панель",
                },
                {
                    "name": "Раковина накладная DURAVIT D-Code",
                    "price": 8500.00,
                    "is_new": False,
                    "main_image_url": "https://example.com/images/duravit-dcode.jpg",
                    "category_id": categories[2].id,
                    "description": "Керамическая раковина белого цвета",
                },
                {
                    "name": "Раковина подвесная Villeroy & Boch",
                    "price": 18500.00,
                    "is_new": True,
                    "main_image_url": "https://example.com/images/villeroy-boch.jpg",
                    "category_id": categories[2].id,
                    "description": "Элегантная подвесная раковина премиум класса",
                },
                {
                    "name": "Держатель для полотенец GROHE Essentials",
                    "price": 3200.00,
                    "is_new": False,
                    "main_image_url": "https://example.com/images/grohe-essentials.jpg",
                    "category_id": categories[3].id,
                    "description": "Хромированный держатель для полотенец",
                },
                {
                    "name": "Полка для ванной стеклянная",
                    "price": 4500.00,
                    "is_new": True,
                    "main_image_url": "https://example.com/images/glass-shelf.jpg",
                    "category_id": categories[3].id,
                    "description": "Стеклянная полка с хромированными креплениями",
                },
                {
                    "name": "Смеситель GROHE BauEdge",
                    "price": 9800.00,
                    "is_new": False,
                    "main_image_url": "https://example.com/images/grohe-bauedge.jpg",
                    "category_id": categories[0].id,
                    "description": "Надежный смеситель для ванной в современном стиле",
                },
                {
                    "name": "Душевой гарнитур Hansgrohe Croma",
                    "price": 12500.00,
                    "is_new": True,
                    "main_image_url": "https://example.com/images/croma.jpg",
                    "category_id": categories[1].id,
                    "description": "Компактный душевой гарнитур с 3 режимами струи",
                },
                {
                    "name": "Раковина встраиваемая Ideal Standard",
                    "price": 11200.00,
                    "is_new": False,
                    "main_image_url": "https://example.com/images/ideal-standard.jpg",
                    "category_id": categories[2].id,
                    "description": "Встраиваемая раковина овальной формы",
                },
                {
                    "name": "Дозатор для мыла GROHE",
                    "price": 2800.00,
                    "is_new": False,
                    "main_image_url": "https://example.com/images/soap-dispenser.jpg",
                    "category_id": categories[3].id,
                    "description": "Настенный дозатор для жидкого мыла",
                },
                {
                    "name": "Смеситель для раковины Kludi",
                    "price": 14500.00,
                    "is_new": True,
                    "main_image_url": "https://example.com/images/kludi.jpg",
                    "category_id": categories[0].id,
                    "description": "Высокий смеситель с поворотным изливом",
                },
                {
                    "name": "Душевая стойка Grohe Tempesta",
                    "price": 8900.00,
                    "is_new": False,
                    "main_image_url": "https://example.com/images/tempesta.jpg",
                    "category_id": categories[1].id,
                    "description": "Душевая стойка с регулируемой высотой",
                },
                {
                    "name": "Раковина угловая компактная",
                    "price": 6500.00,
                    "is_new": True,
                    "main_image_url": "https://example.com/images/corner-sink.jpg",
                    "category_id": categories[2].id,
                    "description": "Угловая раковина для небольших ванных комнат",
                },
                {
                    "name": "Зеркало с подсветкой LED",
                    "price": 15600.00,
                    "is_new": True,
                    "main_image_url": "https://example.com/images/led-mirror.jpg",
                    "category_id": categories[3].id,
                    "description": "Зеркало с LED подсветкой и сенсорным выключателем",
                },
                {
                    "name": "Смеситель для биде Hansgrohe",
                    "price": 11200.00,
                    "is_new": False,
                    "main_image_url": "https://example.com/images/bidet-mixer.jpg",
                    "category_id": categories[0].id,
                    "description": "Однорычажный смеситель для биде",
                },
                {
                    "name": "Душевая кабина Ravak",
                    "price": 67000.00,
                    "is_new": True,
                    "main_image_url": "https://example.com/images/ravak-cabin.jpg",
                    "category_id": categories[1].id,
                    "description": "Угловая душевая кабина 90x90 см",
                },
                {
                    "name": "Раковина двойная Roca",
                    "price": 32000.00,
                    "is_new": False,
                    "main_image_url": "https://example.com/images/double-sink.jpg",
                    "category_id": categories[2].id,
                    "description": "Двойная керамическая раковина для просторных ванных",
                },
                {
                    "name": "Крючок для халата двойной",
                    "price": 1800.00,
                    "is_new": False,
                    "main_image_url": "https://example.com/images/robe-hook.jpg",
                    "category_id": categories[3].id,
                    "description": "Хромированный двойной крючок",
                },
                {
                    "name": "Смеситель Grohe Eurocube",
                    "price": 19500.00,
                    "is_new": True,
                    "main_image_url": "https://example.com/images/eurocube.jpg",
                    "category_id": categories[0].id,
                    "description": "Дизайнерский смеситель с кубической формой",
                },
                {
                    "name": "Тропический душ потолочный",
                    "price": 38000.00,
                    "is_new": True,
                    "main_image_url": "https://example.com/images/rain-shower.jpg",
                    "category_id": categories[1].id,
                    "description": "Потолочный тропический душ 40x40 см",
                },
                {
                    "name": "Раковина чаша накладная",
                    "price": 14500.00,
                    "is_new": False,
                    "main_image_url": "https://example.com/images/vessel-sink.jpg",
                    "category_id": categories[2].id,
                    "description": "Дизайнерская накладная раковина-чаша",
                },
                {
                    "name": "Корзина для белья плетеная",
                    "price": 5600.00,
                    "is_new": False,
                    "main_image_url": "https://example.com/images/laundry-basket.jpg",
                    "category_id": categories[3].id,
                    "description": "Плетеная корзина для белья с крышкой",
                },
                {
                    "name": "Смеситель скрытого монтажа Kludi",
                    "price": 24000.00,
                    "is_new": True,
                    "main_image_url": "https://example.com/images/concealed-mixer.jpg",
                    "category_id": categories[0].id,
                    "description": "Встраиваемый смеситель с термостатом",
                },
                {
                    "name": "Душевой шланг усиленный 2м",
                    "price": 2400.00,
                    "is_new": False,
                    "main_image_url": "https://example.com/images/shower-hose.jpg",
                    "category_id": categories[1].id,
                    "description": "Усиленный душевой шланг с защитой от перекручивания",
                },
                {
                    "name": "Раковина мини 35см",
                    "price": 4200.00,
                    "is_new": False,
                    "main_image_url": "https://example.com/images/mini-sink.jpg",
                    "category_id": categories[2].id,
                    "description": "Компактная раковина для гостевых санузлов",
                },
                {
                    "name": "Щетка для унитаза напольная",
                    "price": 1200.00,
                    "is_new": False,
                    "main_image_url": "https://example.com/images/toilet-brush.jpg",
                    "category_id": categories[3].id,
                    "description": "Напольная щетка для унитаза в хромированном корпусе",
                },
                {
                    "name": "Смеситель для кухни с выдвижным изливом",
                    "price": 17800.00,
                    "is_new": True,
                    "main_image_url": "https://example.com/images/kitchen-mixer.jpg",
                    "category_id": categories[0].id,
                    "description": "Кухонный смеситель с выдвижной лейкой",
                },
                {
                    "name": "Душевая лейка 5 режимов",
                    "price": 3800.00,
                    "is_new": True,
                    "main_image_url": "https://example.com/images/shower-head.jpg",
                    "category_id": categories[1].id,
                    "description": "Ручная душевая лейка с 5 режимами струи",
                },
            ]

            for prod_data in products_data:
                product = Product(**prod_data)
                db.add(product)

            await db.commit()

            print("✅ Database seeded successfully!")
            print(f"Created {len(categories)} categories")
            print(f"Created {len(products_data)} products")

        except Exception as e:
            await db.rollback()
            print(f"❌ Error seeding database: {e}")
            raise


if __name__ == "__main__":
    asyncio.run(seed_database())
