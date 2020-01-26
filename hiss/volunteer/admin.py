from django.contrib import admin
from rangefilter.filter import DateTimeRangeFilter

from volunteer.models import FoodEvent, WorkshopEvent


class FoodEventAdmin(admin.ModelAdmin):
    list_filter = (("timestamp", DateTimeRangeFilter),)


class WorkshopEventAdmin(admin.ModelAdmin):
    list_filter = (("timestamp", DateTimeRangeFilter),)


admin.site.register(FoodEvent, FoodEventAdmin)
admin.site.register(WorkshopEvent, WorkshopEventAdmin)
