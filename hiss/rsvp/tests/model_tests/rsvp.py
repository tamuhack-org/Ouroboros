from django.core import mail

from rsvp.models import Rsvp
from shared import test_case


class RsvpModelTestCase(test_case.SharedTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.rsvp_fields = {
            "shirt_size": "XS",
            "dietary_restrictions": ["Vg", "V", "H", "FA", "K"],
            "notes": "",
        }

    def test_rsvp_creation_sends_email(self):
        rsvp = Rsvp(**self.rsvp_fields, user=self.user)
        rsvp.save()

        self.assertEqual(len(mail.outbox), 1)
