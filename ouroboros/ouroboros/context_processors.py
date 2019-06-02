from django.conf import settings
from django.utils import timesince


def customization(request):
    return {
        "event_name": settings.EVENT_NAME,
        "event_start_date": settings.EVENT_START_DATE,
        "event_end_date": settings.EVENT_END_DATE,
    }

