from .base import *  # noqa: F403
from .customization import *  # noqa: F403

SECRET_KEY = "test"
DEBUG = True

TASKS = {
    "default": {
        "BACKEND": "django_tasks.backends.immediate.ImmediateBackend"
    }
}

PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

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

# Use console backend for tests
EMAIL_BACKEND = "django.core.mail.backends.console.ConsoleBackend"

# A sensible default from-address
DEFAULT_FROM_EMAIL = "webmaster@localhost"
MEDIA_ROOT = "test-resumes"


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

# Used for debug-toolbar use
INTERNAL_IPS = [
    "127.0.0.1",
]

AWS_S3_KEY_PREFIX = "test-resumes"
DEFAULT_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"
