from django.conf import settings  # noqa: I001
from django.db import models


BREAKFAST = "B"
BREAKFAST_2 = "B2"
LUNCH = "L"
LUNCH_2 = "L2"
DINNER = "D"
MIDNIGHT_SNACK = "MS"

MEAL_CHOICES = [
    (BREAKFAST, "Breakfast"),
    (LUNCH, "Lunch"),
    (DINNER, "Dinner"),
    (MIDNIGHT_SNACK, "Midnight Snack"),
    (BREAKFAST_2, "Breakfast (Day 2)"),
    (LUNCH_2, "Lunch (Day 2)"),
]


class Event(models.Model):
    """An abstract model for recording activity during the event.

    (see Django docs: https://docs.djangoproject.com/en/2.2/topics/db/models/#abstract-base-classes)
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True
    )
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


class FoodEvent(Event):  # noqa: DJ008
    meal = models.CharField(max_length=14, choices=MEAL_CHOICES)


class WorkshopEvent(Event):  # noqa: DJ008
    pass


class ScheduleEvent(models.Model):
    """An item on the day-of schedule shown to hackers on their status page."""

    CATEGORY_MAIN = "MAIN"
    CATEGORY_FOOD = "FOOD"
    CATEGORY_WORKSHOP = "WORKSHOP"
    CATEGORY_ACTIVITY = "ACTIVITY"
    CATEGORY_CHOICES = [
        (CATEGORY_MAIN, "Main event"),
        (CATEGORY_FOOD, "Food"),
        (CATEGORY_WORKSHOP, "Workshop"),
        (CATEGORY_ACTIVITY, "Activity"),
    ]

    external_id = models.CharField(
        max_length=64,
        unique=True,
        null=True,
        blank=True,
        editable=False,
        help_text="ID from the website's schedule feed, set by the importer.",
    )
    name = models.CharField(max_length=100)
    start = models.DateTimeField(db_index=True)
    location = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    category = models.CharField(
        max_length=10, choices=CATEGORY_CHOICES, default=CATEGORY_MAIN
    )
    is_visible = models.BooleanField(
        default=True, help_text="Uncheck to hide this event from hackers."
    )

    class Meta:
        ordering = ["start"]

    def __str__(self):
        return self.name
