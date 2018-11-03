from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from multiselectfield import MultiSelectField

SHIRT_SIZE_CHOICES = (
    ('XS', 'XS'),
    ('S', 'S'),
    ('M', 'M'),
    ('L', 'L'),
    ('XL', 'XL'),
    ('XXL', 'XXL'),
) 

GENDER_CHOICES = (
    ('M', 'Male'),
    ('F', 'Female'),
    ('NB', 'Non-binary'),
    ('NA', 'Prefer not to disclose'),
)

CLASSIFICATION_CHOICES = (
    ('U1', 'U1'),
    ('U2', 'U2'),
    ('U3', 'U3'),
    ('U4', 'U4'),
    ('U5', 'U5'),
)


DIETARY_RESTRICTION_CHOICES = (
    ('Vegan', 'Vegan'),
    ('Vegaterian', 'Vegarterian'),
    ('Halal', 'Halal'),
    ('Kosher', 'Kosher'),
    ('Food Allergies', 'Food Allergies'),
)

GRAD_YEAR_CHOICES = [(i,i) for i in range(timezone.now().year, timezone.now().year + 6)]        # TO-DO TEST


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
    first_name = models.CharField(max_length=30, blank=False, verbose_name='First Name')

    # Overrides AbstractUser.last_name to require not blank
    last_name = models.CharField(max_length=150, blank=False, verbose_name='Last Name')
    
    # Overrides AbstractUser.email to require not blank
    email = models.EmailField(blank=False)

    def test_has_related_application(self):
        hacker_to_test = hacker_models.Hacker(**self.hacker_fields)
        self.assertFalse(hacker_to_test.has_related_application())            

        application_to_test = hacker_models.Application(hacker=hacker_to_test, **self.application_fields)
        self.assertTrue(hacker_to_test.has_related_application())  

    def test_has_related_confirmation(self):
        hacker_to_test = hacker_models.Hacker(**self.hacker_fields)
        application_to_test = hacker_models.Application(hacker=hacker_to_test, **self.application_fields)
        self.assertFalse(hacker_to_test.has_related_confirmation())  

        confirmation_to_test = hacker_models.Confirmation(hacker=hacker_to_test, **self.confirmation_fields)
        self.assertTrue(hacker_to_test.has_related_confirmation())  

    def test_has_related_team(self):
        hacker_to_test = hacker_models.Hacker(**self.hacker_fields)
        self.assertFalse(hacker_to_test.has_related_team())

        application_to_test = hacker_models.Application(hacker=hacker_to_test, **self.application_fields)
        self.assertFalse(hacker_to_test.has_related_team())

        team_to_test = hacker_models.Team(**self.team_fields)
        self.assertFalse(hacker_to_test.has_related_team())

        self.confirmation_fields['team'] = team_to_test
        confirmation_to_test = hacker_models.Confirmation(hacker=hacker_to_test, **self.confirmation_fields)
        self.assertTrue(hacker_to_test.has_related_team())

    def __str__(self):
        return '%s, %s' % (self.last_name, self.first_name)


class HackerProfile(models.Model):
    hacker = models.OneToOneField(          # TO-DO TEST
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    major = models.CharField(max_length=50)
    gender = models.CharField(choices=GENDER_CHOICES, max_length=2)
    classification = models.CharField(choices=CLASSIFICATION_CHOICES, max_length=2)
    grad_year = models.IntegerField(choices=GRAD_YEAR_CHOICES, verbose_name='Graduation Year')

    class Meta:         # TO-DO TEST
        abstract = True


class Application(HackerProfile):
    #resume = models.FileField( ... )           # TO-DO TEST
    interests = models.TextField(max_length=200)
    essay = models.TextField(max_length=200)
    approved = models.NullBooleanField(blank=True)
    date_approved = models.DateField(null=True, blank=True)         # TO-DO TEST
    date_submitted = models.DateField(auto_now_add=True, blank=True)
    notes = models.TextField(max_length=300, blank=True, help_text='Provide any additional notes and/or comments in the text box provide')


    def __str__(self):
        return '%s, %s - Profile' % (self.hacker.last_name, self.hacker.first_name)


class Confirmation(models.Model):
    shirt_size = models.CharField(          # TO-DO TEST
        max_length=3,
        choices=SHIRT_SIZE_CHOICES,
        verbose_name='Shirt Size',
    )
    dietary_restrictions = MultiSelectField(choices=DIETARY_RESTRICTION_CHOICES, verbose_name='Dietary Restrictions', blank=True)                                                # TO-DO TEST
    travel_reimbursement_required = models.BooleanField(default=False)          # TO-DO TEST
    date_confirmed = models.DateField(auto_now_add=True, blank=True)
    notes = models.TextField(max_length=300, blank=True, help_text='Provide any additional notes and/or comments in the text box provide')
    hacker = models.OneToOneField(              # TO-DO TEST
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    team = models.ForeignKey(           # TO-DO TEST
        'Team', 
        on_delete=models.SET_NULL,
        null=True, 
        blank=True,
    )

    def __str__(self):
        return '%s, %s - Confirmation' % (self.hacker.last_name, self.hacker.first_name)


class Team(models.Model):
    name = models.CharField(max_length=40)

    def __str__(self):
        return self.name

'''
class Wave(models.Model):
    confirmation_period_start = models.DateTimeField()
    confirmation_period_end = models.DateTimeField()
'''

