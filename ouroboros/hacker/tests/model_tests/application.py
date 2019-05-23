import datetime

from django.conf import settings
from django.core import mail
from django.utils import timezone

from hacker import models as hacker_models
from shared import test


class ApplicationModelTestCase(test.SharedTestCase):
    def setUp(self):
        super().setUp()
        self.create_active_wave()
        self.application_fields["wave"] = self.wave1

    def test_sends_creation_email(self):
        app = hacker_models.Application(**self.application_fields)
        app.save()

        self.assertEqual(len(mail.outbox), 1)
        creation_email_template = "emails/application/created.html"
        context = {
            "first_name": self.hacker.first_name,
            "event_name": settings.EVENT_NAME,
        }
        self.assertEmailBodiesEqual(creation_email_template, context, mail.outbox[0])

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

        self.assertEmailBodiesEqual(update_email_template, context, mail.outbox[1])

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
        self.assertEmailBodiesEqual(approved_email_template, context, mail.outbox[1])

    def test_sets_hacker_rsvp_deadline_when_approved(self):
        app = hacker_models.Application(**self.application_fields)
        app.save()

        app.approved = True
        app.save()

        expected = timezone.now().replace(
            hour=23, minute=59, second=59, microsecond=0
        ) + datetime.timedelta(days=settings.DAYS_TO_RSVP)
        actual = self.hacker.rsvp_deadline

        self.assertEqual(expected, actual)
