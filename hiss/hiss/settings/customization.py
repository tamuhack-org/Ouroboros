from datetime import datetime
from zoneinfo import ZoneInfo

MAX_YEARS_ADMISSION = 6
EVENT_NAME = "HowdyHack"
EVENT_YEAR = "2026"
ORGANIZER_NAME = "TAMUhack"
ORGANIZER_EMAIL = "hello@tamuhack.com"

MAX_TEAM_CAPACITY = 4

EVENT_TIMEZONE = "America/Chicago"
EVENT_START_DATETIME = datetime(2026, 10, 24, hour=9, tzinfo=ZoneInfo(EVENT_TIMEZONE))
EVENT_END_DATETIME = datetime(2026, 10, 25, hour=12, tzinfo=ZoneInfo(EVENT_TIMEZONE))
EVENT_DATE_TEXT = "October 24-25, 2026"
EVENT_WAITLIST_CHECKIN_DATETIME = EVENT_START_DATETIME.replace(hour=11)
# Use the organizer site until an event-specific site and map are available.
EVENT_WEBSITE_URL = "https://tamuhack.org/"
EVENT_MAP_URL = ""

APPLE_WALLET_S3_BUCKET_URL = "https://hh26-apple-wallet-passes.s3.amazonaws.com"

# Miscellaneous Application Question
MISC_SHORT_ANSWER_ENABLED = True
MISC_SHORT_ANSWER_PROMPT = "If you were a sea creature, what sea creature would you be and why? (Keep it brief, like 1 sentence is fine)"
MISC_SHORT_ANSWER_MAX_LENGTH = 500
MISC_SHORT_ANSWER_REQUIRED = True
