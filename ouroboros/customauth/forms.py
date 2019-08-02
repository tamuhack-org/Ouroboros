from django import forms
from django.forms import widgets
from django.contrib.auth import forms as auth_forms
from django.contrib.auth import get_user_model
from django.contrib.auth import password_validation


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
    username = forms.EmailField(
        widget=widgets.EmailInput(attrs={"placeholder": "Email"}), label=""
    )
    password = forms.CharField(
        widget=widgets.PasswordInput(attrs={"placeholder": "Password"}), label=""
    )

    class Meta:
        fields = ["username", "password"]


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
