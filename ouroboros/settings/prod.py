from .base import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = open("/run/secrets/SECRET_DJANGO_KEY", "r").read()

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["*"]

# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": "ouroboros",
        "USER": open("/run/secrets/SECRET_POSTGRES_USER", "r").read(),
        "PASSWORD": open("/run/secrets/SECRET_POSTGRES_PASS", "r").read(),
        "HOST": "db",
        "PORT": "",
    }
}

# Email Configuration Global Settings

"""
Email settings should be in the format:

{
    "EMAIL_HOST": "smtp.gmail.com",
    "EMAIL_HOST_USER": "enter your email address here", 
    "EMAIL_HOST_PASSWORD": "enter your email password here", 
    "EMAIL_PORT": 587
}

"""

email_credentials_file = open("/run/secrets/SECRET_EMAIL_CONFIG", "r")
email_credentials_data = json.load(email_credentials_file)
email_credentials_file.close()

EMAIL_USE_TLS = True
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = email_credentials_data["EMAIL_HOST"]
EMAIL_HOST_PASSWORD = email_credentials_data["EMAIL_HOST_PASSWORD"]
EMAIL_HOST_USER = email_credentials_data["EMAIL_HOST_USER"]
EMAIL_PORT = email_credentials_data["EMAIL_PORT"]
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER


# File Storage
MEDIA_ROOT = "/resumes"
