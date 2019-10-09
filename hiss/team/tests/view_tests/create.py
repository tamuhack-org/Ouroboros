from django.urls import reverse_lazy

from shared import test_case
from team.models import Team


class CreateTeamViewTestCase(test_case.SharedTestCase):
    def setUp(self):
        super().setUp()
        self.team_fields = {"name": "New Team Name"}

    def test_redirects_if_not_logged_in(self):
        response = self.client.get(reverse_lazy("team:create"))

        self.assertRedirects(
            response,
            f"{reverse_lazy('customauth:login')}?next={reverse_lazy('team:create')}",
        )

    def test_fails_if_user_already_on_different_team(self):
        self.client.force_login(self.user)
        old_team = Team.objects.create(name="Old team")
        self.user.team = old_team
        self.user.save()

        self.client.post(reverse_lazy("team:create"), data=self.team_fields)

        self.assertEqual(self.user.team, old_team)

    # def test_successful_team_creation(self):
    #     self.client.force_login(self.user)
    #
    #     response = self.client.post(reverse_lazy("team:create"), data=self.team_fields)
    #     self.user.refresh_from_db()
    #
    #     self.assertIsNotNone(self.user.team)
    #     self.assertRedirects(response, reverse_lazy("team:detail", args=[self.user.team.pk]))
