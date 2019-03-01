from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from multiselectfield import MultiSelectField
from ouroboros import settings
import random
import string


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

WAVE_TYPE_CHOICES = (
    ('Approve', 'Approve Application'),
    ('Reject', 'Reject Application'),
)


class Hacker(AbstractUser):
    checked_in = models.NullBooleanField(blank=True)
    checked_in_datetime = models.DateTimeField(null=True, blank=True)
    email_confirmed = models.BooleanField(blank=True, default=False)
    confirm_code = models.CharField(max_length=6, blank=True, null=True)

    # Overrides AbstractUser.first_name to require not blank
    first_name = models.CharField(max_length=30, blank=False, verbose_name='first name')

    # Overrides AbstractUser.last_name to require not blank
    last_name = models.CharField(max_length=150, blank=False, verbose_name='last name')
    
    # Overrides AbstractUser.email to require not blank
    email = models.EmailField(blank=False)

    def has_related_application(self):
        a = getattr(self, 'application', None)
        return a is not None

    def has_related_confirmation(self):
        c = getattr(self, 'confirmation', None)
        return c is not None

    def has_related_team(self):
        c = getattr(self, 'confirmation', None)
        if c is not None:
            t = getattr(c, 'team', None)
            return t is not None
        else:
            return False

    def get_related_application(self):
        a = getattr(self, 'application', None)
        return a

    def generate_confirm_code(self):
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=settings.EMAIL_CONFIRM_CODE_LENGTH))
        setattr(self, 'confirm_code', code)
        self.save()

    def check_confirm_code(self, code):
        if getattr(self, 'confirm_code', None) is None:
            return False
        else:
            confirm_code = getattr(self, 'confirm_code', None)
            return (str(confirm_code) == str(code))

    def confirm_email(self, code):
        if self.check_confirm_code(code):
            setattr(self, 'email_confirmed', True)
            setattr(self, 'confirm_code', None)
            self.save()
            return True
        # return 'False' if check_confirm_code(code) returns 'False'
        else:
            setattr(self, 'first_name', 'lol nope')
            return False

    def has_confirmed_email(self):
        return self.email_confirmed

    def __str__(self):
        return '%s, %s' % (self.last_name, self.first_name)


class Application(models.Model):
    major = models.CharField(max_length=50)
    gender = models.CharField(choices=GENDER_CHOICES, max_length=2)
    classification = models.CharField(choices=CLASSIFICATION_CHOICES, max_length=2)
    grad_year = models.IntegerField(choices=settings.GRAD_YEAR_CHOICES, verbose_name='graduation year')          
    interests = models.TextField(max_length=200)
    essay = models.TextField(max_length=200)
    #resume = models.FileField( ... ) 
    notes = models.TextField(max_length=300, blank=True, help_text='Provide any additional notes and/or comments in the text box provide')
    approved = models.NullBooleanField(blank=True)
    queued_for_approval = models.NullBooleanField(blank=True)
    date_approved = models.DateField(null=True, blank=True)        
    date_queued_for_approval = models.DateField(null=True, blank=True) 
    date_submitted = models.DateField(auto_now_add=True, blank=True)
    hacker = models.OneToOneField(          
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )    
    
    def __str__(self):
        return '%s, %s - Application' % (self.hacker.last_name, self.hacker.first_name)

    def get_first_name(self):
        fn = getattr(self.hacker, 'first_name', None)
        return fn

    def get_last_name(self):
        ln = getattr(self.hacker, 'last_name', None)
        return ln

    def get_email(self):
        email = getattr(self.hacker, 'email', None)
        return email

    def get_is_active(self):
        active = getattr(self.hacker, 'is_active', None)
        return active

    get_first_name.short_description = "First Name"
    get_last_name.short_description = "Last Name"
    get_is_active.short_description = "Active"


class Confirmation(models.Model):
    dietary_restrictions = MultiSelectField(choices=DIETARY_RESTRICTION_CHOICES, verbose_name='dietary restrictions', blank=True)                                                # TO-DO TEST
    travel_reimbursement_required = models.BooleanField(default=False)          
    date_confirmed = models.DateField(auto_now_add=True, blank=True)
    notes = models.TextField(max_length=300, blank=True, help_text='Provide any additional notes and/or comments in the text box provide')
    shirt_size = models.CharField(         
        max_length=3,
        choices=SHIRT_SIZE_CHOICES,
        verbose_name='shirt size',
    )
    hacker = models.OneToOneField(              
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    team = models.ForeignKey(           
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
