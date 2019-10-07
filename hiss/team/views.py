from django.conf import settings
from django.contrib.auth import mixins
from django.shortcuts import redirect
from django.views import generic

# Create your views here.
from team.forms import CreateTeamForm, JoinTeamForm
from team.models import Team
from user.models import User


class CreateTeamView(mixins.UserPassesTestMixin, generic.CreateView):
    """
    If the user has applied, creates a Team and adds the User to it.
    """

    form_class = CreateTeamForm
    template_name = "team/team_form.html"

    def test_func(self) -> bool:
        # Ensure user is logged-in
        user: User = self.request.user
        if not user.is_authenticated:
            return False

        # Ensure user has applied
        if not user.application_set.exists():
            return False
        return True

    def form_valid(self, form: CreateTeamForm):
        team: Team = form.save(commit=False)
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


class JoinTeamView(mixins.UserPassesTestMixin, generic.FormView):
    """
    Adds the user to a team (if the team isn't already at capacity).
    """

    form_class = JoinTeamForm
    template_name = "team/join_form.html"

    def test_func(self) -> bool:
        # Ensure user is logged-in
        user: User = self.request.user
        if not user.is_authenticated:
            return False

        # Ensure user has applied
        if not user.application_set.exists():
            return False
        return True

    def get_success_url(self):
        return self.request.user.team.get_absolute_url()

    def form_valid(self, form: JoinTeamForm):
        team: Team = Team.objects.get(id=form.cleaned_data["id"])
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


class DetailTeamView(mixins.LoginRequiredMixin, generic.DetailView):
    """
    Renders a Team if the User is a member.
    """

    pass
