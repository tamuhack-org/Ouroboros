from django import test
from django.urls import reverse_lazy

from hacker import models as hacker_models


class StatusViewTestCase(test.TestCase):
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
        response = self.client.get(reverse_lazy("status"), follow=True)
        self.assertRedirects(
            response, f"{reverse_lazy('login')}?next={reverse_lazy('status')}"
        )

    def only_one_context_active(self, desired_variable: str, context) -> bool:
        POSSIBLE_VARIABLES = [
            "NEEDS_TO_APPLY",
            "PENDING",
            "REJECTED",
            "NEEDS_TO_RSVP",
            "COMPLETE",
        ]

        assert desired_variable in POSSIBLE_VARIABLES
        POSSIBLE_VARIABLES.remove(desired_variable)
        for undesired_variable in POSSIBLE_VARIABLES:
            if undesired_variable in context:
                return False
        return desired_variable in context and context[desired_variable]

    def test_application_context_when_havent_applied(self):
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(reverse_lazy("status"))
        self.assertTrue(
            self.only_one_context_active("NEEDS_TO_APPLY", response.context)
        )

    def test_pending_context_when_application_submitted(self):
        app = hacker_models.Application(
            **self.application_fields, hacker=self.hacker
        ).save()
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(reverse_lazy("status"))
        self.assertTrue(self.only_one_context_active("PENDING", response.context))

    def test_rejected_context_when_application_rejected(self):
        app = hacker_models.Application(
            **self.application_fields, hacker=self.hacker, approved=False
        ).save()
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(reverse_lazy("status"))
        self.assertTrue(self.only_one_context_active("REJECTED", response.context))

    def test_rsvp_context_when_application_accepted(self):
        app = hacker_models.Application(
            **self.application_fields, hacker=self.hacker, approved=True
        ).save()
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(reverse_lazy("status"))
        self.assertTrue(self.only_one_context_active("NEEDS_TO_RSVP", response.context))

    def test_complete_context_when_all_steps_completed(self):
        app = hacker_models.Application(
            **self.application_fields, hacker=self.hacker, approved=True
        ).save()

        rsvp = hacker_models.Rsvp.objects.create(shirt_size="S", hacker=self.hacker)

        self.client.login(username=self.username, password=self.password)
        response = self.client.get(reverse_lazy("status"))
        self.assertTrue(self.only_one_context_active("COMPLETE", response.context))
