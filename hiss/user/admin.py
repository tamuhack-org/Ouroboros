import csv

from django.contrib import admin
from django.db.models.query import QuerySet
from django.http import HttpRequest, HttpResponse
from django_admin_listfilter_dropdown.filters import ChoiceDropdownFilter

from user.models import User


def export_user_emails(_modeladmin, _request: HttpRequest, queryset: QuerySet):
    """
    Exports the emails related to the selected `User`s to a CSV file
    """
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="emails.csv"'

    writer = csv.writer(response)
    for instance in queryset:
        writer.writerow([instance.email])

    return response


class UserAdmin(admin.ModelAdmin):
    list_display = ("email", "is_active", "is_staff", "has_applied")
    list_filter = (
        ("is_active", ChoiceDropdownFilter),
        ("is_staff", ChoiceDropdownFilter),
        ("has_applied", ChoiceDropdownFilter),
    )
    readonly_fields = ("email", "password")
    fieldsets = [
        ("User Information", {"fields": ["email", "password"]}),
        (
            "Advanced",
            {
                "fields": ["is_superuser", "is_staff", "is_active"],
                "classes": ["collapse"],
            },
        ),
    ]
    list_per_page = 2000

    export_user_emails.short_description = "Export Emails of Selected Users"
    actions = [export_user_emails]

    def has_applied(self, obj: User):
        return obj.application_set.exists()


admin.site.register(User, UserAdmin)
