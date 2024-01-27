# pylint: disable=C0330
import csv
from typing import List, Tuple

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
from rangefilter.filter import DateRangeFilter

from application.emails import send_confirmation_email
from application.models import (
    RACES,
    STATUS_ADMITTED,
    STATUS_REJECTED,
    Application,
    Wave,
)
from shared.admin_functions import send_mass_html_mail

from address.forms import AddressWidget
from address.models import AddressField


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
    subject = f"ACTION REQUIRED: One last step for your {settings.EVENT_NAME} application!"

    context = {
        "first_name": application.first_name,
        "event_name": settings.EVENT_NAME,
        "organizer_name": settings.ORGANIZER_NAME,
        "event_year": settings.EVENT_YEAR,
        "confirmation_deadline": confirmation_deadline,
        "organizer_email": settings.ORGANIZER_EMAIL,
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

    context = {
        "first_name": application.first_name,
        "event_name": settings.EVENT_NAME,
        "organizer_name": settings.ORGANIZER_NAME,
        "event_year": settings.EVENT_YEAR,
        "organizer_email": settings.ORGANIZER_EMAIL,
    }
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
            approval_email = build_approval_email(application, deadline)
            print(f"approval email built for {approval_email[-1:]}")
            email_tuples.append(approval_email)
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


def resend_confirmation(_modeladmin, _request: HttpRequest, queryset: QuerySet) -> None:
    """
    Resends the confirmation email to the selected applications.
    """
    for application in queryset:
        send_confirmation_email(application)


def export_application_emails(_modeladmin, _request: HttpRequest, queryset: QuerySet):
    """
    Exports the emails related to the selected `Application`s to a CSV file
    """
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="emails.csv"'

    writer = csv.writer(response)
    writer.writerow(
        [
            "email",
            "shirt_size"
        ]
    )
    for instance in queryset:
        instance: Application = instance
        writer.writerow(
            [
                instance.user.email,
                instance.shirt_size
            ]
        )

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

    def lookups(self, request: HttpRequest, model_admin) -> List[Tuple[str, str]]:
        return RACES

    def queryset(self, request: HttpRequest, queryset: QuerySet):
        if self.value():
            return queryset.filter(race__contains=self.value())
        return queryset


class ApplicationAdmin(admin.ModelAdmin):
    form = ApplicationAdminForm
    readonly_fields = [
        "datetime_submitted",
        "user",
        "is_adult",
        "gender",
        "race",
        "major",
        "school",
        "classification",
        "grad_year",
        "num_hackathons_attended",
        "technology_experience",
        "dietary_restrictions",
        "extra_links",
        # "address",
        "question1",
        # "question2",
        # "question3",
        "notes",
        "is_a_walk_in",
    ]
    list_filter = (
        ("school", RelatedOnlyFieldListFilter),
        ("status", ChoiceDropdownFilter),
        ("classification", ChoiceDropdownFilter),
        ("gender", ChoiceDropdownFilter),
        ("grad_year", ChoiceDropdownFilter),
        ("num_hackathons_attended", ChoiceDropdownFilter),
        ("wares", ChoiceDropdownFilter),
        # ("technology_experience", ChoiceDropdownFilter),
        # ("dietary_restrictions", ChoiceDropdownFilter),
        ("shirt_size", ChoiceDropdownFilter),
        ("datetime_submitted", DateRangeFilter),
        RaceFilter,
    )
    list_display = (
        "first_name",
        "last_name",
        "school",
        "user_email",
        "datetime_submitted",
        "classification",
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
                    "age",
                    "phone_number",
                    "country",
                    "extra_links",
                    "question1",
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
                    "classification",
                    "gender",
                    "gender_other",
                    "race",
                    "race_other",
                    "grad_year",
                    "level_of_study",
                    "num_hackathons_attended",
                    "technology_experience",
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
        ("Miscellaneous", {"fields": ["notes"]}),
    ]
    formfield_overrides = {
        AddressField: {"widget": AddressWidget(attrs={"style": "width: 300px;"})}
    }
    list_per_page = 20

    approve.short_description = "Approve Selected Applications"
    reject.short_description = "Reject Selected Applications"
    export_application_emails.short_description = (
        "Export Emails for Selected Applications"
    )
    resend_confirmation.short_description = (
        "Resend Confirmation to Selected Applications"
    )

    actions = [approve, reject, export_application_emails, resend_confirmation]

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
