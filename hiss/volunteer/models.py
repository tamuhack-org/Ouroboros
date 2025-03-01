from django.conf import settings
from django.db import models

from application.models import DietaryRestriction

# BREAKFAST = "B"
# BREAKFAST_2 = "B2"
# LUNCH = "L"
# LUNCH_2 = "L2"
# DINNER = "D"
# MIDNIGHT_SNACK = "MS"
# MEAL_CHOICES = [
#     (BREAKFAST, "Breakfast"),
#     (LUNCH, "Lunch"),
#     (DINNER, "Dinner"),
#     (MIDNIGHT_SNACK, "Midnight Snack"),
#     (BREAKFAST_2, "Breakfast (Day 2)"),
#     (LUNCH_2, "Lunch (Day 2)"),
# ]


# START HOTFIX


BREAKFAST = "B"
BREAKFAST_2 = "B2"
LUNCH = "L"
LUNCH_2 = "L2"
DINNER = "D"
MIDNIGHT_SNACK = "MS"


# MEAL CHOICES & Diet Option merged into one. Hacky hotfix solution
# Vegan Choices
BREAKFAST_V = "B_V"
BREAKFAST_2_V = "B2_V"
LUNCH_V = "L_V"
LUNCH_2_V = "L2_V"
DINNER_V = "D_V"
MIDNIGHT_SNACK_V = "MS_V"

# Gluten Choices
BREAKFAST_G = "B_G"
BREAKFAST_2_G = "B2_G"
LUNCH_G = "L_G"
LUNCH_2_G = "L2_G"
DINNER_G = "D_G"
MIDNIGHT_SNACK_G = "MS_G"


MEAL_CHOICES = [
    (BREAKFAST, "Breakfast"),
    (LUNCH, "Lunch"),
    (DINNER, "Dinner"),
    (MIDNIGHT_SNACK, "Midnight Snack"),
    (BREAKFAST_2, "Breakfast (Day 2)"),
    (LUNCH_2, "Lunch (Day 2)"),
    (BREAKFAST_G, "Breakfast - [Gluten Free]"),
    (LUNCH_G, "Lunch - [Gluten Free]"),
    (DINNER_G, "Dinner - [Gluten Free]"),
    (MIDNIGHT_SNACK_G, "Midnight Snack - [Gluten Free]"),
    (BREAKFAST_2_G, "Breakfast (Day 2) - [Gluten Free]"),
    (LUNCH_2_G, "Lunch (Day 2) - [Gluten Free]"),
    (BREAKFAST_V, "Breakfast - [Vegan]"),
    (LUNCH_V, "Lunch - [Vegan]"),
    (DINNER_V, "Dinner - [Vegan]"),
    (MIDNIGHT_SNACK_V, "Midnight Snack - [Vegan]"),
    (BREAKFAST_2_V, "Breakfast (Day 2) - [Vegan]"),
    (LUNCH_2_V, "Lunch (Day 2) - [Vegan]"),
]


# END HOTFIX


class Event(models.Model):
    """An abstract model (see Django docs: https://docs.djangoproject.com/en/2.2/topics/db/models/#abstract-base-classes)
    for recording activity during the event.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True
    )
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


class FoodEvent(Event):
    meal = models.CharField(max_length=14, choices=MEAL_CHOICES)
    restrictions = models.ManyToManyField(DietaryRestriction)


class WorkshopEvent(Event):
    pass
