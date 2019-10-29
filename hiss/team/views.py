from typing import Optional

from django.conf import settings
from django.http import HttpRequest
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views import generic

from shared import mixins as shared_mixins

from team.forms import CreateTeamForm, JoinTeamForm
from team.models import Team
from user.models import User
from application.models import Application


class CreateTeamView(shared_mixins.UserHasNoTeamMixin, generic.CreateView):
    """
    If the user has applied, creates a Team and adds the User to it.
    """

    form_class = CreateTeamForm
    template_name = "team/team_form.html"

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return redirect(
                f"{reverse_lazy('customauth:login')}?next={reverse_lazy('team:create')}"
            )
        return redirect(reverse_lazy("status"))

    def form_valid(self, form: CreateTeamForm):
        team: Team = form.save()
        user: User = self.request.user
        if self.request.user.team is not None:
            form.add_error(
                None,
                "You cannot create a new team while currently on a team. Please leave your current team "
                "and try again.",
            )
            return self.form_invalid(form)
        user.team = team
        user.save()
        return redirect(team.get_absolute_url())


class JoinTeamView(shared_mixins.UserHasNoTeamMixin, generic.FormView):
    """
    Adds the user to a team (if the team isn't already at capacity).
    """

    form_class = JoinTeamForm
    template_name = "team/join_form.html"

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return redirect(
                f"{reverse_lazy('customauth:login')}?next={reverse_lazy('team:join')}"
            )
        return redirect(reverse_lazy("status"))

    def get_success_url(self):
        return self.request.user.team.get_absolute_url()

    def form_valid(self, form: JoinTeamForm):
        team: Optional[Team] = Team.objects.filter(id=form.cleaned_data["id"]).first()
        if not team:
            form.add_error(None, "No such team exists.")
            return self.form_invalid(form)
        if team.members.count() == settings.MAX_MEMBERS_PER_TEAM:
            form.add_error(None, "This team is already at capacity.")
            return self.form_invalid(form)
        if self.request.user.team is not None:
            form.add_error(
                None,
                "You cannot be on more than one team at a time. Please leave your existing team and try "
                "again.",
            )
            return self.form_invalid(form)
        self.request.user.team = team
        self.request.user.save()
        return super().form_valid(form)


class DetailTeamView(shared_mixins.UserHasTeamMixin, generic.DetailView):
    """
    Renders a Team if the User is a member.
    """

    model = Team
    template_name = "team/team_detail.html"

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            team_pk = self.kwargs["pk"]
            return redirect(
                f"{reverse_lazy('customauth:login')}?next={reverse_lazy('team:detail', args=[team_pk])}"
            )
        if not Application.objects.filter(user=self.request.user.pk):
            return redirect(reverse_lazy("status"))
        if self.request.user.team is None:
            return redirect(reverse_lazy("team:join"))
        return redirect(reverse_lazy("status"))

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        team: Team = self.get_object()
        member_applications = [
            member.application_set.first() for member in team.members.all()
        ]
        context_data["member_applications"] = member_applications
        return context_data

    def get(self, request, *args, **kwargs):
        team: Team = self.get_object()
        if self.request.user.team != team:
            return redirect(
                reverse_lazy("team:detail", args=[self.request.user.team.pk])
            )
        return super().get(request, *args, **kwargs)


class LeaveTeamView(shared_mixins.LoginRequiredAndAppliedMixin, generic.base.View):
    """
    Removes a User from a Team. If the Team no longer has members, deletes the Team.
    """

    def post(self, request: HttpRequest, *_args, **_kwargs):
        team: Team = request.user.team
        request.user.team = None
        request.user.save()

        team.refresh_from_db()
        if team.members.count() == 0:
            team.delete()
        return redirect(reverse_lazy("status"))
