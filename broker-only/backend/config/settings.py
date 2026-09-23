"""Only Broker settings. Everything environment-specific comes from env vars (.env on the laptop)."""
from datetime import timedelta
from pathlib import Path

import environ

BASE_DIR = Path(__file__).resolve().parent.parent
env = environ.Env()
environ.Env.read_env(BASE_DIR / ".env", overwrite=False)

DEBUG = env.bool("DJANGO_DEBUG", default=False)
SECRET_KEY = env("DJANGO_SECRET_KEY", default="dev-insecure-change-me" if DEBUG else environ.Env.NOTSET)
ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS", default=["localhost", "127.0.0.1"])
CSRF_TRUSTED_ORIGINS = env.list("DJANGO_CSRF_TRUSTED_ORIGINS", default=[])

INSTALLED_APPS = [
    "daphne",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.gis",
    "django.contrib.postgres",
    "rest_framework",
    "drf_spectacular",
    "channels",
    "common",
    "apps.identity",
    "apps.orgs",
    "apps.audit",
    "apps.masterdata",
    "apps.status",
    "apps.inventory",
    "apps.crm",
    "apps.matching",
    "apps.visits",
    "apps.marketplace",
    "apps.reviews",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "common.rls.RlsResetMiddleware",
]

ROOT_URLCONF = "config.urls"
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ]
        },
    }
]
WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

DATABASES = {
    "default": env.db_url(
        "DATABASE_URL", default="postgis://ob_app:ob_app_dev_password@localhost:5432/onlybroker"
    )
}
DATABASES["default"]["ENGINE"] = "django.contrib.gis.db.backends.postgis"
# Every request runs in one transaction so the RLS context (SET LOCAL) is scoped to it.
DATABASES["default"]["ATOMIC_REQUESTS"] = True

AUTH_USER_MODEL = "identity.User"
AUTHENTICATION_BACKENDS = ["apps.identity.backends.PhoneBackend"]
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", "OPTIONS": {"min_length": 12}},
]

LANGUAGE_CODE = "en-in"
TIME_ZONE = "Asia/Kolkata"
USE_I18N = True
USE_TZ = True
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

REDIS_URL = env("REDIS_URL", default="redis://localhost:6379/0")
CHANNEL_LAYERS = {
    "default": (
        {"BACKEND": "channels.layers.InMemoryChannelLayer"}
        if env.bool("CHANNELS_IN_MEMORY", default=False)
        else {"BACKEND": "channels_redis.core.RedisChannelLayer", "CONFIG": {"hosts": [REDIS_URL]}}
    )
}
CACHES = {
    "default": (
        {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}
        if env.bool("CACHE_IN_MEMORY", default=False)
        else {"BACKEND": "django.core.cache.backends.redis.RedisCache", "LOCATION": REDIS_URL}
    )
}

CELERY_BROKER_URL = REDIS_URL
CELERY_TASK_ALWAYS_EAGER = env.bool("CELERY_TASK_ALWAYS_EAGER", default=False)
CELERY_BEAT_SCHEDULE = {
    "relay-outbox": {"task": "common.tasks.relay_outbox", "schedule": 1.0},
    "decay-stale-status": {"task": "apps.status.tasks.decay_stale_statuses", "schedule": 3600.0},
    "expire-enquiries": {"task": "apps.marketplace.tasks.expire_enquiries", "schedule": 600.0},
}

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": ["apps.identity.authentication.OrgAwareJWTAuthentication"],
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.CursorPagination",
    "PAGE_SIZE": 50,
    "DEFAULT_THROTTLE_RATES": {"otp": "5/15min", "public_link": "30/min"},
    "TEST_REQUEST_DEFAULT_FORMAT": "json",
}
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=15),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=30),
    "ROTATE_REFRESH_TOKENS": True,
    "USER_ID_FIELD": "id",
}
SPECTACULAR_SETTINGS = {"TITLE": "Only Broker API", "VERSION": "0.1.0", "SERVE_INCLUDE_SCHEMA": False}

# --- Only Broker specifics -------------------------------------------------
# Field encryption key (32 bytes, base64) and HMAC pepper for phone lookups.
# In production both come from AWS Secrets Manager / KMS.
OB_FIELD_KEY = env("OB_FIELD_KEY", default="ZGV2LW9ubHktZmllbGQta2V5LTMyLWJ5dGVzLWxvbmc=" if DEBUG else environ.Env.NOTSET)
OB_PHONE_PEPPER = env("OB_PHONE_PEPPER", default="dev-only-pepper" if DEBUG else environ.Env.NOTSET)
OB_OTP_PROVIDER = env("OB_OTP_PROVIDER", default="console")  # console | msg91
OB_NOTIFY_PROVIDER = env("OB_NOTIFY_PROVIDER", default="console")  # console | whatsapp
OB_PUBLIC_BASE_URL = env("OB_PUBLIC_BASE_URL", default="http://localhost:3000")
OB_STATUS_RULES = {
    "consensus_brokers": 2,
    "consensus_window_days": 7,
    "confirmation_ttl_hours": 72,
    "hold_days": 7,
    "decay_days": {"RENT": 30, "SALE_NEW": 90, "SALE_RESALE": 90},
}
OB_MARKET = {
    "max_open_enquiries_per_customer": 3,
    "max_accepted_proposals": 3,
    "enquiry_ttl_days": 14,
    "broadcast_cap": 200,
    "presence_ttl_s": 600,
}

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "root": {"handlers": ["console"], "level": env("LOG_LEVEL", default="INFO")},
}
