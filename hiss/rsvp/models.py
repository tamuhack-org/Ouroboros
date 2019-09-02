from django.db import models
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


class Rsvp(models.Model):
    """Some extra information provided by a user before the event."""
    datetime_submitted = models.DateTimeField(auto_now_add=True)
    dietary_restrictions = MultiSelectField(choices=DIETARY_RESTRICTIONS, max_length=2)
    shirt_size = models.CharField(choices=SHIRT_SIZES, max_length=3)
    notes = models.TextField(max_length=500)

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return "%s, %s - Rsvp" % {
            self.user.application.last_name,
            self.user.application.first_name,
        }

