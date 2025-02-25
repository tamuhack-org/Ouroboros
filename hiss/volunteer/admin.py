from django.contrib import admin
from django_admin_listfilter_dropdown.filters import ChoiceDropdownFilter
from rangefilter.filters import DateTimeRangeFilter

from volunteer.models import FoodEvent, WorkshopEvent


class FoodEventAdmin(admin.ModelAdmin):
    list_filter = (
        ("timestamp", DateTimeRangeFilter),
        ("meal", ChoiceDropdownFilter),
        ("restrictions", admin.filters.RelatedOnlyFieldListFilter),
    )
    list_display = ("timestamp", "meal", "get_restrictions", "user")

    def get_restrictions(self, obj: FoodEvent):
        return ", ".join([r.name for r in obj.restrictions.all()])


class WorkshopEventAdmin(admin.ModelAdmin):
    list_filter = (("timestamp", DateTimeRangeFilter),)
    list_display = ("timestamp", "user")


admin.site.register(FoodEvent, FoodEventAdmin)
admin.site.register(WorkshopEvent, WorkshopEventAdmin)
