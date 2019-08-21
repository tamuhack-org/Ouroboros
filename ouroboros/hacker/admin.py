import datetime

from django import forms
from django.conf import settings
from django.contrib import admin
from django.core import mail
from django.db import transaction
from django.template.loader import render_to_string
from django.utils import html, timezone
from django.contrib.auth.models import Group

from hacker.models import Application, Hacker, Rsvp, Wave
from hacker.forms import GroupAdminForm


def check_in(modeladmin, request, queryset):  # Needs to be Tested!!!
    queryset.update(checked_in=True)
    queryset.update(checked_in_datetime=timezone.datetime.now())


class HackerAdmin(admin.ModelAdmin):
    list_display = ("email", "is_active", "is_staff", "checked_in")
    readonly_fields = ("email", "password", "is_active")
    fieldsets = [
        ("User Information", {"fields": ["email", "password"]}),
        ("Checkin Status", {"fields": ["checked_in"]}),
        ("RSVP Deadline", {"fields": ["rsvp_deadline"]}),
        (
            "Advanced",
            {
                "fields": ["is_superuser", "is_staff", "is_active"],
                "classes": ["collapse"],
            },
        ),
    ]

    check_in.short_description = "Check-In Selected Hackers"
    actions = [check_in]

    def has_add_permission(self, request, obj=None):
        return True

    def has_change_permission(self, request, obj=None):
        return True

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


class WaveAdmin(admin.ModelAdmin):
    list_display = ("pk", "start", "end")


def create_rsvp_deadline(hacker: Hacker, deadline: timezone.datetime) -> None:
    hacker.rsvp_deadline = deadline
    hacker.save()


def send_application_approval_email(application: Application, rsvp_deadline) -> None:
    """Sends an email to this Hacker when their application has been approved."""
    email_template = "emails/application/approved.html"
    subject = f"Your {settings.EVENT_NAME} application has been approved!"
    context = {
        "first_name": application.first_name,
        "event_name": settings.EVENT_NAME,
        "rsvp_deadline": rsvp_deadline,
    }
    application.hacker.email_html_hacker(email_template, context, subject)


def send_application_rejection_email(application: Application) -> None:
    """Sends an email to this Hacker when their application has been rejected."""
    email_template = "emails/application/rejected.html"
    subject = f"Regarding your {settings.EVENT_NAME} application"
    context = {"first_name": application.first_name, "event_name": settings.EVENT_NAME}
    application.hacker.email_html_hacker(email_template, context, subject)


def approve(modeladmin, request, queryset):  # Needs to be Tested!!!
    with transaction.atomic():
        deadline = timezone.now().replace(
            hour=23, minute=59, second=59, microsecond=0
        ) + timezone.timedelta(settings.DAYS_TO_RSVP)
        for instance in queryset:
            instance.approved = True
            create_rsvp_deadline(instance.hacker, deadline)
            send_application_approval_email(instance, deadline)
            instance.save()


def reject(self, request, queryset):  # Needs to be Tested!!!
    with transaction.atomic():
        for instance in queryset:
            instance.approved = False
            send_application_rejection_email(instance)
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
        "hacker",
        "adult",
        "gender",
        "race",
        "major",
        "classification",
        "grad_year",
        "tamu_student",
        "num_hackathons_attended",
        "previous_attendant",
        "extra_links",
        "programming_joke",
        "resume",
        "unlimited_resource",
        "cool_prize",
        "notes",
        "approved"
    ]
    list_filter = (
        ("gender", custom_titled_filter("gender")),
        ("race", custom_titled_filter("race")),
        ("classification", custom_titled_filter("classification")),
        ("grad_year", custom_titled_filter("graduation year")),
        ("tamu_student", custom_titled_filter("if TAMU student")),
    )
    list_display = (
        "first_name",
        "last_name",
        "classification",
        "grad_year",
        "approved",
    )
    fieldsets = [
        ("Related Objects", {"fields": ["hacker"]}),
        (
            "Personal Information",
            {
                "fields": [
                    "first_name",
                    "last_name",
                    "adult",
                    "gender",
                    "race",
                    "major",
                    "classification",
                    "grad_year",
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
                    "programming_joke",
                    "unlimited_resource",
                    "cool_prize",
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
    actions = [approve, reject]

    def has_add_permission(self, request, obj=None):
        return True

    def has_change_permission(self, request, obj=None):
        return True


class RsvpAdminForm(forms.ModelForm):
    class Meta:
        model = Rsvp
        fields = ["hacker", "dietary_restrictions", "shirt_size"]


class RsvpAdmin(admin.ModelAdmin):
    form = RsvpAdminForm
    list_display = ("hacker_name", "notes")
    fieldsets = [
        ("Related Objects", {"fields": ["hacker"]}),
        (
            "Logistical Information",
            {"fields": ["notes", "dietary_restrictions", "shirt_size"]},
        ),
    ]

    def has_add_permission(self, request, obj=None):
        return True

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def hacker_name(self, obj: Rsvp):
        return " ".join(
            [obj.hacker.application.first_name, obj.hacker.application.last_name]
        )


# Unregister the original Group admin.
admin.site.unregister(Group)

# Create a new Group admin.
class GroupAdmin(admin.ModelAdmin):
    # Use our custom form.
    form = GroupAdminForm
    # Filter permissions horizontal as well.
    filter_horizontal = ["permissions"]


# Register the new Group ModelAdmin.
admin.site.register(Group, GroupAdmin)
admin.site.register(Hacker, HackerAdmin)
admin.site.register(Application, ApplicationAdmin)
admin.site.register(Rsvp, RsvpAdmin)
admin.site.register(Wave, WaveAdmin)
