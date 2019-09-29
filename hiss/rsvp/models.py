from django.db import models
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

    datetime_submitted = models.DateTimeField(auto_now_add=True)
    dietary_restrictions = MultiSelectField(choices=DIETARY_RESTRICTIONS, max_length=2)
    shirt_size = models.CharField(choices=SHIRT_SIZES, max_length=3)
    notes = models.TextField(max_length=500)
    transport_type = models.CharField(choices=OFFERED_TRANSPORTATION, max_length=10)
