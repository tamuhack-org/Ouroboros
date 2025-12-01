# pylint: disable=C0330
import csv
from zoneinfo import ZoneInfo

from address.forms import AddressWidget
from address.models import AddressField
from django import forms
from django.conf import settings
from django.contrib import admin
from django.contrib.admin.filters import RelatedOnlyFieldListFilter
from django.db import transaction
from django.db.models.query import QuerySet
from django.http import HttpRequest, HttpResponse
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.html import strip_tags
from django_admin_listfilter_dropdown.filters import (
    ChoiceDropdownFilter,
)
from rangefilter.filters import DateRangeFilter

from application.constants import (
    RACES,
    STATUS_ADMITTED,
    STATUS_EXPIRED,
    STATUS_REJECTED,
)
from application.emails import send_confirmation_email
from application.models import (
    Application,
    Wave,
)
from hiss.settings.customization import EVENT_TIMEZONE
from shared.admin_functions import send_mass_html_mail


class ApplicationAdminForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = "__all__"  # noqa: DJ007
        widgets = {
            "gender": forms.RadioSelect,
            "grad_year": forms.RadioSelect,
            "status": forms.RadioSelect,
        }


def build_approval_email(
    application: Application, confirmation_deadline: timezone.datetime
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
        "organizer_email": settings.ORGANIZER_EMAIL,
        "event_date_text": settings.EVENT_DATE_TEXT,
    }
    html_message = render_to_string("application/emails/approved.html", context)
    message = strip_tags(html_message)
    return subject, message, html_message, None, [application.user.email]


def build_rejection_email(application: Application) -> tuple[str, str, None, list[str]]:
    """Create email indicating a `User` is rejected.

    Return type is (subject, message, html_message, from_email, [to_email])
    """
    subject = f"Regarding your {settings.EVENT_NAME} application"

    context = {
        "first_name": application.first_name,
        "event_name": settings.EVENT_NAME,
        "organizer_name": settings.ORGANIZER_NAME,
        "event_year": settings.EVENT_YEAR,
        "organizer_email": settings.ORGANIZER_EMAIL,
        "event_date_text": settings.EVENT_DATE_TEXT,
    }
    html_message = render_to_string("application/emails/rejected.html", context)
    message = strip_tags(html_message)
    return subject, message, html_message, None, [application.user.email]


def approve(
    _modeladmin, _request: HttpRequest, queryset: QuerySet[Application]
) -> None:
    """Approve selected Applications.

    Sets the value of the `approved` field for the selected `Application`s to `True`, creates an RSVP deadline for
    each user based on how many days each wave gives to RSVP, and then emails all of the users to inform them that
    their applications have been approved.
    """

    tz = ZoneInfo(EVENT_TIMEZONE)
    today_end = timezone.now().astimezone(tz).replace(hour=23, minute=59, second=59, microsecond=0)
    apps = queryset.select_related("wave")

    to_update = []
    email_tuples = []

    for app in apps:
        deadline = today_end + timezone.timedelta(days=app.wave.num_days_to_rsvp)
        app.status = STATUS_ADMITTED
        app.confirmation_deadline = deadline

        to_update.append(app)
        email_tuples.append(build_approval_email(app, deadline))

    with transaction.atomic():
        Application.objects.bulk_update(to_update, ["status", "confirmation_deadline"])

    send_mass_html_mail(email_tuples)


def reject(_modeladmin, _request: HttpRequest, queryset: QuerySet[Application]) -> None:
    """Set the value of the `approved` field for the selected `Application`s to `False`."""
    email_tuples = []
    with transaction.atomic():
        for application in queryset:
            application.status = STATUS_REJECTED
            email_tuples.append(build_rejection_email(application))
            application.save()
    send_mass_html_mail(email_tuples)


def build_waitlist_email(
    application: Application,
) -> tuple[str, str, str, None, list[str]]:
    """Create an email data tuple indicating that a user's application has been waitlisted.

    Args:
        application (Application): The application object containing user details.

    Returns:
        A tuple representing the email to send.
    """
    subject = f"Regarding your {settings.EVENT_NAME} application"

    context = {
        "first_name": application.first_name,
        "event_name": settings.EVENT_NAME,
        "organizer_name": settings.ORGANIZER_NAME,
        "event_year": settings.EVENT_YEAR,
        "organizer_email": settings.ORGANIZER_EMAIL,
        "event_date_text": settings.EVENT_DATE_TEXT,
    }
    html_message = render_to_string("application/emails/reject-waitlist.html", context)
    message = strip_tags(html_message)
    return subject, message, html_message, None, [application.user.email]


def waitlist(
    _modeladmin, _request: HttpRequest, queryset: QuerySet[Application]
) -> None:
    """Set the status of selected Applications to waitlisted (expired) and send waitlist emails."""
    email_tuples = []
    with transaction.atomic():
        for application in queryset:
            application.status = STATUS_EXPIRED
            email_tuples.append(build_waitlist_email(application))
            application.save()
    send_mass_html_mail(email_tuples)


def resend_confirmation(
    _modeladmin, _request: HttpRequest, queryset: QuerySet[Application]
) -> None:
    """Resends the confirmation email to the selected applications."""
    for application in queryset:
        application.save()
        send_confirmation_email(application)


def export_application_emails(
    _modeladmin, _request: HttpRequest, queryset: QuerySet[Application]
):
    """Export the emails related to the selected `Application`s to a CSV file."""
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="emails.csv"'

    writer = csv.writer(response)
    writer.writerow(["email", "shirt_size"])
    for instance in queryset:
        writer.writerow([instance.user.email, instance.shirt_size])

    return response


def custom_titled_filter(title):
    class Wrapper(admin.FieldListFilter):
        def __new__(cls, *args, **kwargs):
            instance = admin.FieldListFilter.create(*args, **kwargs)
            instance.title = title
            return instance

    return Wrapper


class RaceFilter(admin.SimpleListFilter):
    title = "Race"
    parameter_name = "race"

    def lookups(self, _request: HttpRequest, _model_admin) -> list[tuple[str, str]]:
        return RACES

    def queryset(self, _request: HttpRequest, queryset: QuerySet):
        if self.value():
            return queryset.filter(race__contains=self.value())
        return queryset


class ApplicationAdmin(admin.ModelAdmin):
    form = ApplicationAdminForm
    readonly_fields = [
        "datetime_submitted",
        "user",
        # "is_adult",
        "gender",
        "race",
        "major",
        "school",
        "grad_year",
        "num_hackathons_attended",
        "dietary_restrictions",
        "extra_links",
        # "address",
        # "question2",
        # "question3",
        "notes",
        "is_a_walk_in",
    ]
    list_filter = (
        ("school", RelatedOnlyFieldListFilter),
        ("status", ChoiceDropdownFilter),
        ("gender", ChoiceDropdownFilter),
        ("major", ChoiceDropdownFilter),
        ("grad_year", ChoiceDropdownFilter),
        ("num_hackathons_attended", ChoiceDropdownFilter),
        ("wares", ChoiceDropdownFilter),
        ("shirt_size", ChoiceDropdownFilter),
        ("datetime_submitted", DateRangeFilter),
        ("accessibility_requirements", ChoiceDropdownFilter),
        RaceFilter,
    )
    list_display = (
        "first_name",
        "last_name",
        "school",
        "user_email",
        "datetime_submitted",
        "grad_year",
        "status",
        "additional_accommodations",
    )
    fieldsets = [
        ("Related Objects", {"fields": ["user"]}),
        ("Status", {"fields": ["status"]}),
        (
            "Personal Information",
            {
                "fields": [
                    "first_name",
                    "last_name",
                    "tamu_email",
                    "age",
                    "phone_number",
                    "country",
                    "extra_links",
                    # "question2",
                    # "question3",
                    "resume",
                ]
            },
        ),
        (
            "Demographic Information",
            {
                "fields": [
                    "school",
                    "school_other",
                    "major",
                    "major_other",
                    "gender",
                    "gender_other",
                    "race",
                    "race_other",
                    "grad_year",
                    "level_of_study",
                    "num_hackathons_attended",
                ]
            },
        ),
        (
            "Logistical Information",
            {
                "fields": [
                    "wares",
                    "shirt_size",
                    "dietary_restrictions",
                    "meal_group",
                    "additional_accommodations",
                    # "address",
                    "emergency_contact_name",
                    "emergency_contact_relationship",
                    "emergency_contact_phone",
                    "emergency_contact_email",
                ]
            },
        ),
        ("Confirmation Deadline", {"fields": ["confirmation_deadline"]}),
        (
            "Miscellaneous",
            {"fields": ["notes", "is_adult", "accessibility_requirements"]},
        ),
    ]
    formfield_overrides = {
        AddressField: {"widget": AddressWidget(attrs={"style": "width: 300px;"})}
    }
    list_per_page = 1500

    approve.short_description = "Approve Selected Applications"
    reject.short_description = "Reject Selected Applications"
    waitlist.short_description = "Waitlist Selected Applications"
    export_application_emails.short_description = (
        "Export Emails for Selected Applications"
    )
    resend_confirmation.short_description = (
        "Resend Confirmation to Selected Applications"
    )

    actions = [
        approve,
        reject,
        waitlist,
        export_application_emails,
        resend_confirmation,
    ]

    def has_add_permission(self, _request):
        return True

    def has_change_permission(self, _request, _obj=None):
        return True

    @staticmethod
    def user_email(obj: Application) -> str:
        return obj.user.email

    @staticmethod
    def is_a_walk_in(obj: Application) -> bool:
        return obj.wave.is_walk_in_wave


class WaveAdmin(admin.ModelAdmin):
    list_display = ("start", "end", "is_walk_in_wave")


admin.site.register(Application, ApplicationAdmin)
admin.site.register(Wave, WaveAdmin)
