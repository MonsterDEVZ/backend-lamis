# 🏪 LAMIS Backend API

Production-ready Django + DRF backend для платформы электронной коммерции LAMIS с трёхуровневой фильтрацией, JWT аутентификацией и автоматическим логированием.

## 🚀 Технологии

- **Django 4.2** - Надёжный веб-фреймворк
- **Django REST Framework 3.14** - Мощный REST API toolkit
- **PostgreSQL** - Основная база данных
- **djangorestframework-simplejwt** - JWT аутентификация
- **python-slugify** - Транслитерация кириллических слагов
- **django-filter** - Расширенная фильтрация
- **drf-spectacular** - OpenAPI 3.0 документация

## ⭐ Ключевые возможности

- 📦 **Трёхуровневая фильтрация**: Brand → Category → Collection → Product
- 🔐 **JWT аутентификация** с access/refresh токенами
- 📝 **Автоматическое логирование** всех CRUD операций через Django signals
- 🌐 **Транслитерация** кириллицы в URL-friendly slugs
- 🛡️ **Permissions**: IsAdminOrReadOnly для безопасности
- 📊 **Pagination**: 20 items per page
- 📖 **OpenAPI/Swagger** документация

## 📋 Требования

- Python 3.11+
- PostgreSQL 15+
- pip

## ⚙️ Установка

### 1. Создайте виртуальное окружение

```bash
python -m venv venv
source venv/bin/activate  # На Windows: venv\Scripts\activate
```

### 2. Установите зависимости

```bash
pip install -r requirements_django.txt
```

### 3. Настройте базу данных PostgreSQL

Создайте базу данных:

```sql
CREATE DATABASE lamis_db;
CREATE USER lamis_user WITH PASSWORD 'lamis_password';
GRANT ALL PRIVILEGES ON DATABASE lamis_db TO lamis_user;
```

### 4. Настройте переменные окружения

Создайте файл `.env` в корне проекта:

```env
DB_NAME=lamis_db
DB_USER=lamis_user
DB_PASSWORD=lamis_password
DB_HOST=localhost
DB_PORT=5432
SECRET_KEY=your-django-secret-key-min-50-characters-long
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001
```

### 5. Запустите миграции

```bash
python manage.py migrate
```

### 6. Заполните базу данных тестовыми данными

```bash
python manage.py populate_brands
python manage.py populate_categories
python manage.py populate_collections
python manage.py create_sample_products
```

### 7. Создайте суперпользователя

```bash
python manage.py createsuperuser
```

## 🏃 Запуск

### Режим разработки

```bash
python manage.py runserver 0.0.0.0:8000
```

API будет доступен по адресу: `http://127.0.0.1:8000`

- **Django Admin**: `http://127.0.0.1:8000/admin/`
- **Swagger UI**: `http://127.0.0.1:8000/api/schema/swagger/`
- **ReDoc**: `http://127.0.0.1:8000/api/schema/redoc/`
- **API Root**: `http://127.0.0.1:8000/api/v1/`

### Режим production

```bash
gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 4
```

## 📚 API Endpoints

### 🔓 Public Endpoints (Read-Only)

**Brands**
- `GET /api/v1/brands/` - Список всех брендов
- `GET /api/v1/brands/{id}/` - Детали бренда
- `GET /api/v1/brands/{id}/categories/` - Категории бренда

**Categories**
- `GET /api/v1/categories/` - Список всех категорий
- `GET /api/v1/categories/{id}/` - Детали категории
- `GET /api/v1/categories/{id}/brands/` - Бренды категории

**Collections**
- `GET /api/v1/collections/` - Список всех коллекций
- `GET /api/v1/collections/{id}/` - Детали коллекции
- Фильтры: `?brand_id=1&category_id=2`

**Products**
- `GET /api/v1/products/` - Список всех товаров
- `GET /api/v1/products/{slug}/` - Детали товара
- Фильтры: `?brand_id=1&category_id=2&collection_id=3&is_new=true&is_on_sale=true&min_price=1000&max_price=50000`

### 🔐 Authentication

- `POST /api/v1/auth/register/` - Регистрация
- `POST /api/v1/auth/login/` - Вход (получение JWT токенов)
- `POST /api/v1/auth/logout/` - Выход (blacklist refresh token)
- `POST /api/v1/auth/refresh/` - Обновление access токена
- `GET /api/v1/auth/me/` - Данные текущего пользователя (защищено)

### 🛡️ Admin Endpoints (JWT Required + is_admin=True)

**CRUD Operations** (все защищены `IsAdminOrReadOnly`)
- `POST /api/v1/brands/` - Создать бренд
- `PUT /api/v1/brands/{id}/` - Обновить бренд
- `DELETE /api/v1/brands/{id}/` - Удалить бренд
- (аналогично для categories, collections, products)

**Audit Logs**
- `GET /api/v1/admin/logs/` - История всех изменений

**File Uploads**
- `POST /api/v1/admin/upload/` - Загрузка изображений

## 🗄️ Структура данных

```
Brand (Бренд)
  ├── Lamis
  ├── Caizer
  └── Blesk
      |
      └── Category (Категория) - Many-to-Many через BrandCategory
            ├── Мебель для ванн
            ├── Зеркала
            ├── Водонагреватели
            └── Сантехника
                |
                └── Collection (Коллекция)
                      ├── Solo
                      ├── Harmony
                      ├── Lux
                      └── ...
                          |
                          └── Product (Товар)
                                - name, slug, price
                                - images, colors
                                - is_new, is_on_sale
```

## 🗄️ Миграции базы данных

### Создать новую миграцию

```bash
python manage.py makemigrations
```

### Применить миграции

```bash
python manage.py migrate
```

### Откатить миграцию

```bash
python manage.py migrate app_name migration_name
```

## 🔒 Безопасность

- Пароли хэшируются с помощью Django `make_password`
- JWT токены: 1 час (access), 7 дней (refresh)
- Token blacklisting при logout
- CORS настроен только для фронтенда
- Все входящие данные валидируются DRF serializers
- Custom permissions: `IsAdminOrReadOnly`, `IsAdmin`
- Public endpoints - read-only, admin endpoints - protected

## 📁 Структура проекта

```
backend-lamis/
├── config/                          # Настройки Django проекта
│   ├── settings.py                  # Основные настройки
│   ├── urls.py                      # Главный URL router
│   └── wsgi.py / asgi.py
├── apps/
│   ├── authentication/              # JWT аутентификация
│   │   ├── models.py                # Custom User model
│   │   ├── serializers.py
│   │   ├── views.py                 # Login, Register, Logout, Refresh
│   │   └── urls.py
│   ├── products/                    # Основная логика товаров
│   │   ├── models.py                # Brand, Category, Collection, Product
│   │   ├── serializers.py           # DRF serializers
│   │   ├── views.py                 # ViewSets
│   │   ├── filters.py               # django-filter classes
│   │   ├── permissions.py           # Custom permissions
│   │   ├── signals.py               # Auto-logging via signals
│   │   ├── admin.py                 # Django Admin config
│   │   └── management/commands/     # Management commands
│   │       ├── populate_brands.py
│   │       ├── populate_categories.py
│   │       ├── populate_collections.py
│   │       └── create_sample_products.py
│   ├── logs/                        # Audit logging
│   │   ├── models.py                # AuditLog model
│   │   └── views.py
│   └── uploads/                     # File uploads
│       └── views.py
├── manage.py                        # Django CLI
├── requirements_django.txt          # Dependencies
└── README.md
```

## 🧪 Тестирование

```bash
pytest
```

## 📝 Примеры запросов

### Получить все бренды

```bash
curl http://127.0.0.1:8000/api/v1/brands/
```

### Фильтрация товаров (трёхуровневая)

```bash
# Все товары Lamis
curl http://127.0.0.1:8000/api/v1/products/?brand_id=1

# Мебель Lamis
curl http://127.0.0.1:8000/api/v1/products/?brand_id=1&category_id=1

# Мебель Lamis из коллекции Solo
curl http://127.0.0.1:8000/api/v1/products/?brand_id=1&category_id=1&collection_id=1

# Только новинки на акции
curl 'http://127.0.0.1:8000/api/v1/products/?is_new=true&is_on_sale=true'
```

### Вход (получение JWT токенов)

```bash
curl -X POST http://127.0.0.1:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

Ответ:
```json
{
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@lamis.kg",
    "is_admin": true
  },
  "access_token": "eyJhbGc...",
  "refresh_token": "eyJhbGc..."
}
```

### Обновление access token

```bash
curl -X POST http://127.0.0.1:8000/api/v1/auth/refresh/ \
  -H "Content-Type: application/json" \
  -d '{"refresh":"YOUR_REFRESH_TOKEN"}'
```

### Получить данные текущего пользователя (защищено)

```bash
curl http://127.0.0.1:8000/api/v1/auth/me/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Просмотр audit logs (только admin)

```bash
curl http://127.0.0.1:8000/api/v1/admin/logs/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Создать новый товар (только admin)

```bash
curl -X POST http://127.0.0.1:8000/api/v1/products/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Новый товар",
    "price": "25000.00",
    "brand": 1,
    "category": 1,
    "collection": 1,
    "main_image_url": "https://example.com/image.jpg",
    "description": "Описание товара"
  }'
```

## 🤝 Интеграция с Frontend

### Next.js 16 Integration

1. **Хранение токенов**: Используйте `localStorage` или `cookies`
   ```typescript
   localStorage.setItem('access_token', response.access_token);
   localStorage.setItem('refresh_token', response.refresh_token);
   ```

2. **API запросы с авторизацией**:
   ```typescript
   const response = await fetch('http://api.lamis.kg/api/v1/auth/me/', {
     headers: {
       'Authorization': `Bearer ${localStorage.getItem('access_token')}`
     }
   });
   ```

3. **Автоматическое обновление токена** при 401 ошибке:
   ```typescript
   if (response.status === 401) {
     // Refresh token
     const refreshResponse = await fetch('/api/v1/auth/refresh/', {
       method: 'POST',
       body: JSON.stringify({ refresh: localStorage.getItem('refresh_token') })
     });
     // Retry original request with new token
   }
   ```

4. **Трёхуровневая фильтрация**:
   - Шаг 1: Выбрать бренд → `GET /api/v1/brands/`
   - Шаг 2: Загрузить категории бренда → `GET /api/v1/brands/{id}/categories/`
   - Шаг 3: Загрузить коллекции → `GET /api/v1/collections/?brand_id={id}&category_id={id}`
   - Шаг 4: Показать товары → `GET /api/v1/products/?brand_id={id}&category_id={id}&collection_id={id}`

## 🧪 Management Commands

```bash
# Заполнить базу брендами
python manage.py populate_brands

# Заполнить категориями
python manage.py populate_categories

# Создать коллекции
python manage.py populate_collections

# Создать тестовые товары
python manage.py create_sample_products
```

## 📊 Audit Logging

Все CREATE, UPDATE, DELETE операции автоматически логируются через Django signals:

```python
# Каждый лог содержит:
{
  "timestamp": "2025-11-11T19:28:56+06:00",
  "user": 1,  # ID пользователя (null если система)
  "action": "CREATE",  # CREATE, UPDATE, DELETE
  "table_name": "products",
  "record_id": 10,
  "old_data": {...},  # Для UPDATE/DELETE
  "new_data": {...},  # Для CREATE/UPDATE
  "ip_address": "192.168.1.1"
}
```

Просмотр логов: `GET /api/v1/admin/logs/` (только для админов)

## 📄 Лицензия

Proprietary - LAMIS.KG
