import csv
from typing import List, Tuple

from django import forms
from django.conf import settings
from django.contrib import admin
from django.core import mail
from django.db import transaction
from django.db.models.query import QuerySet
from django.http import HttpRequest, HttpResponse
from django.template.loader import render_to_string
from django.utils import timezone
from rangefilter.filter import DateRangeFilter

from application.models import Application, Wave
from user.models import User


class ApplicationAdminForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = "__all__"
        widgets = {
            "gender": forms.RadioSelect,
            "classification": forms.RadioSelect,
            "grad_term": forms.RadioSelect,
            "status": forms.RadioSelect,
        }


def create_rsvp_deadline(user: User, deadline: timezone.datetime) -> None:
    """
    Generates a datetime representing the deadline for a `User` to create an `Rsvp`
    """
    user.rsvp_deadline = deadline
    user.save()


def build_approval_email(
    application: Application, rsvp_deadline: timezone.datetime
) -> Tuple[str, str, None, List[str]]:
    """
    Sends an email to a queryset of users, each with a message indicating that a `User`'s
    application has been approved.
    """
    subject = f"Your {settings.EVENT_NAME} application has been approved!"

    context = {
        "first_name": application.first_name,
        "event_name": settings.EVENT_NAME,
        "rsvp_deadline": rsvp_deadline,
    }
    message = render_to_string("application/emails/approved.html", context)
    return subject, message, None, [application.user.email]


def build_rejection_email(application: Application) -> Tuple[str, str, None, List[str]]:
    """
    Sends an email to containing a confirmation message indicating that a `User`'s
    application has been rejected.
    """
    subject = f"Regarding your {settings.EVENT_NAME} application"

    context = {"first_name": application.first_name, "event_name": settings.EVENT_NAME}
    message = render_to_string("application/emails/rejected.html", context)
    return subject, message, None, [application.user.email]


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
            application.approved = True
            create_rsvp_deadline(application.user, deadline)
            email_tuples.append(build_approval_email(application, deadline))
            application.save()
    mail.send_mass_mail(email_tuples)


def reject(_modeladmin, _request: HttpRequest, queryset: QuerySet) -> None:
    """
    Sets the value of the `approved` field for the selected `Application`s to `False`
    """
    email_tuples = []
    with transaction.atomic():
        for application in queryset:
            application.approved = False
            email_tuples.append(build_rejection_email(application))
            application.save()
    mail.send_mass_mail(email_tuples)


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
        "grad_term",
        "tamu_student",
        "num_hackathons_attended",
        "previous_attendant",
        "extra_links",
        "question1",
        "question2",
        "question3",
        "notes",
        "approved",
    ]
    list_filter = (
        ("gender", custom_titled_filter("gender")),
        ("race", custom_titled_filter("race")),
        ("classification", custom_titled_filter("classification")),
        ("grad_term", custom_titled_filter("graduation year")),
        ("tamu_student", custom_titled_filter("if TAMU student")),
        ("approved", custom_titled_filter("approved")),
        (
            "num_hackathons_attended",
            custom_titled_filter("number of attended hackathons"),
        ),
        ("datetime_submitted", DateRangeFilter),
    )
    list_display = (
        "first_name",
        "last_name",
        "user_email",
        "datetime_submitted",
        "classification",
        "grad_term",
        "approved",
    )
    fieldsets = [
        ("Related Objects", {"fields": ["user"]}),
        (
            "Personal Information",
            {
                "fields": [
                    "first_name",
                    "last_name",
                    "is_adult",
                    "gender",
                    "race",
                    "major",
                    "classification",
                    "grad_term",
                    "tamu_student",
                ]
            },
        ),
        (
            "Hackathon Information",
            {"fields": ["num_hackathons_attended", "previous_attendant"]},
        ),
        (
            "Free Response Questions",
            {
                "fields": [
                    "extra_links",
                    "question1",
                    "question2",
                    "question3",
                    "notes",
                    "additional_accommodations",
                    "resume",
                ]
            },
        ),
        ("Status", {"fields": ["approved"]}),
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

    def user_email(self, obj: Application) -> str:
        return obj.user.email


class WaveAdmin(admin.ModelAdmin):
    list_display = ("start", "end")


admin.site.register(Application, ApplicationAdmin)
admin.site.register(Wave, WaveAdmin)
