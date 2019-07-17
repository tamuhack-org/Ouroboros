from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from django.db import models
from hacker.models import Hacker, DIETARY_RESTRICTIONS


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


MEAL_CHOICES = [(x, x) for x in ("Breakfast", "Lunch", "Dinner", "Midnight Snack")]


class Event(models.Model):
    hacker = models.ForeignKey(Hacker, on_delete=models.SET_NULL, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


class FoodEvent(Event):
    meal = models.CharField(max_length=14, choices=MEAL_CHOICES)
    restrictions = models.CharField(max_length=14, choices=DIETARY_RESTRICTIONS)


class WorkshopEvent(Event):
    pass
