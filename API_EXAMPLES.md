# API Examples - Product Catalog

Этот документ содержит примеры использования API для продуктового каталога.

## Запуск сервера

```bash
source venv/bin/activate
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

## Endpoints

### 1. Получить все продукты (без параметров)

```bash
curl "http://127.0.0.1:8000/products"
```

### 2. Фильтрация по категории

Получить только товары из категории "Смесители для ванной" (category_id=1):

```bash
curl "http://127.0.0.1:8000/products?category_id=1"
```

### 3. Сортировка по цене (возрастание)

```bash
curl "http://127.0.0.1:8000/products?sort_by=price_asc"
```

### 4. Сортировка по цене (убывание)

```bash
curl "http://127.0.0.1:8000/products?sort_by=price_desc"
```

### 5. Сортировка по новизне

Показать самые новые товары первыми:

```bash
curl "http://127.0.0.1:8000/products?sort_by=newest"
```

### 6. Пагинация

Получить вторую страницу с 12 товарами на странице:

```bash
curl "http://127.0.0.1:8000/products?page=2&limit=12"
```

### 7. Комбинированный запрос (все параметры)

Фильтрация по категории "Смесители для ванной", сортировка по возрастанию цены, вторая страница, 12 товаров:

```bash
curl "http://127.0.0.1:8000/products?category_id=1&sort_by=price_asc&page=2&limit=12"
```

### 8. Получить конкретный продукт по ID

```bash
curl "http://127.0.0.1:8000/products/1"
```

### 9. Получить все категории

```bash
curl "http://127.0.0.1:8000/categories"
```

### 10. Получить конкретную категорию по ID

```bash
curl "http://127.0.0.1:8000/categories/1"
```

## Параметры запроса для GET /products

| Параметр | Тип | Описание | Значение по умолчанию |
|----------|-----|----------|----------------------|
| `category_id` | integer | Фильтр по ID категории | None (все категории) |
| `sort_by` | string | Сортировка: `price_asc`, `price_desc`, `newest` | None (по ID) |
| `page` | integer | Номер страницы (начинается с 1) | 1 |
| `limit` | integer | Количество товаров на странице (1-100) | 12 |

## Формат ответа

### ProductPublic Schema

```json
{
  "id": 1,
  "name": "Смеситель для ванной GROHE Eurosmart",
  "price": "12500.00",
  "is_new": true,
  "main_image_url": "https://example.com/images/grohe-eurosmart.jpg",
  "category_id": 1,
  "category_name": "Смесители для ванной",
  "description": "Современный однорычажный смеситель с хромированным покрытием",
  "created_at": "2025-11-04T21:30:57.245258Z",
  "updated_at": null
}
```

### CategoryPublic Schema

```json
{
  "id": 1,
  "name": "Смесители для ванной",
  "slug": "smesiteli-dlya-vannoy",
  "description": "Высококачественные смесители для ванной комнаты",
  "created_at": "2025-11-04T21:30:57.236874Z",
  "updated_at": null
}
```

## Swagger Documentation

После запуска сервера, документация API доступна по адресу:

- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

## Примечания

- Все запросы возвращают JSON
- Использован eager loading (`joinedload`) для предотвращения N+1 проблемы
- Цены хранятся как `Decimal(10, 2)` для точности
- Все временные метки в UTC с timezone
