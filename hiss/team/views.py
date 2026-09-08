from uuid import UUID

import structlog
from django import views
from django.contrib.auth import mixins
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.http import Http404, HttpRequest, JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse

from application.constants import STATUS_PENDING
from application.models import Application
from status.views import StatusBaseView
from team.models import Team

logger = structlog.get_logger()


class MyTeamView(mixins.LoginRequiredMixin, views.View):
    """
    Get current application's team if it exists

    Create a new Team, mark the current user's application as captain, return the invite link.
    """

    def get(self, request: HttpRequest, *_args, **_kwargs):
        app = Application.objects.filter(user=request.user).first()
        if app is None:
            msg = "You must have an application to view a team."
            raise PermissionDenied(msg)

        return JsonResponse(
            {
                "team_id": str(app.team.id),
                "is_captain": app.is_captain,
                "members": list(
                    app.team.get_members().values(
                        "first_name", "last_name", "is_captain"
                    )
                ),
            },
            status=200,
        )

    def post(self, request: HttpRequest, *_args, **_kwargs):
        app = Application.objects.filter(user=request.user).first()
        if app is None:
            msg = "You must have an application to create a team."
            raise PermissionDenied(msg)
        if app.status != STATUS_PENDING:
            msg = "You must be under review to create a team."
            raise PermissionDenied(msg)
        if app.team is not None:
            msg = "You are already on a team."
            raise PermissionDenied(msg)
        team = Team.objects.create()
        app.team = team
        app.is_captain = True
        app.save()
        logger.info("Created team", team_pk=team.pk, user_pk=request.user.pk)

        # send user to team page after creating team
        return redirect("status_team")


class TeamPageView(StatusBaseView):
    """Render the current user's team page."""

    template_name = "status/team.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        app: Application = context.get("application")

        if app is None or app.team is None:
            return context

        context["team"] = app.team
        context["invite_link"] = self.request.build_absolute_uri(
            reverse("team:join", kwargs={"pk": app.team.id})
        )
        context["self"] = app.id
        context["is_captain"] = app.is_captain
        context["members"] = list(
            app.team.get_members().values("first_name", "last_name", "is_captain", "id")
        )

        return context


class RemoveMemberView(mixins.LoginRequiredMixin, views.View):
    """Remove a member from a team. Used for both kicks and self-removal.

    Expects the target application's pk in the URL.
    """

    def post(self, request: HttpRequest, *_args, **_kwargs):
        pk = self.kwargs["pk"]
        app: Application = get_object_or_404(Application, pk=pk)
        if app.team is None:
            return redirect("status_team")
        if app.is_captain:
            msg = "The captain cannot leave the team; delete the team instead."
            raise PermissionDenied(msg)
        captain = app.team.captain
        is_self = request.user == app.user
        is_captain = captain is not None and request.user == captain.user
        if not is_self and not is_captain:
            msg = "You don't have permission to remove this member."
            raise PermissionDenied(msg)
        app.team = None
        app.is_captain = False
        app.save()
        logger.info("Removed member from team", app_pk=app.pk, actor_pk=request.user.pk)
        return redirect("status_team")


class DeleteTeamView(mixins.LoginRequiredMixin, views.View):
    """Deactivate a team. Only the captain can call it, and only when no other members remain."""

    def post(self, request: HttpRequest, *_args, **_kwargs):
        pk = self.kwargs["pk"]
        team: Team = Team.objects.get(pk=pk)
        app = Application.objects.filter(user=request.user, team=team).first()
        if app is None:
            msg = "You are not on this team."
            raise PermissionDenied(msg)
        if not app.is_captain:
            msg = "Only the team captain can delete the team."
            raise PermissionDenied(msg)
        if team.get_members().count() > 1:
            msg = "Cannot delete a team that still has members."
            raise PermissionDenied(msg)
        app.is_captain = False
        app.team = None
        app.save()
        team.is_active = False
        team.save()
        logger.info("Deactivated team", team_pk=team.pk)
        return redirect("status_team")


class JoinTeamView(mixins.LoginRequiredMixin, views.View):
    """Accept an invite and add application to team if prereq is met"""

    def post(self, request: HttpRequest, *_args, **_kwargs):
        pk = self.kwargs.get("pk")
        if pk is None:
            try:
                pk = UUID(request.POST.get("team_code", "").strip())
            except ValueError as exc:
                msg = "Invalid team code."
                raise Http404(msg) from exc
        team: Team = get_object_or_404(Team, pk=pk)
        app = Application.objects.filter(user=request.user).first()

        if app is None:
            base_url = reverse("application:create")
            return redirect(f"{base_url}?team_id={team.id}")

        if app.status != STATUS_PENDING:
            msg = "unable to join team: not under review"
            raise PermissionDenied(msg)

        if not team.is_active:
            msg = "unable to join team: desired team no longer exists"
            raise PermissionDenied(msg)

        if team.is_at_max_capacity:
            msg = "unable to join team: team is full"
            raise PermissionDenied(msg)

        if app.team:
            msg = "unable to join team: please leave/delete current team"
            raise PermissionDenied(msg)

        app.team = team
        app.save()

        logger.info("Joined team", team_pk=team.pk, user_pk=request.user.pk)
        return redirect("status_team")


class PromoteMemberView(mixins.LoginRequiredMixin, views.View):
    """Transfer captaincy to another member of the captain's team."""

    @transaction.atomic
    def post(self, request, **kwargs):
        target = get_object_or_404(Application, pk=kwargs["pk"])
        if target.team_id is None:
            msg = "This member has no team."
            raise PermissionDenied(msg)
        members = list(
            Application.objects.select_for_update()
            .filter(team_id=target.team_id)
            .order_by("pk")
        )
        captain = next((m for m in members if m.is_captain), None)
        target = next((m for m in members if m.pk == target.pk), None)
        if captain is None or captain.user_id != request.user.pk:
            msg = "Only the captain can transfer captaincy."
            raise PermissionDenied(msg)
        if target is None or target.is_captain:
            msg = "Choose another member of your team."
            raise PermissionDenied(msg)
        captain.is_captain = False
        captain.save(update_fields=["is_captain"])
        target.is_captain = True
        target.save(update_fields=["is_captain"])
        return redirect("status_team")
