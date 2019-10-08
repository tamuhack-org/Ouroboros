import csv

from django.contrib import admin

# Register your models here.
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse
from django import forms

from application.admin import approve, reject
from team.models import Team


def approve_team(_model_admin, _request: HttpRequest, queryset: QuerySet) -> None:
    for team in queryset:
        applications = [member.application_set.first() for member in team.members.all()]
        approve(None, None, applications)


def reject_team(_model_admin, _request: HttpRequest, queryset: QuerySet) -> None:
    for team in queryset:
        applications = [member.application_set.first() for member in team.members.all()]
        reject(None, None, applications)


def export_team_emails(_model_admin, _request: HttpRequest, queryset: QuerySet) -> None:
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="emails.csv"'

    writer = csv.writer(response)
    for team in queryset:
        for member in team.members.all():
            writer.writerow([member.email])

    return response


class TeamAdminForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = "__all__"


class TeamAdmin(admin.ModelAdmin):
    form = TeamAdminForm
    list_display = ("name", "admitted")
    actions = [approve_team, reject_team, export_team_emails]


admin.site.register(Team, TeamAdmin)
