from django.core import mail

from hacker import models as hacker_models
from shared import test
from django.conf import settings


class RsvpModelTestCase(test.SharedTestCase):
    def setUp(self):
        super().setUp()
        self.rsvp_fields = {"shirt_size": "S", "notes": "", "hacker": self.hacker}

    def test_sends_creation_email(self):
        rsvp = hacker_models.Rsvp(**self.rsvp_fields)
        rsvp.save()
        self.assertEqual(len(mail.outbox), 1)

        context = {
            "first_name": self.hacker.first_name,
            "event_name": settings.EVENT_NAME,
        }

        self.assertEmailBodiesEqual("emails/rsvp/created.html", context, mail.outbox[0])

    def test_sends_update_email(self):
        rsvp = hacker_models.Rsvp(**self.rsvp_fields)
        rsvp.save()

        rsvp.shirt_size = "L"
        rsvp.save()
        self.assertEqual(len(mail.outbox), 2)

        context = {
            "first_name": self.hacker.first_name,
            "event_name": settings.EVENT_NAME,
        }

        self.assertEmailBodiesEqual("emails/rsvp/updated.html", context, mail.outbox[1])
