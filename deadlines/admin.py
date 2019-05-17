from django.contrib import admin
from deadlines import models

# Register your models here.
class DeadlineAdmin(admin.ModelAdmin):
    list_display = ("pk", "datetime", "type")

admin.site.register(models.Deadline, DeadlineAdmin)
