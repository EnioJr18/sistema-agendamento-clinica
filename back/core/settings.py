import sys
from datetime import timedelta
from pathlib import Path

import dj_database_url  # type: ignore
from decouple import Csv, UndefinedValueError, config
from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parent.parent


def env_bool(name, default=False):
    try:
        return config(name, default=default, cast=bool)
    except ValueError as exc:
        raise ImproperlyConfigured(
            f'{name} deve ser um booleano valido: True/False, 1/0, yes/no.'
        ) from exc


ENVIRONMENT = config('ENVIRONMENT', default='development')
IS_PRODUCTION = ENVIRONMENT.lower() == 'production'

try:
    SECRET_KEY = config('SECRET_KEY')
except UndefinedValueError as exc:
    if IS_PRODUCTION:
        raise ImproperlyConfigured('SECRET_KEY e obrigatoria em producao.') from exc
    SECRET_KEY = 'dev-only-insecure-secret-key'
if IS_PRODUCTION and (len(SECRET_KEY) < 50 or SECRET_KEY.startswith('dev-only-')):
    raise ImproperlyConfigured('SECRET_KEY de producao deve ser forte e possuir ao menos 50 caracteres.')

DEBUG = env_bool('DEBUG', default=not IS_PRODUCTION)
if IS_PRODUCTION and DEBUG:
    raise ImproperlyConfigured('DEBUG=True nao e permitido em producao.')

try:
    ALLOWED_HOSTS = config(
        'ALLOWED_HOSTS',
        default=None if IS_PRODUCTION else 'localhost,127.0.0.1,0.0.0.0',
        cast=Csv(),
    )
except UndefinedValueError as exc:
    raise ImproperlyConfigured('ALLOWED_HOSTS e obrigatorio em producao.') from exc
if IS_PRODUCTION and (not ALLOWED_HOSTS or '*' in ALLOWED_HOSTS):
    raise ImproperlyConfigured('ALLOWED_HOSTS deve ser explicito em producao.')


INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'drf_spectacular',
    'corsheaders',
    'django_filters',
    'api',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'api.middleware.RequestLoggingMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'


DEFAULT_DATABASE_URL = f"sqlite:///{BASE_DIR / 'db.sqlite3'}"
try:
    DATABASE_URL = config('DATABASE_URL')
except UndefinedValueError as exc:
    if IS_PRODUCTION:
        raise ImproperlyConfigured('DATABASE_URL e obrigatoria em producao.') from exc
    DATABASE_URL = DEFAULT_DATABASE_URL

DATABASES = {
    'default': dj_database_url.parse(
        DATABASE_URL,
        conn_max_age=600,
        conn_health_checks=True,
    )
}


USE_SQLITE_FOR_TESTS = env_bool('USE_SQLITE_FOR_TESTS', default=True)
if 'test' in sys.argv and USE_SQLITE_FOR_TESTS:
    DATABASES['default'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db_test.sqlite3',
    }


AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True


STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


ARQUIVO_CLINICO_MAX_TAMANHO_BYTES = config('ARQUIVO_CLINICO_MAX_TAMANHO_BYTES', default=10 * 1024 * 1024, cast=int)
ARQUIVO_CLINICO_MIME_TYPES = ('application/pdf', 'image/jpeg', 'image/png', 'image/webp')
ARQUIVO_CLINICO_EXTENSOES = ('.pdf', '.jpg', '.jpeg', '.png', '.webp')

CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = config(
    'CORS_ALLOWED_ORIGINS',
    default=None if IS_PRODUCTION else 'http://localhost:5173',
    cast=Csv(),
)
if IS_PRODUCTION and (not CORS_ALLOWED_ORIGINS or '*' in CORS_ALLOWED_ORIGINS):
    raise ImproperlyConfigured('CORS_ALLOWED_ORIGINS deve ser explicito em producao.')

SECURE_SSL_REDIRECT = env_bool('SECURE_SSL_REDIRECT', default=IS_PRODUCTION)
SECURE_HSTS_SECONDS = config('SECURE_HSTS_SECONDS', default=31536000 if IS_PRODUCTION else 0, cast=int)
SECURE_HSTS_INCLUDE_SUBDOMAINS = env_bool('SECURE_HSTS_INCLUDE_SUBDOMAINS', default=False)
SECURE_HSTS_PRELOAD = env_bool('SECURE_HSTS_PRELOAD', default=False)
SESSION_COOKIE_SECURE = env_bool('SESSION_COOKIE_SECURE', default=IS_PRODUCTION)
CSRF_COOKIE_SECURE = env_bool('CSRF_COOKIE_SECURE', default=IS_PRODUCTION)
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = 'same-origin'
X_FRAME_OPTIONS = 'DENY'

FRONTEND_BASE_URL = config('FRONTEND_BASE_URL', default='').rstrip('/')

AUTH_USER_MODEL = 'api.Usuario'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
    'DEFAULT_THROTTLE_RATES': {
        'token': config('THROTTLE_TOKEN_RATE', default='10/min'),
        'public_registration': config('THROTTLE_PUBLIC_REGISTRATION_RATE', default='100/hour'),
        'password_change': config('THROTTLE_PASSWORD_CHANGE_RATE', default='5/hour'),
        'presence_confirmation': config('THROTTLE_PRESENCE_CONFIRMATION_RATE', default='30/hour'),
    },
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=config('JWT_ACCESS_TOKEN_MINUTES', default=5, cast=int)),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=config('JWT_REFRESH_TOKEN_DAYS', default=1, cast=int)),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': False,
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {'console': {'class': 'logging.StreamHandler'}},
    'loggers': {'api.request': {'handlers': ['console'], 'level': 'INFO', 'propagate': False}},
}

REQUEST_LOGGING_ENABLED = env_bool('REQUEST_LOGGING_ENABLED', default=IS_PRODUCTION)

SPECTACULAR_SETTINGS = {
    'TITLE': 'API Clinica Odontologica',
    'DESCRIPTION': (
        'Contrato oficial odontologico da API. Use Bearer JWT no header '
        'Authorization. Endpoints listados usam paginacao DRF no formato '
        '{"count": 0, "next": null, "previous": null, "results": []}.'
    ),
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'COMPONENT_SPLIT_REQUEST': True,
    'SWAGGER_UI_SETTINGS': {
        'persistAuthorization': True,
    },
}
