import structlog
from django import views
from django.contrib.auth import mixins
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest, JsonResponse

from application.models import Application
from application.models import STATUS_PENDING
from team.models import Team

logger = structlog.get_logger()


class CreateTeamView(mixins.LoginRequiredMixin, views.View):
    """Create a new Team, mark the current user's application as captain, return the invite link."""

    def post(self, request: HttpRequest, *_args, **_kwargs):
        app = Application.objects.filter(user=request.user).first()
        if app is None:
            msg = "You must have an application to create a team."
            raise PermissionDenied(msg)
        if app.team is not None:
            msg = "You are already on a team."
            raise PermissionDenied(msg)
        team = Team.objects.create()
        app.team = team
        app.is_captain = True
        app.save()
        invite_link = request.build_absolute_uri(f"/team/join/{team.id}")
        logger.info("Created team", team_pk=team.pk, user_pk=request.user.pk)
        return JsonResponse(
            {"team_id": str(team.id), "invite_link": invite_link},
            status=201,
        )


class RemoveMemberView(mixins.LoginRequiredMixin, views.View):
    """Remove a member from a team. Used for both kicks and self-removal.

    Expects the target application's pk in the URL.
    """

    def post(self, request: HttpRequest, *_args, **_kwargs):
        pk = self.kwargs["pk"]
        app: Application = Application.objects.get(pk=pk)
        if app.team is None:
            return JsonResponse({"ok": True})
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
        logger.info(
            "Removed member from team", app_pk=app.pk, actor_pk=request.user.pk
        )
        return JsonResponse({"ok": True})


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
        return JsonResponse({"ok": True})

class JoinTeamView(mixins.LoginRequiredMixin, views.View):
    """Accept an invite and add application to team if prereq is met"""
    def post(self, request: HttpRequest, *_args, **_kwargs):
        pk = self.kwargs["pk"]
        team: Team = Team.objects.get(pk=pk)
        app = Application.objects.filter(user=request.user).first()

        if app is None:
            msg = "unable to join team: not applied yet"
            raise PermissionDenied(msg)

        if app.status != STATUS_PENDING:
            msg = "unable to join team: not under review"
            raise PermissionDenied(msg)

        if team.is_at_max_capacity():
            msg = "unable to join team: team is full"
            raise PermissionDenied(msg)

        if app.team:
            msg = "unable to join team: please leave/delete current team"
            raise PermissionDenied(msg)


        app.team = team
        app.save()

        logger.info("Joined team", team_pk=team.pk, user_pk=request.user.pk)
        return JsonResponse({"ok": True})
