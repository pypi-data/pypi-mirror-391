DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}}

INSTALLED_APPS = (
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "logger_extra",
    "tests",
    "auditlog",
)

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

MIDDLEWARE = [
    "logger_extra.middleware.XRequestIdMiddleware",
]

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
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


LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        "context": {
            "()": "logger_extra.filter.LoggerContextFilter",
        }
    },
    "formatters": {
        "json": {
            "()": "logger_extra.formatter.JSONFormatter",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "json",
            "filters": ["context"],
        },
    },
    "loggers": {
        "": {
            "handlers": ["console"],
            "level": "INFO",
        },
    },
}

SECRET_KEY = "secret"

ROOT_URLCONF = "tests.urls"
LOGGER_EXTRA_AUGMENT_DJANGO_AUDITLOG = True

USE_TZ = True
DEBUG = True
