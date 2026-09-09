from unittest.mock import patch

from django.db import IntegrityError, transaction
from django.test import TestCase
from django.urls import reverse

from application.constants import STATUS_REJECTED
from application.models import Application
from shared.test_case import SharedTestCase
from team.codes import ADJECTIVES, SEA_CREATURES, generate_team_code
from team.models import Team
from user.models import User


class TeamCodeTestCase(TestCase):
    def test_code_format(self):
        for _ in range(100):
            code = generate_team_code()
            first, second, creature = code.split("-")
            self.assertIn(first, ADJECTIVES)
            self.assertIn(second, ADJECTIVES)
            self.assertIn(creature, SEA_CREATURES)
            self.assertTrue(
                all(word.isalpha() and word.islower() for word in code.split("-"))
            )
            self.assertLessEqual(len(code), 64)

    def test_collision_retries_and_code_survives_updates(self):
        original = Team.objects.create()
        with patch(
            "team.models.generate_team_code", return_value="happy-gentle-dolphin"
        ):
            other = Team.objects.create(code=original.code)
        self.assertEqual(other.code, "happy-gentle-dolphin")
        other.save()
        other.refresh_from_db()
        self.assertEqual(other.code, "happy-gentle-dolphin")

    def test_only_active_codes_must_be_unique(self):
        original = Team.objects.create(is_active=False)
        replacement = Team.objects.create(code=original.code)
        self.assertNotEqual(original.pk, replacement.pk)
        with self.assertRaises(IntegrityError), transaction.atomic():
            Team.objects.filter(pk=original.pk).update(is_active=True)


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
        self.client.post(reverse("team:join-code"), {"team_code": self.team.code})

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

    def test_join_normalizes_code(self):
        response = self.client.post(
            reverse("team:join-code"),
            {"team_code": f"  {self.team.code.upper().replace('-', ' ')}  "},
        )
        self.assertRedirects(response, reverse("status_team"))
        self.member.refresh_from_db()
        self.assertEqual(self.member.team, self.team)
        self.assertContains(self.client.get(reverse("status_team")), self.team.code)

    def test_full_team_returns_inline_error_and_can_retry_after_member_leaves(self):
        for index in range(3):
            user = User.objects.create_user(
                email=f"teammate{index}@example.com", password=None
            )
            Application.objects.create(
                **{
                    **self.application_fields,
                    "user": user,
                    "wave": self.wave1,
                    "resume": "resume.pdf",
                    "team": self.team,
                }
            )

        url = reverse("team:join-code")
        data = {"team_code": self.team.code}
        response = self.client.post(url, data, HTTP_ACCEPT="application/json")
        message = "This team has reached the maximum of 4 members."
        self.assertEqual(response.status_code, 409)
        self.assertEqual(response.json(), {"error": "team_full", "message": message})
        self.member.refresh_from_db()
        self.assertIsNone(self.member.team)
        self.assertEqual(self.team.members.count(), 4)

        # A normal form submission also preserves the code and shows the error.
        fallback = self.client.post(url, data)
        self.assertContains(fallback, message, status_code=409)
        self.assertContains(fallback, 'aria-invalid="true"', status_code=409)
        self.assertContains(fallback, f'value="{self.team.code}"', status_code=409)

        departing = self.team.members.filter(is_captain=False).first()
        departing.team = None
        departing.save()
        response = self.client.post(url, data, HTTP_ACCEPT="application/json")
        self.assertRedirects(response, reverse("status_team"))
        self.member.refresh_from_db()
        self.assertEqual(self.member.team, self.team)
        self.assertEqual(self.team.members.count(), 4)

    def test_reused_code_joins_active_team(self):
        self.team.is_active = False
        self.team.save()
        response = self.client.post(
            reverse("team:join-code"), {"team_code": self.team.code}
        )
        self.assertEqual(response.status_code, 404)
        replacement = Team.objects.create(code=self.team.code)
        self.client.post(reverse("team:join-code"), {"team_code": self.team.code})
        self.member.refresh_from_db()
        self.assertEqual(self.member.team, replacement)

    def test_existing_uuid_invite_still_works(self):
        response = self.client.post(reverse("team:join", kwargs={"pk": self.team.pk}))
        self.assertRedirects(response, reverse("status_team"))
        self.member.refresh_from_db()
        self.assertEqual(self.member.team, self.team)

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
        self.client.post(reverse("team:join-code"), {"team_code": self.team.code})
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
        self.client.post(reverse("team:join-code"), {"team_code": self.team.code})

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
        ineligible_join = self.client.post(url, {"team_code": self.team.code})

        # check: joining is unavailable and the applicant has no team
        self.member.refresh_from_db()
        self.assertEqual(invalid_join.status_code, 404)
        self.assertEqual(ineligible_join.status_code, 403)
        self.assertNotContains(team_page, 'name="team_code"')
        self.assertIsNone(self.member.team)
        self.assertFalse(self.member.is_captain)
