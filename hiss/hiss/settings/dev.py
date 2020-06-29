# noinspection PyUnresolvedReferences
from .base import *

# noinspection PyUnresolvedReferences
from .customization import *

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

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
MEDIA_ROOT = "resumes"

AUTH_CHECK_URL = "http://proxy:8080/auth/user"

URL_ORIGIN = "http://localhost:8080"

AWS_S3_KEY_PREFIX = "dev_resumes"
