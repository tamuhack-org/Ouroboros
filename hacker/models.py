from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser

# GENDER_CHOICES - Previously named 'OPTIONS'; 
#                  Previously found in `HackerProfile` model definition;
GENDER_CHOICES = (
    	('M', 'male'),
    	('F', 'female'), 
    	('NB', 'non-binary'),
    	('NA', 'prefer to not disclose'),
    )


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
    # hacker = ....
    gender = models.CharField(
        max_length=2, 
        choices=GENDER_CHOICES,
    )
    major = models.CharField(max_length=50)
    grad_year = models.CharField(
        max_length=4, 
        choices=GRAD_YEAR_CHOICES,
    )
    date_submitted = models.DateField()     # Something's missing here ...

    class Meta:
        abstract=True
