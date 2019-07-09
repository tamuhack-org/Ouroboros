from shared import test
from hacker import models as hacker_models
from django.core import mail
from django.conf import settings


class RsvpModelTestCase(test.SharedTestCase):
    def setUp(self):
        super().setUp()
        self.create_active_wave()
        self.app = hacker_models.Application(**self.application_fields, wave=self.wave1)
        self.app.full_clean()
        self.app.save()
        self.rsvp_fields = { "notes": "", "dietary_restrictions": "", "shirt_size": ""}

    def sends_email_on_rsvp_creation(self):
        self.rsvp = hacker_models.Rsvp(**self.rsvp_fields, hacker=self.hacker)
        self.rsvp.save()
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(
            mail.outbox[0].subject,
            f"Your {settings.EVENT_NAME} RSVP has been received!",
        )
