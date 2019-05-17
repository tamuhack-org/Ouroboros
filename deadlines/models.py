import datetime as dt
from typing import Union

from django.db import models

DEADLINE_TYPE_CHOICES = [
    ("registration", "registration"),
    ("confirmation", "confirmation"),
]


class DeadlineManager(models.Manager):
    def next_available(self, deadline_type: str, after_datetime: dt.datetime):
        remaining_deadlines = (
            self.get_queryset()
            .filter(type=deadline_type, datetime__gt=after_datetime)
            .order_by("datetime")
        )
        if not remaining_deadlines:
            return None
        return remaining_deadlines.first()


class ConfirmationDeadlineManager(DeadlineManager):
    def next_available(self, after_datetime=dt.datetime.now()):
        return super().next_available("confirmation", after_datetime)


class RegistrationDeadlineManager(DeadlineManager):
    def next_available(self, after_datetime=dt.datetime.now()):
        return super().next_available("registration", after_datetime)


# Create your models here.
class Deadline(models.Model):
    type = models.CharField(max_length=40, choices=DEADLINE_TYPE_CHOICES)
    datetime = models.DateTimeField()

    confirmations = ConfirmationDeadlineManager()
    registrations = RegistrationDeadlineManager()
