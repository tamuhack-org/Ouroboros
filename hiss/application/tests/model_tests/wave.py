import pytz
from django.core.exceptions import ValidationError
from django.utils import timezone

from application.models import Wave
from shared import test_case


class WaveManagerTestCase(test_case.SharedTestCase):
    def setUp(self):
        super().setUp()
        self.create_active_wave()

        self.wave2_start = timezone.datetime(3000, 9, 7, 3, tzinfo=pytz.utc)
        self.wave2_end = self.wave2_start + timezone.timedelta(days=30)
        self.wave2 = Wave(start=self.wave2_start, end=self.wave2_end)
        self.wave2.save()

    def test_active_wave(self):
        wave = Wave.objects.active_wave()
        self.assertEqual(wave, self.wave1)

    def test_next_wave(self):
        wave = Wave.objects.next_wave()
        self.assertEqual(wave, self.wave2)


class WaveModelTestCase(test_case.SharedTestCase):
    def test_cant_have_end_before_start(self):
        bad_wave = Wave(start=self.wave2_end, end=self.wave2_start)
        with self.assertRaises(ValidationError):
            bad_wave.full_clean()

    def test_cant_create_overlapping_waves(self):
        bad_wave_start, bad_wave_end = self.wave2_start, self.wave2_start + timezone.timedelta(days=15)
        bad_wave = Wave(start=bad_wave_start, end=bad_wave_end)
        with self.assertRaises(ValidationError):
            bad_wave.full_clean()

    def test_can_modify_existing_wave(self):
        new_end = timezone.now()
        self.wave1.end = new_end
        self.wave1.full_clean()
        self.wave1.save()
        self.wave1.refresh_from_db()
        self.assertEqual(new_end, self.wave1.end)
