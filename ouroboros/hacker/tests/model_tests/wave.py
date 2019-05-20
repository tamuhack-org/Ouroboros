from shared import test
from hacker import models as hacker_models
from django.utils import timezone
import datetime
import pytz


class WaveManagerTestCase(test.SharedTestCase):
    def setUp(self):
        super().setUp()
        self.create_active_wave()

        self.wave2_start = datetime.datetime(3000, 9, 7, 3, tzinfo=pytz.utc)
        self.wave2_end = self.wave2_start + datetime.timedelta(days=30)
        self.wave2 = hacker_models.Wave(start=self.wave2_start, end=self.wave2_end)
        self.wave2.save()

    def test_active_wave(self):
        wave = hacker_models.Wave.objects.active_wave()
        self.assertEqual(wave, self.wave1)

    def test_next_wave(self):
        wave = hacker_models.Wave.objects.next_wave()
        self.assertEqual(wave, self.wave2)
