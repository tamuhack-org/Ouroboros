from django import forms
from django.contrib import admin

# Register your models here.
from rsvp.models import Rsvp


class RsvpAdminForm(forms.ModelForm):
    class Meta:
        model = Rsvp
        fields = ["user", "dietary_restrictions", "shirt_size"]


class RsvpAdmin(admin.ModelAdmin):
    form = RsvpAdminForm
    list_display = ("user", "notes")
    fieldsets = [
        ("Related Objects", {"fields": ["user"]}),
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
