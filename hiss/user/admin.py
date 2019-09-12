from django.contrib import admin
from django.utils import timezone

from user.models import User


def check_in(modeladmin, request, queryset):  #TO-DO: Needs to be tested!!!
    queryset.update(checked_in=True)
    queryset.update(checked_in_datetime=timezone.datetime.now())

class UserAdmin(admin.ModelAdmin):
    list_display = ("email", "is_active", "is_staff", "checked_in")
    readonly_fields = ("email", "password", "is_active")
    fieldsets = [
        ("User Informatino", {"fields": ["email", "password"]}),
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
            {
                "fields": ["application", "rsvp"],
                "classes": ["collapse"],
            },
        ),
    ]

    check_in.short_description = "Check-In Selected Hackers"
    actions = [check_in]

    def has_add_permissions(self, request, obj=None):
        return True

    def has_change_permissions(self, request, obj=None):
        return True


admin.site.register(User, UserAdmin)