from django.contrib import admin

from application.admin import ApplicationAdminInline

from .models import Team


class TeamAdmin(admin.ModelAdmin):
    inlines = (ApplicationAdminInline,)


admin.site.register(Team, TeamAdmin)
