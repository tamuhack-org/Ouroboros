from django.urls import reverse_lazy

from application.models import Application
from shared import test_case
from team.models import Team


class DetailTeamViewTestCase(test_case.SharedTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.team_fields = {"name": "New Team Name"}

    def test_redirects_if_not_logged_in(self):
        team: Team = Team.objects.create(**self.team_fields)
        response = self.client.get(reverse_lazy("team:detail", args=[team.pk]))

        self.assertRedirects(
            response,
            f"{reverse_lazy('customauth:login')}?next={reverse_lazy('team:detail', args=[team.pk])}",
        )

    def test_fails_if_user_not_applied(self):
        team: Team = Team.objects.create(**self.team_fields)
        self.client.force_login(self.user)

        response = self.client.get(reverse_lazy("team:detail", args=[team.pk]))

        self.assertEqual(response.status_code, 403)

    def test_redirects_if_user_not_member(self):
        team: Team = Team.objects.create(**self.team_fields)
        self.client.force_login(self.user)
        self.create_active_wave()
        Application.objects.create(**self.application_fields, wave=self.wave1)

        response = self.client.get(reverse_lazy("team:detail", args=[team.pk]))

        self.assertRedirects(response, reverse_lazy("team:join"))

    def test_redirects_if_user_member_of_different_team(self):
        team: Team = Team.objects.create(**self.team_fields)
        other_team: Team = Team.objects.create(**self.team_fields)
        self.client.force_login(self.user)
        self.create_active_wave()
        Application.objects.create(**self.application_fields, wave=self.wave1)
        self.user.team = other_team
        self.user.save()

        response = self.client.get(reverse_lazy("team:detail", args=[team.pk]))

        self.assertRedirects(response, reverse_lazy("team:join"))

    def test_succeeds_if_user_member_of_team(self):
        team: Team = Team.objects.create(**self.team_fields)
        self.client.force_login(self.user)
        self.create_active_wave()
        Application.objects.create(**self.application_fields, wave=self.wave1)
        self.user.team = team
        self.user.save()

        response = self.client.get(reverse_lazy("team:detail", args=[team.pk]))

        self.assertEqual(response.status_code, 200)
