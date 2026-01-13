import logging
import os
import sys

import dj_database_url

from .base import *  # noqa: F403
from .customization import *  # noqa: F403

logger = logging.getLogger(__name__)
logger.info("Loading production settings")

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("SECRET_KEY") or sys.exit("SECRET_KEY is not set")
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False
ALLOWED_HOSTS = ["*"]
SESSION_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
CSRF_COOKIE_SECURE = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
SECURE_SSL_REDIRECT = False  # Let cloudflare handle this for us
# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# Email Configuration Global Settings
ANYMAIL = {
    "MAILGUN_API_KEY": os.getenv("MAILGUN_API_KEY"),
    "MAILGUN_SENDER_DOMAIN": "mail.tamuhack.com",
}
EMAIL_BACKEND = "anymail.backends.mailgun.EmailBackend"
DEFAULT_FROM_EMAIL = f"The {ORGANIZER_NAME} Team <{ORGANIZER_EMAIL}>"  # noqa: F405

STORAGES = {
    "default": {
        "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
        "OPTIONS": {
            "default_acl": None,
            "file_overwrite": False,
            "signature_version": "s3v4",
            "region_name": "us-east-2",
        },
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}
AWS_STORAGE_BUCKET_NAME = os.getenv("AWS_STORAGE_BUCKET_NAME")
AWS_LOCATION = "resumes"
MEDIA_URL = f"https://{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/{AWS_LOCATION}/"

logger.info(f"S3 bucket configured: {AWS_STORAGE_BUCKET_NAME}")
logger.info(
    f"AWS Access Key ID present: {'Yes' if os.getenv('AWS_ACCESS_KEY_ID') else 'No'}"
)
logger.info(
    f"AWS Secret Access Key present: {'Yes' if os.getenv('AWS_SECRET_ACCESS_KEY') else 'No'}"
)
DATABASES = {
    # Need persisitent connections for bg worker it seems https://docs.djangoproject.com/en/6.0/ref/databases/#persistent-connections
    "default": dj_database_url.config(
        default=os.environ["DATABASE_URL"],
        engine="django.db.backends.postgresql",
        conn_max_age=600,
        conn_health_checks=True,
    )
}
