from django.conf import settings
from django.http import HttpRequest


def customization(_request: HttpRequest):
    """Includes the event name, start date, and end date in all templates (except for emails).
    """
    return {
        "event_name": settings.EVENT_NAME,
        "event_year": settings.EVENT_YEAR,
        "event_start_date": settings.EVENT_START_DATETIME,
        "event_end_date": settings.EVENT_END_DATETIME,
        "organizer_email": settings.ORGANIZER_EMAIL,
        "organizer_name": settings.ORGANIZER_NAME
    }
