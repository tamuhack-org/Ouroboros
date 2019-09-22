import pytz
from django.core.exceptions import ValidationError
from django.utils import timezone

from application.models import Wave
from shared import test_case


class WaveManagerTestCase(test_case.SharedTestCase):
    def test_active_wave(self):
        curr_wave = Wave(
            start=timezone.now() - timezone.timedelta(days=5),
            end=timezone.now() + timezone.timedelta(days=5),
            num_days_to_rsvp=5,
        )
        curr_wave.save()
        wave = Wave.objects.active_wave()
        self.assertEqual(wave, curr_wave)

    def test_next_wave_gets_next_existing_wave(self):
        next_wave = Wave(
            start=timezone.now() + timezone.timedelta(days=5),
            end=timezone.now() + timezone.timedelta(days=6),
            num_days_to_rsvp=5,
        )
        next_wave.save()
        wave = Wave.objects.next_wave()
        self.assertEqual(wave, next_wave)

    def test_next_wave_returns_none(self):
        wave = Wave.objects.next_wave()
        self.assertIsNone(wave)

    def test_waves_transition_correctly(self):
        expiring_wave = Wave(
            start=timezone.now() - timezone.timedelta(days=5),
            end=timezone.now(),
            num_days_to_rsvp=5,
        )
        expiring_wave.save()

        future_wave = Wave(
            start=timezone.now() + timezone.timedelta(seconds=1),
            end=timezone.now() + timezone.timedelta(days=6),
            num_days_to_rsvp=5,
        )
        future_wave.save()

        self.assertEqual(Wave.objects.next_wave(), future_wave)


class WaveModelTestCase(test_case.SharedTestCase):
    def setUp(self):
        super().setUp()
        self.wave2_start = timezone.datetime(3000, 9, 7, 3, tzinfo=pytz.utc)
        self.wave2_end = self.wave2_start + timezone.timedelta(days=30)
        self.wave2 = Wave(
            start=self.wave2_start, end=self.wave2_end, num_days_to_rsvp=5
        )
        self.wave2.save()

    def test_cant_have_end_before_start(self):
        bad_wave = Wave(start=self.wave2_end, end=self.wave2_start)
        with self.assertRaises(ValidationError):
            bad_wave.full_clean()

    def test_cant_create_overlapping_waves(self):
        bad_wave_start, bad_wave_end = (
            self.wave2_start,
            self.wave2_start + timezone.timedelta(days=15),
        )
        bad_wave = Wave(start=bad_wave_start, end=bad_wave_end, num_days_to_rsvp=5)
        with self.assertRaises(ValidationError):
            bad_wave.full_clean()

    def test_can_modify_existing_wave(self):
        new_end = self.wave2.end - timezone.timedelta(days=1)
        self.wave2.end = new_end
        self.wave2.full_clean()
        self.wave2.save()
        self.wave2.refresh_from_db()
        self.assertEqual(new_end, self.wave2.end)
