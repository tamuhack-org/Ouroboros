from django.contrib.auth import forms as auth_forms
from hacker import models as hacker_models

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