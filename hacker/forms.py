from django.urls import reverse_lazy
from django.contrib.auth import forms as auth_forms
from django.contrib.auth import login, views, REDIRECT_FIELD_NAME
from hacker import models
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
        model = models.Hacker
        fields = ('first_name', 'last_name', 'email', 'username','password1', 'password2')


class SignInForm(auth_forms.AuthenticationForm):

    success_url = reverse_lazy("status")
    redirect_field_name = reverse_lazy("status")
    
    def __init__(self, *args, **kwargs):
        super(SignInForm,self).__init__(*args, **kwargs)
        for fieldname in ['username', 'password']:
            self.fields[fieldname].help_text = None
            self.fields[fieldname].required = True 

    class Meta:
        model = models.Hacker
        fields = ('username', 'password')


class ConfirmEmailForm(forms.Form):

    template_name = 'registration/confirm_email.html'
    success_url = reverse_lazy("apply")
    email = forms.EmailField()
    confirm_code = forms.CharField(
        max_length=settings.EMAIL_CONFIRM_CODE_LENGTH, 
        min_length=settings.EMAIL_CONFIRM_CODE_LENGTH,
    )

CREATE_CONFIRMATION_REQUIRED_FIELDS = ['dietary_restrictions', 'shirt_size', 'hacker', 'team']


'''
VIEW_APPLICATION_FIELDS = ['major', 'gender', 'classification', 'grad_year', 'interests', 'essay', 'notes', 'hacker']

class ViewApplicationForm(forms.ModelForm):

    template_name = 'dashboard/application.html'
    hacker = forms.ChoiceField(
        choices=[(x.id, x.id) for x in models.Hacker.objects.all()],
        required=True,
        widget=forms.Select()
    )

    def __init__(self, *args, **kwargs):
        super(ViewApplicationForm, self).__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
        if instance and instance.pk:
            for fieldname in VIEW_APPLICATION_FIELDS:
                self.fields[fieldname].widget.attrs['readonly']
    
    def clean_data(self):
        instance = getattr(self, '')

    class Meta:
        model = models.Application
        fields = VIEW_APPLICATION_FIELDS
'''
    