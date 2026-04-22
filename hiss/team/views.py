import structlog
from django import views
from django.contrib.auth import mixins
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest, JsonResponse

from application.models import Application
from team.models import Team

logger = structlog.get_logger()


class CreateTeamView(mixins.LoginRequiredMixin, views.View):
    """Create a new Team with the current user as captain and return the invite link."""

    def post(self, request: HttpRequest, *_args, **_kwargs):
        if Team.objects.filter(captain=request.user).exists():
            raise PermissionDenied("You already captain a team.") #change message?
        team = Team.objects.create(captain=request.user)
        invite_link = request.build_absolute_uri(f"/team/join/{team.id}")
        logger.info("Created team", team_pk=team.pk, user_pk=request.user.pk)
        return JsonResponse({"team_id": str(team.id), "invite_link": invite_link})


class RemoveMemberView(mixins.LoginRequiredMixin, views.View):
    """Remove a member from a team. Used for both kicks and self-removal.

    Expects the target application's pk in the URL.
    """

    def post(self, request: HttpRequest, *_args, **_kwargs):
        pk = self.kwargs["pk"]
        app: Application = Application.objects.get(pk=pk)
        if app.team is None:
            return JsonResponse({"ok": True})
        if request.user != app.user and request.user != app.team.captain:
            raise PermissionDenied("You don't have permission to remove this member.")
        app.team = None
        app.save()
        logger.info(
            "Removed member from team", app_pk=app.pk, actor_pk=request.user.pk
        )
        return JsonResponse({"ok": True})


class DeleteTeamView(mixins.LoginRequiredMixin, views.View):
    """Deactivate a team. Only works when no members remain."""

    def post(self, request: HttpRequest, *_args, **_kwargs):
        pk = self.kwargs["pk"]
        team: Team = Team.objects.get(pk=pk)
        if request.user != team.captain:
            raise PermissionDenied("Only the team captain can delete the team.")
        if team.get_members().exists():
            raise PermissionDenied("Cannot delete a team that still has members.")
        team.is_active = False
        team.save()
        logger.info("Deactivated team", team_pk=team.pk)
        return JsonResponse({"ok": True})
