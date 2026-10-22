"""Callbacks referenced from the UNFOLD settings (hiss/settings/admin_ui.py)."""

import json
from datetime import date, timedelta
from zoneinfo import ZoneInfo

from django.conf import settings
from django.db.models import Count
from django.db.models.functions import TruncDate
from django.http import HttpRequest
from django.urls import reverse
from django.utils import timezone
from django.utils.timesince import timesince

from application.constants import (
    GENDERS,
    STATUS_ADMIN_LABELS,
    STATUS_ADMIN_VARIANTS,
    STATUS_ADMITTED,
    STATUS_CHECKED_IN,
    STATUS_CONFIRMED,
    STATUS_EXPIRED,
    STATUS_PENDING,
)
from application.models import Application
from hiss.settings.customization import EVENT_TIMEZONE

ACCEPTED_STATUSES = (STATUS_ADMITTED, STATUS_CONFIRMED, STATUS_CHECKED_IN)
KPI_STATUSES = (
    STATUS_PENDING,
    STATUS_ADMITTED,
    STATUS_CONFIRMED,
    STATUS_CHECKED_IN,
    STATUS_EXPIRED,
)
GENDER_SCOPE_ACCEPTED = "accepted"


def environment_callback(request: HttpRequest) -> list[str]:
    if settings.DEBUG:
        return ["Development", "info"]
    return ["Production", "danger"]


def pending_badge(request: HttpRequest) -> int | str:
    """Sidebar badge: applications still waiting for a decision."""
    count = Application.objects.filter(status=STATUS_PENDING).count()
    return count or ""


def _percent(part: int, whole: int) -> int:
    return round(part * 100 / whole) if whole else 0


def _changelist_url(**params: str) -> str:
    url = reverse("admin:application_application_changelist")
    if params:
        url += "?" + "&".join(f"{key}={value}" for key, value in params.items())
    return url


def _status_cards(counts: dict[str, int], total: int) -> list[dict]:
    cards = [
        {
            "label": "Applied",
            "variant": "total",
            "value": f"{total:,}",
            "share": None,
            "href": _changelist_url(),
        }
    ]
    cards.extend(
        {
            "label": STATUS_ADMIN_LABELS[status],
            "variant": STATUS_ADMIN_VARIANTS[status],
            "value": f"{counts.get(status, 0):,}",
            "share": _percent(counts.get(status, 0), total),
            "href": _changelist_url(status__exact=status),
        }
        for status in KPI_STATUSES
    )
    return cards


def _funnel(counts: dict[str, int], total: int) -> list[dict]:
    accepted = sum(counts.get(status, 0) for status in ACCEPTED_STATUSES)
    confirmed = counts.get(STATUS_CONFIRMED, 0) + counts.get(STATUS_CHECKED_IN, 0)
    checked_in = counts.get(STATUS_CHECKED_IN, 0)

    steps = [
        ("Applied", total, None),
        ("Accepted", accepted, ("applied", total)),
        ("Confirmed", confirmed, ("accepted", accepted)),
        ("Checked in", checked_in, ("confirmed", confirmed)),
    ]
    return [
        {
            "label": label,
            "value": f"{value:,}",
            "width": _percent(value, total),
            "conversion": (
                f"{_percent(value, previous[1])}% of {previous[0]}" if previous else ""
            ),
        }
        for label, value, previous in steps
    ]


def _gender_rows(scope: str) -> tuple[int, list[dict]]:
    queryset = Application.objects.all()
    if scope == GENDER_SCOPE_ACCEPTED:
        queryset = queryset.filter(status__in=ACCEPTED_STATUSES)
    counts = dict(queryset.order_by().values_list("gender").annotate(n=Count("pk")))
    total = sum(counts.values())
    return total, [
        {
            "label": label,
            "value": f"{counts.get(code, 0):,}",
            "share": _percent(counts.get(code, 0), total),
        }
        for code, label in GENDERS
    ]


def _submissions_chart() -> dict | None:
    event_tz = ZoneInfo(EVENT_TIMEZONE)
    per_day = dict(
        Application.objects.order_by()
        .annotate(day=TruncDate("datetime_submitted", tzinfo=event_tz))
        .values_list("day")
        .annotate(n=Count("pk"))
    )
    if not per_day:
        return None

    first_day: date = min(per_day)
    last_day: date = max(*per_day, timezone.now().astimezone(event_tz).date())
    days = [first_day + timedelta(days=i) for i in range((last_day - first_day).days + 1)]
    return {
        "labels": [f"{day:%b} {day.day}" for day in days],
        "datasets": [
            {
                "label": "Applications",
                "data": [per_day.get(day, 0) for day in days],
                "backgroundColor": "var(--color-primary-500)",
                "hoverBackgroundColor": "var(--color-primary-600)",
                "borderRadius": {"topLeft": 3, "topRight": 3},
                "borderSkipped": "bottom",
                "maxBarThickness": 24,
            }
        ],
    }


# Chart.js options: horizontal gridlines only, whole-number ticks, at most 8 date labels.
# Unfold's chart script recolours the gridlines for dark mode.
SUBMISSIONS_CHART_OPTIONS = json.dumps(
    {
        "maintainAspectRatio": False,
        "plugins": {"legend": {"display": False}},
        "scales": {
            "x": {
                "grid": {"display": False},
                "border": {"display": False},
                "ticks": {"color": "#9ca3af", "maxRotation": 0, "autoSkip": True, "maxTicksLimit": 8},
            },
            "y": {
                "beginAtZero": True,
                "grid": {"drawTicks": False},
                "border": {"display": False},
                "ticks": {"color": "#9ca3af", "precision": 0, "maxTicksLimit": 5, "padding": 8},
            },
        },
    }
)


def _waiting_longest(limit: int = 5) -> list[Application]:
    """The applications that have been waiting for a decision the longest."""
    applications = list(
        Application.objects.filter(status=STATUS_PENDING)
        .select_related("school")
        .order_by("datetime_submitted")[:limit]
    )
    for application in applications:
        application.waiting_for = timesince(application.datetime_submitted, depth=1)
    return applications


def _finding(counts: dict[str, int]) -> str:
    """One line on what needs attention, shown under the dashboard title."""
    pending = counts.get(STATUS_PENDING, 0)
    unconfirmed = counts.get(STATUS_ADMITTED, 0)
    parts = [
        f"{pending:,} waiting for review" if pending else "Nothing waiting for review",
    ]
    if unconfirmed:
        parts.append(f"{unconfirmed:,} admitted but not yet confirmed")
    return " · ".join(parts)


def dashboard_callback(request: HttpRequest, context: dict) -> dict:
    counts = dict(
        Application.objects.order_by().values_list("status").annotate(n=Count("pk"))
    )
    total = sum(counts.values())

    gender_scope = request.GET.get("gender_scope", "all")
    if gender_scope != GENDER_SCOPE_ACCEPTED:
        gender_scope = "all"

    gender_total, gender_rows = _gender_rows(gender_scope)
    chart = _submissions_chart()
    context.update(
        {
            "has_applications": total > 0,
            "total_applications": f"{total:,}",
            "pending_count": counts.get(STATUS_PENDING, 0),
            "status_cards": _status_cards(counts, total),
            "funnel": _funnel(counts, total),
            "gender_scope": gender_scope,
            "gender_total": gender_total,
            "gender_description": (
                "Admitted, confirmed, and checked-in applicants"
                if gender_scope == GENDER_SCOPE_ACCEPTED
                else "All applicants"
            ),
            "gender_rows": gender_rows,
            "submissions_chart": json.dumps(chart) if chart else "",
            "submissions_chart_options": SUBMISSIONS_CHART_OPTIONS,
            "finding": _finding(counts),
            "waiting_longest": _waiting_longest(),
            # Oldest first: column 5 of list_display is "Submitted"
            "waiting_longest_url": _changelist_url(status__exact=STATUS_PENDING, o="5"),
            "pending_url": _changelist_url(status__exact=STATUS_PENDING),
        }
    )
    return context
