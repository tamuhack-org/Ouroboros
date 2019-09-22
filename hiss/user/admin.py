from django.contrib import admin
from django.utils import timezone

from user.models import User


def check_in(_modeladmin, _request, queryset) -> None:
    """
    Sets the value of the `checked_in` for the selected `User`s to `True`
    """
    queryset.update(checked_in=True)
    queryset.update(checked_in_at=timezone.datetime.now())


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
        (
            "Related Objects",
            {"fields": ["application", "rsvp"], "classes": ["collapse"]},
        ),
    ]

    check_in.short_description = "Check-In Selected Hackers"
    actions = [check_in]


admin.site.register(User, UserAdmin)
