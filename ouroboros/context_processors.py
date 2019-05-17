from django.conf import settings


def customization(request):
    return {"event_name": settings.EVENT_NAME}

