from datetime import datetime

from django.contrib import admin
from django.db.models import Count
from django.http import HttpRequest
from django.urls import reverse
from unfold.admin import ModelAdmin
from unfold.contrib.filters.admin import BooleanRadioFilter, DropdownFilter
from unfold.decorators import action, display
from unfold.enums import ActionVariant

from application.admin import ApplicationAdminInline, confirm_application_action
from application.models import Application

from .models import Team, TeamStatus

TEAM_STATUS_VARIANTS = {
    TeamStatus.ACCEPTED: "success",
    TeamStatus.REJECTED: "danger",
    TeamStatus.IN_REVIEW: "info",
    TeamStatus.MIXED: "warning",
}


class TeamStatusFilter(DropdownFilter):
    title = "Team status"
    parameter_name = "team_status"

    def lookups(self, request, model_admin):
        return TeamStatus.choices

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(computed_team_status=self.value())
        return queryset


class TeamAdmin(ModelAdmin):
    inlines = (ApplicationAdminInline,)
    list_display = (
        "__str__",
        "member_count",
        "latest_submission_date",
        "team_status",
    )
    list_filter = (TeamStatusFilter, ("is_active", BooleanRadioFilter))
    list_filter_submit = True
    actions_detail = ["approve_team"]

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .with_team_status()
            .order_by_latest_submission()
            .annotate(member_total=Count("members"))
            .prefetch_related("members")
        )

    @display(description="Members", ordering="member_total")
    def member_count(self, obj: Team) -> int:
        return obj.member_total

    @display(description="Latest submission", ordering="latest_submission")
    def latest_submission_date(self, obj: Team) -> datetime | None:
        return obj.latest_submission

    @display(
        description="Team status", ordering="computed_team_status", label=TEAM_STATUS_VARIANTS
    )
    def team_status(self, obj: Team) -> tuple[str, str]:
        status = TeamStatus(obj.computed_team_status)
        return status, status.label

    @action(description="Approve team", icon="check_circle", variant=ActionVariant.PRIMARY)
    def approve_team(self, request: HttpRequest, object_id: str):
        """Approve every application in the team, after confirmation."""
        members = Application.objects.filter(team_id=object_id)
        return confirm_application_action(
            self,
            request,
            members,
            "approve",
            next_url=reverse("admin:team_team_change", args=[object_id]),
        )


admin.site.register(Team, TeamAdmin)
