from django import test
from django.core import mail
from hacker import models as hacker_models
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import html


class ApplicationModelTestCase(test.TestCase):
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

        self.application_fields = {
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
        }

    def ensure_email_bodies_equal(self, template_name, context, email):
        html_output = render_to_string(template_name, context)
        stripped = html.strip_tags(html_output)
        self.assertEqual(email.body, stripped)

    def test_sends_creation_email(self):
        app = hacker_models.Application(**self.application_fields)
        app.save()

        self.assertEqual(len(mail.outbox), 1)

        creation_email_template = "emails/application/created.html"
        context = {
            "first_name": self.hacker.first_name,
            "event_name": settings.EVENT_NAME,
        }
        self.ensure_email_bodies_equal(creation_email_template, context, mail.outbox[0])

    def test_sends_update_email(self):
        app = hacker_models.Application(**self.application_fields)
        app.save()

        update_email_template = "emails/application/updated.html"
        context = {
            "first_name": self.hacker.first_name,
            "event_name": settings.EVENT_NAME,
        }

        app.classification = "U2"
        app.save()
        self.assertEqual(len(mail.outbox), 2)

        self.ensure_email_bodies_equal(update_email_template, context, mail.outbox[1])

    def test_sends_approved_email(self):
        app = hacker_models.Application(**self.application_fields)
        app.save()
        approved_email_template = "emails/application/approved.html"
        context = {
            "first_name": self.hacker.first_name,
            "event_name": settings.EVENT_NAME,
        }

        app.approved = True
        app.save()
        self.assertEqual(len(mail.outbox), 2)

        self.ensure_email_bodies_equal(approved_email_template, context, mail.outbox[1])