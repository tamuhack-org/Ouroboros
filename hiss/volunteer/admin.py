from django.contrib import admin, messages
from django.shortcuts import redirect
from unfold.admin import ModelAdmin
from unfold.contrib.filters.admin import (
    MultipleChoicesDropdownFilter,
    RangeDateTimeFilter,
)
from unfold.decorators import action

from shared.mixins import ListTitleMixin
from volunteer.models import FoodEvent, ScheduleEvent, WorkshopEvent
from volunteer.schedule_import import ScheduleImportError, import_schedule


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


class ScheduleEventAdmin(ListTitleMixin, ModelAdmin):
    list_title = "Schedule"
    list_display = ("name", "start", "location", "category", "is_visible")
    list_editable = ("category", "is_visible")
    list_filter = (
        ("start", RangeDateTimeFilter),
        "is_visible",
    )
    list_filter_submit = True
    search_fields = ("name", "location")
    actions_list = ["import_from_website"]

    @action(
        description="Import from website",
        icon="cloud_download",
        permissions=["add"],
    )
    def import_from_website(self, request):
        try:
            created, updated = import_schedule()
        except ScheduleImportError as e:
            messages.error(request, str(e))
        else:
            messages.success(
                request, f"Imported schedule: {created} new, {updated} updated."
            )
        return redirect("admin:volunteer_scheduleevent_changelist")


admin.site.register(FoodEvent, FoodEventAdmin)
admin.site.register(WorkshopEvent, WorkshopEventAdmin)
admin.site.register(ScheduleEvent, ScheduleEventAdmin)
