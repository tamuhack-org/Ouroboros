from django.urls import reverse_lazy

from application.models import Application
from shared import test_case
from team.models import Team


class LeaveTeamViewTestCase(test_case.SharedTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.team_fields = {"name": "New Team Name"}

    def test_redirects_if_not_logged_in(self):
        Team.objects.create(**self.team_fields)

        response = self.client.post(reverse_lazy("team:leave"))

        self.assertRedirects(
            response,
            f"{reverse_lazy('customauth:login')}?next={reverse_lazy('team:leave')}",
        )

    def test_fails_if_user_hasnt_applied(self):
        self.client.force_login(self.user)
        team: Team = Team.objects.create(**self.team_fields)

        response = self.client.post(reverse_lazy("team:leave"))

        self.assertEqual(response.status_code, 403)
        self.assertNotEqual(self.user.team, team)

    def test_redirects_after_successful_removal(self):
        self.client.force_login(self.user)
        self.create_active_wave()
        Application.objects.create(**self.application_fields, wave=self.wave1)
        team: Team = Team.objects.create(**self.team_fields)
        self.user.team = team
        self.user.save()

        response = self.client.post(reverse_lazy("team:leave"))

        self.assertRedirects(response, reverse_lazy("status"))

    def test_removes_user_from_team(self):
        self.client.force_login(self.user)
        self.create_active_wave()
        Application.objects.create(**self.application_fields, wave=self.wave1)
        team: Team = Team.objects.create(**self.team_fields)
        self.user.team = team
        self.user.save()

        self.client.post(reverse_lazy("team:leave"))
        self.user.refresh_from_db()

        self.assertIsNone(self.user.team)

    def test_deletes_team_with_no_members(self):
        self.client.force_login(self.user)
        self.create_active_wave()
        Application.objects.create(**self.application_fields, wave=self.wave1)
        team: Team = Team.objects.create(**self.team_fields)
        self.user.team = team
        self.user.save()

        self.client.post(reverse_lazy("team:leave"))

        self.assertFalse(Team.objects.filter(id=team.pk).exists())
