from django.contrib import admin
from django_admin_listfilter_dropdown.filters import ChoiceDropdownFilter
from rangefilter.filters import DateTimeRangeFilter

from volunteer.models import FoodEvent, WorkshopEvent


class FoodEventAdmin(admin.ModelAdmin):
    list_filter = (
        ("timestamp", DateTimeRangeFilter),
        ("meal", ChoiceDropdownFilter),
    )
    list_display = ("timestamp", "meal", "user")


class WorkshopEventAdmin(admin.ModelAdmin):
    list_filter = (("timestamp", DateTimeRangeFilter),)
    list_display = ("timestamp", "user")


admin.site.register(FoodEvent, FoodEventAdmin)
admin.site.register(WorkshopEvent, WorkshopEventAdmin)
