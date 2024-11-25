from django.utils import timezone

MAX_YEARS_ADMISSION = 6
EVENT_NAME = "HowdyHack"
EVENT_YEAR = "2024"
ORGANIZER_NAME = "TAMUhack"
ORGANIZER_EMAIL = "hello@tamuhack.com"
EVENT_START_DATETIME = timezone.datetime(2024, 9, 28, hour=9, minute=0, second=0)
EVENT_END_DATETIME = timezone.datetime(2024, 9, 29, hour=12, minute=0, second=0)
EVENT_DATE_TEXT = "September 28-29, 2024"

MAX_MEMBERS_PER_TEAM = 4
APPLE_WALLET_S3_BUCKET_URL = "https://hh24-apple-wallet-passes.s3.amazonaws.com"
