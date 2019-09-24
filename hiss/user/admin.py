import csv

from pdb import set_trace as bp

from django.contrib import admin
from django.db import transaction
from django.http import HttpResponse
from django.utils import timezone

from user.models import User


def check_in(_modeladmin, _request, queryset) -> None:
    """
    Sets the value of the `checked_in` for the selected `User`s to `True`
    """
    queryset.update(checked_in=True)
    queryset.update(checked_in_at=timezone.datetime.now())


def export_emails(_modeladmin, _request, queryset):
    """
    Exports the emails related to the selected `User`s to a CSV file
    """
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="emails.csv"'

    writer = csv.writer(response)
    for instance in queryset:
        writer.writerow([instance.email])

    pb()

    return response


class UserAdmin(admin.ModelAdmin):
    list_display = ("email", "is_active", "is_staff", "checked_in")
    readonly_fields = ("email", "password")
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

    check_in.short_description = "Check-In Selected Users"
    export_emails.short_description = "Export Emails of Selected Users"
    actions = [check_in, export_emails]


admin.site.register(User, UserAdmin)
