from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from multiselectfield import MultiSelectField
from ouroboros import settings
import random
import string
import json


SHIRT_SIZES = (
    ('XS', 'XS'),
    ('S', 'S'),
    ('M', 'M'),
    ('L', 'L'),
    ('XL', 'XL'),
    ('XXL', 'XXL'),
) 

GENDERS = (
    ('M', 'Male'),
    ('F', 'Female'),
    ('NB', 'Non-binary'),
    ('NA', 'Prefer not to disclose'),
)

CLASSIFICATIONS = (
    ('U1', 'U1'),
    ('U2', 'U2'),
    ('U3', 'U3'),
    ('U4', 'U4'),
    ('U5', 'U5'),
)

DIETARY_RESTRICTIONS = (
    ('Vegan', 'Vegan'),
    ('Vegaterian', 'Vegarterian'),
    ('Halal', 'Halal'),
    ('Kosher', 'Kosher'),
    ('Food Allergies', 'Food Allergies'),
)

WAVE_TYPES = (
    ('Approve', 'Approve Application'),
    ('Reject', 'Reject Application'),
)

GRAD_YEARS = [(i,i) for i in range(timezone.now().year, timezone.now().year + settings.EMAIL_CONFIRM_CODE_LENGTH)]


'''
Misc. Information:

    - 'first_name' overrides AbstractUser.first_name to require not blank
    - 'last_name' overrides AbstractUser.last_name to require not blank
    - 'email' overrides AbstractUser.email to require not blank

'''

class Hacker(AbstractUser):
    ### Fields ###
    first_name = models.CharField(max_length=30, blank=False, verbose_name='first name')
    last_name = models.CharField(max_length=150, blank=False, verbose_name='last name')
    email = models.EmailField(blank=False)

    checked_in = models.NullBooleanField(blank=True)
    email_confirmed = models.BooleanField(blank=True, default=False)

    checked_in_datetime = models.DateTimeField(null=True, blank=True)

    confirm_code = models.CharField(max_length=6, blank=True, null=True)

    ### Functions ###
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


'''
~ as of April 17th, 2019 ~

    New Fields:
        - 'essay1'
        - 'essay2'
        - 'essay3'
        - 'resume'
        - 'num_hackathons_attended'
        - 'previous_attendant'
        - 'tamu_student'

    Moved Fields: (moved TO `Application`)
        - 'dietary_restrictions'

    Altered Fields:
        - 'date_submitted' -> 'application_date'

'''



class Application(models.Model):
    ### Fields ###
    major = models.CharField(max_length=50)
    gender = models.CharField(choices=GENDERS, max_length=2)
    classification = models.CharField(choices=CLASSIFICATIONS, max_length=2)
    grad_year = models.IntegerField(choices=GRAD_YEARS, verbose_name='graduation year')          
    dietary_restrictions = MultiSelectField(choices=DIETARY_RESTRICTIONS, verbose_name='dietary restrictions', blank=True)
    travel_reimbursement_required = models.BooleanField(default=False) 

    num_hackathons_attended = models.PositiveSmallIntegerField(default=0)
    previous_attendant = models.BooleanField(default=False)
    tamu_student = models.BooleanField(default=True)

    interests = models.TextField(max_length=200)
    essay1 = models.TextField(max_length=200)
    essay2 = models.TextField(max_length=200, null=True, blank=True)
    essay3 = models.TextField(max_length=200, null=True, blank=True)
    essay4 = models.TextField(max_length=200, null=True, blank=True)
    notes = models.TextField(max_length=300, blank=True, help_text='Provide any additional notes and/or comments in the text box provide')
    resume = models.FileField(upload_to='hacker_resumes', null=True, blank=True)
    
    approved = models.NullBooleanField(blank=True)
    queued_for_approval = models.NullBooleanField(blank=True)
    
    date_approved = models.DateField(null=True, blank=True)        
    date_queued_for_approval = models.DateField(null=True, blank=True) 
    date_submitted = models.DateField(auto_now_add=True, blank=True)
    
    hacker = models.OneToOneField(          
        Hacker,
        on_delete=models.CASCADE,
    )

    ### Functions ###
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
    ### Fields ###
    shirt_size = models.CharField(max_length=3, choices=SHIRT_SIZES, verbose_name='shirt size')         
    notes = models.TextField(max_length=300, blank=True, help_text='Provide any additional notes and/or comments in the text box provide')

    date_confirmed = models.DateField(auto_now_add=True, blank=True)
    
    hacker = models.OneToOneField(              
        Hacker,
        on_delete=models.CASCADE,
    )
    team = models.ForeignKey(           
        'Team', 
        on_delete=models.SET_NULL,
        null=True, 
        blank=True,
    )

    ### Functions ###
    def __str__(self):
        return '%s, %s - Confirmation' % (self.hacker.last_name, self.hacker.first_name)


class Team(models.Model):
    ### Fields ###
    name = models.CharField(max_length=40)

    ### Functions ###
    def __str__(self):
        return self.name
