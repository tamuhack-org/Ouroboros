from django import forms
from django.contrib.auth import forms as auth_forms
from django.contrib.auth import login, views, REDIRECT_FIELD_NAME
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

from hacker import models
from ouroboros import settings


class SignupForm(auth_forms.UserCreationForm):
    username = forms.CharField()
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=150)
    email = forms.EmailField()
    password1 = forms.CharField()
    password2 = forms.CharField()

    class Meta(auth_forms.UserCreationForm.Meta):
        model = models.Hacker
        fields = auth_forms.UserCreationForm.Meta.fields + ('first_name', 'last_name', 'email',)

        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
            'password1': forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}),
            'password2': forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password Again'})
        }


class HackerLoginForm(auth_forms.AuthenticationForm):
    error_messages = {
        'invalid_login': _(
            "Please enter a correct username and password. Note that both "
            "fields may be case sensitive."
        ),
        'inactive': _("This account is inactive."),
    }


class ConfirmEmailForm(forms.Form):
    template_name = 'registration/confirm_email.html'
    success_url = reverse_lazy("apply")
    email = forms.EmailField()
    confirm_code = forms.CharField(
        max_length=settings.EMAIL_CONFIRM_CODE_LENGTH, 
        min_length=settings.EMAIL_CONFIRM_CODE_LENGTH,
    )