from django.utils import timezone

MAX_YEARS_ADMISSION = 6
EVENT_NAME = "HowdyHack"
EVENT_YEAR = "2025"
ORGANIZER_NAME = "TAMUhack"
ORGANIZER_EMAIL = "hello@tamuhack.com"
EVENT_START_DATETIME = timezone.datetime(2025, 10, 18, hour=9, minute=0, second=0)
EVENT_END_DATETIME = timezone.datetime(2025, 10, 19, hour=12, minute=0, second=0)
EVENT_DATE_TEXT = "October 18-19, 2025"
EVENT_TIMEZONE = "America/Chicago"

APPLE_WALLET_S3_BUCKET_URL = "https://th25-apple-wallet-passes.s3.amazonaws.com"
AWS_S3_BUCKET_NAME = "2025-th-resumes"
