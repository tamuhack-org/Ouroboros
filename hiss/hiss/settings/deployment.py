# noinspection PyUnresolvedReferences
from .base import *

# noinspection PyUnresolvedReferences
from .customization import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False
ALLOWED_HOSTS = ["*"]
SESSION_COOKIE_SECURE = False
SECURE_BROWSER_XSS_FILTER = False
CSRF_COOKIE_SECURE = False
SECURE_CONTENT_TYPE_NOSNIFF = False
X_FRAME_OPTIONS = "DENY"

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
    "MAILGUN_SENDER_DOMAIN": "mg.tamuhack.com",
}
EMAIL_BACKEND = "anymail.backends.mailgun.EmailBackend"
DEFAULT_FROM_EMAIL = f"The {EVENT_NAME} Team <hello@tamuhack.com>"

# Static Files URL
STATIC_URL = "https://register.tamuhack.com/public/"

MEDIA_ROOT = "/resumes"
MEDIA_URL = "https://register.tamuhack.com/resumes/"
