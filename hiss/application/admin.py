# pylint: disable=C0330
import csv
from typing import List, Tuple

from django import forms
from django.conf import settings
from django.contrib import admin
from django.db import transaction
from django.db.models.query import QuerySet
from django.http import HttpRequest, HttpResponse
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.html import strip_tags
from rangefilter.filter import DateRangeFilter

from application.models import Application, Wave, STATUS_ADMITTED, STATUS_REJECTED
from shared.admin_functions import send_mass_html_mail


class ApplicationAdminForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = "__all__"
        widgets = {
            "gender": forms.RadioSelect,
            "classification": forms.RadioSelect,
            "grad_year": forms.RadioSelect,
            "status": forms.RadioSelect,
        }


def build_approval_email(
    application: Application, confirmation_deadline: timezone.datetime
) -> Tuple[str, str, str, None, List[str]]:
    """
    Creates a datatuple of (subject, message, html_message, from_email, [to_email]) indicating that a `User`'s
    application has been approved.
    """
    subject = f"Your {settings.EVENT_NAME} application has been approved!"

    context = {
        "first_name": application.first_name,
        "event_name": settings.EVENT_NAME,
        "confirmation_deadline": confirmation_deadline,
    }
    html_message = render_to_string("application/emails/approved.html", context)
    message = strip_tags(html_message)
    return subject, message, html_message, None, [application.user.email]


def build_rejection_email(application: Application) -> Tuple[str, str, None, List[str]]:
    """
    Creates a datatuple of (subject, message, html_message, from_email, [to_email]) indicating that a `User`'s
    application has been rejected.
    """
    subject = f"Regarding your {settings.EVENT_NAME} application"

    context = {"first_name": application.first_name, "event_name": settings.EVENT_NAME}
    html_message = render_to_string("application/emails/rejected.html", context)
    message = strip_tags(html_message)
    return subject, message, html_message, None, [application.user.email]


def approve(_modeladmin, _request: HttpRequest, queryset: QuerySet) -> None:
    """
    Sets the value of the `approved` field for the selected `Application`s to `True`, creates an RSVP deadline for
    each user based on how many days each wave gives to RSVP, and then emails all of the users to inform them that
    their applications have been approved.
    """
    email_tuples = []
    with transaction.atomic():
        for application in queryset:
            deadline = timezone.now().replace(
                hour=23, minute=59, second=59, microsecond=0
            ) + timezone.timedelta(application.wave.num_days_to_rsvp)
            application.status = STATUS_ADMITTED
            application.confirmation_deadline = deadline
            email_tuples.append(build_approval_email(application, deadline))
            application.save()
    send_mass_html_mail(email_tuples)


def reject(_modeladmin, _request: HttpRequest, queryset: QuerySet) -> None:
    """
    Sets the value of the `approved` field for the selected `Application`s to `False`
    """
    email_tuples = []
    with transaction.atomic():
        for application in queryset:
            application.status = STATUS_REJECTED
            email_tuples.append(build_rejection_email(application))
            application.save()
    send_mass_html_mail(email_tuples)


def export_application_emails(_modeladmin, _request: HttpRequest, queryset: QuerySet):
    """
    Exports the emails related to the selected `Application`s to a CSV file
    """
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="emails.csv"'

    writer = csv.writer(response)
    for instance in queryset:
        writer.writerow([instance.user.email])

    return response


def custom_titled_filter(title):
    class Wrapper(admin.FieldListFilter):
        def __new__(cls, *args, **kwargs):
            instance = admin.FieldListFilter.create(*args, **kwargs)
            instance.title = title
            return instance

    return Wrapper


class ApplicationAdmin(admin.ModelAdmin):
    form = ApplicationAdminForm
    readonly_fields = [
        "datetime_submitted",
        "user",
        "is_adult",
        "gender",
        "race",
        "major",
        "classification",
        "grad_year",
        "num_hackathons_attended",
        "extra_links",
        "question1",
        "question2",
        "question3",
        "notes",
        "is_a_walk_in",
    ]
    list_display = (
        "first_name",
        "last_name",
        "datetime_submitted",
        "school",
        "major",
        "classification",
        "grad_year",
        "travel_reimbursement",
        "transport_needed",
        "status",
    )
    list_filter = (
        ("status", custom_titled_filter("status")),
        ("classification", custom_titled_filter("classification")),
        ("gender", custom_titled_filter("gender")),
        ("race", custom_titled_filter("race")),
        ("grad_year", custom_titled_filter("graduation year")),
        (
            "num_hackathons_attended",
            custom_titled_filter("number of attended hackathons"),
        ),
        ("shirt_size", custom_titled_filter("shirt_size")),
        ("transport_needed", custom_titled_filter("transport_needed")),
        ("travel_reimbursement", custom_titled_filter("travel_reimbursement")),
        ("dietary_restrictions", custom_titled_filter("dietary_restrictions")),
        ("datetime_submitted", DateRangeFilter),
    )
    list_display = (
        "first_name",
        "last_name",
        "user_email",
        "datetime_submitted",
        "classification",
        "grad_year",
        "status",
    )
    fieldsets = [
        ("Related Objects", {"fields": ["user"]}),
        (
            "Personal Information",
            {
                "fields": [
                    "first_name",
                    "last_name",
                    "extra_links",
                    "question1",
                    "question2",
                    "question3",
                    "resume",
                ]
            },
        ),
        (
            "Demographic Information",
            {
                "fields": [
                    "school",
                    "major",
                    "classification",
                    "gender",
                    "gender_other",
                    "race",
                    "race_other",
                    "grad_year",
                    "num_hackathons_attended",
                ]
            },
        ),
        (
            "Logistical Information",
            {
                "fields": [
                    "shirt_size",
                    "transport_needed",
                    "travel_reimbursement",
                    "additional_accommodations",
                    "dietary_restrictions",
                ]
            },
        ),
        ("Confirmation Deadline", {"fields": ["confirmation_deadline"]}),
        ("Miscellaneous", {"fields": ["notes"]}),
    ]

    approve.short_description = "Approve Selected Applications"
    reject.short_description = "Reject Selected Applications"
    export_application_emails.short_description = (
        "Export Emails for Selected Applications"
    )
    actions = [approve, reject, export_application_emails]

    def has_add_permission(self, request):
        return True

    def has_change_permission(self, request, obj=None):
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
