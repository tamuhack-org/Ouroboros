from django import forms
from django.contrib import admin

from rsvp.models import Rsvp


class RsvpAdminForm(forms.ModelForm):
    class Meta:
        model = Rsvp
        fields = ["dietary_restrictions", "shirt_size", "notes"]


class RsvpAdmin(admin.ModelAdmin):
    form = RsvpAdminForm
    list_display = ("full_name", "notes")
    fieldsets = [
        ("Related Objects", {"fields": ["user"]}),
        (
            "Logistical Information",
            {"fields": ["notes", "dietary_restrictions", "shirt_size"]},
        ),
    ]

    def has_change_permission(self, request: HttpRequest, obj=None) -> bool:
        return False

    def has_delete_permission(self, request: HttpRequest, obj=None) -> bool:
        return False

    @staticmethod
    def full_name() -> str:
        # TODO(SaltyQuetzals): Add a way to reference user's full name.
        return ""


admin.site.register(Rsvp, RsvpAdmin)
