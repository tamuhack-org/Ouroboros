from datetime import datetime, timedelta

import pytz
from django.test import TestCase
from django.utils import timezone

from deadlines import models


# Create your tests here.
class DeadlineTestCase(TestCase):
    def setUp(self):
        self.now = datetime.now(tz=pytz.utc)
        r1_dt = self.now + timedelta(days=3)
        self.registration1 = models.Deadline(type="registration", datetime=r1_dt)
        self.registration1.save()

        r2_dt = self.now + timedelta(days=30)
        self.registration2 = models.Deadline(type="registration", datetime=r2_dt)
        self.registration2.save()

        c1_dt = self.now + timedelta(days=3)
        self.confirmation1 = models.Deadline(type="confirmation", datetime=c1_dt)
        self.confirmation1.save()

        c2_dt = self.now + timedelta(days=30)
        self.confirmation2 = models.Deadline(type="confirmation", datetime=c2_dt)
        self.confirmation2.save()

    def test_next_available_registration(self):
        nxt = models.Deadline.registrations.next_available(self.now)
        self.assertEqual(self.registration1, nxt)

    def test_next_available_registration_takes_most_up_to_date(self):
        nxt = models.Deadline.registrations.next_available(self.now + timedelta(4))
        self.assertEqual(self.registration2, nxt)

    def test_next_available_registration_is_none_when_none_left(self):
        nxt = models.Deadline.registrations.next_available(
            self.now + timedelta(days=300)
        )
        self.assertIsNone(nxt)

    def test_next_available_confirmation(self):
        nxt = models.Deadline.confirmations.next_available(self.now)
        self.assertEqual(self.confirmation1, nxt)

    def test_next_available_confirmation_takes_most_up_to_date(self):
        nxt = models.Deadline.confirmations.next_available(self.now + timedelta(4))
        self.assertEqual(self.confirmation2, nxt)

    def test_next_available_confirmation_is_none_when_none_left(self):
        nxt = models.Deadline.confirmations.next_available(
            self.now + timedelta(days=300)
        )
        self.assertIsNone(nxt)
