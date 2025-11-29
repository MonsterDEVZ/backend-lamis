"""
Django settings for LAMIS E-commerce Backend
"""

from pathlib import Path
from datetime import timedelta
from decouple import config
import dj_database_url

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', default='django-insecure-change-me-in-production')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=True, cast=bool)

# ALLOWED_HOSTS configuration
# Railway automatically provides RAILWAY_PUBLIC_DOMAIN and RAILWAY_STATIC_URL
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='*').split(',')

# Auto-detect Railway domain
railway_domain = config('RAILWAY_PUBLIC_DOMAIN', default=None)
railway_static_url = config('RAILWAY_STATIC_URL', default=None)

# Add Railway domains automatically
if railway_domain and railway_domain not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append(railway_domain)

if railway_static_url:
    # Extract domain from URL like https://backend-lamis-production.up.railway.app
    import re
    match = re.search(r'https?://([^/]+)', railway_static_url)
    if match:
        domain = match.group(1)
        if domain not in ALLOWED_HOSTS:
            ALLOWED_HOSTS.append(domain)

# Always allow Railway's default domain pattern
if any('railway.app' in host for host in ALLOWED_HOSTS) is False:
    # Add common Railway domain pattern
    ALLOWED_HOSTS.append('backend-lamis-production.up.railway.app')

# Application definition

INSTALLED_APPS = [
    # Jazzmin должен быть ПЕРВЫМ перед django.contrib.admin
    "jazzmin",

    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Third party apps
    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "django_filters",
    "corsheaders",
    "drf_spectacular",
    "ckeditor",  # WYSIWYG редактор для админки

    # Local apps
    "apps.products",
    "apps.authentication",
    "apps.uploads",
    'apps.partners',
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # Serve static files
    "corsheaders.middleware.CorsMiddleware",  # CORS должен быть первым после Security
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / 'templates'],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# Database Configuration
# Railway provides DATABASE_URL automatically
DATABASE_URL = config('DATABASE_URL', default=None)

if DATABASE_URL:
    # Use Railway's DATABASE_URL (PostgreSQL)
    DATABASES = {
        "default": dj_database_url.parse(DATABASE_URL, conn_max_age=600)
    }
else:
    # Fallback for local development
    # Use PostgreSQL if DB_HOST is explicitly set, otherwise use SQLite
    db_host = config('DB_HOST', default=None)

    if db_host and db_host != 'localhost':
        # Use PostgreSQL with explicit configuration
        DATABASES = {
            "default": {
                "ENGINE": "django.db.backends.postgresql",
                "NAME": config('DB_NAME', default='lamis_db'),
                "USER": config('DB_USER', default='lamis_user'),
                "PASSWORD": config('DB_PASSWORD', default='lamis_password'),
                "HOST": db_host,
                "PORT": config('DB_PORT', default='5432'),
            }
        }
    else:
        # SQLite for local development and build phase
        DATABASES = {
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": BASE_DIR / "db.sqlite3",
            }
        }

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Custom User Model
AUTH_USER_MODEL = 'authentication.User'

# Internationalization
LANGUAGE_CODE = "ru-ru"
TIME_ZONE = "Asia/Bishkek"
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

# Only add STATICFILES_DIRS if the 'static' directory exists
import os
if os.path.exists(BASE_DIR / "static"):
    STATICFILES_DIRS = [BASE_DIR / "static"]

# WhiteNoise configuration
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# Media files (Uploaded images, etc.)
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# REST Framework configuration
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',  # По умолчанию открыто для GET
    ],
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_PAGINATION_CLASS': 'config.pagination.CustomPageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

# JWT Settings
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,

    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,

    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',

    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
}

# CORS Settings
CORS_ALLOWED_ORIGINS = config(
    'CORS_ALLOWED_ORIGINS',
    default='http://localhost:3000,http://localhost:3001',
    cast=lambda v: [s.strip() for s in v.split(',')]
)
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

# CSRF Settings
# Django 4.x requires explicit CSRF_TRUSTED_ORIGINS for https origins
CSRF_TRUSTED_ORIGINS = []

# Add HTTPS origins from ALLOWED_HOSTS
for host in ALLOWED_HOSTS:
    if host and host != '*':
        # Add both http and https versions
        if not host.startswith('http'):
            CSRF_TRUSTED_ORIGINS.append(f'https://{host}')
            # Also support http for local development
            if 'localhost' in host or '127.0.0.1' in host:
                CSRF_TRUSTED_ORIGINS.append(f'http://{host}')

# Add Railway domain explicitly
if 'backend-lamis-production.up.railway.app' not in CSRF_TRUSTED_ORIGINS:
    CSRF_TRUSTED_ORIGINS.append('https://backend-lamis-production.up.railway.app')

# Allow configuration via environment variable
csrf_origins_env = config('CSRF_TRUSTED_ORIGINS', default=None)
if csrf_origins_env:
    additional_origins = [s.strip() for s in csrf_origins_env.split(',')]
    CSRF_TRUSTED_ORIGINS.extend(additional_origins)

# DRF Spectacular Settings (Swagger/OpenAPI)
SPECTACULAR_SETTINGS = {
    'TITLE': 'LAMIS E-commerce API',
    'DESCRIPTION': 'Backend API for LAMIS E-commerce Platform with Brand → Category → Collection → Product filtering',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'COMPONENT_SPLIT_REQUEST': True,
}

# Logging
import os

# Determine if we should use file logging (only in local development)
USE_FILE_LOGGING = os.environ.get('RAILWAY_ENVIRONMENT') is None

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
        'apps': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}

# Add file handler only in local development
if USE_FILE_LOGGING:
    import os
    log_dir = BASE_DIR / 'logs'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    LOGGING['handlers']['file'] = {
        'class': 'logging.FileHandler',
        'filename': BASE_DIR / 'logs' / 'django.log',
        'formatter': 'verbose',
    }
    LOGGING['loggers']['django']['handlers'].append('file')
    LOGGING['loggers']['apps']['handlers'].append('file')


# ============================================================
# Django Jazzmin Configuration
# ============================================================
# Современная тема для Django Admin с Bootstrap 4
# Документация: https://django-jazzmin.readthedocs.io/

JAZZMIN_SETTINGS = {
    # Заголовок окна браузера
    "site_title": "LAMIS Admin",

    # Заголовок на странице входа
    "site_header": "LAMIS",

    # Заголовок бренда в сайдбаре
    "site_brand": "LAMIS",

    # Логотип (путь к статике)
    # "site_logo": "images/logo.png",

    # Логотип для страницы логина (будет уменьшен до 32x32)
    # "login_logo": "images/logo.png",

    # CSS-классы для логотипа
    "site_logo_classes": "img-circle",

    # Иконка сайта (favicon)
    # "site_icon": "images/favicon.ico",

    # Приветственный текст на странице входа
    "welcome_sign": "Добро пожаловать в панель администратора LAMIS",

    # Copyright в футере
    "copyright": "LAMIS E-commerce",

    # Поле пользователя для отображения рядом с аватаром
    "user_avatar": None,

    ############
    # Top Menu #
    ############
    # Ссылки в верхнем меню
    "topmenu_links": [
        # URL к главной странице сайта
        {"name": "Сайт", "url": "/", "new_window": True},

        # Внешняя ссылка
        # {"name": "Support", "url": "https://github.com/farridav/django-jazzmin/issues", "new_window": True},

        # Модель для отображения поиска
        {"model": "authentication.User"},
    ],

    #############
    # User Menu #
    #############
    # Дополнительные ссылки в меню пользователя
    "usermenu_links": [
        {"model": "authentication.User"},
    ],

    #############
    # Side Menu #
    #############
    # Показывать сайдбар
    "show_sidebar": True,

    # Автоматически разворачивать меню
    "navigation_expanded": True,

    # Скрывать эти приложения
    "hide_apps": [],

    # Скрывать эти модели
    "hide_models": ["products.MaterialCategory"],

    # Порядок приложений и моделей в сайдбаре
    "order_with_respect_to": [
        "products",
        "products.Section",
        "products.Brand",
        "products.Category",
        "products.Collection",
        "products.Type",
        "products.Product",
        "products.Color",
        "products.TutorialCategory",
        "products.TutorialVideo",
        "products.Material",
        "authentication",
        "authentication.User",
    ],

    # Иконки для приложений/моделей (Font Awesome 5)
    "icons": {
        "authentication": "fas fa-users-cog",
        "authentication.User": "fas fa-user",

        "products": "fas fa-shopping-cart",
        "products.Section": "fas fa-layer-group",
        "products.Brand": "fas fa-trademark",
        "products.Category": "fas fa-tags",
        "products.Collection": "fas fa-th-large",
        "products.Type": "fas fa-cubes",
        "products.Product": "fas fa-box",
        "products.Color": "fas fa-palette",
        "products.ProductImage": "fas fa-images",
        "products.TutorialCategory": "fas fa-graduation-cap",
        "products.TutorialVideo": "fas fa-video",
        "products.Material": "fas fa-file-download",

        "auth": "fas fa-users-cog",
        "auth.Group": "fas fa-users",
    },

    # Иконка по умолчанию
    "default_icon_parents": "fas fa-folder",
    "default_icon_children": "fas fa-circle",

    #################
    # Related Modal #
    #################
    # Использовать модальные окна вместо popup для связанных объектов
    "related_modal_active": False,

    #############
    # UI Tweaks #
    #############
    # Относительные даты (напр. "3 часа назад")
    "use_google_fonts_cdn": True,

    # Показать кнопку переключения UI настроек
    "show_ui_builder": False,

    ###############
    # Change view #
    ###############
    # Показывать атрибуты в табах
    "changeform_format": "horizontal_tabs",

    # Переопределить changeform_format для конкретных моделей
    "changeform_format_overrides": {
        "authentication.User": "collapsible",
        "products.Product": "horizontal_tabs",
    },

    # Язык для интерфейса
    "language_chooser": False,
}

# Настройки UI темы Jazzmin
JAZZMIN_UI_TWEAKS = {
    # Тема navbar (см. https://adminlte.io/docs/3.0/layout.html)
    "navbar": "navbar-white navbar-light",

    # Нет фиксированного navbar
    "navbar_fixed": False,

    # Классы для футера
    "footer_fixed": False,

    # Тема сайдбара
    "sidebar": "sidebar-light-success",

    # Фиксированный сайдбар
    "sidebar_fixed": True,

    # Сайдбар свернут по умолчанию
    "sidebar_nav_compact_style": False,

    # Мини-сайдбар по умолчанию
    "sidebar_disable_expand": False,

    # Наводить на элементы сайдбара
    "sidebar_nav_legacy_style": False,

    # Детский отступ в сайдбаре
    "sidebar_nav_child_indent": True,

    # Плоский стиль
    "sidebar_nav_flat_style": False,

    # Тема (доступные: cerulean, cosmo, cyborg, darkly, flatly, journal, litera, lumen, lux, materia, minty, pulse, sandstone, simplex, sketchy, slate, solar, spacelab, superhero, united, yeti)
    "theme": "flatly",

    # Темная тема для сайдбара (доступные: cyborg, darkly, slate, solar, superhero)
    "dark_mode_theme": None,

    # Кастомные CSS и JS
    "button_classes": {
        "primary": "btn-primary",
        "secondary": "btn-secondary",
        "info": "btn-info",
        "warning": "btn-warning",
        "danger": "btn-danger",
        "success": "btn-success",
    },

    # Акцентный цвет (primary, secondary, info, warning, danger, success)
    "accent": "accent-success",

    # Цвет текста navbar (primary, secondary, info, warning, danger, success, gray-dark, gray, white, light, dark)
    "navbar_small_text": False,
    "footer_small_text": False,
    "body_small_text": False,
    "brand_small_text": False,
    "brand_colour": "navbar-success",
    "no_navbar_border": False,
}
