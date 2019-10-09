import uuid
from typing import Type

from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse_lazy
from multiselectfield import MultiSelectField

from user.models import User

DIETARY_RESTRICTIONS = (
    ("Vg", "Vegan"),
    ("V", "Vegetarian"),
    ("H", "Halal"),
    ("K", "Kosher"),
    ("FA", "Food Allergies"),
)

SHIRT_SIZES = (
    ("XS", "XS"),
    ("S", "S"),
    ("M", "M"),
    ("L", "L"),
    ("XL", "XL"),
    ("XXL", "XXL"),
)

OFFERED_TRANSPORTATION = (
    ("drive", "Driving"),
    ("bus-tu", "TAMUhack Bus - UT Austin"),
    ("bus-utd", "TAMUhack Bus - UTD"),
    ("bus-uta", "TAMUhack Bus - UTA"),
    ("bus-utsa", "TAMUhack Bus - UTSA"),
    ("bus-utrgv", "TAMUhack Bus - UTRGV"),
    ("other-bus", "Other Bus (Greyhound, Megabus, etc.)"),
    ("walk-cycle", "Walking/Cycling"),
)


class Rsvp(models.Model):
    """Some extra information provided by a user before the event."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    datetime_submitted = models.DateTimeField(auto_now_add=True)
    dietary_restrictions = MultiSelectField(
        choices=DIETARY_RESTRICTIONS, null=True, blank=True
    )
    shirt_size = models.CharField(choices=SHIRT_SIZES, max_length=3)
    notes = models.TextField(max_length=500, null=True, blank=True)
    transport_type = models.CharField(choices=OFFERED_TRANSPORTATION, max_length=10)
    user = models.ForeignKey("user.User", on_delete=models.CASCADE, null=False)

    def get_absolute_url(self):
        return reverse_lazy("rsvp:update", args=[self.id])


@receiver(post_save, sender=Rsvp)
def rsvp_post_save(sender: Type[Rsvp], instance: Rsvp, created: bool, **_kwargs):
    if created:
        user: User = instance.user
        user.send_html_email(
            "rsvp/emails/created.html",
            {"event_name": settings.EVENT_NAME},
            f"Regarding your {settings.EVENT_NAME} application",
        )
