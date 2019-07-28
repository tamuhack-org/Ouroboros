from .base import *

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "2ji1v9(v-41lc(ri$aaj=h(yfe&2c5q&#ur4=^6j7q8_cvmffj"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases

DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": "db.sqlite3"}}

# Email Settings
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Upload Settings
MEDIA_ROOT = "hacker_resumes"
