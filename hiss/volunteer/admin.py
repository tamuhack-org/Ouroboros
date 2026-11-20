from django.contrib import admin
from unfold.admin import ModelAdmin
from unfold.contrib.filters.admin import (
    MultipleChoicesDropdownFilter,
    RangeDateTimeFilter,
)

from shared.mixins import ListTitleMixin
from volunteer.models import FoodEvent, WorkshopEvent


class FoodEventAdmin(ListTitleMixin, ModelAdmin):
    list_title = "Food"
    list_filter = (
        ("timestamp", RangeDateTimeFilter),
        ("meal", MultipleChoicesDropdownFilter),
    )
    list_filter_submit = True
    list_display = ("timestamp", "meal", "user")
    list_select_related = ("user",)
    search_fields = ("user__email",)


class WorkshopEventAdmin(ListTitleMixin, ModelAdmin):
    list_title = "Workshops"
    list_filter = (("timestamp", RangeDateTimeFilter),)
    list_filter_submit = True
    list_display = ("timestamp", "user")
    list_select_related = ("user",)
    search_fields = ("user__email",)


admin.site.register(FoodEvent, FoodEventAdmin)
admin.site.register(WorkshopEvent, WorkshopEventAdmin)
