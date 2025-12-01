from django.utils import timezone

MAX_YEARS_ADMISSION = 6
EVENT_NAME = "TAMUhack"
EVENT_YEAR = "2026"
ORGANIZER_NAME = "TAMUhack"
ORGANIZER_EMAIL = "hello@tamuhack.com"

EVENT_START_DATETIME = timezone.datetime(2026, 1, 24, hour=9, minute=0, second=0)
EVENT_END_DATETIME = timezone.datetime(2026, 1, 25, hour=12, minute=0, second=0)
EVENT_DATE_TEXT = "January 24-25, 2026"
EVENT_TIMEZONE = "America/Chicago"

APPLE_WALLET_S3_BUCKET_URL = "https://th25-apple-wallet-passes.s3.amazonaws.com"
AWS_S3_BUCKET_NAME = "th-26-resumes"

# Miscellaneous Application Question
MISC_SHORT_ANSWER_ENABLED = True
MISC_SHORT_ANSWER_PROMPT = "If you were a fruit, what fruit would you be and why? (Keep it brief, like 1 sentence is fine)"
MISC_SHORT_ANSWER_MAX_LENGTH = 500
MISC_SHORT_ANSWER_REQUIRED = False
