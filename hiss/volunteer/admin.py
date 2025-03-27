from django.contrib import admin
from rangefilter.filters import DateTimeRangeFilter
from unfold.contrib.filters.admin import RangeDateTimeFilter,ChoicesDropdownFilter
from volunteer.models import FoodEvent, WorkshopEvent


class FoodEventAdmin(admin.ModelAdmin):
    """Defines filters and display of the food section of admin portal"""
    list_filter = (
        ("timestamp", RangeDateTimeFilter),
        ("meal", ChoicesDropdownFilter),
    )
    list_display = ("timestamp", "meal", "user")


class WorkshopEventAdmin(admin.ModelAdmin):
    """Defines filters and display of the workshop section of admin portal"""
    list_filter = (("timestamp", RangeDateTimeFilter),)
    list_display = ("timestamp", "user")


admin.site.register(FoodEvent, FoodEventAdmin)
admin.site.register(WorkshopEvent, WorkshopEventAdmin)
