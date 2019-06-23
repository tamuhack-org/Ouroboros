import datetime

from django import forms
from django.conf import settings
from django.contrib import admin
from django.core import mail
from django.db import transaction
from django.template.loader import render_to_string
from django.utils import html, timezone

from .models import Application, Hacker, Rsvp, Wave


def check_in(modeladmin, request, queryset):  # Needs to be Tested!!!
    queryset.update(checked_in=True)
    queryset.update(checked_in_datetime=datetime.datetime.now())


class HackerAdmin(admin.ModelAdmin):
    list_display = (
        "email",
        "first_name",
        "last_name",
        "is_active",
        "is_staff",
        "checked_in",
    )
    fieldsets = [
        (
            "User Information",
            {"fields": ["first_name", "last_name", "email", "password"]},
        ),
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
        return False


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


def create_rsvp_deadline(hacker: Hacker, deadline: datetime.datetime) -> None:
    hacker.rsvp_deadline = deadline
    hacker.save()


def send_application_approval_email(hacker: Hacker) -> None:
    """Sends an email to this Hacker when their application has been approved."""
    email_template = "emails/application/approved.html"
    subject = f"Your {settings.EVENT_NAME} application has been approved!"
    context = {"first_name": hacker.first_name, "event_name": settings.EVENT_NAME}
    hacker.email_html_hacker(email_template, context, subject)


def send_application_rejection_email(hacker: Hacker) -> None:
    """Sends an email to this Hacker when their application has been rejected."""
    email_template = "emails/application/rejected.html"
    subject = f"Regarding your {settings.EVENT_NAME} application"
    context = {"first_name": hacker.first_name, "event_name": settings.EVENT_NAME}
    hacker.email_html_hacker(email_template, context, subject)


def approve(modeladmin, request, queryset):  # Needs to be Tested!!!
    with transaction.atomic():
        deadline = timezone.now().replace(
            hour=23, minute=59, second=59, microsecond=0
        ) + datetime.timedelta(settings.DAYS_TO_RSVP)
        for instance in queryset:
            instance.approved = True
            create_rsvp_deadline(instance.hacker, deadline)
            send_application_approval_email(instance.hacker)
            instance.save()


def reject(self, request, queryset):  # Needs to be Tested!!!
    with transaction.atomic():
        for instance in queryset:
            instance.approved = False
            send_application_rejection_email(instance.hacker)
            instance.save()


class ApplicationAdmin(admin.ModelAdmin):
    form = ApplicationAdminForm
    list_display = ("major", "classification", "grad_year", "approved")
    fieldsets = [
        ("Related Objects", {"fields": ["hacker"]}),
        (
            "Personal Information",
            {
                "fields": [
                    "adult",
                    "first_name",
                    "last_name",
                    "gender",
                    "race",
                    "major",
                    "phone_number",
                    "classification",
                    "grad_year",
                    "dietary_restrictions",
                    "tamu_student",
                ]
            },
        ),
        (
            "Hackathon Information",
            {"fields": ["num_hackathons_attended", "previous_attendant", "shirt_size"]},
        ),
        (
            "Free Response Questions",
            {"fields": ["interests", "essay1", "notes", "resume"]},
        ),
        ("Status", {"fields": ["approved"]}),
    ]

    approve.short_description = "Approve Selected Applications"
    reject.short_description = "Reject Selected Applications"
    actions = [approve, reject]

    def has_add_permission(self, request, obj=None):
        return True

    def has_change_permission(self, request, obj=None):
        return False


class RsvpAdminForm(forms.ModelForm):
    class Meta:
        model = Rsvp
        fields = ["notes", "hacker"]


class RsvpAdmin(admin.ModelAdmin):
    form = RsvpAdminForm
    list_display = ("hacker_name", "notes")
    fieldsets = [
        ("Related Objects", {"fields": ["hacker"]}),
        ("Logistical Information", {"fields": ["notes"]}),
    ]

    def has_add_permission(self, request, obj=None):
        return True

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def hacker_name(self, obj: Rsvp):
        return " ".join([obj.hacker.first_name, obj.hacker.last_name])

admin.site.register(Hacker, HackerAdmin)
admin.site.register(Application, ApplicationAdmin)
admin.site.register(Rsvp, RsvpAdmin)
admin.site.register(Wave, WaveAdmin)
