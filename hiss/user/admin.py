import csv

from django.contrib import admin
from django.contrib.auth.models import Group
from django.db.models import Exists, OuterRef
from django.db.models.query import QuerySet
from django.http import HttpRequest, HttpResponse
from rest_framework.authtoken.admin import TokenAdmin as BaseTokenAdmin
from rest_framework.authtoken.models import TokenProxy
from unfold.admin import ModelAdmin
from unfold.contrib.filters.admin import BooleanRadioFilter, RadioFilter
from unfold.decorators import display

from application.models import Application
from user.forms import GroupAdminForm
from user.models import User


@admin.action(description="Export emails of selected users (CSV)")
def export_user_emails(_modeladmin, _request: HttpRequest, queryset: QuerySet):
    """Export the emails related to the selected `User`s to a CSV file."""
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="emails.csv"'

    writer = csv.writer(response)
    for instance in queryset:
        writer.writerow([instance.email])

    return response


class HasAppliedFilter(RadioFilter):
    title = "Has applied"
    parameter_name = "has_applied"

    def lookups(self, request, model_admin):
        return (("Yes", "Yes"), ("No", "No"))

    def queryset(self, _request, queryset):
        value = self.value()
        if value == "Yes":
            return queryset.filter(application__isnull=False)
        if value == "No":
            return queryset.filter(application__isnull=True)
        return queryset


class UserAdmin(ModelAdmin):
    list_display = ("email", "is_active", "is_staff", "has_applied", "last_login")
    list_filter = (
        HasAppliedFilter,
        ("is_staff", BooleanRadioFilter),
        ("is_active", BooleanRadioFilter),
    )
    list_filter_submit = True
    search_fields = ("email",)
    search_help_text = "Search by email"
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
    list_per_page = 100

    actions = [export_user_emails]

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .annotate(
                has_application=Exists(Application.objects.filter(user=OuterRef("pk")))
            )
        )

    @display(description="Applied", boolean=True, ordering="has_application")
    def has_applied(self, obj: User) -> bool:
        return obj.has_application


# Create a new Group admin.
class GroupAdmin(ModelAdmin):
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


# Restyle Django REST Framework's token admin with Unfold.
admin.site.unregister(TokenProxy)


@admin.register(TokenProxy)
class TokenAdmin(BaseTokenAdmin, ModelAdmin):
    pass
