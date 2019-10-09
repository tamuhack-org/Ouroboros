from django.utils import timezone

MAX_YEARS_ADMISSION = 5
EVENT_NAME = "HowdyHack"
EVENT_START_DATETIME = timezone.datetime(2020, 1, 25, hour=9, minute=0, second=0)
EVENT_END_DATETIME = timezone.datetime(2020, 1, 26, hour=12, minute=0, second=0)
LOGIN_REDIRECT_URL = "/status/"

MAX_MEMBERS_PER_TEAM = 5
