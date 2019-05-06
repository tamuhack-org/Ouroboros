import random
import string

from django import test
from django.urls import reverse_lazy
from django.utils import timezone

from core import views as core_views
from hacker import forms as hacker_forms
from hacker import models as hacker_models
from ouroboros import settings


class ViewTests(test.TestCase):

    def setUp(self):
        self.test_username = 'user'
        self.test_password = 'password'
        self.test_email = 'some@email.com'
        self.test_user = hacker_models.Hacker.objects.create_user(
            username=self.test_username,
            email=self.test_email,
            password=self.test_password
        )

    ''' `ConfirmEmailView` '''

    # Confirm that anonymous users are redirected to login page
    def test_confirm_email_view_denies_anonymous(self):     # test fails
        response = self.client.get(reverse_lazy("confirm_email"))
        self.assertRedirects(response, reverse_lazy("login"))
        

    # Confirm
    def test_confirm_email_view_loads(self):                # Test Works!!!
        self.client.login(username=self.test_username, password=self.test_password)
        print(reverse_lazy("confirm_email"))
        response = self.client.get(reverse_lazy("confirm_email"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/confirm_email.html')

    # Confirm that view rejects blank data                  # Test does NOT work
    def test_confirm_email_view_fails_blank(self):
        self.client.login(username=self.test_username, password=self.test_password)
        response = self.client.get(reverse_lazy("confirm_email"), {})
        self.assertFormError(response, hacker_forms.ConfirmEmailForm, 'email', 'This field is required')
        self.assertFormError(response, hacker_forms.ConfirmEmailForm, 'confirm_code', 'This field is required')

    # Confirm that view rejects invalid data
    '''
    def test_confirm_email_view_fails_invalid(self):
        self.client.login(username=self.test_username, password=self.test_password)
        response = self.client.get(reverse_lazy("confirm_email"), {'email': '', })
    '''

    ''' `SignupView` '''

    #

    # Confirm that view rejects blank data

    # Confirm that view rejects invalid data

    # Confirm that view accepts valid data


class CreateApplicationViewTests(test.TestCase):

    def setUp(self):
        self.test_username = 'user'
        self.test_password = 'password'
        self.test_email = 'some@email.com'
        self.test_user = hacker_models.Hacker.objects.create_user(
            username=self.test_username,
            email=self.test_email,
            password=self.test_password
        )

        self.application_fields = {
            'major': 'Engineering',
            'gender': 'M',
            'classification': 'U3',
            'grad_year': timezone.now().year,
            'interests': 'interests',
            'essay1': 'essay1',
            'notes': 'notes',
            'hacker': self.test_user.id,
        }

    def test_create_application_view_denies_anonymous(self):
        response = self.client.get(reverse_lazy("apply"))
        self.assertRedirects(response, reverse_lazy("login"))

    def test_create_application_view_denies_user_email_not_confirmed(self):
        self.client.login(username=self.test_username, password=self.test_password)
        setattr(self.test_user, 'email_confirmed', False)
        response = self.client.get(reverse_lazy("apply"))
        self.assertRedirects(response, reverse_lazy("confirm_email"))

    def test_create_application_view_loads(self):
        self.client.login(username=self.test_username, password=self.test_password)
        setattr(self.test_user, 'email_confirmed', True)
        response = self.client.get(reverse_lazy("apply"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, core_views.CreateApplicationView.template_used)

    def test_create_application_view_fails_blank(self):
        self.client.login(username=self.test_username, password=self.test_password)
        setattr(self.test_user, 'email_confirmed', True)
        response = self.client.post(reverse_lazy("apply"), {})   # blank input data
        self.assertFormError(response, 'CreateApplicationForm', 'major', 'This field is required.')
        self.assertFormError(response, 'CreateApplicationForm', 'gender', 'This field is required.')
        self.assertFormError(response, 'CreateApplicationForm', 'classification', 'This field is required.')
        self.assertFormError(response, 'CreateApplicationForm', 'grad_year', 'This field is required.')
        self.assertFormError(response, 'CreateApplicationForm', 'num_hackathons_attended', 'This field is required.')
        self.assertFormError(response, 'CreateApplicationForm', 'previous_attendant', 'This field is required.')
        self.assertFormError(response, 'CreateApplicationForm', 'tamu_student', 'This field is required.')
        self.assertFormError(response, 'CreateApplicationForm', 'interests', 'This field is required.')
        self.assertFormError(response, 'CreateApplicationForm', 'essay1', 'This field is required.')
        self.assertFormError(response, 'CreateApplicationForm', 'hacker', 'This field is required.')

    '''
    def test_create_application_view_fails_invalid(self):
        # ...

    def test_create_application_view_passes_valid(self):
        # ...
    '''
