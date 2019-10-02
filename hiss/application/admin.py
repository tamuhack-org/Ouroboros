from django import forms
from django.contrib import admin
from django.db import transaction
from django.utils import timezone

from application.models import Application, Wave
from user.models import User

from rangefilter.filter import DateRangeFilter


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


def send_application_approval_email(user: User, deadline: timezone.datetime) -> None:
    """
    Sends an email to containing a confirmation message indicating that a `User`'s
    application has been approved.
    """
    raise NotImplementedError()


def send_application_rejection_email(user: User) -> None:
    """
    Sends an email to containing a confirmation message indicating that a `User`'s
    application has been rejected.
    """
    raise NotImplementedError()


def approve(_modeladmin, _request, queryset) -> None:
    """
    Sets the value of the `approved` field for the selected `Application`s to `True`
    """
    with transaction.atomic():
        for instance in queryset:
            deadline = timezone.now().replace(
                hour=23, minute=59, second=59, microsecond=0
            ) + timezone.timedelta(instance.wave.num_days_to_rsvp)
            instance.approved = True
            create_rsvp_deadline(instance.user, deadline)
            # send_application_approval_email(instance, deadline)
            instance.save()


def reject(_modeladmin, _request, queryset) -> None:
    """
    Sets the value of the `approved` field for the selected `Application`s to `False`
    """
    with transaction.atomic():
        for instance in queryset:
            instance.approved = False
            # send_application_rejection_email(instance)
            instance.save()


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
        "is_a_walk_in",
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
        ("datetime_submitted", custom_titled_filter("date submitted")),
    )
    list_display = (
        "first_name",
        "last_name",
        "user_email",
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
        ("Status", {"fields": ["approved", "is_a_walk_in"]}),
    ]

    approve.short_description = "Approve Selected Applications"
    reject.short_description = "Reject Selected Applications"
    actions = [approve, reject]

    def has_add_permission(self, request):
        return True

    def has_change_permission(self, request, obj=None):
        return True

    def user_email(self, obj: Application) -> str:
        return obj.user.email

    def is_a_walk_in(self, obj: Application) -> bool:
        return obj.wave.is_walk_in_wave


class WaveAdmin(admin.ModelAdmin):
    list_display = ("start", "end", "is_walk_in_wave")


admin.site.register(Application, ApplicationAdmin)
admin.site.register(Wave, WaveAdmin)
