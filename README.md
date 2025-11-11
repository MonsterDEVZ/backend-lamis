# LAMIS Backend API

Backend для платформы электронной коммерции LAMIS на FastAPI с PostgreSQL и JWT аутентификацией.

## 🚀 Технологии

- **FastAPI** - Современный веб-фреймворк
- **SQLAlchemy 2.0** - ORM с асинхронной поддержкой
- **PostgreSQL** - Основная база данных
- **Alembic** - Миграции базы данных
- **JWT** - Токены доступа и обновления
- **Bcrypt** - Хэширование паролей

## 📋 Требования

- Python 3.11+
- PostgreSQL 15+
- pip или poetry

## ⚙️ Установка

### 1. Создайте виртуальное окружение

```bash
python -m venv venv
source venv/bin/activate  # На Windows: venv\Scripts\activate
```

### 2. Установите зависимости

```bash
pip install -r requirements.txt
```

### 3. Настройте базу данных PostgreSQL

Создайте базу данных:

```sql
CREATE DATABASE lamis_db;
CREATE USER lamis_user WITH PASSWORD 'lamis_password';
GRANT ALL PRIVILEGES ON DATABASE lamis_db TO lamis_user;
```

### 4. Настройте переменные окружения

Обновите файл `.env` с вашими настройками:

```env
DATABASE_URL=postgresql+asyncpg://lamis_user:lamis_password@localhost:5432/lamis_db
SECRET_KEY=your-secret-key-min-32-characters-long
```

### 5. Запустите миграции

```bash
alembic upgrade head
```

## 🏃 Запуск

### Режим разработки

```bash
uvicorn app.main:app --reload
```

API будет доступен по адресу: `http://127.0.0.1:8000`

- Документация Swagger UI: `http://127.0.0.1:8000/docs`
- Документация ReDoc: `http://127.0.0.1:8000/redoc`

### Режим production

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## 📚 API Endpoints

### Authentication

- `POST /auth/register` - Регистрация нового пользователя
- `POST /auth/login` - Вход и получение JWT токенов
- `POST /auth/refresh` - Обновление access токена

### Users

- `GET /users/me` - Получить данные текущего пользователя (защищенный эндпоинт)

## 🗄️ Миграции базы данных

### Создать новую миграцию

```bash
alembic revision --autogenerate -m "описание изменений"
```

### Применить миграции

```bash
alembic upgrade head
```

### Откатить миграцию

```bash
alembic downgrade -1
```

## 🔒 Безопасность

- Пароли хэшируются с помощью bcrypt
- JWT токены с ограниченным временем жизни
- CORS настроен только для фронтенда
- Все входящие данные валидируются

## 📁 Структура проекта

```
backend-lamis/
├── app/
│   ├── api/
│   │   └── endpoints/
│   │       ├── auth.py      # Эндпоинты аутентификации
│   │       └── users.py     # Эндпоинты пользователей
│   ├── core/
│   │   ├── config.py        # Конфигурация приложения
│   │   ├── security.py      # JWT и хэширование
│   │   └── dependencies.py  # FastAPI dependencies
│   ├── db/
│   │   └── database.py      # Настройка БД
│   ├── models/
│   │   └── user.py          # Модель User
│   ├── schemas/
│   │   └── user.py          # Pydantic схемы
│   └── main.py              # FastAPI приложение
├── alembic/
│   └── versions/            # Миграции
├── .env                     # Переменные окружения
├── alembic.ini              # Конфигурация Alembic
├── requirements.txt         # Зависимости Python
└── README.md
```

## 🧪 Тестирование

```bash
pytest
```

## 📝 Примеры запросов

### Регистрация

```bash
curl -X POST "http://127.0.0.1:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"securepassword123"}'
```

### Вход

```bash
curl -X POST "http://127.0.0.1:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"securepassword123"}'
```

### Получить данные пользователя

```bash
curl -X GET "http://127.0.0.1:8000/users/me" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## 🤝 Интеграция с Frontend

Frontend должен:
1. Хранить access_token в localStorage/state
2. Включать токен в заголовок: `Authorization: Bearer {token}`
3. Обрабатывать 401 ошибки и обновлять токен через `/auth/refresh`

## 📄 Лицензия

Proprietary - LAMIS.KG
