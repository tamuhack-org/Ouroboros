from django import test
from hacker import forms as hacker_forms
from hacker import models as hacker_models
from ouroboros import settings
from django.utils import timezone
import random
import string


class SignupFormTests(test.TestCase):

    def setUp(self):
        self.form_data = {
            'first_name': 'First',
            'last_name': 'Last',
            'email': 'some@email.com',
            'username': 'user',
            'password1': 'my_password',
            'password2': 'my_password'
        }

    # Valid Form Data
    def test_signup_form_valid(self):
        form = hacker_forms.SignupForm(data=self.form_data)
        self.assertTrue(form.is_valid())

    # Blank Form Data
    def test_signup_form_blank(self):
        del self.form_data['first_name']

        form = hacker_forms.SignupForm(data=self.form_data)
        self.assertFalse(form.is_valid())

    def test_signup_form_invalid(self):
        self.form_data['password1'] = 'p'

        form = hacker_forms.SignupForm(data=self.form_data)
        self.assertFalse(form.is_valid())

'''
class SignInFormTests(test.TestCase):

    def setUp(self):
        self.form_data = {
            'username': 'user',
            'password': 'my_password'
        }
        self.user = hacker_models.Hacker.objects.create_user(
            email='some@email.com', 
            username=self.form_data['username'],
            password=self.form_data['password']
        )

    # Valid Form Data
    def test_sign_in_form_valid(self):
        form = hacker_forms.SignInForm(data=self.form_data)
        self.assertTrue(form.is_valid())

    # Blank Form Data
    def test_sign_in_form_blank(self):
        del self.form_data['username']

        form = hacker_forms.SignInForm(data=self.form_data)
        self.assertFalse(form.is_valid())

    # Invalid Form Data
    def test_sign_in_form_invalid(self):
        self.form_data['password'] = 'p'

        form = hacker_forms.SignInForm(data=self.form_data)
        self.assertFalse(form.is_valid())
'''
'''
class CreateApplicationFormTests(test.TestCase):

    def setUp(self):
        self.test_username = 'user'
        self.test_password = 'password'
        self.test_email = 'some@email.com'
        self.test_user = hacker_models.Hacker.objects.create_user(
            username=self.test_username,
            email=self.test_email,
            password=self.test_password,
            first_name='first',
            last_name='last',
        )
        self.form_data = {
            'major': 'major',
            'gender': 'M',
            'classification': 'U1',
            'grad_year': timezone.now().year,
            'num_hackathons_attended': 2,
            'previous_attendant': True,
            'tamu_student': True,
            'interests': 'interests',
            'essay1': 'essay1',
            'notes': 'notes',
            'hacker': self.test_user.id,
        }
        
    # 
    #def test_create_application_form_valid_hacker_choices(self):



    # Valid Form Data
    def test_create_application_form_valid(self):
        form = hacker_forms.CreateApplicationForm(data=self.form_data)
        self.assertTrue(form.is_valid())

    # Valid Form Data w/ Blank `notes` data field
    def test_create_application_form_valid_blank_notes(self):
        del self.form_data['notes']

        form = hacker_forms.CreateApplicationForm(data=self.form_data)
        self.assertTrue(form.is_valid())

    # Blank Form Data (NOT `notes` data field)
    def test_create_application_form_blank(self):
        del self.form_data['major']

        form = hacker_forms.CreateApplicationForm(data=self.form_data)
        self.assertFalse(form.is_valid())

    # Invalid Form Data - invalid `gender` data
    def test_create_application_form_invalid_gender(self):
        self.form_data['gender'] = 'X'      # "X" is not one of the gender choices defined in `models.py`

        form = hacker_forms.CreateApplicationForm(data=self.form_data)
        self.assertFalse(form.is_valid())

    # Invalid Form Data - invalid `classification data`
    def test_create_application_form_invalid_classification(self):
        self.form_data['classification'] = 'XX'      # "XX" is not one of the classification choices defined in `models.py`

        form = hacker_forms.CreateApplicationForm(data=self.form_data)
        self.assertFalse(form.is_valid())
'''

'''
class ConfirmEmailFormTests(test.TestCase):

    def setUp(self):
        self.form_data = {
            '': '',
        }

    # Valid Form Data
    def test_confirm_email_form_valid(self):

    # Blank Form Data
    def test_confirm_email_form_blank(self):

    # Invalid Form Data
    def test_confirm_email_form_invalid(self):
'''




class FormTests(test.TestCase):         # Remove In Future
    def setUp(self):
        self.test_hacker_fields = {
            'checked_in': None,
            'checked_in_datetime': None,
            'first_name': 'First',
            'last_name': 'Last',
            'email': 'some@email.com',
            'username': 'User',
            'password': 'COFd32fsf',
        }

        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=settings.EMAIL_CONFIRM_CODE_LENGTH))

        # may require automation in future -> to assure test user doesn't exist
        self.signup_form_fields = {     
            'first_name': 'First',
            'last_name': 'Last',
            'email': 'some@email.com',
            'username': 'User',
            'password1': 'COFd32fsf',
            'password2': 'COFd32fsf',
        }

        self.signin_form_fields = {
            'username': 'User',
            'password': 'COFd32fsf',
        }

        self.confirm_email_form_fields = {
            'email': 'some@email.com',
            'confirm_code': code,
        }

        self.create_application_fields = {
            # create test instance of `Hacker`
            'major': 'Major',
            'gender': 'M',
            'classification': 'U1',
            'grad_year': timezone.now().year,
            'num_hackathons_attended': 2,
            'previous_attendant': True,
            'tamu_student': True,
            'interests': 'Interests',
            'essay1': 'Essay1',
            'notes': 'Notes',
        }

        

    def test_confirm_email_form(self):
        form_data = self.confirm_email_form_fields
        form = hacker_forms.ConfirmEmailForm(data=form_data)
        self.assertTrue(form.is_valid())
        #...

        