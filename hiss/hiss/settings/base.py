"""
Django settings for hiss project.

Generated by 'django-admin startproject' using Django 2.2.3.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import os

from django.urls import reverse_lazy
import dj_database_url

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Base Pathname for Obos (when not being hosted at root)
BASE_PATHNAME = (
    os.environ.get("BASE_PATHNAME") if os.environ.get("BASE_PATHNAME") else ""
)
BASE_PATHNAME_REGEX = BASE_PATHNAME + r"/$"

if len(BASE_PATHNAME) > 0:
    BASE_PATHNAME += "/"

# Application definition
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "user.apps.UserConfig",
    "application.apps.ApplicationConfig",
    "volunteer.apps.VolunteerConfig",
    "status.apps.StatusConfig",
    "phonenumber_field",
    "customauth.apps.CustomauthConfig",
    "shared.apps.SharedConfig",
    "team.apps.TeamConfig",
    "anymail",
    "django_admin_listfilter_dropdown",
    "rest_framework",
    "rest_framework.authtoken",
    "corsheaders",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "hiss.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "..", "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "shared.context_processors.customization",
            ]
        },
    }
]

WSGI_APPLICATION = "hiss.wsgi.application"

# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "US/Central"

USE_I18N = True

USE_L10N = True

USE_TZ = True

MEDIA_ROOT = "resumes/"
MEDIA_URL = "/resumes/"
MAX_UPLOAD_SIZE = "10485760"

# See https://docs.djangoproject.com/en/1.11/ref/settings/#data-upload-max-number-fields. Important for exporting
# emails.
DATA_UPLOAD_MAX_NUMBER_FIELDS = 10240
LOGIN_REDIRECT_URL = reverse_lazy("status")
LOGOUT_REDIRECT_URL = reverse_lazy("customauth:login")

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_URL = "/" + BASE_PATHNAME + "static/"
STATICFILES_DIRS = [os.path.join(BASE_DIR, "..", "static/")]
STATIC_ROOT = "public/"
APPEND_SLASH = True
AUTH_USER_MODEL = "user.User"

# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases
DATABASES = {"default": dj_database_url.config(conn_max_age=600)}

CORS_ORIGIN_WHITELIST = [
    "https://volunteer.hacklahoma.org",
    "https://hacklahoma.github.io",
]


CORS_URLS_REGEX = r"^/api/.*$"
