from django.db import models

# Create your models here.

class Hacker(models.Model):
    def __init__(self, *args, **kwargs):
        super(Hacker, self).__init__(*args, **kwargs)
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['email'].required = True
    
    first_name = models.CharField(max_length=100 )
    last_name = models.CharField(max_length=100)
    email=models.EmailField(max_length=100)
    
    # ...

    def __str__(self):
        return self. last_name

class HackerProfile(models.Model):
    major = models.CharField(max_length=100)
    gender_choices = ["Male (M)","Female (F)","Non-Binary (NB)","Prefer to not disclose (NA)" ]

    gender = CharField(max_length=100, choices=gender_choices, default='Male (M)')

    # ...

    class Meta:
        abstract = True

class Team(models.Model):
    name = models.CharField(max_length=40)
    # ... 

class Application(HackerProfile):
    resume=models.FileField(upload_to='idk/',max_length=1000)
    interests=models.TextField(max_length=300)
    essay=models.TextField(max_length=1000)
    team=models.ForeignKey(
        'Team',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    # ...
    
