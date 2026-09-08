from django.urls import reverse

from application.constants import STATUS_REJECTED
from application.models import Application
from shared.test_case import SharedTestCase
from team.models import Team


class TeamActionsTestCase(SharedTestCase):
    def setUp(self):
        super().setUp()
        self.create_active_wave()
        fields = {**self.application_fields, "wave": self.wave1, "resume": "resume.pdf"}
        self.team = Team.objects.create()
        self.captain = Application.objects.create(
            **fields, team=self.team, is_captain=True
        )
        self.member = Application.objects.create(**{**fields, "user": self.user2})
        self.client.force_login(self.user2)

    def test_join_transfer_leave_and_delete(self):
        # Join team
        self.client.post(reverse("team:join-code"), {"team_code": str(self.team.pk)})

        # Transfer captaincy
        self.client.force_login(self.user)
        self.client.post(reverse("team:promote", kwargs={"pk": self.member.pk}))

        # Former captain leaves team
        self.client.post(reverse("team:remove_member", kwargs={"pk": self.captain.pk}))

        # New captain deletes the team and leaves
        self.client.force_login(self.user2)
        self.client.post(reverse("team:delete", kwargs={"pk": self.team.pk}))

        # Check: inactive team with no members or captains
        self.team.refresh_from_db()
        self.captain.refresh_from_db()
        self.member.refresh_from_db()
        self.assertFalse(self.team.is_active)
        self.assertEqual(self.team.members.count(), 0)
        self.assertIsNone(self.captain.team)
        self.assertFalse(self.captain.is_captain)
        self.assertIsNone(self.member.team)
        self.assertFalse(self.member.is_captain)

    def test_team_page_without_team_or_application(self):
        # View the team and status pages without a team
        team_page = self.client.get(reverse("status_team"))
        status_page = self.client.get(reverse("status"))

        # View the team page without an application
        self.client.force_login(self.admin)
        no_application_page = self.client.get(reverse("status_team"))

        # Check: joining is available and neither visitor encounters an error
        self.assertContains(team_page, 'name="team_code"')
        self.assertContains(status_page, "Join Team")
        self.assertEqual(no_application_page.status_code, 200)

    def test_non_captain_cannot_promote(self):
        # Try to promote w/o being in the team
        self.client.post(reverse("team:promote", kwargs={"pk": self.captain.pk}))

        # Join the team and attempt to promote yourself
        self.client.post(reverse("team:join-code"), {"team_code": str(self.team.pk)})
        self.client.post(reverse("team:promote", kwargs={"pk": self.member.pk}))

        # Check: the original captain remains in charge
        self.captain.refresh_from_db()
        self.member.refresh_from_db()
        self.assertEqual(self.captain.team, self.team)
        self.assertTrue(self.captain.is_captain)
        self.assertEqual(self.member.team, self.team)
        self.assertFalse(self.member.is_captain)
        self.assertEqual(self.team.members.filter(is_captain=True).count(), 1)

    def test_captain_cannot_promote_self_or_outsider(self):
        # Attempt to promote yourself
        self.client.force_login(self.user)
        self_promotion = self.client.post(
            reverse("team:promote", kwargs={"pk": self.captain.pk})
        )

        # Attempt to promote someone outside the team
        outsider_promotion = self.client.post(
            reverse("team:promote", kwargs={"pk": self.member.pk})
        )

        # check: both requests are denied and captaincy is unchanged
        self.captain.refresh_from_db()
        self.member.refresh_from_db()
        self.assertEqual(self_promotion.status_code, 403)
        self.assertEqual(outsider_promotion.status_code, 403)
        self.assertTrue(self.captain.is_captain)
        self.assertEqual(self.captain.team, self.team)
        self.assertIsNone(self.member.team)
        self.assertFalse(self.member.is_captain)

    def test_leave_and_delete_permissions(self):
        # Join team
        self.client.post(reverse("team:join-code"), {"team_code": str(self.team.pk)})

        # Captain attempts to leave without transferring captaincy
        self.client.force_login(self.user)
        self.client.post(reverse("team:remove_member", kwargs={"pk": self.captain.pk}))

        # Outsider attempts to remove a member
        self.client.force_login(self.admin)
        self.client.post(reverse("team:remove_member", kwargs={"pk": self.member.pk}))

        # Member attempts to delete the team
        self.client.force_login(self.user2)
        self.client.post(reverse("team:delete", kwargs={"pk": self.team.pk}))

        # Captain attempts to delete a team that still has another member
        self.client.force_login(self.user)
        self.client.post(reverse("team:delete", kwargs={"pk": self.team.pk}))

        # check: the team remains active with its original membership
        self.team.refresh_from_db()
        self.captain.refresh_from_db()
        self.member.refresh_from_db()
        self.assertTrue(self.team.is_active)
        self.assertEqual(self.team.members.count(), 2)
        self.assertEqual(self.captain.team, self.team)
        self.assertTrue(self.captain.is_captain)
        self.assertEqual(self.member.team, self.team)
        self.assertFalse(self.member.is_captain)

    def test_invalid_code_and_ineligible_join(self):
        # Attempt to join with an invalid code
        url = reverse("team:join-code")
        invalid_join = self.client.post(url, {"team_code": "invalid"})

        # Application is rejected; view the page and attempt to join
        self.member.status = STATUS_REJECTED
        self.member.save()
        team_page = self.client.get(reverse("status_team"))
        ineligible_join = self.client.post(url, {"team_code": str(self.team.pk)})

        # check: joining is unavailable and the applicant has no team
        self.member.refresh_from_db()
        self.assertEqual(invalid_join.status_code, 404)
        self.assertEqual(ineligible_join.status_code, 403)
        self.assertNotContains(team_page, 'name="team_code"')
        self.assertIsNone(self.member.team)
        self.assertFalse(self.member.is_captain)
