from django.contrib import admin

from .models import Team


class TeamAdmin(admin.ModelAdmin):
    list_select_related = ["application"]


admin.site.register(Team, TeamAdmin)
