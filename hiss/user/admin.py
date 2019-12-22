import csv

from django.contrib import admin
from django.contrib.auth.models import Group
from django.db.models.query import QuerySet
from django.http import HttpRequest, HttpResponse

from user.forms import GroupAdminForm
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


class HasAppliedFilter(admin.SimpleListFilter):
    title = "has_applied"
    parameter_name = "has_applied"

    def lookups(self, request, model_admin):
        return (("Yes", "Yes"), ("No", "No"))

    def queryset(self, request, queryset):
        value = self.value()
        if value == "Yes":
            return queryset.filter(application__isnull=False)
        elif value == "No":
            return queryset.filter(application__isnull=True)
        return queryset


class UserAdmin(admin.ModelAdmin):
    list_display = (
        "email",
        "is_active",
        "is_staff",
        "has_applied",
    )
    list_filter = ("is_active", "is_staff", HasAppliedFilter)
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


# Create a new Group admin.
class GroupAdmin(admin.ModelAdmin):
    # Use our custom form.
    form = GroupAdminForm
    # Filter permissions horizontal as well.
    filter_horizontal = ["permissions"]


admin.site.register(User, UserAdmin)

# The following code is taken from https://stackoverflow.com/a/39648244
# Unregister the original Group admin.
admin.site.unregister(Group)
# Register the new Group ModelAdmin.
admin.site.register(Group, GroupAdmin)
