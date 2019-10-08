from django.urls import reverse_lazy

from application.models import Application
from shared import test_case
from team.models import Team
from user.models import User


class JoinTeamViewTestCase(test_case.SharedTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.team_fields = {"name": "New Team Name"}

    def test_redirects_if_not_logged_in(self):
        response = self.client.get(reverse_lazy("team:join"))

        self.assertRedirects(
            response,
            f"{reverse_lazy('customauth:login')}?next={reverse_lazy('team:join')}",
        )

    def test_fails_if_user_hasnt_applied(self):
        self.client.force_login(self.user)
        team: Team = Team.objects.create(**self.team_fields)

        self.client.post(reverse_lazy("team:join"), data={"id": team.pk})

        self.assertNotEqual(self.user.team, team)

    def test_fails_if_user_on_different_team(self):
        self.client.force_login(self.user)
        team: Team = Team.objects.create(**self.team_fields)
        other_team: Team = Team.objects.create(name="Other Team Name")
        self.user.team = team
        self.user.save()

        self.client.post(reverse_lazy("team:join"), data={"id": other_team.pk})
        self.user.refresh_from_db()

        self.assertNotEqual(self.user.team, other_team)

    def test_fails_if_team_full(self):
        self.create_active_wave()
        self.client.force_login(self.user)
        team: Team = Team.objects.create(**self.team_fields)
        emails = [
            "a@gmail.com",
            "b@gmail.com",
            "c@gmail.com",
            "d@gmail.com",
            "e@gmail.com",
        ]
        password = "A"
        for email in emails:
            user = User.objects.create_user(email, password, is_active=True)
            app_fields = self.application_fields
            app_fields["user"] = user
            Application.objects.create(**app_fields, wave=self.wave1)
            user.team = team
            user.save()
        Application.objects.create(**self.application_fields, wave=self.wave1)

        self.client.post(reverse_lazy("team:join"), data={"id:": team.pk})
        self.user.refresh_from_db()

        self.assertNotEqual(self.user.team, team)

    def test_succeeds(self):
        self.create_active_wave()
        self.client.force_login(self.user)
        team: Team = Team.objects.create(**self.team_fields)
        Application.objects.create(**self.application_fields, wave=self.wave1)

        self.client.post(reverse_lazy("team:join"), data={"id": team.pk})
        self.user.refresh_from_db()

        self.assertEqual(self.user.team, team)
