import uuid

from django.db import models
from django.urls import reverse_lazy
from multiselectfield import MultiSelectField

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
    notes = models.TextField(max_length=500)
    transport_type = models.CharField(choices=OFFERED_TRANSPORTATION, max_length=10)
    user = models.ForeignKey("user.User", on_delete=models.CASCADE, null=False)

    def get_absolute_url(self):
        return reverse_lazy("rsvp:update", args=[self.id])
