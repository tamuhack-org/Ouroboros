from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from django.conf import settings
from multiselectfield import MultiSelectField
import calendar
from hacker.models import Hacker, DIETARY_RESTRICTIONS, GRAD_YEARS, SHIRT_SIZES


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


class VolunteerApplication(models.Model):
    hacker = models.OneToOneField(
        Hacker, related_name="volunteer_app", on_delete=models.CASCADE
    )
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    phone_number = PhoneNumberField()
    grad_year = models.CharField(
        "What is your anticipated graduation date?", choices=GRAD_YEARS, max_length=11
    )
    shirt_size = models.CharField(
        "Shirt size?", choices=SHIRT_SIZES, default=None, max_length=3
    )


class Shift(models.Model):
    start = models.DateTimeField()
    end = models.DateTimeField()

    volunteers = models.ManyToManyField(VolunteerApplication, related_name="shifts")

    def __str__(self):
        start_str = self.start.strftime(
            f"{calendar.day_name[self.start.weekday()]} %H:%M"
        )
        end_str = self.end.strftime(f"{calendar.day_name[self.end.weekday()]} %H:%M")
        return f"{start_str} - {end_str} ({settings.MAX_VOLUNTEERS_PER_SHIFT - len(self.volunteers.all())} spots remaining)"
