from django.contrib.auth import forms as auth_forms
from django.contrib.auth import login, views, REDIRECT_FIELD_NAME
from hacker import models as hacker_models
from ouroboros import settings
from django import forms

REQUIRED_FIELDS = ('first_name', 'last_name', 'email', 'username', 'password1', 'password2')

class SignupForm(auth_forms.UserCreationForm):

    def __init__(self, *args, **kwargs):
        super(SignupForm, self).__init__(*args, **kwargs)
        for fieldname in ['username', 'password1', 'password2']:
            self.fields[fieldname].help_text = None
        for fieldname in REQUIRED_FIELDS:
            self.fields[fieldname].required = True

    class Meta:
        model = hacker_models.Hacker
        fields = ('first_name', 'last_name', 'email', 'username','password1', 'password2')


class SignInForm(auth_forms.AuthenticationForm):

    success_url = settings.LOGIN_REDIRECT_URL
    redirect_field_name = settings.LOGIN_REDIRECT_URL
    def __init__(self, *args, **kwargs):
        super(SignInForm,self).__init__(*args, **kwargs)
        for fieldname in ['username', 'password']:
            self.fields[fieldname].help_text = None
            self.fields[fieldname].required = True 

    class Meta:
        model = hacker_models.Hacker
        fields = ('username', 'password')


class ConfirmEmailForm(forms.Form):

    email = forms.EmailField()
    confirm_code = forms.CharField(max_length=6, min_length=6)

    
