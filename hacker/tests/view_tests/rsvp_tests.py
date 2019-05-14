from django import test
from django.urls import reverse_lazy
from hacker import models as hacker_models


class RsvpViewTestCase(test.TestCase):
    def setUp(self):
        self.username = "test_username"
        self.password = "abcedfg"
        self.email_addr = "kdoe@email.com"

        self.application_fields = {
            "major": "DUMMY",
            "gender": "M",
            "classification": "U3",
            "grad_year": 2020,
            "dietary_restrictions": "Vegan",
            "travel_reimbursement_required": False,
            "num_hackathons_attended": 0,
            "previous_attendant": False,
            "tamu_student": False,
            "interests": "A",
            "essay1": "A",
        }
        self.hacker = hacker_models.Hacker.objects.create_user(
            username=self.username,
            password=self.password,
            email=self.email_addr,
            first_name="Kennedy",
            last_name="Doe",
            is_active=True,
        )
        super().setUp()

    def test_redirects_when_not_signed_in(self):
        response = self.client.get(reverse_lazy("rsvp"))
        self.assertRedirects(
            response, f"{reverse_lazy('login')}?next={reverse_lazy('rsvp')}"
        )

    def test_denies_rsvp_access_when_not_applied(self):
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(reverse_lazy("rsvp"))
        self.assertEqual(response.status_code, 403)

    def test_denies_rsvp_access_when_not_approved(self):

        app = hacker_models.Application(**self.application_fields, hacker=self.hacker)
        app.save()
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(reverse_lazy("rsvp"))
        self.assertEqual(response.status_code, 403)

        app.approved = False
        app.save()
        response = self.client.get(reverse_lazy("rsvp"))
        self.assertEqual(response.status_code, 403)
