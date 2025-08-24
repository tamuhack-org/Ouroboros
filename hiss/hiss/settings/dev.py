from .base import *  # noqa: F403
from .customization import *  # noqa: F403

SECRET_KEY = "development"
DEBUG = True
# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# settings.py

# Use Django's SMTP backend
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "localhost"
EMAIL_PORT = 1025
EMAIL_HOST_USER = ""
EMAIL_HOST_PASSWORD = ""
EMAIL_USE_TLS = False
EMAIL_USE_SSL = False

# A sensible default from-address
DEFAULT_FROM_EMAIL = "webmaster@localhost"
MEDIA_ROOT = "resumes"


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",  # noqa: F405
    }
}

AWS_S3_KEY_PREFIX = "dev-resumes"
DEFAULT_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"