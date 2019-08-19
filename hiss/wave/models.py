import datetime
from django.core import exceptions
from django.db import models
from django.utils import timezone


class WaveManager(models.Manager):
    def next_wave(self, dt: datetime.datetime = timezone.now()):
        """
        Returns the next INACTIVE wave, if one exists. For the CURRENT active wave, use
        `active_wave`.
        """
        qs = self.get_queryset().filter(start__gt=dt).order_by("start")
        return qs.first()

    def active_wave(self, dt: datetime.datetime = timezone.now()):
        """
        Returns the CURRENTLY active wave, if one exists. For the next INACTIVE wave, use
        `next_wave`.
        """
        qs = self.get_queryset().filter(start__lte=dt, end__gt=dt).order_by("start")
        return qs.first()


class Wave(models.Model):
    """
    Representation of a registration period. `Application`s must be created during
    a `Wave`, and are automatically associated with a wave through the `Application`'s `pre_save` handler.
    """

    start = models.DateTimeField()
    end = models.DateTimeField()
    num_days_to_rsvp = models.IntegerField()

    objects = WaveManager()

    def clean(self):
        super().clean()
        if self.start >= self.end:
            raise exceptions.ValidationError(
                {"start": "Start date can't be after end date."}
            )
        for wave in Wave.objects.all():
            has_start_overlap = wave.start < self.start < wave.end
            has_end_overlap = wave.start < self.end < wave.end
            if has_start_overlap or has_end_overlap:
                raise exceptions.ValidationError(
                    "Cannot create wave; another wave with an overlapping time range exists."
                )
