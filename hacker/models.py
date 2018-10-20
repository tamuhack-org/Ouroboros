from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser

# `Hacker` model - Extends `AbstractUser` model:


class Hacker(AbstractUser):
    admitted = models.NullBooleanField(blank=True)
    # Possible Values:
    #       1. 'True' - application approved & confirmation period has begun
    #       2. 'False' - application approved & confirmation period has NOT begun
    #       3. 'NULL' - application rejected, pending review, cancelled, or DNE
    checked_in = models.NullBooleanField(blank=True)
    # Possible Values:
    #       1. 'True' - has been checked in by staff/volunteers (day of event)
    #       2. 'False' - has NOT been checked in by staff/volunteers (day of event)
    #       3. 'NULL' - will not be attending event
    admitted_datetime = models.DateTimeField(null=True, blank=True)
    checked_in_datetime = models.DateTimeField(null=True, blank=True)

    # Overrides AbstractUser.first_name to require not blank
    first_name = models.CharField(max_length=30, blank=False)

    # Overrides AbstractUser.last_name to require not blank
    last_name = models.CharField(max_length=150, blank=False)
    
    # Overrides AbstractUser.email to require not blank
    email = models.EmailField(blank=False)

    def __str__(self):
        return self.last_name

    # Hacker create() method
    @classmethod
    def create(cls, username, password, email, first_name, last_name):
        return cls(
            username=username,
            password=password,
            email=email,
            first_name=first_name,
            last_name=last_name
        )


# `HackerProfile` model
class HackerProfile(models.Model):
    major = models.CharField(max_length=100)
    # ...
