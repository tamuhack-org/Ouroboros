from django.contrib import admin
from django.db.models import QuerySet

from application.admin import ApplicationAdminInline

from .models import Team


@admin.action(description="Accept selected team")
def approve(modeladmin, request, queryset: QuerySet[Team]):
    apps = [team.get_members() for team in queryset]
    print(apps)


class TeamAdmin(admin.ModelAdmin):
    inlines = (ApplicationAdminInline,)
    actions = [approve]


admin.site.register(Team, TeamAdmin)
