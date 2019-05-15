from django.contrib.auth import forms as auth_forms
from django.contrib.auth import get_user_model


class SignupForm(auth_forms.UserCreationForm):
    class Meta:
        model = get_user_model()
        fields = (
            "email",
            "first_name",
            "last_name",
            "password1",
            "password2",
        )

