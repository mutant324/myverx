"""
настройки джанги для myverx
ВАЖНО: у нас база через sqlalchemy, поэтому джанговский ORM не используется
и в INSTALLED_APPS нет auth/admin/sessions. свои юзеры в shop/models.py
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# на рендере ключ прилетает из переменной окружения, локально — дефолтный
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-myverx-dev-key-pomenyat-na-prod')

# на рендере выключаем, локально работает и так
DEBUG = os.environ.get('DEBUG', 'True') == 'True'

# рендер ходит с домена *.onrender.com
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '.onrender.com']
CSRF_TRUSTED_ORIGINS = ['https://*.onrender.com']

INSTALLED_APPS = [
    'django.contrib.staticfiles',
    'shop',
]

MIDDLEWARE = [
    'whitenoise.middleware.WhiteNoiseMiddleware',  # раздает статику в продакшене
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'shop.middleware.TempProfileMiddleware',  # наш мидлварь с гостевым профилем по кукам
]

ROOT_URLCONF = 'myverx.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        # app_dirs нельзя совмещать с loaders, app-шаблоны ищет app_directories.Loader
        'APP_DIRS': False,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'shop.context_processors.header',  # баланс и корзина для шапки
            ],
            # кэш шаблонов отключаем явно: без этого правки шаблонов
            # подхватываются только после перезапуска сервера
            'loaders': [
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',
            ],
        },
    },
]

WSGI_APPLICATION = 'myverx.wsgi.application'

# джанговские базы не юзаем вообще, у нас алхимия (см. shop/database.py)
DATABASES = {}

AUTH_PASSWORD_VALIDATORS = []

LANGUAGE_CODE = 'en'

TIME_ZONE = 'Europe/Moscow'

USE_I18N = True

USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'  # сюда collectstatic складывает статику для рендера
