from django.contrib.auth import forms as auth_forms
from django.contrib.auth import login, views, REDIRECT_FIELD_NAME
from hacker import models as hacker_models
from ouroboros import settings
from django import forms

SIGNUP_REQUIRED_FIELDS = ('first_name', 'last_name', 'email', 'username', 'password1', 'password2')

class SignupForm(auth_forms.UserCreationForm):

    def __init__(self, *args, **kwargs):
        super(SignupForm, self).__init__(*args, **kwargs)
        for fieldname in ['username', 'password1', 'password2']:
            self.fields[fieldname].help_text = None
        for fieldname in SIGNUP_REQUIRED_FIELDS:
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

    template_name = 'registration/confirm_email.html'
    success_url = settings.CONFIRM_EMAIL_REDIRECT_URL
    email = forms.EmailField()
    confirm_code = forms.CharField(
        max_length=settings.EMAIL_CONFIRM_CODE_LENGTH, 
        min_length=settings.EMAIL_CONFIRM_CODE_LENGTH,
    )


CREATE_APPLICATION_REQUIRED_FIELDS = ['major', 'gender', 'classification', 'grad_year', 'interests', 'essay', 'hacker']

class CreateApplicationForm(forms.ModelForm):

    template_name = 'registration/apply.html'
    success_url = settings.CREATE_APPLICATION_REDIRECT_URL
    hacker = forms.ChoiceField(
        choices=[(x.id, x.id) for x in hacker_models.Hacker.objects.all()],
        required=True,
        widget=forms.Select()
    )

    def __init__(self, *args, **kwargs):
        super(CreateApplicationForm, self).__init__(*args, **kwargs)
        self.fields['hacker'].choices = [(x.id, x.id) for x in hacker_models.Hacker.objects.all()]
        for fieldname in CREATE_APPLICATION_REQUIRED_FIELDS:
            self.fields[fieldname].required = True
        for fieldname in ['notes']:
            self.fields[fieldname].required = False

    class Meta:
        model = hacker_models.Application
        fields = ['major', 'gender', 'classification', 'grad_year', 'interests', 'essay', 'notes', 'hacker']
