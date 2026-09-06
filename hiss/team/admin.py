from django.contrib import admin

from .models import Team


class TeamAdmin(admin.ModelAdmin):
    pass


admin.site.register(Team, TeamAdmin)
