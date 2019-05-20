from django import test
from hacker import models as hacker_models
from django.core import mail
from django.template.loader import render_to_string
from django.utils import html
from django.conf import settings


class RsvpModelTestCase(test.TestCase):
    def setUp(self):
        self.email = "dummy@email.com"
        self.password = "DummyPassword"
        self.hacker = hacker_models.Hacker.objects._create_user(
            self.email,
            self.password,
            first_name="Kennedy",
            last_name="Doe",
            is_active=True,
        )

        application_fields = {
            "major": "A",
            "gender": "M",
            "classification": "U1",
            "grad_year": 2020,
            "dietary_restrictions": "Vegan",
            "num_hackathons_attended": 0,
            "interests": "A",
            "essay1": "A",
            "essay2": "B",
            "essay3": "C",
            "essay4": "D",
            "notes": "E",
            "hacker": self.hacker,
            "approved": True,
        }
        self.app = hacker_models.Application.objects.create(**application_fields)

    def ensure_email_bodies_equal(self, template_name, context, email):
        html_output = render_to_string(template_name, context)
        stripped = html.strip_tags(html_output)
        self.assertEqual(email.body, stripped)

    def test_sends_creation_email(self):
        rsvp = hacker_models.Rsvp(shirt_size="S", notes="", hacker=self.hacker)
        rsvp.save()
        self.assertEqual(len(mail.outbox), 1)

        context = {
            "first_name": self.hacker.first_name,
            "event_name": settings.EVENT_NAME,
        }

        self.ensure_email_bodies_equal(
            "emails/rsvp/created.html", context, mail.outbox[0]
        )

    def test_sends_update_email(self):
        rsvp = hacker_models.Rsvp(shirt_size="S", notes="", hacker=self.hacker)
        rsvp.save()

        context = {
            "first_name": self.hacker.first_name,
            "event_name": settings.EVENT_NAME,
        }

        rsvp.shirt_size = "L"
        rsvp.save()

        self.ensure_email_bodies_equal(
            "emails/rsvp/updated.html", context, mail.outbox[1]
        )

