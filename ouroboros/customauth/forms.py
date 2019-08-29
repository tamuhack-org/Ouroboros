from django import forms
from django.contrib.auth import forms as auth_forms
from django.contrib.auth import get_user_model
from django.contrib.auth import password_validation
from django.core.exceptions import ValidationError
from django.forms import widgets

from hacker import models as hacker_models


class SignupForm(auth_forms.UserCreationForm):
    email = forms.EmailField(
        widget=widgets.EmailInput(attrs={"placeholder": "Email"}), label=""
    )
    password1 = forms.CharField(
        widget=widgets.PasswordInput(attrs={"placeholder": "Enter Password"}), label=""
    )
    password2 = forms.CharField(
        widget=widgets.PasswordInput(attrs={"placeholder": "Confirm Password"}),
        label="",
    )

    def clean_email(self):
        email: str = self.cleaned_data["email"]
        _, domain = email.split("@")
        # TODO(SaltyQuetzals) Delete this line when HH over to enable TH registration
        if not domain.lower().endswith("tamu.edu"):
            raise forms.ValidationError("You must sign up with your TAMU email")
        return email

    class Meta:
        model = get_user_model()
        fields = ("email", "password1", "password2")


class LoginForm(auth_forms.AuthenticationForm):
    error_messages = {
        'invalid_login': "Please enter a correct %(username)s and password. Note that both fields may be "
                         "case-sensitive. Make sure you've activated your account via email as well.",
        'inactive': "This account is inactive.",
    }
    username = forms.EmailField(
        widget=widgets.EmailInput(attrs={"placeholder": "Email"}), label=""
    )
    password = forms.CharField(
        widget=widgets.PasswordInput(attrs={"placeholder": "Password"}), label=""
    )

    class Meta:
        fields = ["username", "password"]


class ResendActivationEmailForm(forms.Form):
    email = forms.EmailField(widget=widgets.EmailInput(attrs={"placeholder": "Email"}), label="")

    def clean_email(self):
        data = self.cleaned_data["email"]
        if not hacker_models.Hacker.objects.filter(email=data).exists():
            raise ValidationError("No account with this email exists.")
        hacker: hacker_models.Hacker = hacker_models.Hacker.objects.get(email=data)
        if hacker.is_active:
            raise ValidationError("This account has already been activated.")
        return data


class PlaceholderPasswordResetForm(auth_forms.PasswordResetForm):
    """
    It's the same as the parent form, just overriding the attributes to be placeholders
    instead of labels.
    """
    email = forms.EmailField(widget=widgets.EmailInput(attrs={"placeholder": "Email"}), label="")


class PlaceholderSetPasswordForm(auth_forms.SetPasswordForm):
    """
    It's the same as the parent form, just overriding attributes to be placeholders instead of labels.
    """
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={"placeholder": "New password"}),
        strip=False,
        help_text=password_validation.password_validators_help_text_html(),
        label=""
    )
    new_password2 = forms.CharField(
        strip=False,
        widget=forms.PasswordInput(attrs={"placeholder": "Confirm new password"}),
        label=""
    )
