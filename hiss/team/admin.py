from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from django.conf import settings
from django.contrib import admin
from django.db import transaction
from django.db.models import Count
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.html import strip_tags

from application.admin import ApplicationAdminInline
from application.constants import STATUS_ADMITTED
from application.models import Application
from hiss.settings.customization import EVENT_TIMEZONE
from shared.admin_functions import send_mass_html_mail

from .models import Team, TeamStatus


# TODO: This is shared with the code in application. It probably should use the task framework and stuff like that
def build_approval_email(
    application: Application, confirmation_deadline: datetime
) -> tuple[str, str, str, None, list[str]]:
    """Create an email data tuple indicating that a user's application has been approved.

    Args:
        application (Application): The application object containing user
        details.
        confirmation_deadline (timezone.datetime): The deadline for
        the user to confirm their application.


    Returns: tuple: A tuple containing the email subject, plain text message,
    HTML message, from email (None), and a list of recipient email addresses.

    """
    subject = (
        f"ACTION REQUIRED: One last step for your {settings.EVENT_NAME} application!"
    )

    context = {
        "first_name": application.first_name,
        "event_name": settings.EVENT_NAME,
        "organizer_name": settings.ORGANIZER_NAME,
        "event_year": settings.EVENT_YEAR,
        "confirmation_deadline": confirmation_deadline.strftime("%B %-d, %Y"),
        "confirmation_time": confirmation_deadline.strftime("%-I:%M %p %Z"),
        "organizer_email": settings.ORGANIZER_EMAIL,
        "event_date_text": settings.EVENT_DATE_TEXT,
    }
    html_message = render_to_string("application/emails/approved.html", context)
    message = strip_tags(html_message)
    return subject, message, html_message, None, [application.user.email]


def approve(team: Team):
    """Approve every application in the selected team"""

    tz = ZoneInfo(EVENT_TIMEZONE)
    today_end = (
        timezone.now()
        .astimezone(tz)
        .replace(hour=23, minute=59, second=59, microsecond=0)
    )
    apps = Application.objects.filter(team=team).select_related("wave", "user")

    to_update = []
    email_tuples = []

    for app in apps:
        deadline = today_end + timedelta(days=app.wave.num_days_to_rsvp)
        app.status = STATUS_ADMITTED
        app.confirmation_deadline = deadline

        to_update.append(app)
        email_tuples.append(build_approval_email(app, deadline))

    with transaction.atomic():
        Application.objects.bulk_update(to_update, ["status", "confirmation_deadline"])

    send_mass_html_mail(email_tuples)


class TeamStatusFilter(admin.SimpleListFilter):
    title = "Team status"
    parameter_name = "team_status"

    def lookups(self, request, model_admin):
        return TeamStatus.choices

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(computed_team_status=self.value())
        return queryset


class TeamAdmin(admin.ModelAdmin):
    inlines = (ApplicationAdminInline,)
    list_display = (
        "__str__",
        "member_count",
        "latest_submission_date",
        "team_status",
    )
    list_filter = ("is_active", TeamStatusFilter)

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .with_team_status()
            .order_by_latest_submission()
            .annotate(member_total=Count("members"))
            .prefetch_related("members")
        )

    @admin.display(description="Members", ordering="member_total")
    def member_count(self, obj: Team) -> int:
        return obj.member_total

    @admin.display(description="Latest submission", ordering="latest_submission")
    def latest_submission_date(self, obj: Team) -> datetime | None:
        return obj.latest_submission

    @admin.display(description="Team status", ordering="computed_team_status")
    def team_status(self, obj: Team) -> str:
        return TeamStatus(obj.computed_team_status).label

    def response_change(self, request, obj):
        # Brittle reference to the request in hiss/templates/admin/team/team/change_form.html make sure edits there are reflected here
        if "_approve" in request.POST:
            approve(obj)
            self.message_user(request, "Team approved.")
        return super().response_change(request, obj)


admin.site.register(Team, TeamAdmin)
