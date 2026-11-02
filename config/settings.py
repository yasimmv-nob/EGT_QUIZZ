"""
Django settings for EGT_QUIZZ (Phase 1: backend + Admin).

Este módulo es el "cerebro" de configuración: apps instaladas, BD, auth,
i18n, estáticos, etc. Se carga vía DJANGO_SETTINGS_MODULE (ver manage.py).
"""

from pathlib import Path

# Raíz del proyecto (carpeta que contiene manage.py).
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
# Firma cookies/sesiones/CSRF. En prod → variable de entorno, nunca hardcode.
SECRET_KEY = "django-insecure-tt#*f=t=rax&ft*ho9kuo^c3&l13sxsw3#4_g3httrgt8dqs6k"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True  # True: páginas de error detalladas; False en producción.

# Hosts permitidos en peticiones HTTP (protección Host header).
ALLOWED_HOSTS: list[str] = ["localhost", "127.0.0.1", "testserver"]

# Apps que Django carga: contrib (admin, auth…), terceros y apps locales.
INSTALLED_APPS = [
    "django.contrib.admin",  # UI /admin/
    "django.contrib.auth",  # User, grupos, permisos
    "django.contrib.contenttypes",  # tipos genéricos (necesario para admin/auth)
    "django.contrib.sessions",  # sesiones (login Admin)
    "django.contrib.messages",  # flash messages
    "django.contrib.staticfiles",  # CSS/JS/imágenes
    # Third-party
    "rest_framework",  # DRF instalado; API scoring = Phase 2
    # Local apps
    "trivia",
    "accounts",
]

# Cadena de middlewares: cada request/response pasa por esta lista en orden.
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",  # token anti-CSRF en forms
    "django.contrib.auth.middleware.AuthenticationMiddleware",  # request.user
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# URLconf raíz: módulo que define urlpatterns.
ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,  # busca templates/ dentro de cada app instalada
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# SQLite for local development (Phase 1). PostgreSQL can replace this later.
# DATABASES["default"] es la conexión que usa el ORM por defecto.
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",  # archivo local; sin servidor aparte
    }
}

# Validadores de contraseña al crear/cambiar users (Admin / createsuperuser).
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

# i18n / zona horaria Chile (Admin y formatos locales).
LANGUAGE_CODE = "es-cl"
TIME_ZONE = "America/Santiago"
USE_I18N = True
USE_TZ = True  # fechas timezone-aware en la BD

STATIC_URL = "static/"  # prefijo URL de archivos estáticos en desarrollo

# PK por defecto global si el AppConfig/modelo no define otra.
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# DRF is installed for Phase 2; keep a minimal default config for now.
REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
}
