import requests
from django.conf import settings
from django.db import transaction
from django.utils.dateparse import parse_datetime

from volunteer.models import ScheduleEvent


class ScheduleImportError(Exception):
    pass


def import_schedule() -> tuple[int, int]:
    """Fetch the website's schedule feed once and upsert it into ScheduleEvent.

    Matches on the feed's `id`, so re-importing updates events instead of
    duplicating them. Only name/start/location/description come from the feed;
    category and visibility stay as set in admin.

    :return: (created, updated) counts
    """
    try:
        response = requests.get(settings.SCHEDULE_IMPORT_URL, timeout=10)
        response.raise_for_status()
        items = response.json()
    except (requests.RequestException, ValueError) as e:
        msg = f"Could not fetch {settings.SCHEDULE_IMPORT_URL}: {e}"
        raise ScheduleImportError(msg) from e

    if not isinstance(items, list):
        msg = "Expected a list of events from the schedule feed."
        raise ScheduleImportError(msg)

    created = updated = 0
    with transaction.atomic():
        for item in items:
            start = parse_datetime(str(item.get("date", "")))
            if not item.get("id") or not item.get("eventName") or not start:
                continue
            _, was_created = ScheduleEvent.objects.update_or_create(
                external_id=item["id"],
                defaults={
                    "name": item["eventName"][:100],
                    "start": start,
                    "location": (item.get("location") or "")[:100],
                    "description": item.get("description") or "",
                },
            )
            if was_created:
                created += 1
            else:
                updated += 1
    return created, updated
